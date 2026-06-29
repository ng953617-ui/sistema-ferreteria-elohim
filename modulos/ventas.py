"""Módulo POS / punto de venta."""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from config.conexion import fetch_df, get_connection


def _init_cart() -> None:
    st.session_state.setdefault("carrito", [])


def _buscar_productos(texto: str) -> pd.DataFrame:
    if not texto:
        return fetch_df(
            """
            SELECT id_producto, codigo_barra, nombre, precio_venta, stock_actual, unidad_medida
            FROM productos
            WHERE activo=1
            ORDER BY nombre
            LIMIT 100
            """
        )
    return fetch_df(
        """
        SELECT id_producto, codigo_barra, nombre, precio_venta, stock_actual, unidad_medida
        FROM productos
        WHERE activo=1 AND (nombre LIKE %s OR codigo_barra LIKE %s)
        ORDER BY nombre
        LIMIT 100
        """,
        (f"%{texto}%", f"%{texto}%"),
    )


def mostrar(rol: str) -> None:
    """Registra ventas rápidas, actualiza inventario y genera movimientos de salida."""
    _init_cart()
    st.title("Punto de venta")
    st.caption("Venta rápida por búsqueda de texto o código de barras. Métodos: efectivo y transferencia.")

    col_buscar, col_resumen = st.columns([1.2, 1])
    with col_buscar:
        st.subheader("Agregar producto")
        texto = st.text_input("Buscar / escanear código", placeholder="cemento, pvc, 902124...")
        productos = _buscar_productos(texto)
        if productos.empty:
            st.info("No hay productos disponibles con esa búsqueda.")
        else:
            id_producto = st.selectbox(
                "Producto",
                productos["id_producto"].tolist(),
                format_func=lambda x: productos.loc[productos["id_producto"] == x, "nombre"].iloc[0],
            )
            prod = productos[productos["id_producto"] == id_producto].iloc[0]
            st.write(f"**Precio:** ${float(prod['precio_venta']):,.2f} | **Stock:** {prod['stock_actual']} {prod['unidad_medida']}")
            cantidad = st.number_input("Cantidad", min_value=0.01, step=1.0, value=1.0)
            if st.button("Agregar al carrito", use_container_width=True):
                if Decimal(str(cantidad)) > Decimal(str(prod["stock_actual"])):
                    st.error("La cantidad solicitada supera el stock disponible.")
                else:
                    item = {
                        "id_producto": int(prod["id_producto"]),
                        "producto": prod["nombre"],
                        "cantidad": float(cantidad),
                        "precio_unitario": float(prod["precio_venta"]),
                        "subtotal": float(Decimal(str(cantidad)) * Decimal(str(prod["precio_venta"]))),
                    }
                    st.session_state["carrito"].append(item)
                    st.success("Producto agregado al carrito.")
                    st.rerun()

    with col_resumen:
        st.subheader("Carrito")
        carrito = st.session_state.get("carrito", [])
        if carrito:
            df_cart = pd.DataFrame(carrito)
            st.dataframe(df_cart[["producto", "cantidad", "precio_unitario", "subtotal"]], use_container_width=True, hide_index=True)
            total = float(df_cart["subtotal"].sum())
            st.metric("Total", f"${total:,.2f}")
            if st.button("Vaciar carrito", use_container_width=True):
                st.session_state["carrito"] = []
                st.rerun()
        else:
            st.info("El carrito está vacío.")

    st.markdown("---")
    st.subheader("Confirmar venta")
    clientes = fetch_df("SELECT id_cliente, nombre, tipo_cliente FROM clientes ORDER BY nombre")
    carrito = st.session_state.get("carrito", [])
    if not carrito:
        st.warning("Agregue productos al carrito para registrar una venta.")
        return

    with st.form("form_confirmar_venta"):
        metodo = st.selectbox("Método de pago", ["Efectivo", "Transferencia"])
        tipo_comp = st.selectbox("Tipo de comprobante", ["Factura interna", "Consumidor final", "CCF"])
        id_cliente = None
        if not clientes.empty:
            opciones = [0] + clientes["id_cliente"].tolist()
            id_sel = st.selectbox(
                "Cliente",
                opciones,
                format_func=lambda x: "Venta rápida / consumidor final" if x == 0 else clientes.loc[clientes["id_cliente"] == x, "nombre"].iloc[0],
            )
            id_cliente = None if id_sel == 0 else int(id_sel)
        observaciones = st.text_area("Observaciones", value="Venta registrada desde POS")
        confirmar = st.form_submit_button("Registrar venta", use_container_width=True)

    if confirmar:
        _registrar_venta(carrito, metodo, tipo_comp, id_cliente, observaciones)


def _registrar_venta(carrito: list[dict], metodo: str, tipo_comp: str, id_cliente: int | None, observaciones: str) -> None:
    total = sum(Decimal(str(item["subtotal"])) for item in carrito)
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Verificación final de inventario con bloqueo.
        for item in carrito:
            cur.execute("SELECT stock_actual FROM productos WHERE id_producto=%s FOR UPDATE", (item["id_producto"],))
            result = cur.fetchone()
            if not result:
                raise ValueError(f"Producto no encontrado: {item['producto']}")
            stock_actual = Decimal(str(result[0]))
            if Decimal(str(item["cantidad"])) > stock_actual:
                raise ValueError(f"Stock insuficiente para {item['producto']}. Disponible: {stock_actual}")

        cur.execute(
            """
            INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago, tipo_comprobante, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (st.session_state.get("id_usuario"), id_cliente, total, metodo, tipo_comp, observaciones),
        )
        id_venta = cur.lastrowid

        for item in carrito:
            cantidad = Decimal(str(item["cantidad"]))
            precio = Decimal(str(item["precio_unitario"]))
            subtotal = Decimal(str(item["subtotal"]))
            cur.execute(
                """
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (id_venta, item["id_producto"], cantidad, precio, subtotal),
            )
            cur.execute(
                "UPDATE productos SET stock_actual = stock_actual - %s WHERE id_producto=%s",
                (cantidad, item["id_producto"]),
            )
            cur.execute(
                """
                INSERT INTO movimientos_inventario
                (id_producto, tipo_movimiento, cantidad, referencia_tipo, referencia_id, id_usuario, motivo)
                VALUES (%s,'salida',%s,'venta',%s,%s,%s)
                """,
                (item["id_producto"], cantidad, id_venta, st.session_state.get("id_usuario"), "Salida por venta"),
            )
        conn.commit()
        st.session_state["carrito"] = []
        st.success(f"Venta #{id_venta} registrada correctamente por ${float(total):,.2f}.")
        st.rerun()
    except Exception as exc:
        conn.rollback()
        st.error("No se pudo registrar la venta.")
        st.caption(f"Detalle técnico: {exc}")
    finally:
        conn.close()
