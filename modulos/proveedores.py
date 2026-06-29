import streamlit as st
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("🚚 Proveedores")
    st.write("Registro de proveedores y datos comerciales requeridos por la ferretería.")

    df = consultar_df(
        """
        SELECT id_proveedor, nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc, activo
        FROM proveedor
        WHERE nombre_razon_social <> 'nombre_razon_social'
        ORDER BY nombre_razon_social
        """
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Registrar proveedor")
    with st.form("form_proveedor"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre empresa / Razón social")
        telefono = c2.text_input("Teléfono")
        direccion = st.text_area("Dirección física comercial")
        c3, c4, c5 = st.columns(3)
        vendedor = c3.text_input("Vendedor / asesor asignado")
        nit = c4.text_input("NIT")
        nrc = c5.text_input("NRC")
        guardar = st.form_submit_button("Guardar proveedor")

    if guardar:
        if not nombre:
            st.warning("Debe ingresar el nombre de la empresa.")
        else:
            ejecutar(
                """
                INSERT INTO proveedor(nombre_razon_social, direccion, telefono, vendedor_asignado, nit, nrc, activo)
                VALUES (%s,%s,%s,%s,%s,%s,1)
                """,
                (nombre, direccion, telefono, vendedor, nit, nrc),
            )
            st.success("Proveedor guardado correctamente.")
            st.rerun()

    st.subheader("Relación producto - proveedor")
    productos = consultar_df("SELECT id_producto, nombre FROM producto WHERE activo = 1 AND nombre <> 'nombre' ORDER BY nombre")
    proveedores = consultar_df("SELECT id_proveedor, nombre_razon_social FROM proveedor WHERE activo = 1 AND nombre_razon_social <> 'nombre_razon_social' ORDER BY nombre_razon_social")

    if productos.empty or proveedores.empty:
        st.info("Debe existir al menos un producto y un proveedor activo.")
        return

    with st.form("form_relacion"):
        producto_nombre = st.selectbox("Producto", productos["nombre"].tolist())
        proveedor_nombre = st.selectbox("Proveedor", proveedores["nombre_razon_social"].tolist())
        costo_ref = st.number_input("Precio de compra / costo de referencia", min_value=0.0, value=0.0, step=0.01)
        principal = st.checkbox("Proveedor principal para este producto")
        guardar_rel = st.form_submit_button("Guardar relación")

    if guardar_rel:
        id_producto = int(productos.loc[productos["nombre"] == producto_nombre, "id_producto"].iloc[0])
        id_proveedor = int(proveedores.loc[proveedores["nombre_razon_social"] == proveedor_nombre, "id_proveedor"].iloc[0])
        try:
            ejecutar(
                """
                INSERT INTO producto_proveedor(id_producto, id_proveedor, precio_compra, es_principal)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE precio_compra=VALUES(precio_compra), es_principal=VALUES(es_principal)
                """,
                (id_producto, id_proveedor, costo_ref, 1 if principal else 0),
            )
            if principal:
                ejecutar("UPDATE producto_proveedor SET es_principal = IF(id_proveedor=%s,1,0) WHERE id_producto=%s", (id_proveedor, id_producto))
            st.success("Relación guardada correctamente.")
            st.rerun()
        except Exception as e:
            st.error("No fue posible guardar la relación.")
            st.exception(e)

    relaciones = consultar_df(
        """
        SELECT p.nombre AS producto, pr.nombre_razon_social AS proveedor,
               pp.precio_compra, IF(pp.es_principal=1,'Sí','No') AS proveedor_principal
        FROM producto_proveedor pp
        INNER JOIN producto p ON pp.id_producto = p.id_producto
        INNER JOIN proveedor pr ON pp.id_proveedor = pr.id_proveedor
        WHERE p.nombre <> 'nombre' AND pr.nombre_razon_social <> 'nombre_razon_social'
        ORDER BY p.nombre, proveedor_principal DESC
        """
    )
    st.dataframe(relaciones, use_container_width=True, hide_index=True)
