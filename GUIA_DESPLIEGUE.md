# Ferretería ELOHIM — Guía de despliegue (hoy mismo)

## 1. Crear la base de datos en Clever Cloud
1. Entra a https://www.clever-cloud.com y crea una cuenta (o usa la del Lab 5/6).
2. Crea un add-on de tipo **MySQL** (plan gratuito "Dev").
3. Cuando esté creado, ve a la pestaña **Information** y copia: host, puerto, base de datos, usuario, contraseña.

## 2. Cargar el esquema de tablas
1. En Clever Cloud, abre **phpMyAdmin** (botón en el add-on de MySQL).
2. Entra con las credenciales del paso 1.
3. Ve a la pestaña **SQL** y pega TODO el contenido de `schema.sql`. Ejecuta.
4. Verifica que aparezcan las 13 tablas (PRODUCTO, VENTA, PROVEEDOR, etc.) en el panel izquierdo.

## 3. Crear los usuarios de acceso
1. En tu computadora (no en Streamlit Cloud), instala las librerías necesarias:
   ```
   pip install mysql-connector-python bcrypt
   ```
2. Abre `config/seed.py` y reemplaza `DB_CONFIG` con tus datos reales de Clever Cloud.
3. Ejecuta:
   ```
   python config/seed.py
   ```
4. Esto crea 4 usuarios con contraseña cifrada:
   - marvin / admin123 (Administrador)
   - dayana / admin123 (Supervisor)
   - juanita / venta123 (Vendedor)
   - bryan / venta123 (Vendedor)

   **Cambia estas contraseñas después del primer ingreso.**

## 4. Subir el código a GitHub
1. Crea un repositorio nuevo en GitHub (ej. `ferreteria-elohim`).
2. Sube TODA la carpeta `ferreteria_elohim/` (app.py, login.py, menu.py, config/, modulos/, requirements.txt).
   No subas `config/seed.py` con tus contraseñas reales escritas, o bórralas antes de subir.

## 5. Desplegar en Streamlit Cloud
1. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
2. Crea una nueva app, selecciona el repositorio y el archivo principal `app.py`.
3. Antes de desplegar, ve a **Advanced settings > Secrets** y pega:
   ```toml
   [mysql]
   host = "TU_HOST.clever-cloud.com"
   port = 3306
   database = "TU_BASE"
   user = "TU_USUARIO"
   password = "TU_PASSWORD"
   ```
4. Haz clic en **Deploy**. En 1-2 minutos tendrás el enlace público funcionando.

## 6. Probar el sistema
1. Abre el enlace de Streamlit Cloud.
2. Inicia sesión con `marvin / admin123`.
3. Ve a **Productos > Nuevo producto** y registra algunos productos de prueba
   (usa los datos reales de tus facturas de marzo si quieres llenarlo rápido).
4. Ve a **Proveedores** y registra tus 6 proveedores.
5. Ve a **Punto de Venta**, busca un producto, agrégalo al carrito y confirma una venta.
6. Verifica en **Reportes** que aparezca la venta y en **Productos** que el stock bajó.
7. Cierra el día desde **Caja**.

## Notas importantes para tu defensa
- El sistema ya implementa las 13 entidades de tu Diccionario de Datos y el modelo ER.
- El flujo de Ventas descuenta stock automáticamente y genera movimiento de inventario (trazabilidad).
- El módulo de Compras, al "recibir" una orden, aumenta el stock (entrada).
- Los roles (Administrador, Supervisor, Vendedor) limitan qué módulos ve cada usuario, igual que tu RBAC.
- Pendiente de mejora si te queda tiempo: lector de código de barras con cámara
  (se puede agregar después con `st.camera_input` + librería `pyzbar`, no es bloqueante para la entrega).
