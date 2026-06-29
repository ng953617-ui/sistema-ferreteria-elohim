"""
modulos/compras.py
Órdenes de compra a proveedores. Al marcar como "recibida" se aumenta
el stock y se genera un movimiento de entrada en inventario.
"""

import streamlit as st
import pandas as pd
from config.db import run_query, run_action


def mostrar(rol):
    st.header("📥 Compras")

    if "carrito_compra" not in st.session_state:
        st.session_state["carrito_compra"] = []

    tab1, tab2 = st.tabs(["Nueva orden de compra", "Órdenes registradas"])

    with tab1:
        proveedores = run_query("SELECT ID_Proveedor, Razon_Social FROM PROVEEDOR")
        productos = run_query("SELECT ID_Producto, Nombre FROM PRODUCTO")

        if not proveedores or not productos:
            st.info("Necesitas al menos un proveedor y un producto registrados.")
        else:
            prov_map = {p["Razon_Social"]: p["ID_Proveedor"] for p in proveedores}
            prod_map = {p["Nombre"]: p["ID_Producto"] for p in productos}

            proveedor_sel = st.selectbox("Proveedor", list(prov_map.keys()))

            col1, col2, col3 = st.columns(3)
            producto_sel = col1.selectbox("Producto", list(prod_map.keys()))
            cantidad = col2.number_input("Cantidad", min_value=0.0, step=1.0)
            precio = col3.number_input("Precio unitario (compra)", min_value=0.0, step=0.01)

            if st.button("Agregar a la orden"):
                if cantidad > 0:
                    st.session_state["carrito_compra"].append({
                        "ID_Producto": prod_map[producto_sel],
                        "Nombre": producto_sel,
                        "Cantidad": cantidad,
                        "Precio_Unitario": precio
                    })
                    st.rerun()

            if st.session_state["carrito_compra"]:
                df = pd.DataFrame(st.session_state["carrito_compra"])
                df["Subtotal"] = df["Cantidad"] * df["Precio_Unitario"]
                st.dataframe(df, use_container_width=True)
                total = df["Subtotal"].sum()
                st.metric("Total de la orden", f"${total:.2f}")

                if st.button("Emitir orden de compra"):
                    orden_id = run_action(
                        "INSERT INTO ORDEN_COMPRA (Proveedor_ID, Estado, Total) VALUES (%s,'pendiente',%s)",
                        (prov_map[proveedor_sel], float(total))
                    )
                    for item in st.session_state["carrito_compra"]:
                        run_action(
                            """INSERT INTO DETALLE_COMPRA (Orden_ID, Producto_ID, Cantidad, Precio_Unitario)
                               VALUES (%s,%s,%s,%s)""",
                            (orden_id, item["ID_Producto"], item["Cantidad"], item["Precio_Unitario"])
                        )
                    st.session_state["carrito_compra"] = []
                    st.success(f"Orden de compra #{orden_id} emitida.")
                    st.rerun()

    with tab2:
        ordenes = run_query("""
            SELECT o.ID_Orden, p.Razon_Social, o.Fecha, o.Estado, o.Total
            FROM ORDEN_COMPRA o JOIN PROVEEDOR p ON o.Proveedor_ID = p.ID_Proveedor
            ORDER BY o.Fecha DESC
        """)
        if not ordenes:
            st.info("No hay órdenes de compra registradas.")
        else:
            st.dataframe(pd.DataFrame(ordenes), use_container_width=True)

            pendientes = [o for o in ordenes if o["Estado"] == "pendiente"]
            if pendientes:
                ids = {f"Orden #{o['ID_Orden']} - {o['Razon_Social']}": o["ID_Orden"] for o in pendientes}
                orden_sel = st.selectbox("Marcar como recibida", list(ids.keys()))
                if st.button("Confirmar recepción de mercancía"):
                    orden_id = ids[orden_sel]
                    detalles = run_query(
                        "SELECT Producto_ID, Cantidad FROM DETALLE_COMPRA WHERE Orden_ID = %s",
                        (orden_id,)
                    )
                    for d in detalles:
                        run_action(
                            "UPDATE PRODUCTO SET Stock_Actual = Stock_Actual + %s WHERE ID_Producto = %s",
                            (d["Cantidad"], d["Producto_ID"])
                        )
                        run_action(
                            """INSERT INTO MOVIMIENTO_INVENTARIO
                               (Producto_ID, Tipo_Movimiento, Cantidad, Referencia_ID, Usuario_ID, Motivo)
                               VALUES (%s,'entrada',%s,%s,%s,'Recepción orden de compra')""",
                            (d["Producto_ID"], d["Cantidad"], orden_id, st.session_state["usuario_id"])
                        )
                    run_action(
                        "UPDATE ORDEN_COMPRA SET Estado='recibida' WHERE ID_Orden = %s",
                        (orden_id,)
                    )
                    st.success("Mercancía recibida y stock actualizado.")
                    st.rerun()
