import streamlit as st
from login import cerrar_sesion
from modulos import inicio, productos, clientes, proveedores, ventas, compras, caja, reportes, usuarios


def mostrar_menu():
    user = st.session_state.get("usuario", {})
    st.sidebar.success(f"Usuario: {user.get('nombre_completo', '')}")
    st.sidebar.caption(f"Rol: {user.get('rol', '')}")

    if st.sidebar.button("Cerrar sesión"):
        cerrar_sesion()

    st.sidebar.markdown("---")
    st.sidebar.title("Menú principal")

    rol = user.get("rol", "")
    if "Vendedor" in rol:
        opciones = ["Inicio", "Productos e inventario", "Punto de venta"]
    else:
        opciones = [
            "Inicio", "Productos e inventario", "Clientes y datos fiscales", "Proveedores",
            "Punto de venta", "Compras y reposición", "Cierre de caja", "Reportes", "Usuarios y roles"
        ]

    seleccion = st.sidebar.radio("Seleccione una sección:", opciones)

    if seleccion == "Inicio":
        inicio.mostrar()
    elif seleccion == "Productos e inventario":
        productos.mostrar(modo_consulta=("Vendedor" in rol))
    elif seleccion == "Clientes y datos fiscales":
        clientes.mostrar()
    elif seleccion == "Proveedores":
        proveedores.mostrar()
    elif seleccion == "Punto de venta":
        ventas.mostrar()
    elif seleccion == "Compras y reposición":
        compras.mostrar()
    elif seleccion == "Cierre de caja":
        caja.mostrar()
    elif seleccion == "Reportes":
        reportes.mostrar()
    elif seleccion == "Usuarios y roles":
        usuarios.mostrar()
