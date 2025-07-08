import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt
import models, schemas
from database import get_db_global, get_db_cliente
import crud

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/")
def register_cuenta(data: schemas.CuentaEmpresaCreate, db: Session = Depends(get_db_global)):
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
    cuenta = models.CuentaEmpresa(
        nombre_empresa=data.nombre_empresa,
        usuario=data.usuario,
        password=hashed_password.decode('utf-8'),
        base_datos=data.base_datos
    )
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta

@app.post("/login/")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db_global)):
    usuario = db.query(models.CuentaEmpresa).filter(models.CuentaEmpresa.usuario == data.usuario).first()
    if not usuario:
        print("❌ Usuario no encontrado en DB")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    print("✅ Usuario encontrado:", usuario.usuario)
    print("✅ Password recibido:", data.password)
    print("✅ Password en DB:", usuario.password)

    if not bcrypt.checkpw(data.password.encode('utf-8'), usuario.password.encode('utf-8')):
        print("❌ Contraseña no coincide con bcrypt")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    print("✅ Login exitoso")
    return {"mensaje": "Login exitoso", "usuario": usuario.usuario}

@app.get("/empleados/")
def obtener_empleados(db: Session = Depends(get_db_cliente)):
    return crud.get_empleados(db)

@app.post("/empleados/")
def crear_empleado(data: schemas.EmpleadoCreate, db: Session = Depends(get_db_cliente)):
    return crud.create_empleado(db, data)

@app.delete("/empleados/{empleado_id}")
def eliminar_empleado(empleado_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_empleado(db, empleado_id)

@app.put("/empleados/{empleado_id}")
def actualizar_empleado(empleado_id: int, data: schemas.EmpleadoCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_empleado(db, empleado_id, data)

@app.get("/centros_costo/")
def obtener_centros_costo(db: Session = Depends(get_db_cliente)):
    return crud.get_centros_costo(db)

@app.post("/centros_costo/")
def crear_centro_costo(data: schemas.CentroCostoCreate, db: Session = Depends(get_db_cliente)):
    return crud.create_centro_costo(db, data)

@app.put("/centros_costo/{centro_id}")
def actualizar_centro_costo(centro_id: int, data: schemas.CentroCostoCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_centro_costo(db, centro_id, data)

@app.delete("/centros_costo/{centro_id}")
def eliminar_centro_costo(centro_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_centro_costo(db, centro_id)

@app.get("/puestos/")
def obtener_puestos(db: Session = Depends(get_db_cliente)):
    return crud.get_puestos(db)

@app.post("/puestos/")
def crear_puesto(data: schemas.PuestoCreate, db: Session = Depends(get_db_cliente)):
    return crud.create_puesto(db, data)

@app.put("/puestos/{puesto_id}")
def actualizar_puesto(puesto_id: int, data: schemas.PuestoCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_puesto(db, puesto_id, data)

@app.delete("/puestos/{puesto_id}")
def eliminar_puesto(puesto_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_puesto(db, puesto_id)

@app.get("/licencias/")
def obtener_licencias(db: Session = Depends(get_db_cliente)):
    return crud.get_licencias(db)

@app.post("/licencias/")
def crear_licencia(data: schemas.LicenciaCreate, db: Session = Depends(get_db_cliente)):
    return crud.create_licencia(db, data)

@app.put("/licencias/{licencia_id}")
def actualizar_licencia(licencia_id: int, data: schemas.LicenciaCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_licencia(db, licencia_id, data)

@app.delete("/licencias/{licencia_id}")
def eliminar_licencia(licencia_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_licencia(db, licencia_id)

@app.get("/busquedas/")
def obtener_busquedas(db: Session = Depends(get_db_cliente)):
    return crud.get_busquedas(db)

@app.post("/busquedas/")
def crear_busqueda(data: schemas.BusquedaCreate, db: Session = Depends(get_db_cliente)):
    return crud.create_busqueda(db, data)

@app.put("/busquedas/{busqueda_id}")
def actualizar_busqueda(busqueda_id: int, data: schemas.BusquedaCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_busqueda(db, busqueda_id, data)

@app.delete("/busquedas/{busqueda_id}")
def eliminar_busqueda(busqueda_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_busqueda(db, busqueda_id)

@app.get("/postulantes/")
def obtener_postulantes(db: Session = Depends(get_db_cliente)):
    return crud.get_postulantes(db)

@app.post("/postulantes/")
async def crear_postulante(
    data_cv: tuple = Depends(schemas.PostulanteCreateForm.as_form),
    db: Session = Depends(get_db_cliente)
):
    data, cv = data_cv
    return crud.create_postulante(db, data, cv)

@app.put("/postulantes/{postulante_id}")
def actualizar_postulante(postulante_id: int, data: schemas.PostulanteCreate, db: Session = Depends(get_db_cliente)):
    return crud.update_postulante(db, postulante_id, data)

@app.delete("/postulantes/{postulante_id}")
def eliminar_postulante(postulante_id: int, db: Session = Depends(get_db_cliente)):
    return crud.delete_postulante(db, postulante_id)