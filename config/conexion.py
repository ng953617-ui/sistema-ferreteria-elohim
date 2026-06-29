import os
import streamlit as st
import pymysql
import pandas as pd


def obtener_configuracion_mysql() -> dict:
    """Obtiene las credenciales de MySQL desde Streamlit Secrets o variables de entorno."""
    try:
        mysql = st.secrets["mysql"]
        return {
            "host": mysql["host"],
            "port": int(mysql.get("port", 3306)),
            "database": mysql["database"],
            "user": mysql["user"],
            "password": mysql["password"],
        }
    except Exception:
        return {
            "host": os.getenv("MYSQL_HOST", ""),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "database": os.getenv("MYSQL_DATABASE", ""),
            "user": os.getenv("MYSQL_USER", ""),
            "password": os.getenv("MYSQL_PASSWORD", ""),
        }


def conectar():
    """Crea una conexión nueva con la base de datos MySQL."""
    cfg = obtener_configuracion_mysql()
    if not cfg["host"] or not cfg["database"] or not cfg["user"]:
        raise RuntimeError(
            "Faltan credenciales de MySQL. Configura [mysql] en Streamlit Secrets."
        )

    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def consultar_df(sql: str, params=None) -> pd.DataFrame:
    """Ejecuta una consulta SELECT y devuelve un DataFrame."""
    conexion = conectar()
    try:
        df = pd.read_sql(sql, conexion, params=params)
        return df
    finally:
        conexion.close()


def ejecutar(sql: str, params=None) -> int:
    """Ejecuta INSERT, UPDATE o DELETE y devuelve el último id insertado."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, params or ())
            last_id = cursor.lastrowid
        conexion.commit()
        return last_id
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def probar_conexion() -> bool:
    """Verifica si la conexión a MySQL funciona."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            return cursor.fetchone()["ok"] == 1
    finally:
        conexion.close()
