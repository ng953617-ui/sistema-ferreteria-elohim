import streamlit as st
from config.conexion import consultar_df


def mostrar():
    st.title("📊 Reportes e inteligencia de negocio")

    st.subheader("Producto estrella y top 10 más vendidos")
    top = consultar_df(
        """
        SELECT p.nombre AS producto, c.nombre AS categoria,
               COALESCE(SUM(d.cantidad),0) AS unidades_vendidas,
               COALESCE(SUM(d.subtotal),0) AS ingresos,
               COALESCE(SUM((d.precio_unitario - d.costo_unitario) * d.cantidad),0) AS utilidad_estimada
        FROM detalle_venta d
        INNER JOIN producto p ON d.id_producto = p.id_producto
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        GROUP BY p.id_producto, p.nombre, c.nombre
        ORDER BY ingresos DESC
        LIMIT 10
        """
    )
    if top.empty:
        st.info("Aún no hay ventas registradas para generar este reporte.")
    else:
        estrella = top.iloc[0]
        st.success(f"Producto estrella por ingresos: {estrella['producto']} (${float(estrella['ingresos']):,.2f})")
        st.dataframe(top, use_container_width=True, hide_index=True)
        st.bar_chart(top.set_index("producto")[["ingresos"]])

    st.subheader("Ventas mensuales históricas")
    mensual = consultar_df(
        """
        SELECT DATE_FORMAT(fecha, '%%Y-%%m') AS mes,
               COUNT(*) AS cantidad_ventas,
               COALESCE(SUM(total),0) AS ingresos
        FROM venta
        GROUP BY DATE_FORMAT(fecha, '%%Y-%%m')
        ORDER BY mes
        """
    )
    if mensual.empty:
        st.info("No hay ventas para graficar.")
    else:
        st.dataframe(mensual, use_container_width=True, hide_index=True)
        st.line_chart(mensual.set_index("mes")[["ingresos"]])

    st.subheader("Reporte de baja rotación")
    baja = consultar_df(
        """
        SELECT p.nombre AS producto, c.nombre AS categoria, p.stock_actual, p.precio_venta,
               MAX(v.fecha) AS ultima_venta,
               COALESCE(SUM(d.cantidad),0) AS unidades_vendidas
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        LEFT JOIN detalle_venta d ON p.id_producto = d.id_producto
        LEFT JOIN venta v ON d.id_venta = v.id_venta
        WHERE p.activo = 1
        GROUP BY p.id_producto, p.nombre, c.nombre, p.stock_actual, p.precio_venta
        HAVING unidades_vendidas <= 1 OR ultima_venta IS NULL
        ORDER BY unidades_vendidas ASC, p.stock_actual DESC
        LIMIT 20
        """
    )
    st.dataframe(baja, use_container_width=True, hide_index=True)

    st.subheader("Alertas de stock mínimo")
    alertas = consultar_df(
        """
        SELECT p.nombre AS producto, c.nombre AS categoria, p.stock_actual, p.stock_minimo,
               pr.nombre_razon_social AS proveedor_principal
        FROM producto p
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        LEFT JOIN producto_proveedor pp ON p.id_producto = pp.id_producto AND pp.es_principal = 1
        LEFT JOIN proveedor pr ON pp.id_proveedor = pr.id_proveedor
        WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC
        """
    )
    st.dataframe(alertas, use_container_width=True, hide_index=True)

    st.subheader("Ventas por método de pago")
    pagos = consultar_df(
        """
        SELECT metodo_pago, COUNT(*) AS cantidad, COALESCE(SUM(total),0) AS total
        FROM venta
        GROUP BY metodo_pago
        """
    )
    if not pagos.empty:
        st.dataframe(pagos, use_container_width=True, hide_index=True)
        st.bar_chart(pagos.set_index("metodo_pago")[["total"]])

    st.subheader("Trazabilidad de movimientos de inventario")
    movimientos = consultar_df(
        """
        SELECT m.id_movimiento, m.fecha, p.nombre AS producto, m.tipo, m.cantidad,
               u.nombre_completo AS usuario, m.referencia, m.motivo
        FROM movimiento_inventario m
        INNER JOIN producto p ON m.id_producto = p.id_producto
        INNER JOIN usuario u ON m.id_usuario = u.id_usuario
        ORDER BY m.fecha DESC
        LIMIT 30
        """
    )
    st.dataframe(movimientos, use_container_width=True, hide_index=True)
