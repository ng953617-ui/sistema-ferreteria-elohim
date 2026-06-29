-- ================================================================
-- Base de datos SGI Ferretería Elohim - Versión alineada al ER
-- Ejecutar en phpMyAdmin dentro de la base MySQL de Clever Cloud.
-- Incluye entidades: CLIENTE, CONSUMIDOR_FINAL, CONTRIBUYENTE y MOVIMIENTO_INVENTARIO.
-- ================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Limpieza de posibles tablas de versiones anteriores
DROP TABLE IF EXISTS arqueos_caja;
DROP TABLE IF EXISTS detalle_compras;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS detalle_ventas;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS ubicaciones;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;

DROP TABLE IF EXISTS movimiento_inventario;
DROP TABLE IF EXISTS arqueo_caja;
DROP TABLE IF EXISTS detalle_compra;
DROP TABLE IF EXISTS orden_compra;
DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS venta;
DROP TABLE IF EXISTS consumidor_final;
DROP TABLE IF EXISTS contribuyente;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS producto_proveedor;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS proveedor;
DROP TABLE IF EXISTS ubicacion;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS usuario;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    rol ENUM('Administrador Principal','Administrador/Supervisor','Vendedor') NOT NULL,
    usuario_login VARCHAR(50) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ubicacion (
    id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    tipo VARCHAR(80),
    descripcion VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre_razon_social VARCHAR(150) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(30),
    vendedor_asignado VARCHAR(120),
    nit VARCHAR(30),
    nrc VARCHAR(30),
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barras VARCHAR(60) NULL UNIQUE,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    id_categoria INT,
    id_ubicacion INT,
    unidad_medida VARCHAR(40) NOT NULL DEFAULT 'Unidad',
    precio_compra DECIMAL(12,2) NOT NULL DEFAULT 0,
    precio_venta DECIMAL(12,2) NOT NULL DEFAULT 0,
    stock_actual DECIMAL(12,2) NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(12,2) NOT NULL DEFAULT 0,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),
    CONSTRAINT fk_producto_ubicacion FOREIGN KEY (id_ubicacion) REFERENCES ubicacion(id_ubicacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE producto_proveedor (
    id_proveedor INT NOT NULL,
    id_producto INT NOT NULL,
    precio_compra DECIMAL(12,2) DEFAULT 0,
    es_principal TINYINT(1) DEFAULT 0,
    PRIMARY KEY (id_proveedor, id_producto),
    CONSTRAINT fk_pp_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),
    CONSTRAINT fk_pp_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(30),
    correo VARCHAR(120),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE consumidor_final (
    id_cliente INT PRIMARY KEY,
    tipo_documento VARCHAR(40),
    num_documento VARCHAR(40),
    CONSTRAINT fk_cf_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE contribuyente (
    id_cliente INT PRIMARY KEY,
    nit VARCHAR(30),
    nrc VARCHAR(30),
    giro VARCHAR(150),
    departamento VARCHAR(80),
    municipio VARCHAR(80),
    CONSTRAINT fk_contrib_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE venta (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_cliente INT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    iva DECIMAL(12,2) NOT NULL DEFAULT 0,
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    metodo_pago ENUM('Efectivo','Transferencia') NOT NULL,
    tipo_comprobante ENUM('Factura interna','Consumidor final','Crédito Fiscal') NOT NULL DEFAULT 'Factura interna',
    descuento DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_venta_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE detalle_venta (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    costo_unitario DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_dv_venta FOREIGN KEY (id_venta) REFERENCES venta(id_venta),
    CONSTRAINT fk_dv_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE orden_compra (
    id_oc INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Pendiente','Recibida','Cancelada') NOT NULL DEFAULT 'Pendiente',
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_oc_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),
    CONSTRAINT fk_oc_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE detalle_compra (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_oc INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_dc_oc FOREIGN KEY (id_oc) REFERENCES orden_compra(id_oc),
    CONSTRAINT fk_dc_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE arqueo_caja (
    id_caja INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha DATE NOT NULL,
    total_efectivo DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_transferencia DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_general DECIMAL(12,2) NOT NULL DEFAULT 0,
    efectivo_contado DECIMAL(12,2) NOT NULL DEFAULT 0,
    diferencia_efectivo DECIMAL(12,2) NOT NULL DEFAULT 0,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_caja_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE movimiento_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_producto INT NOT NULL,
    tipo ENUM('Entrada','Salida','Ajuste') NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    referencia VARCHAR(80),
    motivo VARCHAR(255),
    CONSTRAINT fk_mov_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_mov_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_producto_nombre ON producto(nombre);
CREATE INDEX idx_venta_fecha ON venta(fecha);
CREATE INDEX idx_venta_pago ON venta(metodo_pago);
CREATE INDEX idx_mov_fecha ON movimiento_inventario(fecha);

-- Usuarios de prueba
INSERT INTO usuario(rol, usuario_login, contrasena_hash, nombre_completo) VALUES
('Administrador Principal', 'marvin', '1234', 'Marvin Ramos'),
('Administrador/Supervisor', 'dayana', '1234', 'Dayana Ramos'),
('Vendedor', 'juanita', '1234', 'Juanita de Ramos'),
('Vendedor', 'bryan', '1234', 'Bryan Ramos');

-- Categorías según requerimientos
INSERT INTO categoria(nombre, descripcion) VALUES
('Construcción', 'Cemento, hierro, arena, grava, bloques y materiales pesados'),
('Fontanería', 'PVC, pegamentos, conectores, llaves, grifería y accesorios'),
('Electricidad', 'Cables, breakers, focos, tomacorrientes y accesorios eléctricos'),
('Pinturas', 'Galones, cubetas, brochas, rodillos y complementos'),
('Automotriz', 'Lubricantes, aditivos y herramientas mecánicas'),
('Herramientas', 'Herramientas manuales y eléctricas'),
('Carpintería', 'Accesorios, adhesivos y complementos para madera');

-- Ubicaciones físicas
INSERT INTO ubicacion(nombre, tipo, descripcion) VALUES
('Bodega Pequeña / Interna', 'Bodega', 'Cemento y artículos pequeños de alto valor o cuidado'),
('Área Abierta / Patio de Materiales', 'Patio', 'Bloques, arena, grava, madera y materiales de gran volumen'),
('Mostrador / Exhibición', 'Mostrador', 'Productos de venta rápida y consulta frecuente');

-- Proveedores de ejemplo
INSERT INTO proveedor(nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc) VALUES
('PVC El Salvador', 'San Salvador, El Salvador', '2222-1000', 'Asesor PVC', '', ''),
('Ferretería AZ', 'Santa Ana, El Salvador', '2440-1000', 'Ejecutivo mayorista', '', ''),
('Distribuidora ConstruMax', 'Santa Tecla, El Salvador', '2288-2000', 'Vendedor materiales', '', ''),
('Pinturas ProColor', 'San Salvador, El Salvador', '2211-3000', 'Asesor pinturas', '', ''),
('Lubricantes y Repuestos Ramos', 'Santa Ana, El Salvador', '2447-4500', 'Asesor automotriz', '', ''),
('Herramientas Industriales SV', 'Antiguo Cuscatlán, El Salvador', '2260-1200', 'Asesor herramientas', '', '');

-- Clientes base
INSERT INTO cliente(nombre, direccion, telefono, correo) VALUES
('Cliente mostrador', '', '', ''),
('Consumidor final genérico', '', '', ''),
('Constructora San Miguel', 'Santa Ana, El Salvador', '2440-4567', 'compras@constructorasm.com');

INSERT INTO consumidor_final(id_cliente, tipo_documento, num_documento) VALUES
(2, 'DUI', '');

INSERT INTO contribuyente(id_cliente, nit, nrc, giro, departamento, municipio) VALUES
(3, '0614-000000-000-0', '000000-0', 'Construcción y remodelación', 'Santa Ana', 'Santa Ana');

-- Productos de ejemplo, incluyendo productos con y sin código de barras
INSERT INTO producto(codigo_barras, nombre, descripcion, id_categoria, id_ubicacion, unidad_medida, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES
('902124', 'Cemento gris Fortaleza tipo GU 42.5 kg', 'Saco de cemento para construcción general', 1, 1, 'Saco', 7.20, 8.70, 25, 10),
('CEME-00001', 'Cemento Portland fuerte gris Holcim 42.5 kg', 'Cemento para uso estructural', 1, 1, 'Saco', 8.30, 9.55, 18, 8),
(NULL, 'Arena lavada', 'Material a granel sin código de barras', 1, 2, 'Metro', 16.00, 20.00, 12, 5),
(NULL, 'Bloque de concreto 15 cm', 'Block para pared, venta por unidad', 1, 2, 'Unidad', 0.45, 0.65, 180, 50),
(NULL, 'Grava triturada', 'Material a granel para mezcla', 1, 2, 'Metro', 18.00, 23.00, 10, 4),
('20000214', 'Disco flap 4 1/2 Truper G60', 'Disco para pulido y desbaste', 6, 3, 'Unidad', 1.70, 2.30, 30, 8),
('0600346', 'Tornillo autorroscante 12 x 1 con empaque', 'Tornillo de fijación con empaque', 6, 3, 'Unidad', 0.15, 0.25, 500, 100),
('07008195', 'Brocha de cerda punta blanca 3 pulgadas', 'Brocha para pintura', 4, 3, 'Unidad', 0.60, 0.95, 40, 10),
('0600382', 'Unión PVC lisa 1/2', 'Accesorio de fontanería PVC', 2, 3, 'Unidad', 0.08, 0.12, 80, 20),
('MOTU10W40', 'Aceite Motul 10W40 4T 1L', 'Lubricante para motocicleta', 5, 3, 'Unidad', 10.00, 14.75, 14, 5),
('CABL-0012', 'Cable eléctrico THHN No. 12', 'Cable por metro para instalaciones eléctricas', 3, 3, 'Metro', 0.45, 0.75, 200, 50),
('PINT-0001', 'Pintura látex blanca galón', 'Pintura base agua para interiores', 4, 3, 'Galón', 7.50, 11.00, 16, 5);

-- Relación producto - proveedor
INSERT INTO producto_proveedor(id_producto, id_proveedor, precio_compra, es_principal) VALUES
(1, 3, 7.20, 1), (2, 3, 8.30, 1), (3, 3, 16.00, 1), (4, 3, 0.45, 1),
(5, 3, 18.00, 1), (6, 6, 1.70, 1), (7, 6, 0.15, 1), (8, 4, 0.60, 1),
(9, 1, 0.08, 1), (10, 5, 10.00, 1), (11, 2, 0.45, 1), (12, 4, 7.50, 1);

-- Ventas de ejemplo
INSERT INTO venta(id_usuario, id_cliente, fecha, subtotal, iva, total, metodo_pago, tipo_comprobante, descuento) VALUES
(3, 1, NOW() - INTERVAL 2 DAY, 29.75, 0.00, 29.75, 'Efectivo', 'Factura interna', 0.00),
(4, 2, NOW() - INTERVAL 1 DAY, 16.49, 0.00, 16.49, 'Transferencia', 'Consumidor final', 0.00),
(3, 3, NOW(), 87.00, 0.00, 87.00, 'Efectivo', 'Crédito Fiscal', 0.00);

INSERT INTO detalle_venta(id_venta, id_producto, cantidad, precio_unitario, costo_unitario, subtotal) VALUES
(1, 6, 3, 2.30, 1.70, 6.90),
(1, 8, 2, 0.95, 0.60, 1.90),
(1, 9, 10, 0.12, 0.08, 1.20),
(1, 10, 1, 14.75, 10.00, 14.75),
(1, 11, 4, 0.75, 0.45, 3.00),
(1, 7, 8, 0.25, 0.15, 2.00),
(2, 8, 1, 0.95, 0.60, 0.95),
(2, 7, 10, 0.25, 0.15, 2.50),
(2, 9, 20, 0.12, 0.08, 2.40),
(2, 11, 6, 0.75, 0.45, 4.50),
(2, 12, 1, 6.14, 4.50, 6.14),
(3, 1, 10, 8.70, 7.20, 87.00);

-- Movimientos iniciales y salidas de ejemplo
INSERT INTO movimiento_inventario(id_usuario, id_producto, tipo, cantidad, fecha, referencia, motivo) VALUES
(1, 1, 'Entrada', 25, NOW() - INTERVAL 7 DAY, 'Carga inicial', 'Inventario inicial'),
(1, 2, 'Entrada', 18, NOW() - INTERVAL 7 DAY, 'Carga inicial', 'Inventario inicial'),
(1, 3, 'Entrada', 12, NOW() - INTERVAL 7 DAY, 'Carga inicial', 'Inventario inicial'),
(3, 6, 'Salida', 3, NOW() - INTERVAL 2 DAY, 'Venta 1', 'Venta registrada'),
(4, 12, 'Salida', 1, NOW() - INTERVAL 1 DAY, 'Venta 2', 'Venta registrada'),
(3, 1, 'Salida', 10, NOW(), 'Venta 3', 'Venta registrada');
