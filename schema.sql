-- =====================================================
-- FERRETERÍA ELOHIM - Esquema de Base de Datos (MySQL)
-- Ejecutar este script completo en phpMyAdmin (Clever Cloud)
-- =====================================================

CREATE TABLE IF NOT EXISTS CATEGORIA (
    ID_Categoria INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS UBICACION (
    ID_Ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Tipo ENUM('Bodega Pequeña','Área Abierta') NOT NULL
);

CREATE TABLE IF NOT EXISTS PRODUCTO (
    ID_Producto INT AUTO_INCREMENT PRIMARY KEY,
    Codigo_Barra VARCHAR(50) NULL,
    Nombre VARCHAR(200) NOT NULL,
    Categoria_ID INT NULL,
    Ubicacion_ID INT NULL,
    Precio_Venta DECIMAL(10,2) NOT NULL DEFAULT 0,
    Unidad_Medida VARCHAR(30) NOT NULL DEFAULT 'unidad',
    Stock_Actual DECIMAL(10,2) NOT NULL DEFAULT 0,
    Stock_Minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
    Tiene_Codigo_Barra TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (Categoria_ID) REFERENCES CATEGORIA(ID_Categoria),
    FOREIGN KEY (Ubicacion_ID) REFERENCES UBICACION(ID_Ubicacion)
);

CREATE TABLE IF NOT EXISTS PROVEEDOR (
    ID_Proveedor INT AUTO_INCREMENT PRIMARY KEY,
    Razon_Social VARCHAR(200) NOT NULL,
    Direccion VARCHAR(300),
    Telefono VARCHAR(20),
    Vendedor_Asignado VARCHAR(100),
    NIT VARCHAR(20),
    NRC VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS PRODUCTO_PROVEEDOR (
    Producto_ID INT NOT NULL,
    Proveedor_ID INT NOT NULL,
    Precio_Compra DECIMAL(10,2) NOT NULL DEFAULT 0,
    Es_Principal TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (Producto_ID, Proveedor_ID),
    FOREIGN KEY (Producto_ID) REFERENCES PRODUCTO(ID_Producto),
    FOREIGN KEY (Proveedor_ID) REFERENCES PROVEEDOR(ID_Proveedor)
);

CREATE TABLE IF NOT EXISTS ORDEN_COMPRA (
    ID_Orden INT AUTO_INCREMENT PRIMARY KEY,
    Proveedor_ID INT NOT NULL,
    Fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Estado ENUM('pendiente','recibida','cancelada') NOT NULL DEFAULT 'pendiente',
    Total DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (Proveedor_ID) REFERENCES PROVEEDOR(ID_Proveedor)
);

CREATE TABLE IF NOT EXISTS DETALLE_COMPRA (
    Orden_ID INT NOT NULL,
    Producto_ID INT NOT NULL,
    Cantidad DECIMAL(10,2) NOT NULL,
    Precio_Unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (Orden_ID, Producto_ID),
    FOREIGN KEY (Orden_ID) REFERENCES ORDEN_COMPRA(ID_Orden),
    FOREIGN KEY (Producto_ID) REFERENCES PRODUCTO(ID_Producto)
);

CREATE TABLE IF NOT EXISTS USUARIO (
    ID_Usuario INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Rol ENUM('Administrador','Supervisor','Vendedor') NOT NULL,
    Usuario_Login VARCHAR(50) NOT NULL UNIQUE,
    Contrasena_Hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS CLIENTE (
    ID_Cliente INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(200) NOT NULL,
    NIT VARCHAR(20),
    NRC VARCHAR(20),
    Giro VARCHAR(150),
    Departamento VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS VENTA (
    ID_Venta INT AUTO_INCREMENT PRIMARY KEY,
    Usuario_ID INT NOT NULL,
    Cliente_ID INT NULL,
    Fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Total DECIMAL(10,2) NOT NULL DEFAULT 0,
    Metodo_Pago ENUM('efectivo','transferencia') NOT NULL,
    Tipo_Comprobante ENUM('factura interna','CCF','consumidor final') NOT NULL DEFAULT 'consumidor final',
    FOREIGN KEY (Usuario_ID) REFERENCES USUARIO(ID_Usuario),
    FOREIGN KEY (Cliente_ID) REFERENCES CLIENTE(ID_Cliente)
);

CREATE TABLE IF NOT EXISTS DETALLE_VENTA (
    Venta_ID INT NOT NULL,
    Producto_ID INT NOT NULL,
    Cantidad DECIMAL(10,2) NOT NULL,
    Precio_Unitario DECIMAL(10,2) NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (Venta_ID, Producto_ID),
    FOREIGN KEY (Venta_ID) REFERENCES VENTA(ID_Venta),
    FOREIGN KEY (Producto_ID) REFERENCES PRODUCTO(ID_Producto)
);

CREATE TABLE IF NOT EXISTS ARQUEO_CAJA (
    ID_Arqueo INT AUTO_INCREMENT PRIMARY KEY,
    Usuario_ID INT NOT NULL,
    Fecha DATE NOT NULL,
    Total_Efectivo DECIMAL(10,2) NOT NULL DEFAULT 0,
    Total_Transferencia DECIMAL(10,2) NOT NULL DEFAULT 0,
    Total_General DECIMAL(10,2) NOT NULL DEFAULT 0,
    UNIQUE KEY unico_dia (Fecha),
    FOREIGN KEY (Usuario_ID) REFERENCES USUARIO(ID_Usuario)
);

CREATE TABLE IF NOT EXISTS MOVIMIENTO_INVENTARIO (
    ID_Movimiento INT AUTO_INCREMENT PRIMARY KEY,
    Producto_ID INT NOT NULL,
    Tipo_Movimiento ENUM('entrada','salida','ajuste') NOT NULL,
    Cantidad DECIMAL(10,2) NOT NULL,
    Fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Referencia_ID INT NULL,
    Usuario_ID INT NOT NULL,
    Motivo VARCHAR(200) NULL,
    FOREIGN KEY (Producto_ID) REFERENCES PRODUCTO(ID_Producto),
    FOREIGN KEY (Usuario_ID) REFERENCES USUARIO(ID_Usuario)
);

-- =====================================================
-- DATOS INICIALES (usuarios de prueba y catálogos base)
-- Contraseñas en texto: marvin=admin123, dayana=admin123, juanita=venta123, bryan=venta123
-- (los hashes se generan en la app al primer arranque si la tabla está vacía,
--  pero puedes insertar manualmente con la utilidad incluida en config/seed.py)
-- =====================================================

INSERT INTO CATEGORIA (Nombre) VALUES
('Construcción'),('Fontanería'),('Electricidad'),('Pinturas'),
('Automotriz'),('Herramientas'),('Carpintería');

INSERT INTO UBICACION (Nombre, Tipo) VALUES
('Bodega Pequeña','Bodega Pequeña'),
('Área Abierta / Patio','Área Abierta');
