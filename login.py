import streamlit as st
from config.conexion import consultar


def validar_usuario(usuario, password):
    sql = """
        SELECT id_usuario, usuario, nombre_completo, rol
        FROM usuario
        WHERE usuario = %s AND password_hash = %s AND activo = 1
        LIMIT 1
    """
    datos = consultar(sql, (usuario, password))
    return datos[0] if datos else None


def mostrar_login():
    st.title("🔐 Ferretería Elohim")
    st.subheader("Sistema de Gestión de Información")
    st.write("Ingrese sus credenciales para acceder al sistema.")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        entrar = st.form_submit_button("Iniciar sesión")

    if entrar:
        try:
            datos = validar_usuario(usuario.strip(), password.strip())
            if datos:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = datos
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        except Exception as e:
            st.error("No fue posible conectar con la base de datos.")
            st.exception(e)

    with st.expander("Usuarios de prueba"):
        st.write("marvin / 1234")
        st.write("dayana / 1234")
        st.write("juanita / 1234")
        st.write("bryan / 1234")


def cerrar_sesion():
    st.session_state.clear()
    st.rerun()
