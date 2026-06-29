"""Módulo de órdenes de compra."""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from config.conexion import fetch_df, get_connection


def _init_cart() -> None:
    st.session_state.setdefault("carrito_compra", [])


def mostrar(rol: str) -> None:
    """Registra órdenes de compra uniproveedor y entradas de inventario."""
    _init_cart()
    st.title("Compras")
    st.caption("Órdenes de compra por proveedor y recepción de mercancía.")

    tabs = st.tabs(["Nueva orden", "Historial", "Compras sugeridas"])
    with tabs[0]:
        _nueva_orden()
    with tabs[1]:
        _historial()
    with tabs[2]:
        _compras_sugeridas()


def _nueva_orden() -> None:
    proveedores = fetch_df("SELECT id_proveedor, razon_social FROM proveedores ORDER BY razon_social")
    productos = fetch_df("SELECT id_producto, nombre, precio_venta, stock_actual, stock_minimo FROM productos WHERE activo=1 ORDER BY nombre")
    if proveedores.empty or productos.empty:
        st.info("Debe existir al menos un proveedor y productos activos.")
        return

    id_prov = st.selectbox(
        "Proveedor de la orden",
        proveedores["id_proveedor"].tolist(),
        format_func=lambda x: proveedores.loc[proveedores["id_proveedor"] == x, "razon_social"].iloc[0],
    )

    st.subheader("Agregar producto a la orden")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        id_prod = st.selectbox(
            "Producto",
            productos["id_producto"].tolist(),
            format_func=lambda x: productos.loc[productos["id_producto"] == x, "nombre"].iloc[0],
        )
    with col2:
        cantidad = st.number_input("Cantidad", min_value=0.01, step=1.0, value=1.0)
    with col3:
        precio_default = _precio_compra_default(id_prod, id_prov)
        precio = st.number_input("Precio unitario", min_value=0.0, step=0.01, value=float(precio_default), format="%.2f")

    if st.button("Agregar a orden", use_container_width=True):
        nombre = productos.loc[productos["id_producto"] == id_prod, "nombre"].iloc[0]
        item = {
            "id_producto": int(id_prod),
            "producto": nombre,
            "cantidad": float(cantidad),
            "precio_unitario": float(precio),
            "subtotal": float(Decimal(str(cantidad)) * Decimal(str(precio))),
        }
        st.session_state["carrito_compra"].append(item)
        st.success("Producto agregado a la orden.")
        st.rerun()

    carrito = st.session_state.get("carrito_compra", [])
    st.subheader("Detalle de la orden")
    if carrito:
        df = pd.DataFrame(carrito)
        st.dataframe(df[["producto", "cantidad", "precio_unitario", "subtotal"]], use_container_width=True, hide_index=True)
        total = float(df["subtotal"].sum())
        st.metric("Total orden", f"${total:,.2f}")
        col_a, col_b = st.columns(2)
        with col_a:
            estado = st.selectbox("Estado al guardar", ["recibida", "pendiente", "cancelada"])
        with col_b:
            if st.button("Vaciar orden", use_container_width=True):
                st.session_state["carrito_compra"] = []
                st.rerun()
        if st.button("Guardar orden", use_container_width=True):
            _guardar_orden(id_prov, carrito, estado)
    else:
        st.info("La orden no tiene productos agregados.")


def _precio_compra_default(id_producto: int, id_proveedor: int) -> Decimal:
    df = fetch_df(
        """
        SELECT precio_compra
        FROM producto_proveedor
        WHERE id_producto=%s AND id_proveedor=%s
        LIMIT 1
        """,
        (int(id_producto), int(id_proveedor)),
    )
    if df.empty:
        return Decimal("0.00")
    return Decimal(str(df.iloc[0]["precio_compra"]))


def _guardar_orden(id_proveedor: int, carrito: list[dict], estado: str) -> None:
    total = sum(Decimal(str(item["subtotal"])) for item in carrito)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ordenes_compra (id_proveedor, id_usuario, estado, total) VALUES (%s,%s,%s,%s)",
            (int(id_proveedor), st.session_state.get("id_usuario"), estado, total),
        )
        id_orden = cur.lastrowid
        for item in carrito:
            cantidad = Decimal(str(item["cantidad"]))
            precio = Decimal(str(item["precio_unitario"]))
            subtotal = Decimal(str(item["subtotal"]))
            cur.execute(
                """
                INSERT INTO detalle_compra (id_orden, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (id_orden, item["id_producto"], cantidad, precio, subtotal),
            )
            if estado == "recibida":
                cur.execute(
                    "UPDATE productos SET stock_actual = stock_actual + %s WHERE id_producto=%s",
                    (cantidad, item["id_producto"]),
                )
                cur.execute(
                    """
                    INSERT INTO movimientos_inventario
                    (id_producto, tipo_movimiento, cantidad, referencia_tipo, referencia_id, id_usuario, motivo)
                    VALUES (%s,'entrada',%s,'compra',%s,%s,%s)
                    """,
                    (item["id_producto"], cantidad, id_orden, st.session_state.get("id_usuario"), "Entrada por orden de compra recibida"),
                )
        conn.commit()
        st.session_state["carrito_compra"] = []
        st.success(f"Orden #{id_orden} guardada correctamente.")
        st.rerun()
    except Exception as exc:
        conn.rollback()
        st.error("No se pudo guardar la orden.")
        st.caption(f"Detalle técnico: {exc}")
    finally:
        conn.close()


def _historial() -> None:
    st.subheader("Historial de órdenes")
    df = fetch_df(
        """
        SELECT oc.id_orden, oc.fecha, pr.razon_social AS proveedor,
               u.nombre AS usuario, oc.estado, oc.total
        FROM ordenes_compra oc
        INNER JOIN proveedores pr ON pr.id_proveedor = oc.id_proveedor
        LEFT JOIN usuarios u ON u.id_usuario = oc.id_usuario
        ORDER BY oc.fecha DESC
        LIMIT 500
        """
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        id_orden = st.selectbox("Ver detalle de orden", df["id_orden"].tolist())
        detalle = fetch_df(
            """
            SELECT p.nombre AS producto, dc.cantidad, dc.precio_unitario, dc.subtotal
            FROM detalle_compra dc
            INNER JOIN productos p ON p.id_producto = dc.id_producto
            WHERE dc.id_orden=%s
            """,
            (int(id_orden),),
        )
        st.dataframe(detalle, use_container_width=True, hide_index=True)


def _compras_sugeridas() -> None:
    st.subheader("Compras sugeridas por stock mínimo")
    df = fetch_df(
        """
        SELECT p.id_producto, p.nombre, c.nombre AS categoria,
               p.stock_actual, p.stock_minimo,
               GREATEST(p.stock_minimo * 2 - p.stock_actual, 1) AS cantidad_sugerida,
               pr.razon_social AS proveedor_principal,
               pp.precio_compra
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN producto_proveedor pp ON pp.id_producto = p.id_producto AND pp.es_principal = 1
        LEFT JOIN proveedores pr ON pr.id_proveedor = pp.id_proveedor
        WHERE p.activo=1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC, p.nombre ASC
        """
    )
    if df.empty:
        st.success("No hay productos bajo el mínimo configurado.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
