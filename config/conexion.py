import streamlit as st
import pymysql
import pandas as pd
from pymysql.cursors import DictCursor


def _mysql_config():
    """Lee credenciales desde Streamlit Secrets."""
    return {
        "host": st.secrets["mysql"]["host"].strip(),
        "port": int(st.secrets["mysql"].get("port", 3306)),
        "user": st.secrets["mysql"]["user"].strip(),
        "password": st.secrets["mysql"]["password"],
        "database": st.secrets["mysql"]["database"].strip(),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
        "connect_timeout": 10,
    }


def conectar():
    """Abre una conexión con MySQL."""
    return pymysql.connect(**_mysql_config())


def probar_conexion():
    try:
        con = conectar()
        con.close()
        return True
    except Exception:
        return False


def consultar(sql, params=None):
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        con.close()


def consultar_df(sql, params=None):
    data = consultar(sql, params)
    return pd.DataFrame(data)


def ejecutar(sql, params=None):
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params or ())
        con.commit()
        return True
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def ejecutar_insert(sql, params=None):
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params or ())
            new_id = cur.lastrowid
        con.commit()
        return new_id
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _count_table(cur, table_name):
    cur.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
    return int(cur.fetchone()["total"])


def inicializar_bd():
    """
    Crea tablas y carga datos iniciales si la base está vacía.
    No borra datos existentes. Esta es la solución definitiva para evitar importar SQL manualmente.
    """
    con = conectar()
    try:
        with con.cursor() as cur:
            # Tablas principales
            cur.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) NOT NULL UNIQUE,
                nombre_completo VARCHAR(120) NOT NULL,
                rol VARCHAR(50) NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                activo TINYINT DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS categoria (
                id_categoria INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                activo TINYINT DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS ubicacion (
                id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL UNIQUE,
                tipo VARCHAR(80) DEFAULT 'General',
                activo TINYINT DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS proveedor (
                id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
                nombre_razon_social VARCHAR(180) NOT NULL,
                direccion VARCHAR(255),
                telefono VARCHAR(30),
                vendedor_asignado VARCHAR(120),
                nit VARCHAR(40),
                nrc VARCHAR(40),
                activo TINYINT DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                direccion VARCHAR(255),
                telefono VARCHAR(30),
                correo VARCHAR(120),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo TINYINT DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS consumidor_final (
                id_cliente INT PRIMARY KEY,
                tipo_documento VARCHAR(40),
                num_documento VARCHAR(40),
                CONSTRAINT fk_cf_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS contribuyente (
                id_cliente INT PRIMARY KEY,
                nit VARCHAR(40),
                nrc VARCHAR(40),
                giro VARCHAR(150),
                departamento VARCHAR(80),
                municipio VARCHAR(80),
                CONSTRAINT fk_cont_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS producto (
                id_producto INT AUTO_INCREMENT PRIMARY KEY,
                codigo_barras VARCHAR(80),
                nombre VARCHAR(180) NOT NULL,
                descripcion VARCHAR(255),
                id_categoria INT,
                id_ubicacion INT,
                unidad VARCHAR(40) DEFAULT 'Unidad',
                stock_actual DECIMAL(10,2) DEFAULT 0,
                stock_minimo DECIMAL(10,2) DEFAULT 0,
                precio_compra DECIMAL(10,2) DEFAULT 0,
                precio_venta DECIMAL(10,2) DEFAULT 0,
                tiene_codigo TINYINT DEFAULT 1,
                activo TINYINT DEFAULT 1,
                CONSTRAINT fk_prod_categoria FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),
                CONSTRAINT fk_prod_ubicacion FOREIGN KEY (id_ubicacion) REFERENCES ubicacion(id_ubicacion)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS producto_proveedor (
                id_producto INT NOT NULL,
                id_proveedor INT NOT NULL,
                precio_compra DECIMAL(10,2) DEFAULT 0,
                es_principal TINYINT DEFAULT 0,
                PRIMARY KEY (id_producto, id_proveedor),
                CONSTRAINT fk_pp_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_pp_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS venta (
                id_venta INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT,
                id_cliente INT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                subtotal DECIMAL(10,2) DEFAULT 0,
                iva DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2) DEFAULT 0,
                metodo_pago VARCHAR(40) DEFAULT 'Efectivo',
                tipo_comprobante VARCHAR(60) DEFAULT 'Factura interna',
                CONSTRAINT fk_venta_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
                CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id_detalle INT AUTO_INCREMENT PRIMARY KEY,
                id_venta INT NOT NULL,
                id_producto INT NOT NULL,
                cantidad DECIMAL(10,2) NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                CONSTRAINT fk_dv_venta FOREIGN KEY (id_venta) REFERENCES venta(id_venta)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_dv_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS orden_compra (
                id_orden INT AUTO_INCREMENT PRIMARY KEY,
                id_proveedor INT NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR(40) DEFAULT 'Recibida',
                total DECIMAL(10,2) DEFAULT 0,
                CONSTRAINT fk_oc_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS detalle_compra (
                id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
                id_orden INT NOT NULL,
                id_producto INT NOT NULL,
                cantidad DECIMAL(10,2) NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
                CONSTRAINT fk_dc_orden FOREIGN KEY (id_orden) REFERENCES orden_compra(id_orden)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_dc_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS arqueo_caja (
                id_arqueo INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT NOT NULL,
                fecha DATE NOT NULL,
                total_efectivo DECIMAL(10,2) DEFAULT 0,
                total_transferencia DECIMAL(10,2) DEFAULT 0,
                total_general DECIMAL(10,2) DEFAULT 0,
                observaciones VARCHAR(255),
                CONSTRAINT fk_arqueo_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS movimiento_inventario (
                id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
                id_producto INT NOT NULL,
                tipo_movimiento VARCHAR(30) NOT NULL,
                cantidad DECIMAL(10,2) NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                referencia_id INT NULL,
                id_usuario INT NULL,
                motivo VARCHAR(255),
                CONSTRAINT fk_mi_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
                CONSTRAINT fk_mi_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Seed de usuarios
            if _count_table(cur, "usuario") == 0:
                cur.executemany("""
                    INSERT INTO usuario (usuario, nombre_completo, rol, password_hash, activo)
                    VALUES (%s, %s, %s, %s, 1)
                """, [
                    ("marvin", "Marvin Ramos", "Administrador Principal", "1234"),
                    ("dayana", "Dayana Ramos", "Administrador/Supervisor", "1234"),
                    ("juanita", "Juanita", "Vendedor", "1234"),
                    ("bryan", "Bryan", "Vendedor", "1234"),
                ])

            if _count_table(cur, "categoria") == 0:
                cur.executemany("INSERT INTO categoria (nombre, activo) VALUES (%s, 1)", [
                    ("Construcción",), ("Fontanería",), ("Electricidad",), ("Pinturas",),
                    ("Automotriz",), ("Herramientas",), ("Carpintería",), ("Ferretería general",)
                ])

            if _count_table(cur, "ubicacion") == 0:
                cur.executemany("INSERT INTO ubicacion (nombre, tipo, activo) VALUES (%s, %s, 1)", [
                    ("Mostrador", "Sala de venta"),
                    ("Bodega interna", "Almacenamiento"),
                    ("Patio de materiales", "Área abierta"),
                    ("Estante de pinturas", "Sala de venta"),
                    ("Área de herramientas", "Sala de venta"),
                ])

            if _count_table(cur, "proveedor") == 0:
                cur.executemany("""
                    INSERT INTO proveedor
                    (nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                """, [
                    ("Distribuidora ConstruMax", "San Salvador", "2222-1000", "Carlos Pérez", "0614-010101-001-1", "123456-7"),
                    ("PVC El Salvador", "Santa Ana", "2440-2020", "Ana López", "0210-020202-002-2", "234567-8"),
                    ("Pinturas ProColor", "San Salvador", "2260-3030", "Marta Rivas", "0614-030303-003-3", "345678-9"),
                    ("Herramientas El Constructor", "Santa Tecla", "2288-4040", "Luis Gómez", "0511-040404-004-4", "456789-0"),
                ])

            if _count_table(cur, "cliente") == 0:
                cur.execute("""
                    INSERT INTO cliente (nombre, direccion, telefono, correo, activo)
                    VALUES ('Cliente mostrador', 'Venta rápida', 'N/A', 'N/A', 1)
                """)
                cliente_id = cur.lastrowid
                cur.execute("INSERT INTO consumidor_final (id_cliente, tipo_documento, num_documento) VALUES (%s, 'N/A', 'N/A')", (cliente_id,))
                cur.execute("""
                    INSERT INTO cliente (nombre, direccion, telefono, correo, activo)
                    VALUES ('Constructora Santa Ana', 'Santa Ana', '2400-9090', 'compras@constructora.com', 1)
                """)
                cliente_id = cur.lastrowid
                cur.execute("""
                    INSERT INTO contribuyente (id_cliente, nit, nrc, giro, departamento, municipio)
                    VALUES (%s, '0614-111111-101-1', '998877-6', 'Construcción', 'Santa Ana', 'Santa Ana')
                """, (cliente_id,))

            if _count_table(cur, "producto") == 0:
                # Obtener IDs base
                cur.execute("SELECT id_categoria, nombre FROM categoria")
                cat = {r["nombre"]: r["id_categoria"] for r in cur.fetchall()}
                cur.execute("SELECT id_ubicacion, nombre FROM ubicacion")
                ubi = {r["nombre"]: r["id_ubicacion"] for r in cur.fetchall()}
                productos = [
                    ("750100000001", "Cemento gris Fortaleza tipo GU 42.5 kg", "Bolsa de cemento para construcción", cat["Construcción"], ubi["Patio de materiales"], "Bolsa", 85, 15, 7.20, 8.75, 1),
                    (None, "Arena lavada", "Arena por metro cúbico", cat["Construcción"], ubi["Patio de materiales"], "m³", 12, 4, 18.00, 25.00, 0),
                    (None, "Grava triturada", "Grava para mezcla de concreto", cat["Construcción"], ubi["Patio de materiales"], "m³", 10, 3, 22.00, 30.00, 0),
                    (None, "Bloque de concreto 15 cm", "Bloque para pared", cat["Construcción"], ubi["Patio de materiales"], "Unidad", 300, 80, 0.46, 0.65, 0),
                    ("750100000005", "Tubo PVC 1/2 pulg", "Tubo para fontanería", cat["Fontanería"], ubi["Bodega interna"], "Unidad", 65, 20, 1.10, 1.65, 1),
                    ("750100000006", "Unión PVC 1/2 pulg", "Accesorio PVC", cat["Fontanería"], ubi["Mostrador"], "Unidad", 120, 30, 0.18, 0.35, 1),
                    ("750100000007", "Cable eléctrico THHN No. 12", "Cable eléctrico por metro", cat["Electricidad"], ubi["Mostrador"], "Metro", 500, 100, 0.35, 0.55, 1),
                    ("750100000008", "Tomacorriente doble", "Tomacorriente residencial", cat["Electricidad"], ubi["Mostrador"], "Unidad", 45, 10, 1.25, 2.00, 1),
                    ("750100000009", "Pintura látex blanca galón", "Pintura para interiores", cat["Pinturas"], ubi["Estante de pinturas"], "Galón", 30, 8, 13.00, 18.50, 1),
                    ("750100000010", "Brocha 2 pulgadas", "Brocha de cerda", cat["Pinturas"], ubi["Estante de pinturas"], "Unidad", 55, 12, 0.85, 1.50, 1),
                    ("750100000011", "Martillo uña 16 oz", "Herramienta manual", cat["Herramientas"], ubi["Área de herramientas"], "Unidad", 18, 5, 4.50, 7.95, 1),
                    ("750100000012", "Disco flap 4 1/2 Truper G60", "Disco para pulido", cat["Herramientas"], ubi["Área de herramientas"], "Unidad", 40, 10, 1.10, 1.85, 1),
                    (None, "Regla de madera 1x2 pulg", "Madera para construcción", cat["Carpintería"], ubi["Patio de materiales"], "Vara", 80, 20, 1.25, 2.00, 0),
                    (None, "Cuartón de madera", "Madera estructural", cat["Carpintería"], ubi["Patio de materiales"], "Unidad", 35, 10, 3.75, 5.50, 0),
                    ("750100000015", "Aceite Motul 20W50", "Lubricante automotriz", cat["Automotriz"], ubi["Mostrador"], "Litro", 24, 6, 4.25, 6.75, 1),
                ]
                cur.executemany("""
                    INSERT INTO producto
                    (codigo_barras, nombre, descripcion, id_categoria, id_ubicacion, unidad,
                     stock_actual, stock_minimo, precio_compra, precio_venta, tiene_codigo, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """, productos)

                cur.execute("SELECT id_proveedor, nombre_razon_social FROM proveedor")
                proveedores = cur.fetchall()
                prov_ids = [p["id_proveedor"] for p in proveedores]
                cur.execute("SELECT id_producto, precio_compra FROM producto")
                for idx, p in enumerate(cur.fetchall()):
                    prov = prov_ids[idx % len(prov_ids)]
                    cur.execute("""
                        INSERT INTO producto_proveedor (id_producto, id_proveedor, precio_compra, es_principal)
                        VALUES (%s, %s, %s, 1)
                    """, (p["id_producto"], prov, p["precio_compra"]))

                # Movimientos iniciales
                cur.execute("SELECT id_usuario FROM usuario WHERE usuario='marvin'")
                user_id = cur.fetchone()["id_usuario"]
                cur.execute("SELECT id_producto, stock_actual FROM producto")
                for p in cur.fetchall():
                    cur.execute("""
                        INSERT INTO movimiento_inventario
                        (id_producto, tipo_movimiento, cantidad, referencia_id, id_usuario, motivo)
                        VALUES (%s, 'Entrada', %s, NULL, %s, 'Carga inicial de inventario')
                    """, (p["id_producto"], p["stock_actual"], user_id))

            if _count_table(cur, "venta") == 0:
                cur.execute("SELECT id_usuario FROM usuario WHERE usuario='marvin'")
                user_id = cur.fetchone()["id_usuario"]
                cur.execute("SELECT id_cliente FROM cliente WHERE nombre='Cliente mostrador'")
                cliente_id = cur.fetchone()["id_cliente"]
                cur.execute("""
                    INSERT INTO venta (id_usuario, id_cliente, subtotal, iva, total, metodo_pago, tipo_comprobante)
                    VALUES (%s, %s, 16.49, 0, 16.49, 'Efectivo', 'Factura interna')
                """, (user_id, cliente_id))
                venta_id = cur.lastrowid
                cur.execute("SELECT id_producto, precio_venta FROM producto WHERE nombre LIKE 'Martillo%' LIMIT 1")
                prod = cur.fetchone()
                if prod:
                    cur.execute("""
                        INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, 1, %s, %s)
                    """, (venta_id, prod["id_producto"], prod["precio_venta"], prod["precio_venta"]))

        con.commit()
        return True
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
