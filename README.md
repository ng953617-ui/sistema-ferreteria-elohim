# SGI Ferretería Elohim - Streamlit + MySQL

Aplicación web funcional para el proyecto final de Sistemas de Gestión de la Información. Esta versión está alineada con el diagrama de contexto y el diagrama Entidad-Relación del equipo.

## Módulos incluidos

- Login con roles.
- Panel principal.
- Productos e inventario.
- Clientes y datos fiscales.
- Proveedores.
- Punto de venta.
- Compras y reposición.
- Cierre de caja.
- Reportes.
- Usuarios y roles.

## Tablas principales

- usuario
- categoria
- ubicacion
- proveedor
- producto
- producto_proveedor
- cliente
- consumidor_final
- contribuyente
- venta
- detalle_venta
- orden_compra
- detalle_compra
- arqueo_caja
- movimiento_inventario

## Usuarios de prueba

- marvin / 1234
- dayana / 1234
- juanita / 1234
- bryan / 1234

## Despliegue

1. Crear base MySQL en Clever Cloud.
2. Abrir phpMyAdmin.
3. Importar `database/schema.sql`.
4. Subir el proyecto a GitHub.
5. Crear app en Streamlit Cloud con `app.py` como archivo principal.
6. Configurar secrets:

```toml
[mysql]
host = "TU_HOST"
port = 3306
database = "TU_DATABASE"
user = "TU_USER"
password = "TU_PASSWORD"
```

7. Usar Python 3.11 y desplegar.
