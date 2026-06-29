import streamlit as st
from config.conexion import consultar_df, conectar, ejecutar


def cargar_categorias():
    return consultar_df("SELECT id_categoria, nombre FROM categoria ORDER BY nombre")


def cargar_ubicaciones():
    return consultar_df("SELECT id_ubicacion, nombre FROM ubicacion ORDER BY nombre")


def cargar_proveedores():
    return consultar_df("SELECT id_proveedor, nombre_razon_social FROM proveedor ORDER BY nombre_razon_social")


def proveedor_principal_sql():
    return """
        SELECT pp.id_producto, pr.nombre_razon_social AS proveedor_principal
        FROM producto_proveedor pp
        INNER JOIN proveedor pr ON pp.id_proveedor = pr.id_proveedor
        WHERE pp.es_principal = 1
    """


def registrar_producto_con_movimiento(datos, id_proveedor, id_usuario):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO producto
                (codigo_barras, nombre, descripcion, id_categoria, id_ubicacion, unidad_medida,
                 precio_compra, precio_venta, stock_actual, stock_minimo, activo)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
                """,
                (
                    datos["codigo"], datos["nombre"], datos["descripcion"], datos["id_categoria"],
                    datos["id_ubicacion"], datos["unidad"], datos["precio_compra"], datos["precio_venta"],
                    datos["stock"], datos["stock_minimo"],
                ),
            )
            id_producto = cursor.lastrowid
            if id_proveedor:
                cursor.execute(
                    """
                    INSERT INTO producto_proveedor(id_producto, id_proveedor, precio_compra, es_principal)
                    VALUES (%s,%s,%s,1)
                    """,
                    (id_producto, id_proveedor, datos["precio_compra"]),
                )
            if float(datos["stock"]) > 0:
                cursor.execute(
                    """
                    INSERT INTO movimiento_inventario(id_usuario, id_producto, tipo, cantidad, referencia, motivo)
                    VALUES (%s,%s,'Entrada',%s,'Carga inicial','Registro de producto')
                    """,
                    (id_usuario, id_producto, datos["stock"]),
                )
        conexion.commit()
        return id_producto
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def actualizar_producto_con_movimiento(id_producto, actual, nuevo_stock, nuevo_minimo, nuevo_compra, nuevo_venta, id_usuario):
    diferencia = float(nuevo_stock) - float(actual["stock_actual"])
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE producto
                SET stock_actual=%s, stock_minimo=%s, precio_compra=%s, precio_venta=%s
                WHERE id_producto=%s
                """,
                (nuevo_stock, nuevo_minimo, nuevo_compra, nuevo_venta, id_producto),
            )
            if abs(diferencia) > 0.0001:
                cursor.execute(
                    """
                    INSERT INTO movimiento_inventario(id_usuario, id_producto, tipo, cantidad, referencia, motivo)
                    VALUES (%s,%s,'Ajuste',%s,'Ajuste manual','Actualización desde módulo de productos')
                    """,
                    (id_usuario, id_producto, diferencia),
                )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def mostrar(modo_consulta=False):
    st.title("📦 Productos e inventario" if not modo_consulta else "🔎 Consulta de productos")

    busqueda = st.text_input("Buscar por código, nombre o descripción")
    condicion = "WHERE p.activo = 1"
    params = []
    if busqueda:
        condicion += " AND (p.codigo_barras LIKE %s OR p.nombre LIKE %s OR p.descripcion LIKE %s)"
        patron = f"%{busqueda}%"
        params.extend([patron, patron, patron])

    df = consultar_df(
        f"""
        SELECT p.id_producto, p.codigo_barras AS codigo, p.nombre, p.descripcion,
               c.nombre AS categoria, p.unidad_medida AS unidad, p.stock_actual, p.stock_minimo,
               p.precio_venta, p.precio_compra, u.nombre AS ubicacion,
               pp.proveedor_principal,
               CASE WHEN p.codigo_barras IS NULL OR p.codigo_barras = '' THEN 'Selección manual' ELSE 'Código de barras' END AS entrada
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        LEFT JOIN ubicacion u ON p.id_ubicacion = u.id_ubicacion
        LEFT JOIN ({proveedor_principal_sql()}) pp ON p.id_producto = pp.id_producto
        {condicion}
        ORDER BY p.nombre
        """,
        params,
    )

    columnas_visibles = [
        "codigo", "nombre", "categoria", "unidad", "stock_actual", "stock_minimo", "precio_venta", "ubicacion", "entrada"
    ]
    if not modo_consulta:
        columnas_visibles.insert(8, "precio_compra")
        columnas_visibles.append("proveedor_principal")

    st.dataframe(df[columnas_visibles] if not df.empty else df, use_container_width=True, hide_index=True)

    if modo_consulta:
        st.info("Modo vendedor: solo consulta de stock y precios. No permite modificar costos ni márgenes.")
        return

    st.subheader("Registrar nuevo producto")
    categorias = cargar_categorias()
    ubicaciones = cargar_ubicaciones()
    proveedores = cargar_proveedores()

    with st.form("form_producto"):
        c1, c2, c3 = st.columns(3)
        codigo = c1.text_input("Código de barras (opcional)")
        nombre = c2.text_input("Nombre del producto")
        unidad = c3.selectbox("Unidad", ["Unidad", "Bolsa", "Saco", "Metro", "Libra", "Galón", "Cubeta", "Caja", "Docena"])

        descripcion = st.text_area("Descripción")
        c4, c5, c6 = st.columns(3)
        categoria_nombre = c4.selectbox("Categoría", categorias["nombre"].tolist())
        ubicacion_nombre = c5.selectbox("Ubicación", ubicaciones["nombre"].tolist())
        proveedor_nombre = c6.selectbox("Proveedor principal", proveedores["nombre_razon_social"].tolist())

        c7, c8, c9, c10 = st.columns(4)
        stock = c7.number_input("Stock inicial", min_value=0.0, value=0.0, step=1.0)
        stock_minimo = c8.number_input("Stock mínimo", min_value=0.0, value=5.0, step=1.0)
        precio_compra = c9.number_input("Precio compra", min_value=0.0, value=0.0, step=0.01)
        precio_venta = c10.number_input("Precio venta", min_value=0.0, value=0.0, step=0.01)

        guardar = st.form_submit_button("Guardar producto")

    if guardar:
        if not nombre or precio_venta <= 0:
            st.warning("Debe ingresar nombre y precio de venta mayor a cero.")
        else:
            id_categoria = int(categorias.loc[categorias["nombre"] == categoria_nombre, "id_categoria"].iloc[0])
            id_ubicacion = int(ubicaciones.loc[ubicaciones["nombre"] == ubicacion_nombre, "id_ubicacion"].iloc[0])
            id_proveedor = int(proveedores.loc[proveedores["nombre_razon_social"] == proveedor_nombre, "id_proveedor"].iloc[0])
            registrar_producto_con_movimiento(
                {
                    "codigo": codigo or None,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "id_categoria": id_categoria,
                    "id_ubicacion": id_ubicacion,
                    "unidad": unidad,
                    "stock": stock,
                    "stock_minimo": stock_minimo,
                    "precio_compra": precio_compra,
                    "precio_venta": precio_venta,
                },
                id_proveedor,
                st.session_state["usuario"]["id_usuario"],
            )
            st.success("Producto guardado correctamente.")
            st.rerun()

    st.subheader("Actualizar stock, precios o ubicación")
    if df.empty:
        st.info("No hay productos para actualizar.")
        return

    opciones = {f"{row.nombre} | Stock: {row.stock_actual} | ${row.precio_venta:.2f}": int(row.id_producto) for row in df.itertuples()}
    seleccionado = st.selectbox("Seleccione producto", list(opciones.keys()))
    id_producto = opciones[seleccionado]
    actual = consultar_df("SELECT * FROM producto WHERE id_producto = %s", [id_producto]).iloc[0]

    with st.form("form_actualizar"):
        c1, c2, c3, c4 = st.columns(4)
        nuevo_stock = c1.number_input("Stock", min_value=0.0, value=float(actual["stock_actual"]), step=1.0)
        nuevo_minimo = c2.number_input("Stock mínimo", min_value=0.0, value=float(actual["stock_minimo"]), step=1.0)
        nuevo_compra = c3.number_input("Precio compra", min_value=0.0, value=float(actual["precio_compra"]), step=0.01)
        nuevo_venta = c4.number_input("Precio venta", min_value=0.0, value=float(actual["precio_venta"]), step=0.01)
        actualizar = st.form_submit_button("Actualizar producto")

    if actualizar:
        actualizar_producto_con_movimiento(
            id_producto,
            actual,
            nuevo_stock,
            nuevo_minimo,
            nuevo_compra,
            nuevo_venta,
            st.session_state["usuario"]["id_usuario"],
        )
        st.success("Producto actualizado correctamente y movimiento de inventario registrado si hubo cambio de stock.")
        st.rerun()
