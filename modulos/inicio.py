import streamlit as st
import pandas as pd
from config.conexion import consultar_df, probar_conexion


def valor(df, col, default=0):
    try:
        if df is None or df.empty or col not in df.columns or pd.isna(df.iloc[0][col]):
            return default
        return float(df.iloc[0][col])
    except Exception:
        return default


def mostrar():
    st.title("🛠️ Panel principal - Ferretería Elohim")
    st.write("Sistema para controlar productos, inventario, ventas, compras, caja, clientes y reportes del negocio.")

    if probar_conexion():
        st.sidebar.caption("Base de datos conectada")

    total_productos = consultar_df("SELECT COUNT(*) AS total FROM producto WHERE activo=1")
    stock_bajo = consultar_df("SELECT COUNT(*) AS total FROM producto WHERE activo=1 AND stock_actual <= stock_minimo")
    ventas_hoy = consultar_df("SELECT COUNT(*) AS total, COALESCE(SUM(total),0) AS ingresos FROM venta WHERE DATE(fecha)=CURDATE()")
    proveedores = consultar_df("SELECT COUNT(*) AS total FROM proveedor WHERE activo=1")
    clientes = consultar_df("SELECT COUNT(*) AS total FROM cliente WHERE activo=1")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Productos activos", int(valor(total_productos, "total")))
    c2.metric("Bajo mínimo", int(valor(stock_bajo, "total")))
    c3.metric("Ventas hoy", int(valor(ventas_hoy, "total")))
    c4.metric("Ingresos hoy", f"${valor(ventas_hoy, 'ingresos'):,.2f}")
    c5.metric("Proveedores", int(valor(proveedores, "total")))

    st.metric("Clientes registrados", int(valor(clientes, "total")))

    st.subheader("Productos con alerta de stock mínimo")
    df_alertas = consultar_df("""
        SELECT p.codigo_barras AS codigo, p.nombre, c.nombre AS categoria, p.stock_actual,
               p.stock_minimo, u.nombre AS ubicacion
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria=c.id_categoria
        LEFT JOIN ubicacion u ON p.id_ubicacion=u.id_ubicacion
        WHERE p.activo=1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC, p.nombre ASC
    """)
    if df_alertas.empty:
        st.info("No hay productos bajo stock mínimo.")
    else:
        st.dataframe(df_alertas, use_container_width=True, hide_index=True)

    st.subheader("Últimas ventas")
    df_ventas = consultar_df("""
        SELECT v.id_venta, v.fecha, u.nombre_completo AS vendedor,
               COALESCE(c.nombre, 'Cliente mostrador') AS cliente,
               v.metodo_pago, v.tipo_comprobante, v.total
        FROM venta v
        LEFT JOIN usuario u ON v.id_usuario=u.id_usuario
        LEFT JOIN cliente c ON v.id_cliente=c.id_cliente
        ORDER BY v.fecha DESC
        LIMIT 10
    """)
    if df_ventas.empty:
        st.info("Aún no hay ventas registradas.")
    else:
        st.dataframe(df_ventas, use_container_width=True, hide_index=True)
