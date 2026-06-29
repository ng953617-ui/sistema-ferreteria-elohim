import streamlit as st
import pandas as pd
from config.conexion import consultar, consultar_df, ejecutar, ejecutar_insert


def _productos(filtro):
    like = f"%{filtro}%"
    return consultar("""
        SELECT id_producto, nombre, codigo_barras, stock_actual, precio_venta, unidad
        FROM producto
        WHERE activo=1 AND stock_actual > 0
          AND (nombre LIKE %s OR COALESCE(codigo_barras,'') LIKE %s OR COALESCE(descripcion,'') LIKE %s)
        ORDER BY nombre
        LIMIT 60
    """, (like, like, like))


def mostrar():
    st.title("🧾 Punto de venta")
    st.write("Permite venta rápida mediante búsqueda por texto o código de barras. Para productos sin código, seleccione manualmente el producto.")

    if "carrito" not in st.session_state:
        st.session_state["carrito"] = []

    filtro = st.text_input("Escanear código de barras o buscar producto")
    productos = _productos(filtro)

    if not productos:
        st.warning("No se encontraron productos con ese filtro.")
    else:
        opciones = {
            f"{p['nombre']} | Código: {p['codigo_barras'] or 'Sin código'} | Stock: {p['stock_actual']} {p['unidad']} | ${float(p['precio_venta']):.2f}": p
            for p in productos
        }
        sel = st.selectbox("Producto", list(opciones.keys()))
        prod = opciones[sel]
        c1, c2 = st.columns(2)
        cant = c1.number_input("Cantidad", min_value=0.01, max_value=float(prod["stock_actual"]), step=1.0)
        c2.metric("Precio unitario", f"${float(prod['precio_venta']):.2f}")
        if st.button("Agregar al carrito"):
            subtotal = float(cant) * float(prod["precio_venta"])
            st.session_state["carrito"].append({
                "id_producto": prod["id_producto"],
                "producto": prod["nombre"],
                "cantidad": float(cant),
                "precio_unitario": float(prod["precio_venta"]),
                "subtotal": subtotal,
            })
            st.success("Producto agregado.")
            st.rerun()

    st.subheader("Carrito de venta")
    if not st.session_state["carrito"]:
        st.info("El carrito está vacío.")
        return

    df = pd.DataFrame(st.session_state["carrito"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    total = float(df["subtotal"].sum())
    st.metric("Total", f"${total:,.2f}")

    clientes = consultar("SELECT id_cliente, nombre FROM cliente WHERE activo=1 ORDER BY nombre")
    dic_clientes = {"Cliente mostrador": None}
    for c in clientes:
        dic_clientes[c["nombre"]] = c["id_cliente"]

    c1, c2, c3 = st.columns(3)
    cliente = c1.selectbox("Cliente", list(dic_clientes.keys()))
    metodo = c2.selectbox("Método de pago", ["Efectivo", "Transferencia"])
    comprobante = c3.selectbox("Tipo de comprobante", ["Factura interna", "Consumidor final", "CCF"])

    col_a, col_b = st.columns(2)
    if col_a.button("Confirmar venta"):
        user_id = st.session_state["usuario"]["id_usuario"]
        venta_id = ejecutar_insert("""
            INSERT INTO venta (id_usuario, id_cliente, subtotal, iva, total, metodo_pago, tipo_comprobante)
            VALUES (%s,%s,%s,0,%s,%s,%s)
        """, (user_id, dic_clientes[cliente], total, total, metodo, comprobante))

        for item in st.session_state["carrito"]:
            ejecutar("""
                INSERT INTO detalle_venta (id_venta,id_producto,cantidad,precio_unitario,subtotal)
                VALUES (%s,%s,%s,%s,%s)
            """, (venta_id, item["id_producto"], item["cantidad"], item["precio_unitario"], item["subtotal"]))
            ejecutar("UPDATE producto SET stock_actual = stock_actual - %s WHERE id_producto=%s", (item["cantidad"], item["id_producto"]))
            ejecutar("""
                INSERT INTO movimiento_inventario (id_producto,tipo_movimiento,cantidad,referencia_id,id_usuario,motivo)
                VALUES (%s,'Salida',%s,%s,%s,'Venta en punto de venta')
            """, (item["id_producto"], item["cantidad"], venta_id, user_id))

        st.session_state["carrito"] = []
        st.success("Venta registrada correctamente.")
        st.rerun()

    if col_b.button("Vaciar carrito"):
        st.session_state["carrito"] = []
        st.rerun()
