# Sistema Ferretería Elohim

Sistema de Gestión de Información desarrollado en Python + Streamlit + MySQL para Ferretería Elohim.

## Funcionamiento

La aplicación crea automáticamente las tablas y carga datos iniciales en MySQL al iniciar. Por eso no es obligatorio importar el schema manualmente.

## Usuarios de prueba

- marvin / 1234
- dayana / 1234
- juanita / 1234
- bryan / 1234

## Secrets de Streamlit

```toml
[mysql]
host = "TU_HOST"
port = 3306
database = "TU_DATABASE"
user = "TU_USER"
password = "TU_PASSWORD"
```
