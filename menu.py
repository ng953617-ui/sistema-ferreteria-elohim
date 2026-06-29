"""Menú lateral y permisos por rol."""
from __future__ import annotations

import streamlit as st

from login import cerrar_sesion


ROLE_LABELS = {
    "ADMIN_PRINCIPAL": "Administrador principal",
    "SUPERVISOR": "Administrador / Supervisor",
    "VENDEDOR": "Vendedor",
}


def opciones_por_rol(rol: str) -> list[str]:
    """Devuelve las opciones visibles según el rol del usuario."""
    if rol == "ADMIN_PRINCIPAL":
        return [
            "Dashboard",
            "Productos e Inventario",
            "Proveedores",
            "Clientes",
            "Punto de Venta",
            "Compras",
            "Caja",
            "Reportes",
            "Usuarios",
        ]
    if rol == "SUPERVISOR":
        return [
            "Dashboard",
            "Productos e Inventario",
            "Proveedores",
            "Clientes",
            "Punto de Venta",
            "Compras",
            "Caja",
            "Reportes",
        ]
    return ["Dashboard", "Productos e Inventario", "Clientes", "Punto de Venta"]


def mostrar_menu() -> str:
    """Renderiza el sidebar y devuelve la opción seleccionada."""
    rol = st.session_state.get("rol", "VENDEDOR")
    nombre = st.session_state.get("nombre_usuario", "Usuario")

    st.sidebar.markdown("### 🧰 Ferretería ELOHIM")
    st.sidebar.caption("Sistema SGI - Streamlit + MySQL")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Usuario:** {nombre}")
    st.sidebar.write(f"**Rol:** {ROLE_LABELS.get(rol, rol)}")
    st.sidebar.markdown("---")

    opcion = st.sidebar.radio("Menú", opciones_por_rol(rol), label_visibility="collapsed")
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
    return opcion
