"""
login.py
Pantalla de inicio de sesión. Valida usuario contra la tabla USUARIO
y guarda en session_state los datos del usuario autenticado.
"""

import streamlit as st
import bcrypt
from config.db import run_query


def mostrar_login():
    st.title("🔧 Ferretería ELOHIM")
    st.subheader("Iniciar sesión")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Ingresar")

    if enviar:
        if not usuario or not contrasena:
            st.warning("Completa usuario y contraseña.")
            return

        rows = run_query(
            "SELECT * FROM USUARIO WHERE Usuario_Login = %s",
            (usuario,)
        )

        if not rows:
            st.error("Usuario no encontrado.")
            return

        user = rows[0]
        hash_guardado = user["Contrasena_Hash"].encode()

        if bcrypt.checkpw(contrasena.encode(), hash_guardado):
            st.session_state["autenticado"] = True
            st.session_state["usuario_id"] = user["ID_Usuario"]
            st.session_state["usuario_nombre"] = user["Nombre"]
            st.session_state["usuario_rol"] = user["Rol"]
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
