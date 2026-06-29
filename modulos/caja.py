"""Módulo de arqueo y cierre de caja."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import streamlit as st

from config.conexion import execute, fetch_df


def mostrar(rol: str) -> None:
    """Calcula ingresos diarios separados por efectivo y transferencia."""
    st.title("Caja")
    st.caption("Arqueo diario con separación de efectivo y transferencias.")

    fecha = st.date_input("Fecha de cierre", value=date.today())
    resumen = fetch_df(
        """
        SELECT metodo_pago, COUNT(*) AS transacciones, COALESCE(SUM(total),0) AS total
        FROM ventas
        WHERE DATE(fecha) = %s
        GROUP BY metodo_pago
        """,
        (fecha,),
    )

    efectivo = Decimal("0.00")
    transferencia = Decimal("0.00")
    if not resumen.empty:
        for _, row in resumen.iterrows():
            if row["metodo_pago"] == "Efectivo":
                efectivo = Decimal(str(row["total"]))
            elif row["metodo_pago"] == "Transferencia":
                transferencia = Decimal(str(row["total"]))
    total = efectivo + transferencia

    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo", f"${float(efectivo):,.2f}")
    c2.metric("Transferencias", f"${float(transferencia):,.2f}")
    c3.metric("Total general", f"${float(total):,.2f}")

    st.subheader("Ventas del día")
    ventas = fetch_df(
        """
        SELECT v.id_venta, v.fecha, u.nombre AS vendedor, COALESCE(c.nombre,'Consumidor final') AS cliente,
               v.metodo_pago, v.tipo_comprobante, v.total
        FROM ventas v
        LEFT JOIN usuarios u ON u.id_usuario = v.id_usuario
        LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
        WHERE DATE(v.fecha) = %s
        ORDER BY v.fecha DESC
        """,
        (fecha,),
    )
    st.dataframe(ventas, use_container_width=True, hide_index=True)

    observaciones = st.text_area("Observaciones del cierre", value="Cierre de caja generado desde el sistema")
    if st.button("Registrar / actualizar arqueo", use_container_width=True):
        execute(
            """
            INSERT INTO arqueos_caja
            (id_usuario, fecha, total_efectivo, total_transferencia, total_general, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                id_usuario=VALUES(id_usuario),
                total_efectivo=VALUES(total_efectivo),
                total_transferencia=VALUES(total_transferencia),
                total_general=VALUES(total_general),
                observaciones=VALUES(observaciones)
            """,
            (st.session_state.get("id_usuario"), fecha, efectivo, transferencia, total, observaciones),
        )
        st.success("Arqueo registrado correctamente.")
        st.rerun()

    st.subheader("Arqueos registrados")
    arqueos = fetch_df(
        """
        SELECT a.fecha, u.nombre AS usuario, a.total_efectivo, a.total_transferencia,
               a.total_general, a.observaciones
        FROM arqueos_caja a
        LEFT JOIN usuarios u ON u.id_usuario = a.id_usuario
        ORDER BY a.fecha DESC
        LIMIT 100
        """
    )
    st.dataframe(arqueos, use_container_width=True, hide_index=True)
