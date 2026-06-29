import streamlit as st
from config.conexion import inicializar_bd
from login import mostrar_login
from menu import mostrar_menu

st.set_page_config(
    page_title="Ferretería Elohim",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 2rem;}
[data-testid="stSidebar"] {min-width: 290px;}
</style>
""", unsafe_allow_html=True)

try:
    inicializar_bd()
except Exception as e:
    st.error("No fue posible inicializar la base de datos. Revise los Secrets de Streamlit y que Clever Cloud esté activo.")
    st.exception(e)
    st.stop()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_menu()
