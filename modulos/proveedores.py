import streamlit as st
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("🚚 Proveedores")
    st.write("Registro de proveedores y datos comerciales requeridos por la ferretería.")

    df = consultar_df("""
        SELECT id_proveedor, nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc
        FROM proveedor WHERE activo=1 ORDER BY nombre_razon_social
    """)
    if df.empty:
        st.info("No hay proveedores registrados.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Registrar proveedor")
    with st.form("form_proveedor"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre empresa / Razón social")
        telefono = c2.text_input("Teléfono")
        direccion = st.text_area("Dirección física comercial")
        c3, c4, c5 = st.columns(3)
        vendedor = c3.text_input("Vendedor / asesor asignado")
        nit = c4.text_input("NIT")
        nrc = c5.text_input("NRC")
        guardar = st.form_submit_button("Guardar proveedor")

    if guardar:
        if not nombre.strip():
            st.error("Ingrese el nombre o razón social.")
            return
        ejecutar("""
            INSERT INTO proveedor (nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc, activo)
            VALUES (%s,%s,%s,%s,%s,%s,1)
        """, (nombre, direccion, telefono, vendedor, nit, nrc))
        st.success("Proveedor registrado correctamente.")
        st.rerun()
