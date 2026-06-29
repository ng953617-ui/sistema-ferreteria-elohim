"""Dashboard principal."""
from __future__ import annotations

import streamlit as st

from config.conexion import fetch_df


def _safe_value(df, default=0):
    if df.empty:
        return default
    value = df.iloc[0, 0]
    return default if value is None else value


def mostrar(rol: str) -> None:
    """Muestra indicadores principales del negocio."""
    st.title("Dashboard general")
    st.caption("Indicadores operativos de Ferretería ELOHIM")

    try:
        total_productos = _safe_value(fetch_df("SELECT COUNT(*) FROM productos WHERE activo = 1"))
        bajo_stock = _safe_value(fetch_df("SELECT COUNT(*) FROM productos WHERE activo = 1 AND stock_actual <= stock_minimo"))
        ventas_hoy = _safe_value(fetch_df("SELECT COALESCE(SUM(total),0) FROM ventas WHERE DATE(fecha)=CURDATE()"), 0)
        num_ventas_hoy = _safe_value(fetch_df("SELECT COUNT(*) FROM ventas WHERE DATE(fecha)=CURDATE()"), 0)
    except Exception as exc:
        st.error("No se pudieron cargar los indicadores. Revise la conexión y el esquema SQL.")
        st.caption(f"Detalle técnico: {exc}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Productos activos", f"{int(total_productos):,}")
    c2.metric("Productos bajo stock", f"{int(bajo_stock):,}")
    c3.metric("Ventas de hoy", f"${float(ventas_hoy):,.2f}")
    c4.metric("Transacciones de hoy", f"{int(num_ventas_hoy):,}")

    st.markdown("---")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Inventario por categoría")
        df_cat = fetch_df(
            """
            SELECT c.nombre AS categoria, COUNT(p.id_producto) AS productos
            FROM categorias c
            LEFT JOIN productos p ON p.id_categoria = c.id_categoria AND p.activo = 1
            GROUP BY c.id_categoria, c.nombre
            ORDER BY productos DESC
            """
        )
        if not df_cat.empty:
            st.bar_chart(df_cat.set_index("categoria"))
        else:
            st.info("Aún no hay categorías registradas.")

    with col_b:
        st.subheader("Ventas recientes")
        df_ventas = fetch_df(
            """
            SELECT v.id_venta AS venta, v.fecha, u.nombre AS vendedor, v.metodo_pago, v.total
            FROM ventas v
            INNER JOIN usuarios u ON u.id_usuario = v.id_usuario
            ORDER BY v.fecha DESC
            LIMIT 10
            """
        )
        if df_ventas.empty:
            st.info("Aún no hay ventas registradas.")
        else:
            st.dataframe(df_ventas, use_container_width=True, hide_index=True)

    st.subheader("Alertas de stock mínimo")
    df_low = fetch_df(
        """
        SELECT p.id_producto, p.nombre, c.nombre AS categoria, p.stock_actual,
               p.stock_minimo, u.nombre AS ubicacion
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN ubicaciones u ON u.id_ubicacion = p.id_ubicacion
        WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC, p.nombre ASC
        LIMIT 20
        """
    )
    if df_low.empty:
        st.success("No hay productos bajo el mínimo configurado.")
    else:
        st.warning("Revise estos productos para reposición.")
        st.dataframe(df_low, use_container_width=True, hide_index=True)
