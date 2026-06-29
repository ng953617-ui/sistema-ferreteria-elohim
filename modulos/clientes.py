import streamlit as st
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("👤 Clientes y datos fiscales")
    st.write("Módulo agregado para alinear el sistema con las entidades CLIENTE, CONSUMIDOR_FINAL y CONTRIBUYENTE del diagrama ER.")

    df = consultar_df(
        """
        SELECT c.id_cliente, c.nombre, c.direccion, c.telefono, c.correo,
               cf.tipo_documento, cf.num_documento,
               ct.nit, ct.nrc, ct.giro, ct.departamento, ct.municipio,
               CASE
                   WHEN ct.id_cliente IS NOT NULL THEN 'Contribuyente'
                   WHEN cf.id_cliente IS NOT NULL THEN 'Consumidor final'
                   ELSE 'Cliente general'
               END AS tipo_cliente
        FROM cliente c
        LEFT JOIN consumidor_final cf ON c.id_cliente = cf.id_cliente
        LEFT JOIN contribuyente ct ON c.id_cliente = ct.id_cliente
        WHERE c.nombre <> 'nombre'
        ORDER BY c.id_cliente DESC
        """
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Registrar cliente")
    with st.form("form_cliente"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del cliente")
        telefono = c2.text_input("Teléfono")
        direccion = st.text_area("Dirección")
        correo = st.text_input("Correo")
        tipo_cliente = st.selectbox("Tipo de cliente", ["Cliente general", "Consumidor final", "Contribuyente"])

        if tipo_cliente == "Consumidor final":
            c3, c4 = st.columns(2)
            tipo_documento = c3.selectbox("Tipo de documento", ["DUI", "Pasaporte", "Otro"])
            num_documento = c4.text_input("Número de documento")
            nit = nrc = giro = departamento = municipio = ""
        elif tipo_cliente == "Contribuyente":
            c5, c6 = st.columns(2)
            nit = c5.text_input("NIT")
            nrc = c6.text_input("NRC")
            giro = st.text_input("Giro")
            c7, c8 = st.columns(2)
            departamento = c7.text_input("Departamento")
            municipio = c8.text_input("Municipio")
            tipo_documento = num_documento = ""
        else:
            tipo_documento = num_documento = nit = nrc = giro = departamento = municipio = ""

        guardar = st.form_submit_button("Guardar cliente")

    if guardar:
        if not nombre:
            st.warning("Debe ingresar el nombre del cliente.")
            return
        id_cliente = ejecutar(
            """
            INSERT INTO cliente(nombre, direccion, telefono, correo)
            VALUES (%s,%s,%s,%s)
            """,
            (nombre, direccion, telefono, correo),
        )
        if tipo_cliente == "Consumidor final":
            ejecutar(
                """
                INSERT INTO consumidor_final(id_cliente, tipo_documento, num_documento)
                VALUES (%s,%s,%s)
                """,
                (id_cliente, tipo_documento, num_documento),
            )
        elif tipo_cliente == "Contribuyente":
            ejecutar(
                """
                INSERT INTO contribuyente(id_cliente, nit, nrc, giro, departamento, municipio)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (id_cliente, nit, nrc, giro, departamento, municipio),
            )
        st.success("Cliente guardado correctamente.")
        st.rerun()
