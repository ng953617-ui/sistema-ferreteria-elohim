import streamlit as st
from config.conexion import consultar_df, conectar


def registrar_compra(id_proveedor, id_producto, cantidad, precio_unitario, id_usuario):
    total = float(cantidad) * float(precio_unitario)
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orden_compra(id_proveedor, fecha, estado, total, id_usuario)
                VALUES (%s, NOW(), 'Recibida', %s, %s)
                """,
                (id_proveedor, total, id_usuario),
            )
            id_oc = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO detalle_compra(id_oc, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (id_oc, id_producto, cantidad, precio_unitario, total),
            )
            cursor.execute(
                """
                UPDATE producto
                SET stock_actual = stock_actual + %s, precio_compra = %s
                WHERE id_producto = %s
                """,
                (cantidad, precio_unitario, id_producto),
            )
            cursor.execute(
                """
                INSERT INTO movimiento_inventario(id_usuario, id_producto, tipo, cantidad, referencia, motivo)
                VALUES (%s,%s,'Entrada',%s,%s,'Compra recibida')
                """,
                (id_usuario, id_producto, cantidad, f"OC {id_oc}"),
            )
        conexion.commit()
        return id_oc
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def mostrar():
    st.title("🛒 Compras y reposición")

    st.subheader("Compras sugeridas por stock mínimo")
    sugeridas = consultar_df(
        """
        SELECT p.id_producto, p.nombre, c.nombre AS categoria, p.stock_actual, p.stock_minimo,
               GREATEST(p.stock_minimo * 2 - p.stock_actual, 1) AS cantidad_sugerida,
               pr.nombre_razon_social AS proveedor_principal
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        LEFT JOIN producto_proveedor pp ON p.id_producto = pp.id_producto AND pp.es_principal = 1
        LEFT JOIN proveedor pr ON pp.id_proveedor = pr.id_proveedor
        WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC
        """
    )
    st.dataframe(sugeridas, use_container_width=True, hide_index=True)

    st.subheader("Registrar orden de compra recibida")
    proveedores = consultar_df("SELECT id_proveedor, nombre_razon_social FROM proveedor WHERE activo = 1 ORDER BY nombre_razon_social")
    productos = consultar_df("SELECT id_producto, nombre, stock_actual, precio_compra FROM producto WHERE activo = 1 ORDER BY nombre")

    if proveedores.empty or productos.empty:
        st.warning("Debe existir al menos un proveedor y un producto activo.")
        return

    with st.form("form_compra"):
        proveedor_nombre = st.selectbox("Proveedor", proveedores["nombre_razon_social"].tolist())
        producto_nombre = st.selectbox("Producto", productos["nombre"].tolist())
        cantidad = st.number_input("Cantidad recibida", min_value=0.01, value=1.0, step=1.0)
        precio_unitario = st.number_input("Precio unitario de compra", min_value=0.0, value=1.0, step=0.01)
        guardar = st.form_submit_button("Registrar compra")

    if guardar:
        id_proveedor = int(proveedores.loc[proveedores["nombre_razon_social"] == proveedor_nombre, "id_proveedor"].iloc[0])
        id_producto = int(productos.loc[productos["nombre"] == producto_nombre, "id_producto"].iloc[0])
        try:
            id_usuario = st.session_state["usuario"]["id_usuario"]
            id_oc = registrar_compra(id_proveedor, id_producto, cantidad, precio_unitario, id_usuario)
            st.success(f"Compra registrada correctamente. Orden No. {id_oc}")
            st.rerun()
        except Exception as e:
            st.error("No fue posible registrar la compra.")
            st.exception(e)

    st.subheader("Historial de órdenes de compra")
    historial = consultar_df(
        """
        SELECT oc.id_oc, oc.fecha, pr.nombre_razon_social AS proveedor, oc.estado, oc.total
        FROM orden_compra oc
        INNER JOIN proveedor pr ON oc.id_proveedor = pr.id_proveedor
        ORDER BY oc.fecha DESC
        LIMIT 20
        """
    )
    st.dataframe(historial, use_container_width=True, hide_index=True)
