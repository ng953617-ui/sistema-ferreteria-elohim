"""
config/db.py
Conexión centralizada a MySQL (Clever Cloud) usando los secretos de Streamlit.
En Streamlit Cloud, configura esto en Settings > Secrets:

[mysql]
host = "TU_HOST.clever-cloud.com"
port = 3306
database = "TU_BASE"
user = "TU_USUARIO"
password = "TU_PASSWORD"
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        cfg = st.secrets["mysql"]
        conn = mysql.connector.connect(
            host=cfg["host"],
            port=int(cfg.get("port", 3306)),
            database=cfg["database"],
            user=cfg["user"],
            password=cfg["password"],
            autocommit=False,
        )
        return conn
    except Error as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None


def run_query(query, params=None, fetch=True):
    """Ejecuta SELECT y devuelve lista de dicts."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        result = cur.fetchall() if fetch else []
        return result
    finally:
        cur.close()
        conn.close()


def run_action(query, params=None):
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve lastrowid."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    except Error as e:
        conn.rollback()
        st.error(f"Error ejecutando la operación: {e}")
        return None
    finally:
        cur.close()
        conn.close()
