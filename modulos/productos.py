"""
modulos/productos.py
Gestión de productos: catálogo, alta, edición de stock, alertas de stock mínimo.
"""

import streamlit as st
import pandas as pd
from config.db import run_query, run_action


def mostrar(rol):
    st.header("📦 Productos e Inventario")

    tab1, tab2, tab3 = st.tabs(["Catálogo", "Nuevo producto", "Alertas de stock"])

    # --- Catálogo ---
    with tab1:
        buscar = st.text_input("Buscar producto por nombre o código")
        query = """
            SELECT p.ID_Producto, p.Codigo_Barra, p.Nombre, c.Nombre AS Categoria,
                   u.Nombre AS Ubicacion, p.Precio_Venta, p.Unidad_Medida,
                   p.Stock_Actual, p.Stock_Minimo
            FROM PRODUCTO p
            LEFT JOIN CATEGORIA c ON p.Categoria_ID = c.ID_Categoria
            LEFT JOIN UBICACION u ON p.Ubicacion_ID = u.ID_Ubicacion
        """
        params = ()
        if buscar:
            query += " WHERE p.Nombre LIKE %s OR p.Codigo_Barra LIKE %s"
            params = (f"%{buscar}%", f"%{buscar}%")
        productos = run_query(query, params)
        if productos:
            st.dataframe(pd.DataFrame(productos), use_container_width=True)
        else:
            st.info("No hay productos registrados todavía.")

    # --- Nuevo producto (solo admin/supervisor) ---
    with tab2:
        if rol == "Vendedor":
            st.info("No tienes permiso para agregar productos.")
        else:
            categorias = run_query("SELECT * FROM CATEGORIA")
            ubicaciones = run_query("SELECT * FROM UBICACION")
            cat_map = {c["Nombre"]: c["ID_Categoria"] for c in categorias}
            ubi_map = {u["Nombre"]: u["ID_Ubicacion"] for u in ubicaciones}

            with st.form("nuevo_producto"):
                nombre = st.text_input("Nombre del producto")
                codigo = st.text_input("Código de barras (déjalo vacío si no tiene)")
                categoria = st.selectbox("Categoría", list(cat_map.keys()))
                ubicacion = st.selectbox("Ubicación", list(ubi_map.keys()))
                precio = st.number_input("Precio de venta (USD)", min_value=0.0, step=0.01)
                unidad = st.text_input("Unidad de medida", value="unidad")
                stock_actual = st.number_input("Stock actual", min_value=0.0, step=1.0)
                stock_minimo = st.number_input("Stock mínimo", min_value=0.0, step=1.0)
                guardar = st.form_submit_button("Guardar producto")

            if guardar:
                if not nombre:
                    st.warning("El nombre es obligatorio.")
                else:
                    run_action(
                        """INSERT INTO PRODUCTO
                           (Codigo_Barra, Nombre, Categoria_ID, Ubicacion_ID, Precio_Venta,
                            Unidad_Medida, Stock_Actual, Stock_Minimo, Tiene_Codigo_Barra)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (codigo or None, nombre, cat_map[categoria], ubi_map[ubicacion],
                         precio, unidad, stock_actual, stock_minimo, 1 if codigo else 0)
                    )
                    st.success(f"Producto '{nombre}' registrado correctamente.")
                    st.rerun()

    # --- Alertas de stock mínimo ---
    with tab3:
        alertas = run_query(
            "SELECT Nombre, Stock_Actual, Stock_Minimo FROM PRODUCTO "
            "WHERE Stock_Actual <= Stock_Minimo"
        )
        if alertas:
            st.warning(f"{len(alertas)} producto(s) bajo el stock mínimo:")
            st.dataframe(pd.DataFrame(alertas), use_container_width=True)
        else:
            st.success("Todos los productos están dentro de su nivel normal de stock.")
