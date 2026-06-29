"""Módulo de reportes e inteligencia de negocio."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from config.conexion import fetch_df


def mostrar(rol: str) -> None:
    """Presenta reportes administrativos para toma de decisiones."""
    st.title("Reportes")
    st.caption("Producto estrella, top ventas, baja rotación, stock mínimo y estacionalidad mensual.")

    hoy = date.today()
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=hoy - timedelta(days=90))
    with col2:
        fecha_fin = st.date_input("Hasta", value=hoy)

    tabs = st.tabs(["Ventas", "Producto estrella", "Stock y baja rotación", "Movimientos"])

    with tabs[0]:
        _ventas(fecha_inicio, fecha_fin)
    with tabs[1]:
        _producto_estrella(fecha_inicio, fecha_fin)
    with tabs[2]:
        _stock_baja_rotacion(fecha_inicio, fecha_fin)
    with tabs[3]:
        _movimientos()


def _ventas(fecha_inicio, fecha_fin) -> None:
    st.subheader("Ventas mensuales")
    df = fetch_df(
        """
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
               COUNT(*) AS transacciones,
               COALESCE(SUM(total),0) AS ventas
        FROM ventas
        WHERE DATE(fecha) BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(fecha, '%Y-%m')
        ORDER BY mes
        """,
        (fecha_inicio, fecha_fin),
    )
    if df.empty:
        st.info("No hay ventas en el período seleccionado.")
        return
    c1, c2 = st.columns(2)
    c1.metric("Ventas acumuladas", f"${float(df['ventas'].sum()):,.2f}")
    c2.metric("Transacciones", f"{int(df['transacciones'].sum()):,}")
    st.line_chart(df.set_index("mes")[["ventas"]])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Ventas por método de pago")
    pago = fetch_df(
        """
        SELECT metodo_pago, COUNT(*) AS transacciones, COALESCE(SUM(total),0) AS total
        FROM ventas
        WHERE DATE(fecha) BETWEEN %s AND %s
        GROUP BY metodo_pago
        """,
        (fecha_inicio, fecha_fin),
    )
    st.dataframe(pago, use_container_width=True, hide_index=True)


def _producto_estrella(fecha_inicio, fecha_fin) -> None:
    st.subheader("Producto estrella y Top 10")
    df = fetch_df(
        """
        SELECT p.nombre AS producto, c.nombre AS categoria,
               SUM(dv.cantidad) AS unidades_vendidas,
               SUM(dv.subtotal) AS ingresos
        FROM detalle_venta dv
        INNER JOIN ventas v ON v.id_venta = dv.id_venta
        INNER JOIN productos p ON p.id_producto = dv.id_producto
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        WHERE DATE(v.fecha) BETWEEN %s AND %s
        GROUP BY p.id_producto, p.nombre, c.nombre
        ORDER BY ingresos DESC
        LIMIT 10
        """,
        (fecha_inicio, fecha_fin),
    )
    if df.empty:
        st.info("No hay ventas para calcular producto estrella.")
        return
    estrella = df.iloc[0]
    st.success(f"Producto estrella por ingresos: **{estrella['producto']}** (${float(estrella['ingresos']):,.2f}).")
    st.bar_chart(df.set_index("producto")[["ingresos"]])
    st.dataframe(df, use_container_width=True, hide_index=True)


def _stock_baja_rotacion(fecha_inicio, fecha_fin) -> None:
    st.subheader("Productos bajo stock")
    bajo = fetch_df(
        """
        SELECT p.nombre AS producto, c.nombre AS categoria, p.stock_actual, p.stock_minimo,
               u.nombre AS ubicacion
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN ubicaciones u ON u.id_ubicacion = p.id_ubicacion
        WHERE p.activo=1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC, p.nombre
        """
    )
    st.dataframe(bajo, use_container_width=True, hide_index=True)

    st.subheader("Baja rotación")
    baja = fetch_df(
        """
        SELECT p.id_producto, p.nombre AS producto, c.nombre AS categoria,
               p.stock_actual,
               COALESCE(SUM(CASE WHEN v.id_venta IS NOT NULL THEN dv.cantidad ELSE 0 END),0) AS unidades_vendidas_periodo
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN detalle_venta dv ON dv.id_producto = p.id_producto
        LEFT JOIN ventas v ON v.id_venta = dv.id_venta AND DATE(v.fecha) BETWEEN %s AND %s
        WHERE p.activo=1
        GROUP BY p.id_producto, p.nombre, c.nombre, p.stock_actual
        HAVING unidades_vendidas_periodo = 0
        ORDER BY p.stock_actual DESC, p.nombre
        LIMIT 100
        """,
        (fecha_inicio, fecha_fin),
    )
    st.dataframe(baja, use_container_width=True, hide_index=True)


def _movimientos() -> None:
    st.subheader("Movimientos recientes de inventario")
    df = fetch_df(
        """
        SELECT mi.fecha, p.nombre AS producto, mi.tipo_movimiento, mi.cantidad,
               mi.referencia_tipo, mi.referencia_id, u.nombre AS usuario, mi.motivo
        FROM movimientos_inventario mi
        INNER JOIN productos p ON p.id_producto = mi.id_producto
        LEFT JOIN usuarios u ON u.id_usuario = mi.id_usuario
        ORDER BY mi.fecha DESC
        LIMIT 300
        """
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
