"""Módulo de proveedores y relación producto-proveedor."""
from __future__ import annotations

from decimal import Decimal

import streamlit as st

from config.conexion import execute, fetch_df


def mostrar(rol: str) -> None:
    """Gestiona proveedores y precios de compra por proveedor."""
    st.title("Proveedores")
    st.caption("Registro de proveedores y relación muchos a muchos con productos.")

    tabs = st.tabs(["Consultar", "Nuevo proveedor", "Producto - proveedor"])

    with tabs[0]:
        st.subheader("Listado de proveedores")
        df = fetch_df("SELECT * FROM proveedores ORDER BY razon_social")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Productos asociados a proveedores")
        rel = fetch_df(
            """
            SELECT pr.razon_social AS proveedor, p.nombre AS producto,
                   pp.precio_compra, IF(pp.es_principal=1,'Sí','No') AS proveedor_principal
            FROM producto_proveedor pp
            INNER JOIN proveedores pr ON pr.id_proveedor = pp.id_proveedor
            INNER JOIN productos p ON p.id_producto = pp.id_producto
            ORDER BY pr.razon_social, p.nombre
            LIMIT 1000
            """
        )
        st.dataframe(rel, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Registrar proveedor")
        with st.form("form_proveedor", clear_on_submit=True):
            razon = st.text_input("Razón social / empresa *")
            direccion = st.text_area("Dirección comercial")
            telefono = st.text_input("Teléfono")
            vendedor = st.text_input("Vendedor asignado")
            nit = st.text_input("NIT")
            nrc = st.text_input("NRC")
            guardar = st.form_submit_button("Guardar proveedor", use_container_width=True)

        if guardar:
            if not razon.strip():
                st.error("La razón social es obligatoria.")
            else:
                execute(
                    """
                    INSERT INTO proveedores (razon_social, direccion, telefono, vendedor_asignado, nit, nrc)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (razon.strip(), direccion.strip(), telefono.strip(), vendedor.strip(), nit.strip(), nrc.strip()),
                )
                st.success("Proveedor registrado correctamente.")
                st.rerun()

    with tabs[2]:
        st.subheader("Asignar proveedor a producto")
        productos = fetch_df("SELECT id_producto, nombre FROM productos WHERE activo=1 ORDER BY nombre")
        proveedores = fetch_df("SELECT id_proveedor, razon_social FROM proveedores ORDER BY razon_social")
        if productos.empty or proveedores.empty:
            st.info("Debe existir al menos un producto y un proveedor.")
            return
        with st.form("form_relacion_pp"):
            id_producto = st.selectbox(
                "Producto",
                productos["id_producto"].tolist(),
                format_func=lambda x: productos.loc[productos["id_producto"] == x, "nombre"].iloc[0],
            )
            id_proveedor = st.selectbox(
                "Proveedor",
                proveedores["id_proveedor"].tolist(),
                format_func=lambda x: proveedores.loc[proveedores["id_proveedor"] == x, "razon_social"].iloc[0],
            )
            precio = st.number_input("Precio de compra ($)", min_value=0.0, step=0.01, format="%.2f")
            principal = st.checkbox("Proveedor principal para este producto", value=True)
            guardar = st.form_submit_button("Guardar relación", use_container_width=True)

        if guardar:
            if principal:
                execute("UPDATE producto_proveedor SET es_principal=0 WHERE id_producto=%s", (int(id_producto),))
            execute(
                """
                INSERT INTO producto_proveedor (id_producto, id_proveedor, precio_compra, es_principal)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE precio_compra=VALUES(precio_compra), es_principal=VALUES(es_principal)
                """,
                (int(id_producto), int(id_proveedor), Decimal(str(precio)), 1 if principal else 0),
            )
            st.success("Relación producto-proveedor guardada.")
            st.rerun()
