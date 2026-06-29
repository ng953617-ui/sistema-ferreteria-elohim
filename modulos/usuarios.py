import streamlit as st
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("👥 Usuarios y roles")
    rol_actual = st.session_state["usuario"]["rol"]
    if "Administrador" not in rol_actual:
        st.warning("Solo administradores pueden administrar usuarios.")
        return

    df = consultar_df("SELECT id_usuario, usuario, nombre_completo, rol, activo FROM usuario ORDER BY nombre_completo")
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
        if not usuario.strip() or not nombre.strip() or not password.strip():
            st.error("Complete usuario, nombre y contraseña.")
            return
        try:
            ejecutar("INSERT INTO usuario (usuario,nombre_completo,rol,password_hash,activo) VALUES (%s,%s,%s,%s,1)",
                    (usuario, nombre, rol, password))
            st.success("Usuario creado correctamente.")
            st.rerun()
        except Exception as e:
            st.error("No se pudo crear el usuario. Revise si el usuario ya existe.")
            st.exception(e)
