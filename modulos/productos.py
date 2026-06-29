"""Módulo de productos e inventario."""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from config.conexion import execute, fetch_df, get_connection


def _admin(rol: str) -> bool:
    return rol in {"ADMIN_PRINCIPAL", "SUPERVISOR"}


def _catalogos():
    categorias = fetch_df("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    ubicaciones = fetch_df("SELECT id_ubicacion, nombre FROM ubicaciones ORDER BY nombre")
    return categorias, ubicaciones


def _producto_label(row) -> str:
    return f"{int(row['id_producto'])} - {row['nombre']} | Stock: {row['stock_actual']}"


def mostrar(rol: str) -> None:
    """Gestiona catálogo, consulta de stock y ajustes."""
    st.title("Productos e inventario")
    st.caption("Control de catálogo, ubicación, stock y alertas de reposición.")

    if _admin(rol):
        tabs = st.tabs(["Consultar", "Nuevo / editar", "Ajuste de inventario", "Carga masiva CSV"])
    else:
        tabs = st.tabs(["Consultar"])

    with tabs[0]:
        _consultar(rol)

    if _admin(rol):
        with tabs[1]:
            _nuevo_editar()
        with tabs[2]:
            _ajuste_inventario()
        with tabs[3]:
            _carga_csv()


def _consultar(rol: str) -> None:
    st.subheader("Consulta de productos")
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        texto = st.text_input("Buscar por nombre o código de barra", placeholder="cemento, tubo PVC, 20000214...")
    with col2:
        categorias = fetch_df("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
        opciones_cat = ["Todas"] + categorias["nombre"].tolist()
        cat_sel = st.selectbox("Categoría", opciones_cat)
    with col3:
        solo_bajo = st.checkbox("Solo bajo stock")

    query = """
        SELECT p.id_producto, p.codigo_barra, p.nombre, c.nombre AS categoria,
               ub.nombre AS ubicacion, p.unidad_medida, p.precio_venta,
               p.stock_actual, p.stock_minimo, p.tiene_codigo_barra,
               CASE WHEN p.stock_actual <= p.stock_minimo THEN 'Bajo stock' ELSE 'OK' END AS estado
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN ubicaciones ub ON ub.id_ubicacion = p.id_ubicacion
        WHERE p.activo = 1
    """
    params: list = []
    if texto:
        query += " AND (p.nombre LIKE %s OR p.codigo_barra LIKE %s)"
        params.extend([f"%{texto}%", f"%{texto}%"])
    if cat_sel != "Todas":
        query += " AND c.nombre = %s"
        params.append(cat_sel)
    if solo_bajo:
        query += " AND p.stock_actual <= p.stock_minimo"
    query += " ORDER BY p.nombre LIMIT 1000"

    df = fetch_df(query, tuple(params))
    if df.empty:
        st.info("No se encontraron productos con esos filtros.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Registros mostrados: {len(df)}")


def _nuevo_editar() -> None:
    st.subheader("Registrar nuevo producto")
    categorias, ubicaciones = _catalogos()

    with st.form("form_producto_nuevo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del producto *")
            codigo = st.text_input("Código de barra", placeholder="Dejar vacío si no aplica")
            categoria_nombre = st.selectbox("Categoría *", categorias["nombre"].tolist())
            ubicacion_nombre = st.selectbox("Ubicación", ubicaciones["nombre"].tolist())
        with col2:
            unidad = st.text_input("Unidad de medida", value="Unidad")
            precio = st.number_input("Precio de venta ($) *", min_value=0.0, step=0.01, format="%.2f")
            stock = st.number_input("Stock actual *", min_value=0.0, step=1.0)
            stock_min = st.number_input("Stock mínimo *", min_value=0.0, step=1.0, value=5.0)
            tiene_barra = st.checkbox("Tiene código de barra", value=True)
        guardar = st.form_submit_button("Guardar producto", use_container_width=True)

    if guardar:
        if not nombre.strip():
            st.error("El nombre del producto es obligatorio.")
        else:
            id_cat = int(categorias.loc[categorias["nombre"] == categoria_nombre, "id_categoria"].iloc[0])
            id_ubi = int(ubicaciones.loc[ubicaciones["nombre"] == ubicacion_nombre, "id_ubicacion"].iloc[0])
            execute(
                """
                INSERT INTO productos
                (codigo_barra, nombre, id_categoria, id_ubicacion, precio_venta,
                 unidad_medida, stock_actual, stock_minimo, tiene_codigo_barra)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    codigo.strip() or None,
                    nombre.strip(),
                    id_cat,
                    id_ubi,
                    Decimal(str(precio)),
                    unidad.strip() or "Unidad",
                    Decimal(str(stock)),
                    Decimal(str(stock_min)),
                    1 if tiene_barra else 0,
                ),
            )
            st.success("Producto registrado correctamente.")
            st.rerun()

    st.markdown("---")
    st.subheader("Editar producto existente")
    productos = fetch_df(
        """
        SELECT p.*, c.nombre AS categoria, u.nombre AS ubicacion
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN ubicaciones u ON u.id_ubicacion = p.id_ubicacion
        WHERE p.activo = 1
        ORDER BY p.nombre
        """
    )
    if productos.empty:
        st.info("No hay productos para editar.")
        return
    id_sel = st.selectbox(
        "Seleccione producto",
        productos["id_producto"].tolist(),
        format_func=lambda x: _producto_label(productos[productos["id_producto"] == x].iloc[0]),
    )
    row = productos[productos["id_producto"] == id_sel].iloc[0]
    categorias, ubicaciones = _catalogos()
    with st.form("form_producto_editar"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=row["nombre"])
            codigo = st.text_input("Código de barra", value="" if pd.isna(row["codigo_barra"]) else row["codigo_barra"])
            cat_idx = categorias.index[categorias["id_categoria"] == row["id_categoria"]].tolist()
            categoria_nombre = st.selectbox("Categoría", categorias["nombre"].tolist(), index=cat_idx[0] if cat_idx else 0)
            ubi_idx = ubicaciones.index[ubicaciones["id_ubicacion"] == row["id_ubicacion"]].tolist()
            ubicacion_nombre = st.selectbox("Ubicación", ubicaciones["nombre"].tolist(), index=ubi_idx[0] if ubi_idx else 0)
        with col2:
            unidad = st.text_input("Unidad de medida", value=row["unidad_medida"])
            precio = st.number_input("Precio de venta ($)", min_value=0.0, step=0.01, value=float(row["precio_venta"]), format="%.2f")
            stock_min = st.number_input("Stock mínimo", min_value=0.0, step=1.0, value=float(row["stock_minimo"]))
            tiene_barra = st.checkbox("Tiene código de barra", value=bool(row["tiene_codigo_barra"]))
            activo = st.checkbox("Producto activo", value=bool(row["activo"]))
        actualizar = st.form_submit_button("Actualizar producto", use_container_width=True)

    if actualizar:
        id_cat = int(categorias.loc[categorias["nombre"] == categoria_nombre, "id_categoria"].iloc[0])
        id_ubi = int(ubicaciones.loc[ubicaciones["nombre"] == ubicacion_nombre, "id_ubicacion"].iloc[0])
        execute(
            """
            UPDATE productos
            SET codigo_barra=%s, nombre=%s, id_categoria=%s, id_ubicacion=%s,
                precio_venta=%s, unidad_medida=%s, stock_minimo=%s,
                tiene_codigo_barra=%s, activo=%s
            WHERE id_producto=%s
            """,
            (
                codigo.strip() or None,
                nombre.strip(),
                id_cat,
                id_ubi,
                Decimal(str(precio)),
                unidad.strip() or "Unidad",
                Decimal(str(stock_min)),
                1 if tiene_barra else 0,
                1 if activo else 0,
                int(id_sel),
            ),
        )
        st.success("Producto actualizado correctamente.")
        st.rerun()


def _ajuste_inventario() -> None:
    st.subheader("Ajuste manual de inventario")
    productos = fetch_df(
        """
        SELECT id_producto, nombre, stock_actual
        FROM productos
        WHERE activo = 1
        ORDER BY nombre
        """
    )
    if productos.empty:
        st.info("No hay productos registrados.")
        return

    with st.form("form_ajuste"):
        id_prod = st.selectbox(
            "Producto",
            productos["id_producto"].tolist(),
            format_func=lambda x: _producto_label(productos[productos["id_producto"] == x].iloc[0]),
        )
        tipo = st.selectbox("Tipo de movimiento", ["entrada", "salida", "ajuste"])
        cantidad = st.number_input("Cantidad", min_value=0.01, step=1.0)
        motivo = st.text_area("Motivo", value="Ajuste manual de inventario")
        guardar = st.form_submit_button("Registrar movimiento", use_container_width=True)

    if guardar:
        delta = Decimal(str(cantidad)) if tipo in {"entrada", "ajuste"} else -Decimal(str(cantidad))
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT stock_actual FROM productos WHERE id_producto=%s FOR UPDATE", (int(id_prod),))
            stock_actual = Decimal(str(cur.fetchone()[0]))
            nuevo_stock = stock_actual + delta
            if nuevo_stock < 0:
                st.error("El ajuste dejaría el stock negativo.")
                conn.rollback()
                return
            cur.execute("UPDATE productos SET stock_actual=%s WHERE id_producto=%s", (nuevo_stock, int(id_prod)))
            cur.execute(
                """
                INSERT INTO movimientos_inventario
                (id_producto, tipo_movimiento, cantidad, referencia_tipo, referencia_id, id_usuario, motivo)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (int(id_prod), tipo, Decimal(str(cantidad)), "ajuste", None, st.session_state.get("id_usuario"), motivo),
            )
            conn.commit()
            st.success("Movimiento registrado y stock actualizado.")
            st.rerun()
        except Exception as exc:
            conn.rollback()
            st.error("No se pudo registrar el ajuste.")
            st.caption(f"Detalle técnico: {exc}")
        finally:
            conn.close()


def _carga_csv() -> None:
    st.subheader("Carga masiva de productos desde CSV")
    st.write(
        "El CSV debe contener columnas: nombre, categoria, ubicacion, precio_venta, unidad_medida, "
        "stock_actual, stock_minimo, codigo_barra, tiene_codigo_barra."
    )
    archivo = st.file_uploader("Subir archivo CSV", type=["csv"])
    if archivo is None:
        return
    df = pd.read_csv(archivo)
    st.dataframe(df.head(20), use_container_width=True)
    if not st.button("Importar productos", use_container_width=True):
        return

    categorias = fetch_df("SELECT id_categoria, nombre FROM categorias")
    ubicaciones = fetch_df("SELECT id_ubicacion, nombre FROM ubicaciones")
    cat_map = {r["nombre"].lower(): int(r["id_categoria"]) for _, r in categorias.iterrows()}
    ubi_map = {r["nombre"].lower(): int(r["id_ubicacion"]) for _, r in ubicaciones.iterrows()}

    insertados = 0
    errores = []
    for idx, row in df.iterrows():
        try:
            id_cat = cat_map[str(row["categoria"]).lower()]
            id_ubi = ubi_map[str(row["ubicacion"]).lower()]
            execute(
                """
                INSERT INTO productos
                (codigo_barra, nombre, id_categoria, id_ubicacion, precio_venta,
                 unidad_medida, stock_actual, stock_minimo, tiene_codigo_barra)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    nombre=VALUES(nombre), id_categoria=VALUES(id_categoria), id_ubicacion=VALUES(id_ubicacion),
                    precio_venta=VALUES(precio_venta), unidad_medida=VALUES(unidad_medida),
                    stock_actual=VALUES(stock_actual), stock_minimo=VALUES(stock_minimo),
                    tiene_codigo_barra=VALUES(tiene_codigo_barra), activo=1
                """,
                (
                    None if pd.isna(row.get("codigo_barra")) or str(row.get("codigo_barra")).strip() == "" else str(row.get("codigo_barra")).strip(),
                    str(row["nombre"]).strip(),
                    id_cat,
                    id_ubi,
                    Decimal(str(row["precio_venta"])),
                    str(row.get("unidad_medida", "Unidad")).strip(),
                    Decimal(str(row.get("stock_actual", 0))),
                    Decimal(str(row.get("stock_minimo", 0))),
                    int(row.get("tiene_codigo_barra", 1)),
                ),
            )
            insertados += 1
        except Exception as exc:
            errores.append(f"Fila {idx + 2}: {exc}")
    st.success(f"Productos importados/actualizados: {insertados}")
    if errores:
        st.error("Algunas filas no se importaron.")
        st.write(errores[:20])
