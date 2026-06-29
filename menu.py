import streamlit as st
from modulos import inicio, productos, proveedores, ventas, compras, caja, reportes, usuarios, clientes


def cerrar_sesion():
    st.session_state.clear()
    st.rerun()


def mostrar_menu():
    usuario = st.session_state.get("usuario", {})
    rol = usuario.get("rol", "")

    st.sidebar.success(f"Usuario: {usuario.get('nombre_completo', '')}")
    st.sidebar.caption(f"Rol: {rol}")

    if st.sidebar.button("Cerrar sesión"):
        cerrar_sesion()

    st.sidebar.markdown("---")
    st.sidebar.header("Menú principal")

    if rol == "Vendedor":
        opciones = ["Inicio", "Punto de venta", "Consulta de productos", "Cierre de caja"]
    else:
        opciones = [
            "Inicio",
            "Productos e inventario",
            "Clientes y datos fiscales",
            "Proveedores",
            "Punto de venta",
            "Compras y reposición",
            "Cierre de caja",
            "Reportes",
            "Usuarios y roles",
        ]

    seleccion = st.sidebar.radio("Seleccione una sección:", opciones)

    if seleccion == "Inicio":
        inicio.mostrar()
    elif seleccion == "Productos e inventario":
        productos.mostrar(modo_consulta=False)
    elif seleccion == "Consulta de productos":
        productos.mostrar(modo_consulta=True)
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
