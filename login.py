"""Pantalla de autenticación del sistema."""
from __future__ import annotations

import streamlit as st

from config.conexion import DBConfigError, fetch_df
from utils.security import check_password


def inicializar_estado_login() -> None:
    """Inicializa variables de sesión usadas por el login."""
    st.session_state.setdefault("autenticado", False)
    st.session_state.setdefault("usuario", None)
    st.session_state.setdefault("rol", None)
    st.session_state.setdefault("id_usuario", None)
    st.session_state.setdefault("nombre_usuario", None)


def cerrar_sesion() -> None:
    """Limpia la sesión del usuario actual."""
    for key in ["autenticado", "usuario", "rol", "id_usuario", "nombre_usuario", "carrito", "carrito_compra"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def mostrar_login() -> None:
    """Renderiza el formulario de inicio de sesión."""
    inicializar_estado_login()

    st.markdown(
        """
        <div class='login-card'>
            <h1>Ferretería ELOHIM</h1>
            <p>Sistema de Gestión de Información</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            st.subheader("Inicio de sesión")
            usuario = st.text_input("Usuario", placeholder="marvin")
            contrasena = st.text_input("Contraseña", type="password", placeholder="1234")
            ingresar = st.form_submit_button("Ingresar", use_container_width=True)

        if ingresar:
            try:
                df = fetch_df(
                    """
                    SELECT id_usuario, nombre, rol, usuario_login, contrasena_hash
                    FROM usuarios
                    WHERE usuario_login = %s AND activo = 1
                    LIMIT 1
                    """,
                    (usuario.strip().lower(),),
                )
            except DBConfigError as exc:
                st.error(str(exc))
                st.info("Primero configure las credenciales en Streamlit Cloud > Settings > Secrets.")
                return
            except Exception as exc:
                st.error("No se pudo validar el usuario. Verifique que ya importó el archivo SQL en phpMyAdmin.")
                st.caption(f"Detalle técnico: {exc}")
                return

            if df.empty:
                st.error("Usuario o contraseña incorrectos.")
                return

            row = df.iloc[0]
            if check_password(contrasena, row["contrasena_hash"]):
                st.session_state["autenticado"] = True
                st.session_state["id_usuario"] = int(row["id_usuario"])
                st.session_state["nombre_usuario"] = row["nombre"]
                st.session_state["usuario"] = row["usuario_login"]
                st.session_state["rol"] = row["rol"]
                st.success("Acceso concedido.")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.caption("Usuarios de prueba incluidos en el SQL: marvin, dayana, juanita y bryan. Contraseña: 1234.")
