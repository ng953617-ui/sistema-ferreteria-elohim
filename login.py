import streamlit as st
from config.conexion import conectar


def validar_usuario(usuario: str, password: str):
    """Valida las credenciales contra la tabla usuario del modelo ER."""
    sql = """
        SELECT id_usuario, usuario_login AS usuario, nombre_completo, rol
        FROM usuario
        WHERE usuario_login = %s AND contrasena_hash = %s AND activo = 1
        LIMIT 1
    """
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, (usuario, password))
            return cursor.fetchone()
    finally:
        conexion.close()


def mostrar_login():
    """Pantalla de inicio de sesión."""
    st.title("🔐 Ferretería Elohim")
    st.subheader("Sistema de Gestión de Información")
    st.write("Ingrese sus credenciales para acceder al sistema.")

    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Iniciar sesión")

    if enviar:
        if not usuario or not password:
            st.warning("Debe ingresar usuario y contraseña.")
            return
        try:
            datos_usuario = validar_usuario(usuario.strip(), password.strip())
            if datos_usuario:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = datos_usuario
                st.success("Inicio de sesión correcto.")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        except Exception as e:
            st.error("No fue posible conectar con la base de datos.")
            st.exception(e)

    with st.expander("Usuarios de prueba"):
        st.write("Administrador principal: **marvin / 1234**")
        st.write("Supervisor: **dayana / 1234**")
        st.write("Vendedor: **juanita / 1234** o **bryan / 1234**")
