"""
modulos/clientes.py
Gestión de clientes (consumidor final / contribuyente con datos fiscales para CCF).
"""

import streamlit as st
import pandas as pd
from config.db import run_query, run_action


def mostrar(rol):
    st.header("🧾 Clientes")

    tab1, tab2 = st.tabs(["Listado", "Nuevo cliente"])

    with tab1:
        clientes = run_query("SELECT * FROM CLIENTE")
        if clientes:
            st.dataframe(pd.DataFrame(clientes), use_container_width=True)
        else:
            st.info("No hay clientes registrados (las ventas de mostrador no lo requieren).")

    with tab2:
        st.caption("Solo necesario para clientes que requieren Crédito Fiscal (CCF).")
        with st.form("nuevo_cliente"):
            nombre = st.text_input("Nombre o razón social")
            nit = st.text_input("NIT")
            nrc = st.text_input("NRC")
            giro = st.text_input("Giro")
            departamento = st.text_input("Departamento")
            guardar = st.form_submit_button("Guardar cliente")

        if guardar:
            if not nombre:
                st.warning("El nombre es obligatorio.")
            else:
                run_action(
                    """INSERT INTO CLIENTE (Nombre, NIT, NRC, Giro, Departamento)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (nombre, nit, nrc, giro, departamento)
                )
                st.success(f"Cliente '{nombre}' registrado.")
                st.rerun()
