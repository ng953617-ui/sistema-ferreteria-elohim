"""Módulo de administración de usuarios."""
from __future__ import annotations

import streamlit as st

from config.conexion import execute, fetch_df
from utils.security import hash_password


ROLES = ["ADMIN_PRINCIPAL", "SUPERVISOR", "VENDEDOR"]


def mostrar(rol: str) -> None:
    """Administra usuarios y roles RBAC."""
    st.title("Usuarios y accesos")
    st.caption("Solo el administrador principal debe gestionar usuarios y contraseñas.")

    if rol != "ADMIN_PRINCIPAL":
        st.error("No tiene permiso para administrar usuarios.")
        return

    tabs = st.tabs(["Consultar", "Nuevo usuario", "Actualizar usuario"])

    with tabs[0]:
        df = fetch_df(
            """
            SELECT id_usuario, nombre, rol, usuario_login, activo, creado_en
            FROM usuarios
            ORDER BY id_usuario
            """
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[1]:
        with st.form("form_nuevo_usuario", clear_on_submit=True):
            nombre = st.text_input("Nombre completo *")
            usuario = st.text_input("Usuario login *").lower()
            rol_sel = st.selectbox("Rol", ROLES)
            contrasena = st.text_input("Contraseña *", type="password")
            activo = st.checkbox("Activo", value=True)
            guardar = st.form_submit_button("Guardar usuario", use_container_width=True)
        if guardar:
            if not nombre.strip() or not usuario.strip() or not contrasena:
                st.error("Nombre, usuario y contraseña son obligatorios.")
            else:
                execute(
                    """
                    INSERT INTO usuarios (nombre, rol, usuario_login, contrasena_hash, activo)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (nombre.strip(), rol_sel, usuario.strip(), hash_password(contrasena), 1 if activo else 0),
                )
                st.success("Usuario creado correctamente.")
                st.rerun()

    with tabs[2]:
        usuarios = fetch_df("SELECT id_usuario, nombre, rol, usuario_login, activo FROM usuarios ORDER BY nombre")
        if usuarios.empty:
            st.info("No hay usuarios registrados.")
            return
        id_usuario = st.selectbox(
            "Usuario",
            usuarios["id_usuario"].tolist(),
            format_func=lambda x: usuarios.loc[usuarios["id_usuario"] == x, "usuario_login"].iloc[0],
        )
        row = usuarios[usuarios["id_usuario"] == id_usuario].iloc[0]
        with st.form("form_editar_usuario"):
            nombre = st.text_input("Nombre", value=row["nombre"])
            rol_sel = st.selectbox("Rol", ROLES, index=ROLES.index(row["rol"]) if row["rol"] in ROLES else 0)
            activo = st.checkbox("Activo", value=bool(row["activo"]))
            nueva_contrasena = st.text_input("Nueva contraseña (opcional)", type="password")
            actualizar = st.form_submit_button("Actualizar usuario", use_container_width=True)
        if actualizar:
            if nueva_contrasena:
                execute(
                    """
                    UPDATE usuarios
                    SET nombre=%s, rol=%s, activo=%s, contrasena_hash=%s
                    WHERE id_usuario=%s
                    """,
                    (nombre.strip(), rol_sel, 1 if activo else 0, hash_password(nueva_contrasena), int(id_usuario)),
                )
            else:
                execute(
                    "UPDATE usuarios SET nombre=%s, rol=%s, activo=%s WHERE id_usuario=%s",
                    (nombre.strip(), rol_sel, 1 if activo else 0, int(id_usuario)),
                )
            st.success("Usuario actualizado correctamente.")
            st.rerun()
