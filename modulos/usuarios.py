"""
modulos/usuarios.py
Gestión de usuarios del sistema (solo Administrador).
"""

import streamlit as st
import pandas as pd
import bcrypt
from config.db import run_query, run_action


def mostrar(rol):
    st.header("👥 Usuarios")

    if rol != "Administrador":
        st.info("Solo el Administrador puede gestionar usuarios.")
        return

    tab1, tab2 = st.tabs(["Listado", "Nuevo usuario"])

    with tab1:
        usuarios = run_query("SELECT ID_Usuario, Nombre, Rol, Usuario_Login FROM USUARIO")
        st.dataframe(pd.DataFrame(usuarios), use_container_width=True)

    with tab2:
        with st.form("nuevo_usuario"):
            nombre = st.text_input("Nombre completo")
            login = st.text_input("Usuario de acceso")
            password = st.text_input("Contraseña", type="password")
            rol_nuevo = st.selectbox("Rol", ["Administrador", "Supervisor", "Vendedor"])
            guardar = st.form_submit_button("Crear usuario")

        if guardar:
            if not nombre or not login or not password:
                st.warning("Todos los campos son obligatorios.")
            else:
                hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                run_action(
                    """INSERT INTO USUARIO (Nombre, Rol, Usuario_Login, Contrasena_Hash)
                       VALUES (%s,%s,%s,%s)""",
                    (nombre, rol_nuevo, login, hash_pw)
                )
                st.success(f"Usuario '{login}' creado correctamente.")
                st.rerun()
