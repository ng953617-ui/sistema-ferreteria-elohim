"""Módulo de clientes."""
from __future__ import annotations

import streamlit as st

from config.conexion import execute, fetch_df


def mostrar(rol: str) -> None:
    """Permite consultar y registrar clientes para venta rápida y CCF futuro."""
    st.title("Clientes")
    st.caption("Datos de consumidor final y contribuyentes para comprobantes fiscales futuros.")

    tabs = st.tabs(["Consultar", "Nuevo cliente"])

    with tabs[0]:
        texto = st.text_input("Buscar cliente", placeholder="nombre, NIT, NRC o teléfono")
        query = "SELECT * FROM clientes WHERE 1=1"
        params = []
        if texto:
            query += " AND (nombre LIKE %s OR nit LIKE %s OR nrc LIKE %s OR telefono LIKE %s)"
            params = [f"%{texto}%"] * 4
        query += " ORDER BY nombre LIMIT 1000"
        df = fetch_df(query, tuple(params))
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[1]:
        with st.form("form_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre / razón social *")
                tipo = st.selectbox("Tipo de cliente", ["CONSUMIDOR_FINAL", "CONTRIBUYENTE"])
                documento = st.text_input("DUI / Documento")
                telefono = st.text_input("Teléfono")
                correo = st.text_input("Correo")
            with col2:
                nit = st.text_input("NIT")
                nrc = st.text_input("NRC")
                giro = st.text_input("Giro")
                departamento = st.text_input("Departamento", value="San Salvador")
                municipio = st.text_input("Municipio")
            guardar = st.form_submit_button("Guardar cliente", use_container_width=True)

        if guardar:
            if not nombre.strip():
                st.error("El nombre es obligatorio.")
            else:
                execute(
                    """
                    INSERT INTO clientes
                    (nombre, tipo_cliente, documento, nit, nrc, giro, departamento, municipio, telefono, correo)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        nombre.strip(), tipo, documento.strip(), nit.strip(), nrc.strip(), giro.strip(),
                        departamento.strip(), municipio.strip(), telefono.strip(), correo.strip(),
                    ),
                )
                st.success("Cliente registrado correctamente.")
                st.rerun()
