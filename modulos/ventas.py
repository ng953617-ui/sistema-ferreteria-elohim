import streamlit as st
import pandas as pd
from config.conexion import consultar_df, conectar


def numero(valor, defecto=0.0):
    valor = pd.to_numeric(valor, errors="coerce")
    return float(defecto if pd.isna(valor) else valor)


def inicializar_carrito():
    if "carrito" not in st.session_state:
        st.session_state["carrito"] = []


def cargar_productos(filtro=""):
    condicion = "WHERE p.activo = 1 AND p.nombre <> 'nombre'"
    params = []
    if filtro:
        condicion += " AND (p.codigo_barras LIKE %s OR p.nombre LIKE %s OR p.descripcion LIKE %s)"
        patron = f"%{filtro}%"
        params.extend([patron, patron, patron])
    df = consultar_df(
        f"""
        SELECT p.id_producto, p.codigo_barras, p.nombre, p.stock_actual, p.unidad_medida,
               p.precio_venta, p.precio_compra, u.nombre AS ubicacion
        FROM producto p
        LEFT JOIN ubicacion u ON p.id_ubicacion = u.id_ubicacion
        {condicion}
        ORDER BY p.nombre
        LIMIT 50
        """,
        params,
    )
    for col in ["stock_actual", "precio_venta", "precio_compra"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def cargar_clientes():
    return consultar_df(
        """
        SELECT c.id_cliente, c.nombre,
               CASE
                   WHEN ct.id_cliente IS NOT NULL THEN 'Contribuyente'
                   WHEN cf.id_cliente IS NOT NULL THEN 'Consumidor final'
                   ELSE 'Cliente general'
               END AS tipo_cliente
        FROM cliente c
        LEFT JOIN consumidor_final cf ON c.id_cliente = cf.id_cliente
        LEFT JOIN contribuyente ct ON c.id_cliente = ct.id_cliente
        WHERE c.nombre <> 'nombre'
        ORDER BY c.nombre
        """
    )


def crear_cliente_desde_venta(cursor, datos_venta):
    nombre = datos_venta.get("cliente_nombre") or "Cliente mostrador"
    cursor.execute(
        """
        INSERT INTO cliente(nombre, direccion, telefono, correo)
        VALUES (%s,%s,%s,%s)
        """,
        (nombre, datos_venta.get("cliente_direccion", ""), datos_venta.get("cliente_telefono", ""), datos_venta.get("cliente_correo", "")),
    )
    id_cliente = cursor.lastrowid

    if datos_venta["tipo_comprobante"] == "Consumidor final":
        cursor.execute(
            """
            INSERT INTO consumidor_final(id_cliente, tipo_documento, num_documento)
            VALUES (%s,%s,%s)
            """,
            (id_cliente, datos_venta.get("tipo_documento", "DUI"), datos_venta.get("num_documento", "")),
        )
    elif datos_venta["tipo_comprobante"] == "Crédito Fiscal":
        cursor.execute(
            """
            INSERT INTO contribuyente(id_cliente, nit, nrc, giro, departamento, municipio)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                id_cliente,
                datos_venta.get("cliente_nit", ""),
                datos_venta.get("cliente_nrc", ""),
                datos_venta.get("cliente_giro", ""),
                datos_venta.get("cliente_departamento", ""),
                datos_venta.get("cliente_municipio", ""),
            ),
        )
    return id_cliente


def registrar_venta(carrito, datos_venta, id_usuario):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            id_cliente = datos_venta.get("id_cliente")
            if datos_venta.get("crear_cliente"):
                id_cliente = crear_cliente_desde_venta(cursor, datos_venta)

            cursor.execute(
                """
                INSERT INTO venta
                (fecha, id_usuario, id_cliente, tipo_comprobante, metodo_pago, subtotal, iva, descuento, total)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_usuario,
                    id_cliente,
                    datos_venta["tipo_comprobante"],
                    datos_venta["metodo_pago"],
                    datos_venta["subtotal"],
                    datos_venta["iva"],
                    datos_venta["descuento"],
                    datos_venta["total"],
                ),
            )
            id_venta = cursor.lastrowid

            for item in carrito:
                cursor.execute("SELECT stock_actual FROM producto WHERE id_producto=%s FOR UPDATE", (item["id_producto"],))
                stock_row = cursor.fetchone()
                stock_actual = numero(stock_row["stock_actual"] if stock_row else 0)
                if stock_actual < numero(item["cantidad"]):
                    raise ValueError(f"Stock insuficiente para {item['nombre']}")

                cursor.execute(
                    """
                    INSERT INTO detalle_venta
                    (id_venta, id_producto, cantidad, precio_unitario, costo_unitario, subtotal)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (id_venta, item["id_producto"], item["cantidad"], item["precio_venta"], item["precio_compra"], item["total_linea"]),
                )
                cursor.execute("UPDATE producto SET stock_actual = stock_actual - %s WHERE id_producto = %s", (item["cantidad"], item["id_producto"]))
                cursor.execute(
                    """
                    INSERT INTO movimiento_inventario(id_usuario, id_producto, tipo, cantidad, referencia, motivo)
                    VALUES (%s,%s,'Salida',%s,%s,'Venta registrada')
                    """,
                    (id_usuario, item["id_producto"], item["cantidad"], f"Venta {id_venta}"),
                )
        conexion.commit()
        return id_venta
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def mostrar():
    st.title("🧾 Punto de venta")
    inicializar_carrito()
    st.write("Permite venta rápida mediante búsqueda por texto o código de barras. Para productos sin código, seleccione manualmente el producto.")

    filtro = st.text_input("Escanear código de barras o buscar producto")
    productos = cargar_productos(filtro)

    if productos.empty:
        st.warning("No se encontraron productos con ese filtro.")
    else:
        opciones = {
            f"{row.nombre} | Código: {row.codigo_barras or 'Sin código'} | Stock: {numero(row.stock_actual):,.2f} {row.unidad_medida} | ${numero(row.precio_venta):,.2f}": row
            for row in productos.itertuples()
        }
        seleccionado = st.selectbox("Producto", list(opciones.keys()))
        producto = opciones[seleccionado]
        c1, c2 = st.columns(2)
        cantidad = c1.number_input("Cantidad", min_value=0.01, value=1.0, step=1.0)
        c2.metric("Ubicación física", producto.ubicacion or "Sin ubicación")

        if st.button("Agregar al carrito"):
            if cantidad > numero(producto.stock_actual):
                st.error("No hay stock suficiente para agregar esa cantidad.")
            else:
                st.session_state["carrito"].append(
                    {
                        "id_producto": int(producto.id_producto),
                        "nombre": producto.nombre,
                        "cantidad": float(cantidad),
                        "precio_venta": numero(producto.precio_venta),
                        "precio_compra": numero(producto.precio_compra),
                        "total_linea": float(cantidad) * numero(producto.precio_venta),
                    }
                )
                st.success("Producto agregado al carrito.")
                st.rerun()

    st.subheader("Carrito de venta")
    carrito = st.session_state["carrito"]
    if not carrito:
        st.info("El carrito está vacío.")
        return

    df_carrito = pd.DataFrame(carrito)
    st.dataframe(df_carrito[["nombre", "cantidad", "precio_venta", "total_linea"]], use_container_width=True, hide_index=True)
    subtotal = numero(df_carrito["total_linea"].sum())
    descuento = st.number_input("Descuento", min_value=0.0, max_value=subtotal, value=0.0, step=0.01)
    base = subtotal - descuento
    iva = 0.0
    total = base + iva
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subtotal", f"${subtotal:,.2f}")
    c2.metric("Descuento", f"${descuento:,.2f}")
    c3.metric("IVA", f"${iva:,.2f}")
    c4.metric("Total", f"${total:,.2f}")

    with st.expander("Datos de comprobante / cliente"):
        tipo_comprobante = st.selectbox("Tipo de comprobante", ["Factura interna", "Consumidor final", "Crédito Fiscal"])
        clientes = cargar_clientes()
        opcion_cliente = st.radio("Cliente", ["Usar cliente registrado", "Crear cliente desde esta venta"], horizontal=True)

        id_cliente = None
        crear_cliente = opcion_cliente == "Crear cliente desde esta venta"
        datos_cliente = {
            "cliente_nombre": "Cliente mostrador",
            "cliente_direccion": "",
            "cliente_telefono": "",
            "cliente_correo": "",
            "tipo_documento": "DUI",
            "num_documento": "",
            "cliente_nit": "",
            "cliente_nrc": "",
            "cliente_giro": "",
            "cliente_departamento": "",
            "cliente_municipio": "",
        }

        if not crear_cliente:
            if clientes.empty:
                st.warning("No hay clientes registrados. Use la opción crear cliente desde esta venta.")
                crear_cliente = True
            else:
                opciones_clientes = {f"{row.nombre} | {row.tipo_cliente}": int(row.id_cliente) for row in clientes.itertuples()}
                seleccionado_cliente = st.selectbox("Seleccione cliente", list(opciones_clientes.keys()))
                id_cliente = opciones_clientes[seleccionado_cliente]

        if crear_cliente:
            datos_cliente["cliente_nombre"] = st.text_input("Nombre del cliente", value="Consumidor final")
            c5, c6 = st.columns(2)
            datos_cliente["cliente_telefono"] = c5.text_input("Teléfono")
            datos_cliente["cliente_correo"] = c6.text_input("Correo")
            datos_cliente["cliente_direccion"] = st.text_area("Dirección")

            if tipo_comprobante == "Consumidor final":
                c7, c8 = st.columns(2)
                datos_cliente["tipo_documento"] = c7.selectbox("Tipo de documento", ["DUI", "Pasaporte", "Otro"])
                datos_cliente["num_documento"] = c8.text_input("Número de documento")
            elif tipo_comprobante == "Crédito Fiscal":
                c9, c10 = st.columns(2)
                datos_cliente["cliente_nit"] = c9.text_input("NIT")
                datos_cliente["cliente_nrc"] = c10.text_input("NRC")
                datos_cliente["cliente_giro"] = st.text_input("Giro")
                c11, c12 = st.columns(2)
                datos_cliente["cliente_departamento"] = c11.text_input("Departamento")
                datos_cliente["cliente_municipio"] = c12.text_input("Municipio")

    metodo_pago = st.radio("Método de pago", ["Efectivo", "Transferencia"], horizontal=True)
    c13, c14 = st.columns(2)
    if c13.button("Registrar venta", type="primary"):
        try:
            id_venta = registrar_venta(
                carrito,
                {
                    "id_cliente": id_cliente,
                    "crear_cliente": crear_cliente,
                    "tipo_comprobante": tipo_comprobante,
                    "metodo_pago": metodo_pago,
                    "subtotal": subtotal,
                    "iva": iva,
                    "descuento": descuento,
                    "total": total,
                    **datos_cliente,
                },
                st.session_state["usuario"]["id_usuario"],
            )
            st.session_state["carrito"] = []
            st.success(f"Venta registrada correctamente. Número de venta: {id_venta}")
            st.rerun()
        except Exception as e:
            st.error("No fue posible registrar la venta.")
            st.exception(e)

    if c14.button("Vaciar carrito"):
        st.session_state["carrito"] = []
        st.rerun()
