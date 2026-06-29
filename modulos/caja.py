"""
modulos/caja.py
Arqueo y cierre de caja diario, separando efectivo y transferencia.
"""

import streamlit as st
import pandas as pd
from datetime import date
from config.db import run_query, run_action


def mostrar(rol):
    st.header("💰 Arqueo de Caja")

    hoy = date.today()
    ya_existe = run_query("SELECT * FROM ARQUEO_CAJA WHERE Fecha = %s", (hoy,))

    ventas_hoy = run_query(
        "SELECT Metodo_Pago, SUM(Total) AS Total FROM VENTA WHERE DATE(Fecha) = %s GROUP BY Metodo_Pago",
        (hoy,)
    )
    efectivo = sum(v["Total"] for v in ventas_hoy if v["Metodo_Pago"] == "efectivo") or 0
    transferencia = sum(v["Total"] for v in ventas_hoy if v["Metodo_Pago"] == "transferencia") or 0
    total_general = efectivo + transferencia

    col1, col2, col3 = st.columns(3)
    col1.metric("Efectivo", f"${efectivo:.2f}")
    col2.metric("Transferencia", f"${transferencia:.2f}")
    col3.metric("Total del día", f"${total_general:.2f}")

    if ya_existe:
        st.success(f"El arqueo de hoy ({hoy}) ya fue cerrado.")
    else:
        if st.button("Cerrar caja del día de hoy"):
            run_action(
                """INSERT INTO ARQUEO_CAJA (Usuario_ID, Fecha, Total_Efectivo, Total_Transferencia, Total_General)
                   VALUES (%s,%s,%s,%s,%s)""",
                (st.session_state["usuario_id"], hoy, efectivo, transferencia, total_general)
            )
            st.success("Arqueo de caja registrado.")
            st.rerun()

    st.divider()
    st.subheader("Historial de arqueos")
    historial = run_query("SELECT * FROM ARQUEO_CAJA ORDER BY Fecha DESC LIMIT 30")
    if historial:
        st.dataframe(pd.DataFrame(historial), use_container_width=True)
    else:
        st.info("Aún no hay arqueos registrados.")
