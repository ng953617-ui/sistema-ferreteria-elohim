# Diccionario de datos - SGI Ferretería Elohim

Versión actualizada para coincidir con el diagrama Entidad-Relación presentado por el equipo.

## usuario
| Campo | Tipo | Descripción |
|---|---|---|
| id_usuario | INT PK | Identificador del usuario. |
| rol | ENUM | Administrador Principal, Administrador/Supervisor o Vendedor. |
| usuario_login | VARCHAR(50) | Nombre de acceso al sistema. |
| contrasena_hash | VARCHAR(100) | Contraseña de acceso usada para el prototipo. |
| nombre_completo | VARCHAR(120) | Nombre del colaborador. |
| activo | TINYINT | Indica si el usuario puede ingresar. |

## categoria
| Campo | Tipo | Descripción |
|---|---|---|
| id_categoria | INT PK | Identificador de categoría. |
| nombre | VARCHAR(80) | Nombre de categoría de producto. |
| descripcion | VARCHAR(255) | Descripción de la categoría. |

## ubicacion
| Campo | Tipo | Descripción |
|---|---|---|
| id_ubicacion | INT PK | Identificador de ubicación física. |
| nombre | VARCHAR(80) | Nombre de área de almacenamiento. |
| tipo | VARCHAR(80) | Bodega, patio, mostrador u otro. |
| descripcion | VARCHAR(255) | Descripción del área. |

## proveedor
| Campo | Tipo | Descripción |
|---|---|---|
| id_proveedor | INT PK | Identificador del proveedor. |
| nombre_razon_social | VARCHAR(150) | Nombre comercial o razón social. |
| direccion | VARCHAR(255) | Dirección física comercial. |
| telefono | VARCHAR(30) | Teléfono de contacto. |
| vendedor_asignado | VARCHAR(120) | Asesor asignado. |
| nit | VARCHAR(30) | NIT del proveedor. |
| nrc | VARCHAR(30) | NRC del proveedor. |

## producto
| Campo | Tipo | Descripción |
|---|---|---|
| id_producto | INT PK | Identificador del producto. |
| codigo_barras | VARCHAR(60) | Código de barras, puede ser nulo para productos pesados o a granel. |
| nombre | VARCHAR(160) | Nombre del producto. |
| descripcion | TEXT | Descripción del producto. |
| id_categoria | INT FK | Categoría del producto. |
| id_ubicacion | INT FK | Ubicación física del producto. |
| unidad_medida | VARCHAR(40) | Unidad, metro, saco, galón, etc. |
| precio_compra | DECIMAL | Precio de compra. |
| precio_venta | DECIMAL | Precio de venta. |
| stock_actual | DECIMAL | Existencia actual. |
| stock_minimo | DECIMAL | Umbral mínimo para alerta. |
| activo | TINYINT | Producto activo o inactivo. |

## producto_proveedor
| Campo | Tipo | Descripción |
|---|---|---|
| id_proveedor | INT PK/FK | Proveedor asociado. |
| id_producto | INT PK/FK | Producto asociado. |
| precio_compra | DECIMAL | Precio de compra de referencia. |
| es_principal | TINYINT | Indica si es proveedor principal. |

## cliente
| Campo | Tipo | Descripción |
|---|---|---|
| id_cliente | INT PK | Identificador del cliente. |
| nombre | VARCHAR(150) | Nombre del cliente. |
| direccion | VARCHAR(255) | Dirección. |
| telefono | VARCHAR(30) | Teléfono. |
| correo | VARCHAR(120) | Correo electrónico. |

## consumidor_final
| Campo | Tipo | Descripción |
|---|---|---|
| id_cliente | INT PK/FK | Cliente asociado. |
| tipo_documento | VARCHAR(40) | DUI, pasaporte u otro. |
| num_documento | VARCHAR(40) | Número de documento. |

## contribuyente
| Campo | Tipo | Descripción |
|---|---|---|
| id_cliente | INT PK/FK | Cliente asociado. |
| nit | VARCHAR(30) | NIT del cliente. |
| nrc | VARCHAR(30) | NRC del cliente. |
| giro | VARCHAR(150) | Giro comercial. |
| departamento | VARCHAR(80) | Departamento. |
| municipio | VARCHAR(80) | Municipio. |

## venta
| Campo | Tipo | Descripción |
|---|---|---|
| id_venta | INT PK | Identificador de venta. |
| id_usuario | INT FK | Vendedor responsable. |
| id_cliente | INT FK | Cliente asociado. |
| fecha | DATETIME | Fecha y hora de venta. |
| subtotal | DECIMAL | Subtotal antes de IVA y descuento. |
| iva | DECIMAL | Impuesto calculado. |
| total | DECIMAL | Total final. |
| metodo_pago | ENUM | Efectivo o Transferencia. |
| tipo_comprobante | ENUM | Factura interna, Consumidor final o Crédito Fiscal. |
| descuento | DECIMAL | Descuento aplicado. |

## detalle_venta
| Campo | Tipo | Descripción |
|---|---|---|
| id_detalle_venta | INT PK | Identificador de línea de venta. |
| id_venta | INT FK | Venta asociada. |
| id_producto | INT FK | Producto vendido. |
| cantidad | DECIMAL | Cantidad vendida. |
| precio_unitario | DECIMAL | Precio unitario de venta. |
| costo_unitario | DECIMAL | Costo unitario. |
| subtotal | DECIMAL | Total de la línea. |

## orden_compra
| Campo | Tipo | Descripción |
|---|---|---|
| id_oc | INT PK | Identificador de orden de compra. |
| id_proveedor | INT FK | Proveedor de la compra. |
| id_usuario | INT FK | Usuario responsable. |
| fecha | DATETIME | Fecha de la orden. |
| estado | ENUM | Pendiente, recibida o cancelada. |
| total | DECIMAL | Total de la orden. |

## detalle_compra
| Campo | Tipo | Descripción |
|---|---|---|
| id_detalle_compra | INT PK | Identificador de línea de compra. |
| id_oc | INT FK | Orden de compra asociada. |
| id_producto | INT FK | Producto comprado. |
| cantidad | DECIMAL | Cantidad comprada. |
| precio_unitario | DECIMAL | Precio unitario de compra. |
| subtotal | DECIMAL | Total de la línea. |

## arqueo_caja
| Campo | Tipo | Descripción |
|---|---|---|
| id_caja | INT PK | Identificador del cierre. |
| id_usuario | INT FK | Usuario que realiza el cierre. |
| fecha | DATE | Fecha de cierre. |
| total_efectivo | DECIMAL | Ventas en efectivo según sistema. |
| total_transferencia | DECIMAL | Ventas por transferencia según sistema. |
| total_general | DECIMAL | Total del día. |
| efectivo_contado | DECIMAL | Efectivo contado físicamente. |
| diferencia_efectivo | DECIMAL | Diferencia entre sistema y conteo físico. |
| observaciones | TEXT | Comentarios del cierre. |

## movimiento_inventario
| Campo | Tipo | Descripción |
|---|---|---|
| id_movimiento | INT PK | Identificador de movimiento. |
| id_usuario | INT FK | Usuario que genera el movimiento. |
| id_producto | INT FK | Producto afectado. |
| tipo | ENUM | Entrada, salida o ajuste. |
| cantidad | DECIMAL | Cantidad del movimiento. |
| fecha | DATETIME | Fecha y hora del movimiento. |
| referencia | VARCHAR(80) | Venta, orden de compra o ajuste relacionado. |
| motivo | VARCHAR(255) | Motivo del movimiento. |
