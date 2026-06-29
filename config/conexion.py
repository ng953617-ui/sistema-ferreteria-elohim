import os
import streamlit as st
import pymysql
import pandas as pd


def obtener_configuracion_mysql() -> dict:
    """Obtiene credenciales de MySQL desde Streamlit Secrets o variables de entorno."""
    try:
        mysql = st.secrets["mysql"]
        return {
            "host": str(mysql["host"]).strip(),
            "port": int(mysql.get("port", 3306)),
            "database": str(mysql["database"]).strip(),
            "user": str(mysql["user"]).strip(),
            "password": str(mysql["password"]),
        }
    except Exception:
        return {
            "host": os.getenv("MYSQL_HOST", "").strip(),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "database": os.getenv("MYSQL_DATABASE", "").strip(),
            "user": os.getenv("MYSQL_USER", "").strip(),
            "password": os.getenv("MYSQL_PASSWORD", ""),
        }


def conectar():
    """Crea una conexión nueva con la base de datos MySQL."""
    cfg = obtener_configuracion_mysql()
    if not cfg["host"] or not cfg["database"] or not cfg["user"]:
        raise RuntimeError("Faltan credenciales de MySQL. Configura [mysql] en Streamlit Secrets.")

    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=15,
        read_timeout=30,
        write_timeout=30,
    )


def sanear_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas corruptas que pueden aparecer cuando se cargan encabezados como datos,
    por ejemplo filas donde los valores son 'nombre', 'stock_actual', 'precio_venta', etc.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    filas_validas = []
    columnas = [str(c).strip().lower() for c in df.columns]
    for _, fila in df.iterrows():
        coincidencias = 0
        for col_original, col_limpia in zip(df.columns, columnas):
            valor = fila[col_original]
            if pd.notna(valor) and str(valor).strip().lower() == col_limpia:
                coincidencias += 1
        filas_validas.append(coincidencias < 2)

    return df.loc[filas_validas].reset_index(drop=True)


def consultar_df(sql: str, params=None) -> pd.DataFrame:
    """Ejecuta una consulta SELECT y devuelve un DataFrame limpio."""
    conexion = conectar()
    try:
        df = pd.read_sql(sql, conexion, params=params)
        return sanear_dataframe(df)
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
