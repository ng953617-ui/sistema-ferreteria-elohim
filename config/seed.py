"""
config/seed.py
Ejecuta este script UNA SOLA VEZ desde tu computadora (no en Streamlit Cloud)
para crear los usuarios iniciales con contraseña cifrada (bcrypt).

Uso:
    pip install mysql-connector-python bcrypt
    python config/seed.py
"""

import bcrypt
import mysql.connector

# --- EDITA ESTOS DATOS CON TUS CREDENCIALES DE CLEVER CLOUD ---
DB_CONFIG = {
    "host": "TU_HOST.clever-cloud.com",
    "port": 3306,
    "database": "TU_BASE",
    "user": "TU_USUARIO",
    "password": "TU_PASSWORD",
}

USUARIOS = [
    ("Marvin Ramos", "Administrador", "marvin", "admin123"),
    ("Dayana Ramos", "Supervisor", "dayana", "admin123"),
    ("Juanita de Ramos", "Vendedor", "juanita", "venta123"),
    ("Bryan Ramos", "Vendedor", "bryan", "venta123"),
]

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    for nombre, rol, login, pw in USUARIOS:
        hash_pw = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO USUARIO (Nombre, Rol, Usuario_Login, Contrasena_Hash) "
            "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE Contrasena_Hash=%s",
            (nombre, rol, login, hash_pw, hash_pw)
        )
    conn.commit()
    cur.close()
    conn.close()
    print("Usuarios creados/actualizados correctamente.")

if __name__ == "__main__":
    main()
