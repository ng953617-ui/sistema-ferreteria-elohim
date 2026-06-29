"""
modulos/proveedores.py
Gestión de proveedores y su relación N:M con productos.
"""

import streamlit as st
import pandas as pd
from config.db import run_query, run_action


def mostrar(rol):
    st.header("🚚 Proveedores")

    tab1, tab2, tab3 = st.tabs(["Listado", "Nuevo proveedor", "Asociar producto"])

    with tab1:
        proveedores = run_query("SELECT * FROM PROVEEDOR")
        if proveedores:
            st.dataframe(pd.DataFrame(proveedores), use_container_width=True)
        else:
            st.info("No hay proveedores registrados.")

    with tab2:
        with st.form("nuevo_proveedor"):
            razon = st.text_input("Razón social")
            direccion = st.text_input("Dirección")
            telefono = st.text_input("Teléfono")
            vendedor = st.text_input("Vendedor asignado")
            nit = st.text_input("NIT")
            nrc = st.text_input("NRC")
            guardar = st.form_submit_button("Guardar proveedor")

        if guardar:
            if not razon:
                st.warning("La razón social es obligatoria.")
            else:
                run_action(
                    """INSERT INTO PROVEEDOR
                       (Razon_Social, Direccion, Telefono, Vendedor_Asignado, NIT, NRC)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (razon, direccion, telefono, vendedor, nit, nrc)
                )
                st.success(f"Proveedor '{razon}' registrado.")
                st.rerun()

    with tab3:
        productos = run_query("SELECT ID_Producto, Nombre FROM PRODUCTO")
        proveedores = run_query("SELECT ID_Proveedor, Razon_Social FROM PROVEEDOR")

        if not productos or not proveedores:
            st.info("Necesitas al menos un producto y un proveedor registrados.")
        else:
            prod_map = {p["Nombre"]: p["ID_Producto"] for p in productos}
            prov_map = {p["Razon_Social"]: p["ID_Proveedor"] for p in proveedores}

            with st.form("asociar"):
                producto = st.selectbox("Producto", list(prod_map.keys()))
                proveedor = st.selectbox("Proveedor", list(prov_map.keys()))
                precio_compra = st.number_input("Precio de compra (USD)", min_value=0.0, step=0.01)
                principal = st.checkbox("Marcar como proveedor principal")
                asociar = st.form_submit_button("Asociar")

            if asociar:
                run_action(
                    """INSERT INTO PRODUCTO_PROVEEDOR (Producto_ID, Proveedor_ID, Precio_Compra, Es_Principal)
                       VALUES (%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE Precio_Compra=%s, Es_Principal=%s""",
                    (prod_map[producto], prov_map[proveedor], precio_compra, int(principal),
                     precio_compra, int(principal))
                )
                st.success("Relación producto-proveedor guardada.")
