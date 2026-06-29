import streamlit as st
from config.conexion import consultar_df, ejecutar, ejecutar_insert


def mostrar():
    st.title("👥 Clientes y datos fiscales")
    st.write("Módulo para registrar CLIENTE, CONSUMIDOR_FINAL y CONTRIBUYENTE del diagrama ER.")

    df = consultar_df("""
        SELECT c.id_cliente, c.nombre, c.direccion, c.telefono, c.correo,
               cf.tipo_documento, cf.num_documento, co.nit, co.nrc, co.giro, co.departamento, co.municipio
        FROM cliente c
        LEFT JOIN consumidor_final cf ON c.id_cliente=cf.id_cliente
        LEFT JOIN contribuyente co ON c.id_cliente=co.id_cliente
        WHERE c.activo=1
        ORDER BY c.nombre
    """)
    if df.empty:
        st.info("No hay clientes registrados.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Registrar cliente")
    with st.form("form_cliente"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del cliente")
        telefono = c2.text_input("Teléfono")
        direccion = st.text_area("Dirección")
        correo = st.text_input("Correo")
        tipo = st.selectbox("Tipo de cliente", ["Consumidor final", "Contribuyente"])
        if tipo == "Consumidor final":
            c3, c4 = st.columns(2)
            tipo_doc = c3.selectbox("Tipo de documento", ["DUI", "Pasaporte", "Otro", "N/A"])
            num_doc = c4.text_input("Número de documento")
            nit = nrc = giro = dep = mun = None
        else:
            tipo_doc = num_doc = None
            c5, c6 = st.columns(2)
            nit = c5.text_input("NIT")
            nrc = c6.text_input("NRC")
            giro = st.text_input("Giro")
            c7, c8 = st.columns(2)
            dep = c7.text_input("Departamento")
            mun = c8.text_input("Municipio")
        guardar = st.form_submit_button("Guardar cliente")

    if guardar:
        if not nombre.strip():
            st.error("Ingrese el nombre del cliente.")
            return
        cliente_id = ejecutar_insert("INSERT INTO cliente (nombre,direccion,telefono,correo,activo) VALUES (%s,%s,%s,%s,1)",
                                    (nombre, direccion, telefono, correo))
        if tipo == "Consumidor final":
            ejecutar("INSERT INTO consumidor_final (id_cliente,tipo_documento,num_documento) VALUES (%s,%s,%s)",
                     (cliente_id, tipo_doc, num_doc))
        else:
            ejecutar("INSERT INTO contribuyente (id_cliente,nit,nrc,giro,departamento,municipio) VALUES (%s,%s,%s,%s,%s,%s)",
                     (cliente_id, nit, nrc, giro, dep, mun))
        st.success("Cliente registrado correctamente.")
        st.rerun()
