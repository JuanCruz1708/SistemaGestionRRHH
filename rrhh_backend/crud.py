from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, UploadFile
import models, schemas, shutil
import os

# --------------------- Empleados ---------------------
def get_empleados(db: Session):
    return db.query(models.Empleado)\
        .options(
            joinedload(models.Empleado.puesto),
            joinedload(models.Empleado.centro_costo)
        )\
        .all()

def create_empleado(db: Session, empleado: schemas.EmpleadoCreate):
    existente = db.query(models.Empleado).filter(
        (models.Empleado.dni == empleado.dni) | (models.Empleado.legajo == empleado.legajo)
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="El empleado con este DNI o Legajo ya existe.")
    nuevo = models.Empleado(**empleado.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_empleado(db: Session, empleado_id: int):
    empleado = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")
    db.delete(empleado)
    db.commit()
    return {"detail": "Empleado eliminado correctamente."}

def update_empleado(db: Session, empleado_id: int, empleado: schemas.EmpleadoCreate):
    existente = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")
    for key, value in empleado.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    db.commit()
    db.refresh(existente)
    return existente

# --------------------- Centros de Costo ---------------------
def get_centros_costo(db: Session):
    return db.query(models.CentroCosto).all()

def create_centro_costo(db: Session, centro: schemas.CentroCostoCreate):
    existente = db.query(models.CentroCosto).filter(models.CentroCosto.nombre == centro.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="El centro de costo ya existe.")
    nuevo = models.CentroCosto(**centro.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_centro_costo(db: Session, centro_id: int):
    centro = db.query(models.CentroCosto).filter(models.CentroCosto.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro de costo no encontrado.")
    db.delete(centro)
    db.commit()
    return {"detail": "Centro de costo eliminado correctamente."}

def update_centro_costo(db: Session, centro_id: int, centro: schemas.CentroCostoCreate):
    existente = db.query(models.CentroCosto).filter(models.CentroCosto.id == centro_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Centro de costo no encontrado.")
    for key, value in centro.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    db.commit()
    db.refresh(existente)
    return existente

# --------------------- Puestos ---------------------
def get_puestos(db: Session):
    return db.query(models.Puesto).all()

def create_puesto(db: Session, puesto: schemas.PuestoCreate):
    existente = db.query(models.Puesto).filter(models.Puesto.nombre == puesto.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="El puesto ya existe.")
    nuevo = models.Puesto(**puesto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_puesto(db: Session, puesto_id: int):
    puesto = db.query(models.Puesto).filter(models.Puesto.id == puesto_id).first()
    if not puesto:
        raise HTTPException(status_code=404, detail="Puesto no encontrado.")
    db.delete(puesto)
    db.commit()
    return {"detail": "Puesto eliminado correctamente."}

def update_puesto(db: Session, puesto_id: int, puesto: schemas.PuestoCreate):
    existente = db.query(models.Puesto).filter(models.Puesto.id == puesto_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Puesto no encontrado.")
    for key, value in puesto.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    db.commit()
    db.refresh(existente)
    return existente

# --------------------- Licencias ---------------------
def get_licencias(db: Session):
    return db.query(models.Licencia).all()

def create_licencia(db: Session, licencia: schemas.LicenciaCreate):
    nuevo = models.Licencia(**licencia.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_licencia(db: Session, licencia_id: int):
    licencia = db.query(models.Licencia).filter(models.Licencia.id == licencia_id).first()
    if not licencia:
        raise HTTPException(status_code=404, detail="Licencia no encontrada.")
    db.delete(licencia)
    db.commit()
    return {"detail": "Licencia eliminada correctamente."}

def update_licencia(db: Session, licencia_id: int, licencia: schemas.LicenciaCreate):
    existente = db.query(models.Licencia).filter(models.Licencia.id == licencia_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Licencia no encontrada.")
    for key, value in licencia.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    db.commit()
    db.refresh(existente)
    return existente

# --------------------- Busquedas ---------------------
def get_busquedas(db: Session):
    return db.query(models.Busqueda).all()

def create_busqueda(db: Session, busqueda: schemas.BusquedaCreate):
    nuevo = models.Busqueda(**busqueda.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_busqueda(db: Session, busqueda_id: int):
    busqueda = db.query(models.Busqueda).filter(models.Busqueda.id == busqueda_id).first()
    if not busqueda:
        raise HTTPException(status_code=404, detail="Búsqueda no encontrada.")
    db.delete(busqueda)
    db.commit()
    return {"detail": "Búsqueda eliminada correctamente."}

def update_busqueda(db: Session, busqueda_id: int, busqueda: schemas.BusquedaCreate):
    existente = db.query(models.Busqueda).filter(models.Busqueda.id == busqueda_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Búsqueda no encontrada.")
    for key, value in busqueda.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    db.commit()
    db.refresh(existente)
    return existente

# --------------------- Postulantes ---------------------
def get_postulantes(db: Session):
    return db.query(models.Postulante).all()

def create_postulante(db: Session, postulante: schemas.PostulanteBase, cv_file: UploadFile = None):
    cv_filename = None
    if cv_file:
        os.makedirs("uploads", exist_ok=True)
        cv_filename = f"uploads/{cv_file.filename}"
        with open(cv_filename, "wb") as buffer:
            shutil.copyfileobj(cv_file.file, buffer)
    postulante_data = postulante.dict(exclude_unset=True)  # 🚩 usa exclude_unset para evitar conflictos
    if cv_filename:
        postulante_data["cv"] = cv_filename
    else:
        postulante_data["cv"] = None
    nuevo = models.Postulante(**postulante_data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_postulante(db: Session, postulante_id: int):
    postulante = db.query(models.Postulante).filter(models.Postulante.id == postulante_id).first()
    if not postulante:
        raise HTTPException(status_code=404, detail="Postulante no encontrado.")
    db.delete(postulante)
    db.commit()
    return {"detail": "Postulante eliminado correctamente."}

def update_postulante(db: Session, postulante_id: int, postulante: schemas.PostulanteCreate, cv_file: UploadFile = None):
    existente = db.query(models.Postulante).filter(models.Postulante.id == postulante_id).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Postulante no encontrado.")
    for key, value in postulante.dict(exclude_unset=True).items():
        setattr(existente, key, value)
    if cv_file:
        cv_filename = f"uploads/{cv_file.filename}"
        with open(cv_filename, "wb") as buffer:
            shutil.copyfileobj(cv_file.file, buffer)
        existente.cv = cv_filename
    db.commit()
    db.refresh(existente)
    return existente