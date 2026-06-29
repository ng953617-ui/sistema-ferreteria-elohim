import streamlit as st
import pandas as pd
from config.conexion import consultar_df, probar_conexion


def valor_numero(df, columna, defecto=0):
    """Devuelve un valor numérico seguro desde un DataFrame."""
    try:
        if df is None or df.empty or columna not in df.columns:
            return defecto
        valor = pd.to_numeric(df.iloc[0][columna], errors="coerce")
        if pd.isna(valor):
            return defecto
        return float(valor)
    except Exception:
        return defecto


def mostrar():
    st.title("🛠️ Panel principal - Ferretería Elohim")
    st.write("Sistema para controlar productos, inventario, ventas, compras, caja, clientes y reportes del negocio.")

    try:
        if probar_conexion():
            st.sidebar.caption("Base de datos conectada")
    except Exception as e:
        st.error("No hay conexión con la base de datos. Revise los Secrets de Streamlit.")
        st.exception(e)
        return

    try:
        total_productos = consultar_df("SELECT COUNT(*) AS total FROM producto WHERE activo = 1 AND nombre <> 'nombre'")
        stock_bajo = consultar_df("""
            SELECT COUNT(*) AS total
            FROM producto
            WHERE activo = 1 AND nombre <> 'nombre' AND stock_actual <= stock_minimo
        """)
        ventas_hoy = consultar_df("""
            SELECT COUNT(*) AS total, COALESCE(SUM(total), 0) AS ingresos
            FROM venta
            WHERE DATE(fecha) = CURDATE()
        """)
        valor_inv = consultar_df("""
            SELECT COALESCE(SUM(stock_actual * precio_compra), 0) AS valor
            FROM producto
            WHERE activo = 1 AND nombre <> 'nombre'
        """)
        clientes = consultar_df("SELECT COUNT(*) AS total FROM cliente WHERE nombre <> 'nombre'")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Productos activos", int(valor_numero(total_productos, "total")))
        c2.metric("Productos bajo mínimo", int(valor_numero(stock_bajo, "total")))
        c3.metric("Ventas de hoy", int(valor_numero(ventas_hoy, "total")))
        c4.metric("Ingresos de hoy", f"${valor_numero(ventas_hoy, 'ingresos'):,.2f}")
        c5.metric("Clientes registrados", int(valor_numero(clientes, "total")))
        st.metric("Valor estimado del inventario", f"${valor_numero(valor_inv, 'valor'):,.2f}")
    except Exception as e:
        st.error("Ocurrió un error al cargar los indicadores del panel principal.")
        st.exception(e)
        return

    st.subheader("Productos con alerta de stock mínimo")
    try:
        df_alertas = consultar_df("""
            SELECT p.codigo_barras AS codigo, p.nombre, c.nombre AS categoria,
                   p.stock_actual, p.stock_minimo, u.nombre AS ubicacion
            FROM producto p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN ubicacion u ON p.id_ubicacion = u.id_ubicacion
            WHERE p.activo = 1 AND p.nombre <> 'nombre' AND p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual ASC, p.nombre ASC
            LIMIT 15
        """)
        if df_alertas.empty:
            st.info("No hay productos bajo el stock mínimo.")
        else:
            st.dataframe(df_alertas, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning("No se pudieron cargar las alertas de stock mínimo.")
        st.exception(e)

    st.subheader("Últimas ventas registradas")
    try:
        df_ventas = consultar_df("""
            SELECT v.id_venta, v.fecha, u.nombre_completo AS vendedor,
                   COALESCE(c.nombre, 'Cliente mostrador') AS cliente,
                   v.metodo_pago, v.tipo_comprobante, v.total
            FROM venta v
            LEFT JOIN usuario u ON v.id_usuario = u.id_usuario
            LEFT JOIN cliente c ON v.id_cliente = c.id_cliente
            ORDER BY v.fecha DESC
            LIMIT 10
        """)
        if df_ventas.empty:
            st.info("Aún no hay ventas registradas.")
        else:
            st.dataframe(df_ventas, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning("No se pudieron cargar las últimas ventas.")
        st.exception(e)
