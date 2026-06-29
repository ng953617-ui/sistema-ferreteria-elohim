import streamlit as st
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("👥 Usuarios y roles")
    usuario_actual = st.session_state.get("usuario", {})
    if usuario_actual.get("rol") != "Administrador Principal":
        st.warning("Solo el Administrador Principal puede administrar usuarios.")
        return

    df = consultar_df(
        """
        SELECT id_usuario, usuario_login AS usuario, nombre_completo, rol, activo
        FROM usuario
        WHERE usuario_login <> 'usuario' AND nombre_completo <> 'nombre_completo'
        ORDER BY rol, nombre_completo
        """
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Crear usuario")
    with st.form("form_usuario"):
        c1, c2 = st.columns(2)
        usuario = c1.text_input("Usuario")
        nombre = c2.text_input("Nombre completo")
        c3, c4 = st.columns(2)
        password = c3.text_input("Contraseña", type="password")
        rol = c4.selectbox("Rol", ["Administrador Principal", "Administrador/Supervisor", "Vendedor"])
        guardar = st.form_submit_button("Guardar usuario")

    if guardar:
        if not usuario or not nombre or not password:
            st.warning("Complete todos los campos.")
        else:
            ejecutar(
                """
                INSERT INTO usuario(usuario_login, contrasena_hash, nombre_completo, rol, activo)
                VALUES (%s,%s,%s,%s,1)
                """,
                (usuario, password, nombre, rol),
            )
            st.success("Usuario creado correctamente.")
            st.rerun()
