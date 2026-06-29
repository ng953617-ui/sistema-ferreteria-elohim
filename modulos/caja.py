import streamlit as st
from config.conexion import consultar_df, ejecutar


def _num(df, col):
    if df.empty or col not in df.columns or df.iloc[0][col] is None:
        return 0.0
    return float(df.iloc[0][col])


def mostrar():
    st.title("💵 Cierre de caja")
    fecha = st.date_input("Fecha de cierre")

    efectivo = consultar_df("SELECT COALESCE(SUM(total),0) AS total FROM venta WHERE DATE(fecha)=%s AND metodo_pago='Efectivo'", (fecha,))
    transferencia = consultar_df("SELECT COALESCE(SUM(total),0) AS total FROM venta WHERE DATE(fecha)=%s AND metodo_pago='Transferencia'", (fecha,))
    total_ef = _num(efectivo, "total")
    total_tr = _num(transferencia, "total")
    total = total_ef + total_tr

    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo", f"${total_ef:,.2f}")
    c2.metric("Transferencia", f"${total_tr:,.2f}")
    c3.metric("Total general", f"${total:,.2f}")

    obs = st.text_area("Observaciones")
    if st.button("Registrar arqueo"):
        ejecutar("""
            INSERT INTO arqueo_caja (id_usuario, fecha, total_efectivo, total_transferencia, total_general, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (st.session_state["usuario"]["id_usuario"], fecha, total_ef, total_tr, total, obs))
        st.success("Arqueo registrado correctamente.")
        st.rerun()

    st.subheader("Historial")
    df = consultar_df("""
        SELECT a.id_arqueo, a.fecha, u.nombre_completo AS usuario,
               a.total_efectivo, a.total_transferencia, a.total_general, a.observaciones
        FROM arqueo_caja a
        JOIN usuario u ON a.id_usuario=u.id_usuario
        ORDER BY a.fecha DESC, a.id_arqueo DESC
    """)
    if df.empty:
        st.info("No hay arqueos registrados.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
