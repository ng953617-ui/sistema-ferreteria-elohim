"""
menu.py
Menú lateral. Muestra las opciones disponibles según el rol del usuario (RBAC).
"""

import streamlit as st

OPCIONES_POR_ROL = {
    "Administrador": [
        "Punto de Venta", "Productos", "Proveedores", "Clientes",
        "Compras", "Caja", "Usuarios", "Reportes"
    ],
    "Supervisor": [
        "Punto de Venta", "Productos", "Proveedores", "Clientes",
        "Compras", "Caja", "Reportes"
    ],
    "Vendedor": [
        "Punto de Venta", "Productos"
    ],
}


def mostrar_menu():
    st.sidebar.title("🔧 Ferretería ELOHIM")
    st.sidebar.write(f"👤 {st.session_state['usuario_nombre']}")
    st.sidebar.write(f"Rol: {st.session_state['usuario_rol']}")
    st.sidebar.divider()

    opciones = OPCIONES_POR_ROL.get(st.session_state["usuario_rol"], [])
    seleccion = st.sidebar.radio("Menú", opciones)

    st.sidebar.divider()
    if st.sidebar.button("Cerrar sesión"):
        for key in ["autenticado", "usuario_id", "usuario_nombre", "usuario_rol"]:
            st.session_state.pop(key, None)
        st.rerun()

    return seleccion
