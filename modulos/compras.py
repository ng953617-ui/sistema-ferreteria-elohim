import streamlit as st
from config.conexion import consultar, consultar_df, ejecutar, ejecutar_insert


def mostrar():
    st.title("🛒 Compras y reposición")

    st.subheader("Compras sugeridas por stock mínimo")
    sugeridas = consultar_df("""
        SELECT p.id_producto, p.nombre, c.nombre AS categoria, p.stock_actual, p.stock_minimo,
               GREATEST(p.stock_minimo*2 - p.stock_actual, 1) AS cantidad_sugerida,
               COALESCE(pr.nombre_razon_social,'Sin proveedor') AS proveedor_principal
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria=c.id_categoria
        LEFT JOIN producto_proveedor pp ON p.id_producto=pp.id_producto AND pp.es_principal=1
        LEFT JOIN proveedor pr ON pp.id_proveedor=pr.id_proveedor
        WHERE p.activo=1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC
    """)
    if sugeridas.empty:
        st.info("No hay productos bajo stock mínimo.")
    else:
        st.dataframe(sugeridas, use_container_width=True, hide_index=True)

    st.subheader("Registrar orden de compra recibida")
    proveedores = consultar("SELECT id_proveedor, nombre_razon_social FROM proveedor WHERE activo=1 ORDER BY nombre_razon_social")
    productos = consultar("SELECT id_producto, nombre, precio_compra FROM producto WHERE activo=1 ORDER BY nombre")
    if not proveedores or not productos:
        st.warning("Debe existir al menos un proveedor y un producto activo.")
        return

    dic_prov = {p["nombre_razon_social"]: p["id_proveedor"] for p in proveedores}
    dic_prod = {p["nombre"]: p for p in productos}

    with st.form("form_compra"):
        proveedor = st.selectbox("Proveedor", list(dic_prov.keys()))
        producto = st.selectbox("Producto", list(dic_prod.keys()))
        c1, c2 = st.columns(2)
        cantidad = c1.number_input("Cantidad recibida", min_value=0.01, step=1.0)
        precio = c2.number_input("Precio unitario", min_value=0.0, step=0.01, value=float(dic_prod[producto]["precio_compra"] or 0))
        guardar = st.form_submit_button("Registrar compra")

    if guardar:
        total = float(cantidad) * float(precio)
        user_id = st.session_state["usuario"]["id_usuario"]
        orden_id = ejecutar_insert("INSERT INTO orden_compra (id_proveedor, estado, total) VALUES (%s,'Recibida',%s)", (dic_prov[proveedor], total))
        prod_id = dic_prod[producto]["id_producto"]
        ejecutar("INSERT INTO detalle_compra (id_orden,id_producto,cantidad,precio_unitario) VALUES (%s,%s,%s,%s)",
                 (orden_id, prod_id, cantidad, precio))
        ejecutar("UPDATE producto SET stock_actual = stock_actual + %s, precio_compra=%s WHERE id_producto=%s", (cantidad, precio, prod_id))
        ejecutar("""
            INSERT INTO movimiento_inventario (id_producto,tipo_movimiento,cantidad,referencia_id,id_usuario,motivo)
            VALUES (%s,'Entrada',%s,%s,%s,'Compra recibida')
        """, (prod_id, cantidad, orden_id, user_id))
        st.success("Compra registrada y stock actualizado.")
        st.rerun()

    st.subheader("Últimas compras")
    df = consultar_df("""
        SELECT oc.id_orden, oc.fecha, pr.nombre_razon_social AS proveedor, oc.estado, oc.total
        FROM orden_compra oc
        JOIN proveedor pr ON oc.id_proveedor=pr.id_proveedor
        ORDER BY oc.fecha DESC LIMIT 10
    """)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
