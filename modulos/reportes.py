"""
modulos/reportes.py
Reportes para toma de decisiones: producto estrella, baja rotación,
estadísticas mensuales, compras sugeridas.
"""

import streamlit as st
import pandas as pd
from config.db import run_query


def mostrar(rol):
    st.header("📊 Reportes")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Más vendidos", "Baja rotación", "Ventas mensuales", "Compras sugeridas"]
    )

    with tab1:
        top = run_query("""
            SELECT p.Nombre, SUM(dv.Cantidad) AS Unidades_Vendidas, SUM(dv.Subtotal) AS Ingresos
            FROM DETALLE_VENTA dv JOIN PRODUCTO p ON dv.Producto_ID = p.ID_Producto
            GROUP BY p.ID_Producto ORDER BY Ingresos DESC LIMIT 10
        """)
        if top:
            st.dataframe(pd.DataFrame(top), use_container_width=True)
            st.bar_chart(pd.DataFrame(top).set_index("Nombre")["Ingresos"])
        else:
            st.info("Aún no hay ventas registradas.")

    with tab2:
        baja = run_query("""
            SELECT p.Nombre, p.Stock_Actual, COALESCE(SUM(dv.Cantidad), 0) AS Vendido
            FROM PRODUCTO p
            LEFT JOIN DETALLE_VENTA dv ON p.ID_Producto = dv.Producto_ID
            GROUP BY p.ID_Producto
            HAVING Vendido = 0 OR Vendido < 5
            ORDER BY Vendido ASC
        """)
        if baja:
            st.dataframe(pd.DataFrame(baja), use_container_width=True)
        else:
            st.info("No hay productos de baja rotación detectados todavía.")

    with tab3:
        mensual = run_query("""
            SELECT DATE_FORMAT(Fecha, '%Y-%m') AS Mes, SUM(Total) AS Ventas
            FROM VENTA GROUP BY Mes ORDER BY Mes
        """)
        if mensual:
            df = pd.DataFrame(mensual)
            st.dataframe(df, use_container_width=True)
            st.line_chart(df.set_index("Mes")["Ventas"])
        else:
            st.info("Aún no hay historial de ventas suficiente.")

    with tab4:
        sugeridas = run_query("""
            SELECT Nombre, Stock_Actual, Stock_Minimo
            FROM PRODUCTO WHERE Stock_Actual <= Stock_Minimo
        """)
        if sugeridas:
            st.dataframe(pd.DataFrame(sugeridas), use_container_width=True)
        else:
            st.success("No hay productos que requieran reposición urgente.")
