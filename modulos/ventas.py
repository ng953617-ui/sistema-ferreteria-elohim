"""
modulos/ventas.py
Punto de Venta (POS): búsqueda de producto, carrito, registro de venta,
descuento automático de stock y generación de movimiento de inventario.
"""

import streamlit as st
import pandas as pd
from config.db import run_query, run_action


def mostrar(rol):
    st.header("🛒 Punto de Venta")

    if "carrito" not in st.session_state:
        st.session_state["carrito"] = []

    # --- Buscar producto ---
    buscar = st.text_input("Buscar producto por nombre o código de barras")
    if buscar:
        resultados = run_query(
            "SELECT ID_Producto, Nombre, Precio_Venta, Stock_Actual, Unidad_Medida "
            "FROM PRODUCTO WHERE Nombre LIKE %s OR Codigo_Barra LIKE %s LIMIT 10",
            (f"%{buscar}%", f"%{buscar}%")
        )
        for prod in resultados:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"**{prod['Nombre']}** (stock: {prod['Stock_Actual']} {prod['Unidad_Medida']})")
            col2.write(f"${prod['Precio_Venta']}")
            cantidad = col3.number_input(
                "Cant.", min_value=0.0, step=1.0, key=f"cant_{prod['ID_Producto']}", label_visibility="collapsed"
            )
            if col4.button("Agregar", key=f"add_{prod['ID_Producto']}"):
                if cantidad <= 0:
                    st.warning("Indica una cantidad mayor a 0.")
                elif cantidad > prod["Stock_Actual"]:
                    st.error("No hay suficiente stock disponible.")
                else:
                    st.session_state["carrito"].append({
                        "ID_Producto": prod["ID_Producto"],
                        "Nombre": prod["Nombre"],
                        "Cantidad": cantidad,
                        "Precio_Unitario": float(prod["Precio_Venta"]),
                        "Subtotal": cantidad * float(prod["Precio_Venta"])
                    })
                    st.success(f"{prod['Nombre']} agregado al carrito.")
                    st.rerun()

    st.divider()
    st.subheader("Carrito")

    if not st.session_state["carrito"]:
        st.info("El carrito está vacío.")
    else:
        df_carrito = pd.DataFrame(st.session_state["carrito"])
        st.dataframe(df_carrito[["Nombre", "Cantidad", "Precio_Unitario", "Subtotal"]],
                     use_container_width=True)
        total = df_carrito["Subtotal"].sum()
        st.metric("Total de la venta", f"${total:.2f}")

        if st.button("Vaciar carrito"):
            st.session_state["carrito"] = []
            st.rerun()

        with st.form("cerrar_venta"):
            metodo_pago = st.selectbox("Método de pago", ["efectivo", "transferencia"])
            tipo_comp = st.selectbox(
                "Tipo de comprobante", ["consumidor final", "factura interna", "CCF"]
            )
            cliente_id = None
            if tipo_comp == "CCF":
                clientes = run_query("SELECT ID_Cliente, Nombre FROM CLIENTE")
                if clientes:
                    cli_map = {c["Nombre"]: c["ID_Cliente"] for c in clientes}
                    cliente_sel = st.selectbox("Cliente (requerido para CCF)", list(cli_map.keys()))
                    cliente_id = cli_map[cliente_sel]
                else:
                    st.warning("No hay clientes registrados. Regístralo primero en el módulo Clientes.")
            confirmar = st.form_submit_button("Confirmar venta")

        if confirmar:
            venta_id = run_action(
                """INSERT INTO VENTA (Usuario_ID, Cliente_ID, Total, Metodo_Pago, Tipo_Comprobante)
                   VALUES (%s,%s,%s,%s,%s)""",
                (st.session_state["usuario_id"], cliente_id, float(total), metodo_pago, tipo_comp)
            )
            if venta_id:
                for item in st.session_state["carrito"]:
                    run_action(
                        """INSERT INTO DETALLE_VENTA
                           (Venta_ID, Producto_ID, Cantidad, Precio_Unitario, Subtotal)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (venta_id, item["ID_Producto"], item["Cantidad"],
                         item["Precio_Unitario"], item["Subtotal"])
                    )
                    # Descontar stock
                    run_action(
                        "UPDATE PRODUCTO SET Stock_Actual = Stock_Actual - %s WHERE ID_Producto = %s",
                        (item["Cantidad"], item["ID_Producto"])
                    )
                    # Movimiento de inventario (salida)
                    run_action(
                        """INSERT INTO MOVIMIENTO_INVENTARIO
                           (Producto_ID, Tipo_Movimiento, Cantidad, Referencia_ID, Usuario_ID, Motivo)
                           VALUES (%s,'salida',%s,%s,%s,'Venta POS')""",
                        (item["ID_Producto"], item["Cantidad"], venta_id, st.session_state["usuario_id"])
                    )
                st.session_state["carrito"] = []
                st.success(f"Venta #{venta_id} registrada correctamente por ${total:.2f}.")
                st.rerun()
