import streamlit as st
import pandas as pd
from config.conexion import consultar_df, consultar, ejecutar, ejecutar_insert


def mostrar(modo_consulta=False):
    st.title("📦 Productos e inventario")
    filtro = st.text_input("Buscar por código, nombre o descripción")
    like = f"%{filtro}%"

    df = consultar_df("""
        SELECT p.id_producto, p.codigo_barras, p.nombre, c.nombre AS categoria, p.unidad,
               p.stock_actual, p.stock_minimo, p.precio_venta, u.nombre AS ubicacion,
               p.precio_compra, COALESCE(pr.nombre_razon_social,'') AS proveedor_principal
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria=c.id_categoria
        LEFT JOIN ubicacion u ON p.id_ubicacion=u.id_ubicacion
        LEFT JOIN producto_proveedor pp ON p.id_producto=pp.id_producto AND pp.es_principal=1
        LEFT JOIN proveedor pr ON pp.id_proveedor=pr.id_proveedor
        WHERE p.activo=1 AND (p.nombre LIKE %s OR COALESCE(p.codigo_barras,'') LIKE %s OR COALESCE(p.descripcion,'') LIKE %s)
        ORDER BY p.nombre
    """, (like, like, like))

    if df.empty:
        st.info("No hay productos registrados o no coinciden con la búsqueda.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    if modo_consulta:
        return

    st.subheader("Registrar nuevo producto")
    categorias = consultar("SELECT id_categoria, nombre FROM categoria WHERE activo=1 ORDER BY nombre")
    ubicaciones = consultar("SELECT id_ubicacion, nombre FROM ubicacion WHERE activo=1 ORDER BY nombre")
    proveedores = consultar("SELECT id_proveedor, nombre_razon_social FROM proveedor WHERE activo=1 ORDER BY nombre_razon_social")

    if not categorias or not ubicaciones or not proveedores:
        st.warning("No hay datos base. La app debe autocargar categorías, ubicaciones y proveedores. Reinicie la app si no aparecen.")
        return

    dic_cat = {c["nombre"]: c["id_categoria"] for c in categorias}
    dic_ubi = {u["nombre"]: u["id_ubicacion"] for u in ubicaciones}
    dic_prov = {p["nombre_razon_social"]: p["id_proveedor"] for p in proveedores}

    with st.form("form_producto"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del producto")
            codigo = st.text_input("Código de barras")
            categoria = st.selectbox("Categoría", list(dic_cat.keys()))
            unidad = st.text_input("Unidad de medida", value="Unidad")
            tiene_codigo = st.checkbox("Tiene código de barras", value=True)
        with col2:
            descripcion = st.text_area("Descripción")
            ubicacion = st.selectbox("Ubicación", list(dic_ubi.keys()))
            proveedor = st.selectbox("Proveedor principal", list(dic_prov.keys()))
            precio_compra = st.number_input("Precio de compra", min_value=0.0, step=0.01)
            precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.01)
        col3, col4 = st.columns(2)
        with col3:
            stock_actual = st.number_input("Stock actual", min_value=0.0, step=1.0)
        with col4:
            stock_minimo = st.number_input("Stock mínimo", min_value=0.0, step=1.0)
        guardar = st.form_submit_button("Guardar producto")

    if guardar:
        if not nombre.strip():
            st.error("Ingrese el nombre del producto.")
            return
        prod_id = ejecutar_insert("""
            INSERT INTO producto (codigo_barras, nombre, descripcion, id_categoria, id_ubicacion, unidad,
                                  stock_actual, stock_minimo, precio_compra, precio_venta, tiene_codigo, activo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
        """, (codigo if tiene_codigo and codigo else None, nombre, descripcion, dic_cat[categoria], dic_ubi[ubicacion], unidad,
              stock_actual, stock_minimo, precio_compra, precio_venta, 1 if tiene_codigo else 0))
        ejecutar("INSERT INTO producto_proveedor (id_producto, id_proveedor, precio_compra, es_principal) VALUES (%s,%s,%s,1)",
                 (prod_id, dic_prov[proveedor], precio_compra))
        st.success("Producto registrado correctamente.")
        st.rerun()
