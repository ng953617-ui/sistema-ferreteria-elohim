import streamlit as st
from login import mostrar_login
from menu import mostrar_menu

st.set_page_config(
    page_title="SGI Ferretería Elohim",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {padding-top: 2rem;}
    div[data-testid="stMetric"] {
        background-color: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.16);
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_menu()
