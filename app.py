"""
app.py
Punto de entrada de la aplicación Streamlit - Sistema Ferretería ELOHIM.
"""

import streamlit as st
from login import mostrar_login
from menu import mostrar_menu
from modulos import productos, proveedores, clientes, ventas, compras, caja, usuarios, reportes

st.set_page_config(page_title="Ferretería ELOHIM", page_icon="🔧", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    seleccion = mostrar_menu()
    rol = st.session_state["usuario_rol"]

    if seleccion == "Punto de Venta":
        ventas.mostrar(rol)
    elif seleccion == "Productos":
        productos.mostrar(rol)
    elif seleccion == "Proveedores":
        proveedores.mostrar(rol)
    elif seleccion == "Clientes":
        clientes.mostrar(rol)
    elif seleccion == "Compras":
        compras.mostrar(rol)
    elif seleccion == "Caja":
        caja.mostrar(rol)
    elif seleccion == "Usuarios":
        usuarios.mostrar(rol)
    elif seleccion == "Reportes":
        reportes.mostrar(rol)
