"""Aplicación principal SGI Ferretería ELOHIM."""
from __future__ import annotations

import streamlit as st

from login import inicializar_estado_login, mostrar_login
from menu import mostrar_menu
from modulos import caja, clientes, compras, dashboard, productos, proveedores, reportes, usuarios, ventas

st.set_page_config(
    page_title="SGI Ferretería ELOHIM",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #f7f7f8; }
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
    .login-card {
        background: linear-gradient(135deg, #2b2b2b 0%, #4f3b10 100%);
        color: white;
        padding: 2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
    }
    .login-card h1 { margin-bottom: 0.2rem; font-size: 2.2rem; }
    .login-card p { margin-top: 0; opacity: 0.88; }
    div[data-testid="stMetricValue"] { font-size: 1.55rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """Controla autenticación y navegación del sistema."""
    inicializar_estado_login()

    if not st.session_state.get("autenticado"):
        mostrar_login()
        return

    opcion = mostrar_menu()
    rol = st.session_state.get("rol", "VENDEDOR")

    if opcion == "Dashboard":
        dashboard.mostrar(rol)
    elif opcion == "Productos e Inventario":
        productos.mostrar(rol)
    elif opcion == "Proveedores":
        proveedores.mostrar(rol)
    elif opcion == "Clientes":
        clientes.mostrar(rol)
    elif opcion == "Punto de Venta":
        ventas.mostrar(rol)
    elif opcion == "Compras":
        compras.mostrar(rol)
    elif opcion == "Caja":
        caja.mostrar(rol)
    elif opcion == "Reportes":
        reportes.mostrar(rol)
    elif opcion == "Usuarios":
        usuarios.mostrar(rol)
    else:
        st.info("Seleccione una opción del menú.")


if __name__ == "__main__":
    main()
