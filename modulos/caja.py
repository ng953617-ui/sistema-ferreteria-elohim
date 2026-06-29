import streamlit as st
from datetime import date
from config.conexion import consultar_df, ejecutar


def mostrar():
    st.title("💵 Arqueo y cierre de caja")
    st.write("Separa ingresos en efectivo y transferencias para facilitar la conciliación diaria.")

    fecha = st.date_input("Fecha de cierre", value=date.today())

    resumen = consultar_df(
        """
        SELECT metodo_pago, COUNT(*) AS cantidad_ventas, COALESCE(SUM(total),0) AS total
        FROM venta
        WHERE DATE(fecha) = %s
        GROUP BY metodo_pago
        """,
        [fecha],
    )

    efectivo_sistema = 0.0
    transferencia_sistema = 0.0
    if not resumen.empty:
        for row in resumen.itertuples():
            if row.metodo_pago == "Efectivo":
                efectivo_sistema = float(row.total)
            elif row.metodo_pago == "Transferencia":
                transferencia_sistema = float(row.total)

    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo según sistema", f"${efectivo_sistema:,.2f}")
    c2.metric("Transferencias según sistema", f"${transferencia_sistema:,.2f}")
    c3.metric("Total del día", f"${efectivo_sistema + transferencia_sistema:,.2f}")

    st.dataframe(resumen, use_container_width=True, hide_index=True)

    with st.form("form_arqueo"):
        efectivo_contado = st.number_input("Efectivo contado físicamente", min_value=0.0, value=efectivo_sistema, step=0.01)
        observaciones = st.text_area("Observaciones")
        guardar = st.form_submit_button("Guardar cierre de caja")

    if guardar:
        diferencia = efectivo_contado - efectivo_sistema
        id_usuario = st.session_state["usuario"]["id_usuario"]
        ejecutar(
            """
            INSERT INTO arqueo_caja
            (fecha, id_usuario, total_efectivo, total_transferencia,
             efectivo_contado, diferencia_efectivo, total_general, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha,
                id_usuario,
                efectivo_sistema,
                transferencia_sistema,
                efectivo_contado,
                diferencia,
                efectivo_sistema + transferencia_sistema,
                observaciones,
            ),
        )
        st.success("Cierre de caja guardado correctamente.")
        st.rerun()

    st.subheader("Cierres registrados")
    cierres = consultar_df(
        """
        SELECT a.id_caja, a.fecha, u.nombre_completo AS responsable,
               a.total_efectivo, a.total_transferencia, a.efectivo_contado,
               a.diferencia_efectivo, a.total_general, a.observaciones
        FROM arqueo_caja a
        INNER JOIN usuario u ON a.id_usuario = u.id_usuario
        ORDER BY a.fecha_registro DESC
        LIMIT 20
        """
    )
    st.dataframe(cierres, use_container_width=True, hide_index=True)
