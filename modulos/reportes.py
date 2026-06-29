import streamlit as st
from config.conexion import consultar_df


def mostrar():
    st.title("📊 Reportes e inteligencia de negocio")

    st.subheader("Producto estrella y top 10 más vendidos")
    top = consultar_df("""
        SELECT p.nombre AS producto, SUM(dv.cantidad) AS cantidad_vendida, SUM(dv.subtotal) AS ingresos
        FROM detalle_venta dv
        JOIN producto p ON dv.id_producto=p.id_producto
        GROUP BY p.id_producto, p.nombre
        ORDER BY ingresos DESC
        LIMIT 10
    """)
    if top.empty:
        st.info("Aún no hay ventas suficientes para calcular productos más vendidos.")
    else:
        estrella = top.iloc[0]
        st.success(f"Producto estrella por ingresos: {estrella['producto']} (${float(estrella['ingresos']):,.2f})")
        st.dataframe(top, use_container_width=True, hide_index=True)
        st.bar_chart(top.set_index("producto")["ingresos"])

    st.subheader("Ventas mensuales")
    ventas = consultar_df("""
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes, COUNT(*) AS cantidad_ventas, SUM(total) AS ingresos
        FROM venta
        GROUP BY DATE_FORMAT(fecha, '%Y-%m')
        ORDER BY mes
    """)
    if ventas.empty:
        st.info("No hay ventas registradas.")
    else:
        st.dataframe(ventas, use_container_width=True, hide_index=True)
        st.bar_chart(ventas.set_index("mes")["ingresos"])

    st.subheader("Productos con baja rotación")
    baja = consultar_df("""
        SELECT p.id_producto, p.nombre, p.stock_actual, COALESCE(SUM(dv.cantidad),0) AS cantidad_vendida
        FROM producto p
        LEFT JOIN detalle_venta dv ON p.id_producto=dv.id_producto
        WHERE p.activo=1
        GROUP BY p.id_producto, p.nombre, p.stock_actual
        HAVING cantidad_vendida = 0
        ORDER BY p.nombre
    """)
    if baja.empty:
        st.success("No hay productos sin movimiento.")
    else:
        st.dataframe(baja, use_container_width=True, hide_index=True)

    st.subheader("Movimientos recientes de inventario")
    mov = consultar_df("""
        SELECT mi.id_movimiento, p.nombre AS producto, mi.tipo_movimiento, mi.cantidad,
               mi.fecha, u.nombre_completo AS usuario, mi.motivo
        FROM movimiento_inventario mi
        JOIN producto p ON mi.id_producto=p.id_producto
        LEFT JOIN usuario u ON mi.id_usuario=u.id_usuario
        ORDER BY mi.fecha DESC
        LIMIT 50
    """)
    if mov.empty:
        st.info("No hay movimientos registrados.")
    else:
        st.dataframe(mov, use_container_width=True, hide_index=True)
