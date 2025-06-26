import streamlit as st
from models import Base, Empleado, Licencia, Puesto, Usuario, CentroCosto, Busqueda, Postulante, EstadoSeleccion
import pandas as pd
from sqlalchemy.orm import joinedload
import networkx as nx
import matplotlib.pyplot as plt
import tempfile
import os
import textwrap
from datetime import date
from models import CuentaEmpresa
from main import get_engine_for_user, SessionGlobal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import inicializar_base_cliente  # Asegurate de importar esta función
import matplotlib.pyplot as plt
import uuid
import os

# Crear carpeta si no existe
if not os.path.exists("archivos_cv"):
    os.makedirs("archivos_cv")
#from openai import OpenAI
#client = OpenAI(api_key="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")
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
temp_engine = create_engine("sqlite:///./rrhh.db", connect_args={"check_same_thread": False})
SessionTemp = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

def autenticar_usuario(username, password):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models import CuentaEmpresa

    engine_global = create_engine("sqlite:///./cuentas.db", connect_args={"check_same_thread": False})
    SessionGlobal = sessionmaker(autocommit=False, autoflush=False, bind=engine_global)
    db = SessionGlobal()
    cuenta = db.query(CuentaEmpresa).filter_by(usuario=username, password=password).first()
    db.close()
    if cuenta:
        return cuenta
    else:
        return None

def inicializar_base_de_datos():
    try:
        # Crea las tablas si no existen
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Crear base temporal solo para definir tablas en rrhh.db (por compatibilidad)
        temp_engine = create_engine("sqlite:///./rrhh.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=temp_engine)
        SessionTemp = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
        db = SessionTemp()

        # Verifica si el usuario admin ya existe
        if not db.query(Usuario).filter_by(username="admin").first():
            admin = Usuario(username="admin", password="admin123", rol="admin")
            db.add(admin)
            db.commit()
            print("✅ Usuario admin creado correctamente.")
        else:
            print("ℹ️ Usuario admin ya existe.")
        db.close()
    except Exception as e:
        print("⚠️ Error al inicializar la base de datos:", e)

inicializar_base_de_datos()
def crear_base_y_usuario_admin():
    db = SessionTemp()
    try:
        # Intenta consultar usuarios. Si falla, la tabla no existe
        db.query(Usuario).all()
    except:
        # Si no existe la tabla, la crea
        Usuario.metadata.create_all(bind=db.bind)

    existente = db.query(Usuario).filter_by(username="admin").first()
    if not existente:
        nuevo = Usuario(username="admin", password="admin123", rol="admin")
        db.add(nuevo)
        db.commit()
        print("✅ Usuario 'admin' creado automáticamente.")
    db.close()
crear_base_y_usuario_admin()

def obtener_usuarios():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    db.close()
    return usuarios

st.set_page_config(page_title="RRHH", layout="wide")

def agregar_columna_busqueda_si_falta(engine):
    with engine.connect() as connection:
        try:
            connection.execute("ALTER TABLE postulantes ADD COLUMN busqueda_id INTEGER;")
            print("✅ Columna 'busqueda_id' agregada a la tabla 'postulantes'.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ La columna 'busqueda_id' ya existía.")
            elif "no such table" in str(e).lower():
                print("ℹ️ La tabla 'postulantes' aún no existe.")
            else:
                print("❌ Error al agregar columna:", e)

def iniciar_sesion():
    st.header("🔐 Iniciar sesión")  # se ve solo en login
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        cuenta = autenticar_usuario(username, password)
        if cuenta:
            engine, nueva_sesion = get_engine_for_user(cuenta.base_datos)
            st.session_state["engine"] = engine
            st.session_state["SessionLocal"] = nueva_sesion
            inicializar_base_cliente(engine)
            st.session_state["usuario"] = {
                "username": cuenta.usuario,
                "rol": "admin"
            }
            st.success("Sesión iniciada correctamente")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

def cerrar_sesion():
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.pop("usuario", None)
        st.rerun()

# 🔐 Control de sesión
if "usuario" not in st.session_state:
    iniciar_sesion()
    st.stop()  # NO continúa ejecutando el resto del sistema si no hay login

# ✅ Si hay usuario, ahora sí mostramos todo el sistema
usuario_actual = st.session_state["usuario"]
st.sidebar.markdown(f"👤 Usuario: **{usuario_actual['username']}** ({usuario_actual['rol']})")
cerrar_sesion()

# Agregá esta función acá arriba:
def generar_reporte_empleados_pdf(empleados):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Reporte de Empleados")
    y -= 30
    c.setFont("Helvetica", 10)

    for emp in empleados:
        texto = f"{emp.apellido}, {emp.nombre} | DNI: {emp.dni} | Puesto: {emp.puesto} | Estado: {emp.estado}"
        c.drawString(50, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return temp.name

def generar_formulario_pdf(nombre_archivo, contenido):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import tempfile

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter

    # Configurar texto
    x = 50
    y = height - 50
    c.setFont("Helvetica", 11)

    # Envolver texto en líneas
    for linea in contenido.strip().split("\n"):
        lineas_envueltas = textwrap.wrap(linea, width=90)  # ajustá el width si querés más o menos palabras por línea
        for sublinea in lineas_envueltas:
            c.drawString(x, y, sublinea)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

    c.save()
    return temp.name

#def responder_mensaje(mensajes):
    #respuesta = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        #messages=mensajes,
        #temperature=0.7,
        #max_tokens=300
    #)
    #return respuesta.choices[0].message.content

# ======================== FUNCIONES BASE DE DATOS ==========================
def obtener_empleados():
    db = st.session_state["SessionLocal"]()
    empleados = db.query(Empleado).all()
    db.close()
    return empleados

def obtener_licencias():
    db = st.session_state["SessionLocal"]()
    licencias = db.query(Licencia).options(joinedload(Licencia.empleado)).all()
    db.close()
    return licencias

def obtener_puestos():
    db = st.session_state["SessionLocal"]()
    puestos = db.query(Puesto).all()
    db.close()
    return puestos

def agregar_empleado(**kwargs):
    db = st.session_state["SessionLocal"]()
    nuevo = Empleado(**kwargs)
    db.add(nuevo)
    db.commit()
    db.close()

def editar_empleado(empleado_id, **kwargs):
    db = st.session_state["SessionLocal"]()
    empleado = db.query(Empleado).filter_by(id=empleado_id).first()
    for key, value in kwargs.items():
        setattr(empleado, key, value)
    db.commit()
    db.close()

def eliminar_empleado(empleado_id):
    db = st.session_state["SessionLocal"]()
    empleado = db.query(Empleado).filter_by(id=empleado_id).first()
    if empleado:
        db.delete(empleado)
        db.commit()
    db.close()

def agregar_licencia(empleado_id, tipo, fecha_inicio, fecha_fin, observaciones):
    db = st.session_state["SessionLocal"]()
    nueva = Licencia(
        empleado_id=empleado_id,
        tipo=tipo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        observaciones=observaciones
    )
    db.add(nueva)
    db.commit()
    db.close()

def editar_licencia(licencia_id, tipo, fecha_inicio, fecha_fin, observaciones):
    db = st.session_state["SessionLocal"]()
    licencia = db.query(Licencia).filter_by(id=licencia_id).first()
    if licencia:
        licencia.tipo = tipo
        licencia.fecha_inicio = fecha_inicio
        licencia.fecha_fin = fecha_fin
        licencia.observaciones = observaciones
        db.commit()
    db.close()

def eliminar_licencia(licencia_id):
    db = st.session_state["SessionLocal"]()
    licencia = db.query(Licencia).filter_by(id=licencia_id).first()
    if licencia:
        db.delete(licencia)
        db.commit()
    db.close()

def agregar_puesto(nombre, descripcion, jefe_id=None):
    db = st.session_state["SessionLocal"]()
    nuevo = Puesto(nombre=nombre, descripcion=descripcion, jefe_id=jefe_id)
    db.add(nuevo)
    db.commit()
    db.close()

def editar_puesto(puesto_id, nombre, descripcion, jefe_id):
    db = st.session_state["SessionLocal"]()
    puesto = db.query(Puesto).filter_by(id=puesto_id).first()
    if puesto:
        puesto.nombre = nombre
        puesto.descripcion = descripcion
        puesto.jefe_id = jefe_id
        db.commit()
    db.close()

def eliminar_puesto(puesto_id):
    db = st.session_state["SessionLocal"]()
    puesto = db.query(Puesto).filter_by(id=puesto_id).first()
    if puesto:
        db.delete(puesto)
        db.commit()
    db.close()

def obtener_centros_costo():
    db = st.session_state["SessionLocal"]()
    centros = db.query(CentroCosto).all()
    db.close()
    return centros

def agregar_centro_costo(nombre):
    db = st.session_state["SessionLocal"]()
    nuevo = CentroCosto(nombre=nombre)
    db.add(nuevo)
    db.commit()
    db.close()

# ========================= INTERFAZ STREAMLIT =============================
st.sidebar.title("RRHH")

menu_principal = st.sidebar.radio("Menú", ["Inicio", "Gestión Nómina", "Formularios", "Reclutamiento", "Asesoramiento", "Simulador"])

if menu_principal == "Inicio":
    st.empty()
    with st.container():
        st.markdown("<style>.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True)
        st.title("🏠 Bienvenido al sistema RRHH")
        st.markdown("Accedé a las funciones del sistema desde el menú lateral.")
        st.markdown("---")

        st.title("🏠 Dashboard de RRHH")

        empleados = obtener_empleados()
        licencias = obtener_licencias()
        puestos = obtener_puestos()

        total_empleados = len(empleados)
        activos = sum(1 for e in empleados if e.estado == "Activo")
        inactivos = total_empleados - activos
        total_licencias = len(licencias)
        total_puestos = len(puestos)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Empleados activos", activos)
        col2.metric("🛌 Licencias registradas", total_licencias)
        col3.metric("🏷️ Puestos definidos", total_puestos)

        st.markdown("---")
        st.markdown("Usá el menú lateral para navegar por las funcionalidades.")
    
if menu_principal == "Gestión Nómina":
    seccion = st.sidebar.radio("Administración del Personal", ["Empleados", "Licencias", "Puestos", "Centro de Costo", "Organigrama"])
    if seccion == "Empleados":
        st.empty()
        st.title("👥 Gestión de Empleados")
        empleados = obtener_empleados()
        puestos = obtener_puestos()

        # Filtros visuales
        with st.container():
            st.subheader("🔍 Filtros")
            col1, col2, col3 = st.columns(3)

            opciones_estado = ["Todos"] + sorted(list(set(e.estado for e in empleados)))
            opciones_cc = ["Todos"] + sorted(list(set(e.centro_costo for e in empleados)))
            opciones_puesto = ["Todos"] + sorted(list(set(e.puesto for e in empleados)))

            with col1:
                filtro_estado = st.selectbox("Estado", opciones_estado, index=0)
            with col2:
                filtro_centro_costo = st.selectbox("Centro de Costo", opciones_cc, index=0)
            with col3:
                filtro_puesto = st.selectbox("Puesto", opciones_puesto, index=0)

        # Aplicar filtros
        empleados_filtrados = empleados
        if filtro_estado != "Todos":
            empleados_filtrados = [e for e in empleados_filtrados if e.estado == filtro_estado]
        if filtro_centro_costo != "Todos":
            empleados_filtrados = [e for e in empleados_filtrados if e.centro_costo == filtro_centro_costo]
        if filtro_puesto != "Todos":
            empleados_filtrados = [e for e in empleados_filtrados if e.puesto == filtro_puesto]
            

        df = pd.DataFrame([{k: getattr(e, k) for k in [
            "apellido", "nombre", "legajo", "genero", "estado_civil", "fecha_nacimiento",
            "dni", "direccion", "telefono", "centro_costo", "puesto",
            "remuneracion_bruta", "estado", "fecha_alta", "fecha_baja"
        ]} for e in empleados_filtrados])
        st.dataframe(df, use_container_width=True)

        if st.button("📄 Descargar PDF de empleados filtrados"):
            if empleados_filtrados:
                path_pdf = generar_reporte_empleados_pdf(empleados_filtrados)
                with open(path_pdf, "rb") as file:
                    st.download_button(
                        label="Descargar PDF",
                        data=file,
                        file_name="reporte_empleados_filtrados.pdf",
                        mime="application/pdf"
                    )
                os.remove(path_pdf)
            else:
                st.warning("No hay empleados filtrados para incluir en el PDF.")
        with st.expander("➕ Agregar nuevo empleado"):
            datos = {}
            datos["apellido"] = st.text_input("Apellido", key="nuevo_apellido")
            datos["nombre"] = st.text_input("Nombre", key="nuevo_nombre")
            datos["legajo"] = st.text_input("Legajo", key="nuevo_legajo")
            datos["genero"] = st.selectbox("Género", ["Masculino", "Femenino", "Otro"], key="nuevo_genero")
            datos["estado_civil"] = st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Otro"], key="nuevo_estado_civil")
            datos["fecha_nacimiento"] = str(
                st.date_input("Fecha de Nacimiento", min_value=date(1950, 1, 1), max_value=date.today(), key="nuevo_fecha_nacimiento")
            )
            datos["dni"] = st.text_input("DNI", key="nuevo_dni")
            datos["direccion"] = st.text_input("Dirección", key="nuevo_direccion")
            datos["telefono"] = st.text_input("Teléfono", key="nuevo_telefono")
            centros = obtener_centros_costo()
            datos["centro_costo"] = st.selectbox("Centro de Costo", [c.nombre for c in centros], key="nuevo_centro_costo")
            datos["puesto"] = st.selectbox("Puesto", [p.nombre for p in puestos], key="nuevo_puesto")
            datos["remuneracion_bruta"] = st.number_input("Remuneración Bruta", min_value=0, key="nuevo_remuneracion")
            datos["estado"] = st.selectbox("Estado", ["Activo", "Inactivo"], key="nuevo_estado")
            datos["fecha_alta"] = str(st.date_input("Fecha de Alta", key="nuevo_fecha_alta"))
            datos["fecha_baja"] = ""
            opciones_jefes = {"Ninguno": None}
            for p in puestos:
                opciones_jefes[p.nombre] = p.id
            jefe_nombre = st.selectbox("Puesto superior", list(opciones_jefes.keys()), key="nuevo_jefe")
            datos["jefe_id"] = opciones_jefes[jefe_nombre]

            if st.button("Agregar empleado"):
                agregar_empleado(**datos)
                st.success("Empleado agregado correctamente.")

        with st.expander("✏️ Editar empleado"):
            if empleados:
                opciones = {f"{e.id} - {e.apellido}, {e.nombre}": e.id for e in empleados}
                seleccionado = st.selectbox("Seleccionar empleado", list(opciones.keys()), key="editar_empleado")
                eid = opciones[seleccionado]
                emp = next(e for e in empleados if e.id == eid)
                centros = obtener_centros_costo()
                nombres_centros = [c.nombre for c in centros]
                if emp.centro_costo in nombres_centros:
                    idx_cc = nombres_centros.index(emp.centro_costo)
                else:
                    nombres_centros.insert(0, emp.centro_costo or "Sin asignar")
                    idx_cc = 0

                datos = {
                    "apellido": st.text_input("Apellido", value=emp.apellido, key=f"edit_apellido_{eid}"),
                    "nombre": st.text_input("Nombre", value=emp.nombre, key=f"edit_nombre_{eid}"),
                    "legajo": st.text_input("Legajo", value=emp.legajo, key=f"edit_legajo_{eid}"),
                    "genero": st.selectbox("Género", ["Masculino", "Femenino", "Otro"], index=["Masculino", "Femenino", "Otro"].index(emp.genero), key=f"edit_genero_{eid}"),
                    "estado_civil": st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Otro"], index=["Soltero/a", "Casado/a", "Divorciado/a", "Otro"].index(emp.estado_civil), key=f"edit_estado_civil_{eid}"),
                    "fecha_nacimiento": str(
                        st.date_input(
                            "Fecha de Nacimiento",
                            value=pd.to_datetime(emp.fecha_nacimiento),
                            min_value=date(1950, 1, 1),
                            max_value=date.today(),
                            key=f"edit_fecha_nac_{eid}"
                        )
                    ),
                    "dni": st.text_input("DNI", value=emp.dni, key=f"edit_dni_{eid}"),
                    "direccion": st.text_input("Dirección", value=emp.direccion, key=f"edit_direccion_{eid}"),
                    "telefono": st.text_input("Teléfono", value=emp.telefono, key=f"edit_telefono_{eid}"),
                    "centro_costo": st.selectbox(
                        "Centro de Costo",
                        nombres_centros,
                        index=idx_cc,
                        key=f"edit_cc_{eid}"
                    ),
                    "puesto": st.text_input("Puesto", value=emp.puesto, key=f"edit_puesto_{eid}"),
                    "remuneracion_bruta": st.number_input("Remuneración Bruta", value=emp.remuneracion_bruta, min_value=0, key=f"edit_remu_{eid}"),
                    "estado": st.selectbox("Estado", ["Activo", "Inactivo"], index=0 if emp.estado == "Activo" else 1, key=f"edit_estado_{eid}"),
                    "fecha_alta": str(st.date_input("Fecha de Alta", value=pd.to_datetime(emp.fecha_alta), key=f"edit_fecha_alta_{eid}")),
                    "fecha_baja": str(emp.fecha_baja) if emp.fecha_baja else "",
                }

                opciones_jefes = {"Ninguno": None}
                for p in puestos:
                    opciones_jefes[p.nombre] = p.id

                jefe_valor = next((k for k, v in opciones_jefes.items() if v == emp.jefe_id), "Ninguno")
                jefe_nombre = st.selectbox("Puesto superior", list(opciones_jefes.keys()), index=list(opciones_jefes.keys()).index(jefe_valor), key=f"edit_jefe_{eid}")
                datos["jefe_id"] = opciones_jefes[jefe_nombre]
                

                if st.button("Guardar cambios", key=f"btn_guardar_{eid}"):
                    editar_empleado(eid, **datos)
                    st.success("Empleado actualizado")
                else:
                    st.info("No hay empleados para editar.")

        with st.expander("🗑️ Eliminar empleado"):
            if empleados:
                opciones = {f"{e.id} - {e.apellido}, {e.nombre}": e.id for e in empleados}
                seleccionado = st.selectbox("Seleccionar empleado", list(opciones.keys()), key="eliminar_empleado")
                eid = opciones[seleccionado]
                if st.button("Eliminar empleado"):
                    eliminar_empleado(eid)
                    st.success("Empleado eliminado")
            else:
                st.info("No hay empleados para eliminar.")
    
    elif seccion == "Licencias":
        st.empty()
        st.title("📅 Registro de Licencias")
        licencias = obtener_licencias()
        empleados = obtener_empleados()

        data = [
            {
                "ID": l.id,
                "Empleado": f"{l.empleado.apellido}, {l.empleado.nombre}" if l.empleado else "-",
                "Tipo": l.tipo,
                "Desde": l.fecha_inicio,
                "Hasta": l.fecha_fin,
                "Observaciones": l.observaciones
            } for l in licencias
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True)

        with st.expander("➕ Agregar licencia"):
            opciones = {f"{e.apellido}, {e.nombre}": e.id for e in empleados}
            seleccionado = st.selectbox("Empleado", list(opciones.keys()), key="lic_nueva")
            tipo = st.text_input("Tipo de licencia")
            desde = st.date_input("Desde")
            hasta = st.date_input("Hasta")
            observaciones = st.text_area("Observaciones")
            if st.button("Guardar licencia"):
                agregar_licencia(opciones[seleccionado], tipo, str(desde), str(hasta), observaciones)
                st.success("Licencia registrada")

        with st.expander("✏️ Editar licencia"):
            if licencias:
                opciones = {f"{l.id} - {l.tipo} ({l.empleado.nombre if l.empleado else 'Sin asignar'})": l.id for l in licencias}
                seleccion = st.selectbox("Seleccionar licencia", list(opciones.keys()), key="lic_edit")
                lid = opciones[seleccion]
                lic = next(l for l in licencias if l.id == lid)

                tipo_edit = st.text_input("Tipo", value=lic.tipo)
                desde_edit = st.date_input("Desde", value=pd.to_datetime(lic.fecha_inicio))
                hasta_edit = st.date_input("Hasta", value=pd.to_datetime(lic.fecha_fin))
                obs_edit = st.text_area("Observaciones", value=lic.observaciones)

                if st.button("Guardar cambios licencia"):
                    editar_licencia(lid, tipo_edit, str(desde_edit), str(hasta_edit), obs_edit)
                    st.success("Licencia actualizada")
            else:
                st.info("No hay licencias para editar.")

        with st.expander("🗑️ Eliminar licencia"):
            if licencias:
                opciones = {f"{l.id} - {l.tipo} ({l.empleado.nombre if l.empleado else 'Sin asignar'})": l.id for l in licencias}
                seleccion = st.selectbox("Seleccionar licencia", list(opciones.keys()), key="lic_eliminar")
                if st.button("Eliminar licencia"):
                    eliminar_licencia(opciones[seleccion])
                    st.success("Licencia eliminada")
            else:
                st.info("No hay licencias registradas.")


    elif seccion == "Puestos":
        st.empty()
        st.title("🏷️ Gestión de Puestos")
        puestos = obtener_puestos()
        df = pd.DataFrame([p.__dict__ for p in puestos]).drop(columns=["_sa_instance_state"], errors='ignore')
        st.dataframe(df, use_container_width=True)

        with st.expander("➕ Crear nuevo puesto"):
            nombre = st.text_input("Nombre del puesto")
            descripcion = st.text_area("Descripción")
            opciones_jefes = {"Sin jefe": None}
            for p in puestos:
                opciones_jefes[p.nombre] = p.id
            jefe_nombre = st.selectbox("Depende de", list(opciones_jefes.keys()))
            if st.button("Guardar puesto"):
                agregar_puesto(nombre, descripcion, opciones_jefes[jefe_nombre])
                st.success("Puesto creado")

        with st.expander("✏️ Editar puesto"):
            if puestos:
                opciones = {f"{p.id} - {p.nombre}": p.id for p in puestos}
                seleccionado = st.selectbox("Seleccionar puesto", list(opciones.keys()), key="editar_puesto")
                pid = int(seleccionado.split(" - ")[0])
                puesto = next(p for p in puestos if p.id == pid)

                nuevo_nombre = st.text_input("Nuevo nombre", value=puesto.nombre, key="nuevo_nombre_puesto")
                nueva_desc = st.text_area("Nueva descripción", value=puesto.descripcion, key="nueva_desc_puesto")
                opciones_jefes = {"Sin jefe": None}
                for p in puestos:
                    if p.id != puesto.id:
                        opciones_jefes[p.nombre] = p.id
                jefe_actual = next((k for k, v in opciones_jefes.items() if v == puesto.jefe_id), "Sin jefe")
                nuevo_jefe = st.selectbox("Nuevo superior", list(opciones_jefes.keys()), index=list(opciones_jefes.keys()).index(jefe_actual), key="nuevo_jefe_puesto")

                if st.button("Guardar cambios puesto"):
                    editar_puesto(pid, nuevo_nombre, nueva_desc, opciones_jefes[nuevo_jefe])
                    st.success("Puesto actualizado")

        with st.expander("🗑️ Eliminar puesto"):
            if puestos:
                opciones = {f"{p.id} - {p.nombre}": p.id for p in puestos}
                seleccionado = st.selectbox("Puesto a eliminar", list(opciones.keys()), key="eliminar_puesto")
                if seleccionado:
                    pid = int(seleccionado.split(" - ")[0])
                    if st.button("Eliminar puesto"):
                        eliminar_puesto(pid)
                        st.success("Puesto eliminado")
            else:
                st.info("No hay puestos registrados.")
    
    elif seccion == "Centro de Costo":
        st.empty()
        st.title("🏢 Gestión de Centros de Costo")
        centros = obtener_centros_costo()
        df = pd.DataFrame([{"ID": c.id, "Nombre": c.nombre} for c in centros])
        st.dataframe(df, use_container_width=True)

        with st.expander("➕ Crear nuevo centro de costo"):
            nombre_nuevo = st.text_input("Nombre del centro de costo", key="nuevo_cc")
            if st.button("Guardar centro de costo"):
                if nombre_nuevo.strip():
                    agregar_centro_costo(nombre_nuevo.strip())
                    st.success("Centro de costo creado correctamente.")
                    st.rerun()
                else:
                    st.warning("El nombre no puede estar vacío.")

        with st.expander("✏️ Editar centro de costo"):
            if centros:
                opciones = {f"{c.id} - {c.nombre}": c.id for c in centros}
                seleccionado = st.selectbox("Seleccionar centro", list(opciones.keys()), key="editar_cc")
                cc_id = opciones[seleccionado]
                actual = next((c for c in centros if c.id == cc_id), None)
                nuevo_nombre = st.text_input("Nuevo nombre", value=actual.nombre, key="nuevo_nombre_cc")

                if st.button("Guardar cambios", key="guardar_cambios_cc"):
                    db = st.session_state["SessionLocal"]()
                    centro = db.query(CentroCosto).filter_by(id=cc_id).first()
                    if centro:
                        centro.nombre = nuevo_nombre
                        db.commit()
                        db.close()
                        st.success("Centro de costo actualizado.")
                        st.rerun()
                    else:
                        db.close()
                        st.error("No se encontró el centro de costo.")

        with st.expander("🗑️ Eliminar centro de costo"):
            if centros:
                opciones = {f"{c.id} - {c.nombre}": c.id for c in centros}
                seleccionado = st.selectbox("Centro a eliminar", list(opciones.keys()), key="eliminar_cc")
                cc_id = opciones[seleccionado]
                centro_nombre = next(c.nombre for c in centros if c.id == cc_id)

                if st.button("Eliminar centro", key="btn_eliminar_cc"):
                    empleados = obtener_empleados()
                    en_uso = any(e.centro_costo == centro_nombre for e in empleados)

                    if en_uso:
                        st.warning("❌ No se puede eliminar este centro de costo porque está siendo utilizado por al menos un empleado.")
                    else:
                        db = st.session_state["SessionLocal"]()
                        centro = db.query(CentroCosto).filter_by(id=cc_id).first()
                        if centro:
                            db.delete(centro)
                            db.commit()
                            db.close()
                            st.success("Centro eliminado correctamente.")
                            st.rerun()
                        else:
                            db.close()
                            st.error("No se encontró el centro de costo.")
            else:
                st.info("No hay centros registrados.")

    elif seccion == "Organigrama":
        st.empty()
        st.title("🏢 Organigrama Jerárquico de Puestos")
        puestos = obtener_puestos()

        if puestos:
            G = nx.DiGraph()
            etiquetas = {}

            # Crear nodos y aristas
            for puesto in puestos:
                G.add_node(puesto.id)
                etiquetas[puesto.id] = puesto.nombre
                if puesto.jefe_id:
                    G.add_edge(puesto.jefe_id, puesto.id)

            # Calcular niveles jerárquicos
            niveles = {}
            def asignar_niveles(p, nivel=0):
                niveles[p.id] = nivel
                hijos = [x for x in puestos if x.jefe_id == p.id]
                for hijo in hijos:
                    asignar_niveles(hijo, nivel + 1)

            raices = [p for p in puestos if p.jefe_id is None]
            for raiz in raices:
                asignar_niveles(raiz)

            # Posicionar: mismo nivel → misma fila (mismo Y), separados horizontalmente (X)
            posiciones = {}
            x_counter = {}

            for nivel in sorted(set(niveles.values())):
                puestos_nivel = [pid for pid, lvl in niveles.items() if lvl == nivel]
                for idx, pid in enumerate(puestos_nivel):
                    posiciones[pid] = (idx, -nivel)

            # Dibujar el organigrama
            fig, ax = plt.subplots(figsize=(10, 6))
            nx.draw(
                G,
                pos=posiciones,
                labels=etiquetas,
                with_labels=True,
                node_color="lightblue",
                node_size=3000,
                font_size=10,
                font_weight='bold',
                edge_color="gray",
                ax=ax
            )
            st.pyplot(fig)
        else:
            st.info("No hay puestos cargados aún.")

if menu_principal == "Asesoramiento":
    st.empty()
    with st.container():
        st.markdown("<style>.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True)
        st.title("🧠 Asesoramiento para RRHH")
        st.markdown("Accedé a contenido de ayuda y buenas prácticas para la gestión de Recursos Humanos en tu organización.")

        st.subheader("📚 Guías y Buenas Prácticas")
        with st.expander("✅ Gestión de licencias y ausencias"):
            st.markdown("""
    - **Comunicación previa:** Siempre pedir al empleado que notifique la ausencia con la mayor anticipación posible.
    - **Documentación:** Requerir certificado médico o respaldo en casos de enfermedad.
    - **Registro en el sistema:** Cargar la licencia en el módulo correspondiente y actualizar el estado.
    - **Seguimiento:** Contactar al empleado si se extiende la ausencia.

    **Tip:** Usá el módulo “Licencias” para mantener trazabilidad completa.
    """)

        with st.expander("📄 Procedimiento de desvinculación responsable"):
            st.markdown("""
    - **Preaviso obligatorio:** Debe enviarse con la antelación legal (15 días mínimo).
    - **Generar documentación:** Usá el módulo Formularios → “Preaviso” y “Carta de despido”.
    - **Firma de recibos:** Documentar todo el proceso con recibos firmados.
    - **Certificados:** Emitir el Certificado de trabajo y asegurar liquidación final.

    **Consejo:** Comunicá con respeto y empatía, incluso en desvinculaciones disciplinarias.
    """)

        with st.expander("👥 Armado de organigramas y jerarquías"):
            st.markdown("""
    - **Claridad de roles:** Cada puesto debe tener un jefe definido (cuando aplique).
    - **Estructura jerárquica:** Revisar que los puestos se conecten adecuadamente en el organigrama.
    - **Actualización frecuente:** Al cambiar roles o estructura, actualizar el módulo “Puestos”.

    **Herramienta clave:** Usá el módulo “Organigrama” para visualizar dependencias jerárquicas.
    """)

        st.subheader("🔗 Recursos útiles")
        st.markdown("""
    - [Ley de Contrato de Trabajo (Argentina)](https://www.argentina.gob.ar/normativa/nacional/ley-20744-2668)
    - [AFIP – Manual empleadores](https://www.afip.gob.ar/empleadores/)
    - [Ministerio de Trabajo](https://www.argentina.gob.ar/trabajo)
    """)
        #st.markdown("Podés conversar con el asistente para resolver dudas de gestión de RRHH.")

        #if "chat" not in st.session_state:
            #st.session_state.chat = [
                #{"role": "system", "content": "Sos un asistente especializado en Recursos Humanos para PYMEs argentinas. Respondé en español con ejemplos claros."}
            #]

        # Mostrar el historial
        #for m in st.session_state.chat[1:]:
            #if m["role"] == "user":
                #st.markdown(f"**👤 Usuario:** {m['content']}")
            #else:
                #st.markdown(f"**🤖 Asistente:** {m['content']}")

        # Ingreso de nuevo mensaje
        #pregunta = st.text_input("Escribí tu consulta:", key="input_usuario")
        #if st.button("Enviar"):
            #if pregunta:
                #st.session_state.chat.append({"role": "user", "content": pregunta})
                #respuesta = responder_mensaje(st.session_state.chat)
                #st.session_state.chat.append({"role": "assistant", "content": respuesta})
                    #st.rerun()

if menu_principal == "Formularios":
    st.empty()
    with st.container():
        st.markdown("<style>.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True)
        st.title("📑 Formularios RRHH")
        formulario = st.sidebar.radio("Seleccioná un formulario", [
            "Carta de despido",
            "Certificado de trabajo",
            "Comunicación de vacaciones",
            "Notificación de sanción",
            "Preaviso"
        ])

        if formulario == "Carta de despido":
            st.subheader("📄 Carta de despido")
            nombre = st.text_input("Nombre del empleado")
            dni = st.text_input("DNI")
            fecha = st.date_input("Fecha")
            motivo = st.text_area("Motivo del despido")

            if st.button("Generar carta"):
                contenido = f"""
    [CARTA DE DESPIDO]

    A la fecha {fecha}, notificamos al Sr./Sra. {nombre}, DNI {dni}, su desvinculación de la empresa por el siguiente motivo:

    {motivo}

    Saludos cordiales,

    Firma
    Empresa
    """
                st.success("Carta generada:")
                st.code(contenido)

                path = generar_formulario_pdf("carta_despido", contenido)
                with open(path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="carta_despido.pdf", mime="application/pdf")

        elif formulario == "Certificado de trabajo":
            st.subheader("📄 Certificado de trabajo")
            nombre = st.text_input("Nombre del empleado")
            fecha_ingreso = st.date_input("Fecha de ingreso")
            fecha_egreso = st.date_input("Fecha de egreso")
            puesto = st.text_input("Puesto desempeñado")

            if st.button("Generar certificado"):
                contenido = f"""
    [CERTIFICADO DE TRABAJO]

    Se deja constancia que el Sr./Sra. {nombre} trabajó en esta empresa desde el {fecha_ingreso} hasta el {fecha_egreso}, desempeñándose en el puesto de {puesto}.

    Firma
    Empresa
    """
                st.success("Certificado generado:")
                st.code(contenido)

                path = generar_formulario_pdf("certificado_trabajo", contenido)
                with open(path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="certificado_trabajo.pdf", mime="application/pdf")

        elif formulario == "Comunicación de vacaciones":
            st.subheader("📝 Comunicación de vacaciones")
            nombre = st.text_input("Nombre del empleado")
            desde = st.date_input("Desde")
            hasta = st.date_input("Hasta")

            if st.button("Generar comunicación"):
                contenido = f"""
    [COMUNICACIÓN DE VACACIONES]

    Se informa al Sr./Sra. {nombre} que se le otorgarán vacaciones desde el día {desde} hasta el {hasta}, inclusive.

    Saludos cordiales,

    Firma
    Empresa
    """
                st.success("Comunicación generada:")
                st.code(contenido)

                path = generar_formulario_pdf("comunicacion_vacaciones", contenido)
                with open(path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="comunicacion_vacaciones.pdf", mime="application/pdf")

        elif formulario == "Notificación de sanción":
            st.subheader("📋 Notificación de sanción")
            nombre = st.text_input("Nombre del empleado")
            motivo = st.text_area("Motivo de la sanción")
            fecha = st.date_input("Fecha de notificación")

            if st.button("Generar notificación"):
                contenido = f"""
    [NOTIFICACIÓN DE SANCIÓN]

    Por medio de la presente se informa al Sr./Sra. {nombre} que se le aplica una sanción disciplinaria con fecha {fecha}, por el siguiente motivo:

    {motivo}

    Firma
    Empresa
    """
                st.success("Notificación generada:")
                st.code(contenido)

                path = generar_formulario_pdf("notificacion_sancion", contenido)
                with open(path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="notificacion_sancion.pdf", mime="application/pdf")

        elif formulario == "Preaviso":
            st.subheader("📃 Preaviso")
            nombre = st.text_input("Nombre del empleado")
            fecha = st.date_input("Fecha")
            motivo = st.text_area("Motivo del preaviso")

            if st.button("Generar preaviso"):
                contenido = f"""
    [PREAVISO DE DESVINCULACIÓN]

    En fecha {fecha} se notifica al Sr./Sra. {nombre} el preaviso correspondiente por:

    {motivo}

    Firma
    Empresa
    """
                st.success("Preaviso generado:")
                st.code(contenido)

                path = generar_formulario_pdf("preaviso", contenido)
                with open(path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="preaviso.pdf", mime="application/pdf")

def crear_cuentas_de_prueba():
    engine_global = create_engine("sqlite:///./cuentas.db", connect_args={"check_same_thread": False})
    SessionGlobal = sessionmaker(autocommit=False, autoflush=False, bind=engine_global)

    Base.metadata.create_all(bind=engine_global)

    db = SessionGlobal()
    if not db.query(CuentaEmpresa).filter_by(usuario="empresa1").first():
        db.add(CuentaEmpresa(nombre_empresa="Empresa Uno", usuario="empresa1", password="123", base_datos="empresa1.db"))
    if not db.query(CuentaEmpresa).filter_by(usuario="empresa2").first():
        db.add(CuentaEmpresa(nombre_empresa="Empresa Dos", usuario="empresa2", password="123", base_datos="empresa2.db"))
    db.commit()
    db.close()

crear_cuentas_de_prueba()

if menu_principal == "Simulador":
    st.empty()
    with st.container():
        st.markdown("<style>.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True)
        import pandas as pd
        st.title("🧠 Simulador de Situaciones Laborales")
        st.markdown("Estas son situaciones reales que pueden surgir en una PyME. Elegí una categoría y una situación, y hacé clic en 'Generar respuestas' para ver cómo actuar.")

        try:
            df = pd.read_csv("Simulador_de_Situaciones_PYME.csv")

            # Limpiar espacios invisibles
            df["Categoría"] = df["Categoría"].astype(str).str.strip().str.replace("\n", "").str.replace("\r", "")
            df["Situación"] = df["Situación"].astype(str).str.strip().str.replace("\n", "").str.replace("\r", "")
            df = df.drop_duplicates(subset=["Categoría", "Situación"])

            # Selección de categoría y situación
            categorias = sorted(df["Categoría"].unique())
            categoria_seleccionada = st.selectbox("Seleccioná una categoría", categorias)

            df_filtrado = df[df["Categoría"] == categoria_seleccionada]
            situaciones = sorted(df_filtrado["Situación"].unique())
            situacion_seleccionada = st.selectbox("Seleccioná una situación", situaciones)

            # Botón para generar respuestas
            if st.button("🔄 Generar respuestas"):
                fila = df_filtrado[df_filtrado["Situación"] == situacion_seleccionada]

                if not fila.empty:
                    st.markdown("### 💡 Posibles respuestas:")
                    for i in range(1, 4):
                        st.markdown(f"**Respuesta {i}:** {fila.iloc[0][f'Respuesta {i}']}")
                else:
                    st.warning("No se encontró la situación seleccionada.")

        except Exception as e:
            st.error("No se pudo cargar el simulador. Verificá que el archivo esté correcto.")
            st.exception(e)

def mostrar_reclutamiento():
    st.title("📋 Módulo de Reclutamiento")
    opcion = st.radio("Seleccionar sección", ["Búsquedas abiertas", "Postulantes"])

    if opcion == "Búsquedas abiertas":
        mostrar_busquedas()
    elif opcion == "Postulantes":
        mostrar_postulantes()
def mostrar_busquedas():
    st.title("🔍 Gestión de Búsquedas Laborales")
    SessionLocal = st.session_state["SessionLocal"]
    db = SessionLocal()

    puestos = db.query(Puesto).all()
    opciones_puestos = {p.nombre: p.id for p in puestos}

    with st.form("form_busqueda"):
        nombre = st.text_input("Nombre de la búsqueda")
        puesto_nombre = st.selectbox("Puesto buscado", list(opciones_puestos.keys()))
        descripcion = st.text_area("Descripción del perfil")
        fecha_apertura = st.date_input("Fecha de apertura")

        if st.form_submit_button("Crear búsqueda"):
            nueva_busqueda = Busqueda(
                nombre=nombre,
                puesto_id=opciones_puestos[puesto_nombre],
                descripcion=descripcion,
                fecha_apertura=fecha_apertura
            )
            db.add(nueva_busqueda)
            db.commit()
            st.success("✅ Búsqueda creada correctamente")

    st.subheader("📋 Búsquedas existentes")
    busquedas = db.query(Busqueda).all()
    for b in busquedas:
        st.markdown(f"**{b.nombre}** - {b.fecha_apertura.strftime('%d/%m/%Y')}  \n_Puesto: {b.puesto.nombre}_  \n{b.descripcion}")
        st.divider()

def mostrar_postulantes():
    st.subheader("👤 Postulantes")

    db = st.session_state["SessionLocal"]()
    postulantes = db.query(Postulante).all()
    busquedas = db.query(Busqueda).all()

    # Crear diccionario para búsqueda: nombre → id
    opciones_busquedas = {b.puesto: b.id for b in busquedas}

    # Filtros
    filtro_busqueda = st.selectbox("🔍 Filtrar por Búsqueda", ["Todas"] + list(opciones_busquedas.keys()))
    filtro_estado = st.selectbox("🔍 Filtrar por Estado", ["Todos", "En revisión", "Entrevistado", "Descartado", "Seleccionado"])

    # Construir query filtrada
    query = db.query(Postulante)
    if filtro_busqueda != "Todas":
        busqueda_id = opciones_busquedas[filtro_busqueda]
        query = query.filter(Postulante.busqueda_id == busqueda_id)
    if filtro_estado != "Todos":
        query = query.filter(Postulante.estado == filtro_estado)

    postulantes_filtrados = query.all()
    st.write(f"🔎 Se encontraron {len(postulantes_filtrados)} postulantes.")

    # Mostrar postulantes
    for p in postulantes_filtrados:
        st.markdown(f"**{p.nombre}** - {p.email}")
        st.text(f"📞 Teléfono: {p.telefono}")
        st.text(f"📌 Estado: {p.estado}")
        st.write(f"📝 Notas: {p.notas or 'Sin notas'}")
        if p.cv:
            ruta_cv = os.path.join("archivos_cv", p.cv)
            if os.path.exists(ruta_cv):
                with open(ruta_cv, "rb") as f:
                    st.download_button("⬇️ Descargar CV", f, file_name=p.cv)
        st.markdown("---")

    # Formulario para nuevo postulante
    st.subheader("➕ Nuevo Postulante")
    nombre = st.text_input("Nombre")
    email = st.text_input("Email")
    telefono = st.text_input("Teléfono")
    estado = st.selectbox("Estado", ["En revisión", "Entrevistado", "Descartado", "Seleccionado"])
    notas = st.text_area("Notas")
    busqueda_nombre = st.selectbox("Asociar a Búsqueda", ["Seleccionar..."] + list(opciones_busquedas.keys()))
    if busqueda_nombre != "Seleccionar...":
        busqueda_id = opciones_busquedas[busqueda_nombre]
    else:
        busqueda_id = None
    cv_file = st.file_uploader("📄 Subir CV", type=["pdf", "doc", "docx"])

    if st.button("Guardar Postulante"):
        if not busqueda_id:
            st.error("⚠️ Debes seleccionar una búsqueda para asociar al postulante.")
        else:
            nuevo_postulante = Postulante(
                nombre=nombre,
                email=email,
                telefono=telefono,
                estado=estado,
                notas=notas,
                busqueda_id=busqueda_id,
            )

        if cv_file:
            cv_filename = f"{uuid.uuid4()}_{cv_file.name}"
            with open(os.path.join("archivos_cv", cv_filename), "wb") as f:
                f.write(cv_file.read())
            nuevo_postulante.cv = cv_filename

        db.add(nuevo_postulante)
        db.commit()
        st.success("✅ Postulante guardado con éxito.")

def mostrar_embudo(postulantes):
    estados = [e.value for e in EstadoSeleccion]
    conteo = {estado: 0 for estado in estados}
    for p in postulantes:
        conteo[p.estado] += 1

    fig, ax = plt.subplots()
    ax.barh(list(conteo.keys()), list(conteo.values()))
    ax.set_xlabel("Cantidad")
    ax.set_title("Embudo de Selección")
    st.pyplot(fig)

if menu_principal == "Reclutamiento":
    seccion_reclutamiento = st.sidebar.radio("Secciones", ["Búsquedas", "Postulantes"])
    if seccion_reclutamiento == "Búsquedas":
        mostrar_busquedas()
    elif seccion_reclutamiento == "Postulantes":
        mostrar_postulantes()