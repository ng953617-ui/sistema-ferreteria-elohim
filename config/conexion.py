"""Conexión centralizada a MySQL para Streamlit Cloud / Clever Cloud."""
from __future__ import annotations

import os
from typing import Any, Iterable

import mysql.connector
import pandas as pd
import streamlit as st


class DBConfigError(RuntimeError):
    """Error de configuración de base de datos."""


def _read_secret_value(secrets_obj: Any, *names: str, default: Any = None) -> Any:
    """Lee una llave aceptando variantes usadas en la práctica."""
    for name in names:
        try:
            if name in secrets_obj:
                return secrets_obj[name]
        except Exception:
            pass
    return default


def get_mysql_config() -> dict[str, Any]:
    """Obtiene credenciales desde st.secrets o variables de entorno.

    En Streamlit Cloud usar Settings > Secrets:
    [mysql]
    host = "..."
    port = 3306
    database = "..."
    user = "..."
    password = "..."

    También acepta la llave Contrasena si se copió desde el documento del proyecto.
    """
    mysql_section: Any = {}
    try:
        mysql_section = st.secrets.get("mysql", {})
    except Exception:
        mysql_section = {}

    host = _read_secret_value(mysql_section, "host", default=os.getenv("MYSQL_HOST"))
    port = int(_read_secret_value(mysql_section, "port", default=os.getenv("MYSQL_PORT", 3306)))
    database = _read_secret_value(mysql_section, "database", "db", default=os.getenv("MYSQL_DATABASE"))
    user = _read_secret_value(mysql_section, "user", "username", default=os.getenv("MYSQL_USER"))
    password = _read_secret_value(
        mysql_section,
        "password",
        "Contrasena",
        "contraseña",
        "contrasena",
        default=os.getenv("MYSQL_PASSWORD"),
    )

    missing = [name for name, value in {
        "host": host,
        "database": database,
        "user": user,
        "password": password,
    }.items() if not value]
    if missing:
        raise DBConfigError(
            "Faltan credenciales de MySQL en Streamlit Secrets o variables de entorno: "
            + ", ".join(missing)
        )

    return {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password,
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
    }


def get_connection():
    """Abre una conexión nueva a MySQL."""
    return mysql.connector.connect(**get_mysql_config())


def fetch_df(query: str, params: Iterable[Any] | None = None) -> pd.DataFrame:
    """Ejecuta una consulta SELECT y devuelve un DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


def execute(query: str, params: Iterable[Any] | None = None, many: bool = False) -> int:
    """Ejecuta INSERT/UPDATE/DELETE y devuelve filas afectadas."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        if many:
            cur.executemany(query, params or [])
        else:
            cur.execute(query, params or ())
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_return_id(query: str, params: Iterable[Any] | None = None) -> int:
    """Ejecuta INSERT y devuelve el ID autogenerado."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return int(cur.lastrowid)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
