# SGI Ferretería ELOHIM

Sistema de Gestión de Información desarrollado en **Python + Streamlit + MySQL** para Ferretería ELOHIM.

Incluye:

- Login con usuarios y contraseña desde MySQL.
- Menú lateral por rol.
- Gestión de productos e inventario.
- Proveedores y relación producto-proveedor.
- Clientes y campos fiscales para CCF / consumidor final.
- Punto de venta con carrito, efectivo y transferencia.
- Órdenes de compra y recepción de inventario.
- Arqueo de caja diario.
- Reportes: ventas, producto estrella, top 10, bajo stock, baja rotación y movimientos.
- Base de datos MySQL en un solo archivo SQL.

---

## 1. Estructura del proyecto

```text
sistema_ferreteria_elohim/
├── app.py
├── login.py
├── menu.py
├── requirements.txt
├── config/
│   └── conexion.py
├── modulos/
│   ├── dashboard.py
│   ├── productos.py
│   ├── proveedores.py
│   ├── clientes.py
│   ├── ventas.py
│   ├── compras.py
│   ├── caja.py
│   ├── reportes.py
│   └── usuarios.py
├── utils/
│   └── security.py
├── sql/
│   └── ferreteria_elohim_schema_y_datos.sql
├── data/
│   ├── productos_ejemplo_645.csv
│   ├── proveedores_ejemplo.csv
│   └── clientes_ejemplo.csv
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

---

## 2. Crear base de datos en Clever Cloud/phpMyAdmin

1. Entrar a phpMyAdmin de Clever Cloud.
2. Seleccionar la base de datos de la ferretería.
3. Ir a la pestaña **SQL**.
4. Abrir el archivo:

```text
sql/ferreteria_elohim_schema_y_datos.sql
```

5. Copiar todo el contenido y ejecutarlo completo.

El archivo SQL elimina y vuelve a crear las tablas, por eso debe usarse en una base nueva o de prueba.

---

## 3. Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---:|---|
| marvin | 1234 | Administrador principal |
| dayana | 1234 | Administrador / Supervisor |
| juanita | 1234 | Vendedor |
| bryan | 1234 | Vendedor |

Las contraseñas están guardadas con bcrypt, no como texto plano.

---

## 4. Configurar Streamlit Cloud

1. Subir todo el proyecto a GitHub.
2. Entrar a Streamlit Cloud.
3. Crear una nueva app.
4. Seleccionar el repositorio.
5. En **Main file path**, colocar:

```text
app.py
```

6. En **Settings > Secrets**, pegar la configuración MySQL:

```toml
[mysql]
host = "TU_HOST_CLEVER_CLOUD"
port = 3306
database = "TU_BASE_DE_DATOS"
user = "TU_USUARIO"
password = "TU_PASSWORD"
```

También funciona si la llave se llama `Contrasena`, pero se recomienda usar `password`.

No subas credenciales reales a GitHub. Usa solo Streamlit Secrets.

---

## 5. Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para ejecución local, puedes crear un archivo `.streamlit/secrets.toml` copiando el ejemplo `.streamlit/secrets.toml.example` y colocando tus datos reales.

---

## 6. Datos incluidos

El SQL incluye:

- 7 categorías con las cantidades de referencia del levantamiento: construcción, fontanería, electricidad, pinturas, automotriz, herramientas y carpintería.
- 645 productos iniciales para que el catálogo cargue con el volumen del proyecto.
- Productos reconocibles de los comprobantes/anexos: cemento Fortaleza, cemento Holcim, hierro, lámina, polín, tubo galvanizado, unión PVC, llaves de chorro, pegamentos PVC, brochas, rodillos, bandeja, aceites, filtros, discos Truper, tornillos, clavos y lijas.
- Productos sin código de barra para venta por búsqueda/selección: arena, grava, block, madera y otros materiales a granel.
- 6 proveedores iniciales.
- Clientes base para venta rápida y ejemplos de contribuyente.
- Ventas de ejemplo para validar reportes.

El CSV `data/productos_ejemplo_645.csv` permite revisar o reemplazar el catálogo desde el módulo de carga masiva.

---

## 7. Orden recomendado para probar

1. Iniciar sesión como `marvin / 1234`.
2. Revisar Dashboard.
3. Ir a Productos e Inventario y buscar: `cemento`, `PVC`, `arena`, `Truper`.
4. Registrar una venta desde Punto de Venta.
5. Confirmar que bajó el stock del producto.
6. Revisar Caja para el día actual.
7. Revisar Reportes.
8. Entrar como `juanita / 1234` para comprobar que el rol vendedor no tiene acceso a usuarios, compras ni reportes administrativos.
