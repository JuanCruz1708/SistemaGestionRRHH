import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Gestión de Empleados", page_icon="🧑‍💼", layout="wide")

st.title("🧑‍💼 Gestión de Empleados")

# --- Conexión ---
conn = sqlite3.connect("rrhh.db", check_same_thread=False)
c = conn.cursor()

# --- Helpers ---
def obtener_empleados():
    query = """
    SELECT e.id, e.legajo, e.apellido, e.nombre, e.dni, e.genero, e.telefono, e.email, e.direccion,
           p.nombre as puesto, c.nombre as centro_costo, e.estado
    FROM empleados e
    LEFT JOIN puestos p ON e.puesto_id = p.id
    LEFT JOIN centros_costo c ON e.centro_costo_id = c.id
    """
    df = pd.read_sql_query(query, conn)
    return df

def agregar_empleado(datos):
    c.execute("""
    INSERT INTO empleados (legajo, apellido, nombre, dni, genero, telefono, email, direccion,
                           puesto_id, centro_costo_id, estado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()

def eliminar_empleado(id):
    c.execute("DELETE FROM empleados WHERE id = ?", (id,))
    conn.commit()

def editar_empleado(datos):
    c.execute("""
    UPDATE empleados
    SET legajo = ?, apellido = ?, nombre = ?, dni = ?, genero = ?, telefono = ?, email = ?,
        direccion = ?, puesto_id = ?, centro_costo_id = ?, estado = ?
    WHERE id = ?
    """, datos)
    conn.commit()

# --- Formularios desplegables ---
if "mostrar_formulario" not in st.session_state:
    st.session_state["mostrar_formulario"] = False

with st.expander("➕ Agregar nuevo empleado", expanded=st.session_state["mostrar_formulario"]):
    with st.form("form_agregar"):
        col1, col2, col3 = st.columns(3)
        with col1:
            legajo = st.text_input("Legajo")
            apellido = st.text_input("Apellido")
            nombre = st.text_input("Nombre")
            dni = st.text_input("DNI")
        with col2:
            genero = st.selectbox("Género", ["", "Femenino", "Masculino", "Otro"])
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            direccion = st.text_input("Dirección")
        with col3:
            puestos_df = pd.read_sql_query("SELECT id, nombre FROM puestos", conn)
            centros_df = pd.read_sql_query("SELECT id, nombre FROM centros_costo", conn)
            puesto_id = st.selectbox("Puesto", [""] + puestos_df["nombre"].tolist())
            centro_id = st.selectbox("Centro de Costo", [""] + centros_df["nombre"].tolist())
            estado = st.selectbox("Estado", ["", "Activo", "Inactivo"])
        submitted = st.form_submit_button("Agregar Empleado")
        if submitted:
            if not all([legajo, apellido, nombre, dni, genero, estado]):
                st.error("Completa los campos obligatorios.")
            else:
                puesto_idx = puestos_df[puestos_df["nombre"] == puesto_id]["id"].values
                centro_idx = centros_df[centros_df["nombre"] == centro_id]["id"].values
                agregar_empleado((
                    legajo, apellido, nombre, dni, genero, telefono, email, direccion,
                    int(puesto_idx[0]) if len(puesto_idx) > 0 else None,
                    int(centro_idx[0]) if len(centro_idx) > 0 else None,
                    estado
                ))
                st.success("Empleado agregado correctamente.")

# --- Filtros ---
with st.expander("🔍 Filtros"):
    filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "Activo", "Inactivo"])
    filtro_centro = st.selectbox("Filtrar por Centro de Costo", ["Todos"] + centros_df["nombre"].tolist())
    busqueda = st.text_input("Buscar por Nombre, Apellido, Legajo, DNI, Email, Teléfono")

# --- Mostrar empleados ---
df = obtener_empleados()

if filtro_estado != "Todos":
    df = df[df["estado"] == filtro_estado]

if filtro_centro != "Todos":
    df = df[df["centro_costo"] == filtro_centro]

if busqueda:
    mask = df.apply(lambda row: busqueda.lower() in str(row).lower(), axis=1)
    df = df[mask]

st.dataframe(df, use_container_width=True)

# --- Editar / Eliminar ---
with st.expander("✏️ Editar o Eliminar Empleado"):
    id_editar = st.number_input("ID del empleado a editar/eliminar", min_value=1, step=1)
    accion = st.selectbox("Acción", ["Selecciona", "Editar", "Eliminar"])
    if accion == "Editar":
        empleado = df[df["id"] == id_editar]
        if not empleado.empty:
            with st.form("form_editar"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    legajo = st.text_input("Legajo", empleado["legajo"].values[0])
                    apellido = st.text_input("Apellido", empleado["apellido"].values[0])
                    nombre = st.text_input("Nombre", empleado["nombre"].values[0])
                    dni = st.text_input("DNI", empleado["dni"].values[0])
                with col2:
                    genero = st.selectbox("Género", ["Femenino", "Masculino", "Otro"], index=["Femenino", "Masculino", "Otro"].index(empleado["genero"].values[0]) if empleado["genero"].values[0] in ["Femenino", "Masculino", "Otro"] else 0)
                    telefono = st.text_input("Teléfono", empleado["telefono"].values[0])
                    email = st.text_input("Email", empleado["email"].values[0])
                    direccion = st.text_input("Dirección", empleado["direccion"].values[0])
                with col3:
                    puesto_id = st.selectbox("Puesto", puestos_df["nombre"].tolist(), index=list(puestos_df["nombre"]).index(empleado["puesto"].values[0]) if empleado["puesto"].values[0] in list(puestos_df["nombre"]) else 0)
                    centro_id = st.selectbox("Centro de Costo", centros_df["nombre"].tolist(), index=list(centros_df["nombre"]).index(empleado["centro_costo"].values[0]) if empleado["centro_costo"].values[0] in list(centros_df["nombre"]) else 0)
                    estado = st.selectbox("Estado", ["Activo", "Inactivo"], index=["Activo", "Inactivo"].index(empleado["estado"].values[0]) if empleado["estado"].values[0] in ["Activo", "Inactivo"] else 0)
                submitted = st.form_submit_button("Guardar Cambios")
                if submitted:
                    puesto_idx = puestos_df[puestos_df["nombre"] == puesto_id]["id"].values
                    centro_idx = centros_df[centros_df["nombre"] == centro_id]["id"].values
                    editar_empleado((
                        legajo, apellido, nombre, dni, genero, telefono, email, direccion,
                        int(puesto_idx[0]) if len(puesto_idx) > 0 else None,
                        int(centro_idx[0]) if len(centro_idx) > 0 else None,
                        estado,
                        int(id_editar)
                    ))
                    st.success("Empleado editado correctamente.")
        else:
            st.warning("ID no encontrado.")
    elif accion == "Eliminar":
        if st.button("Eliminar Empleado"):
            eliminar_empleado(int(id_editar))
            st.success("Empleado eliminado correctamente.")
