from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date
from fastapi import Form, UploadFile, File

# --------------------- CuentaEmpresa ---------------------
class CuentaEmpresaBase(BaseModel):
    nombre_empresa: str
    usuario: str
    base_datos: str

class CuentaEmpresaCreate(CuentaEmpresaBase):
    password: str

class CuentaEmpresaResponse(CuentaEmpresaBase):
    id: int

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    usuario: str
    password: str

# --------------------- CentroCosto ---------------------
class CentroCostoBase(BaseModel):
    nombre: str

class CentroCostoCreate(CentroCostoBase):
    pass

class CentroCosto(CentroCostoBase):
    id: int

    class Config:
        orm_mode = True

# --------------------- Puesto ---------------------
class PuestoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    jefe_id: Optional[int] = None

class PuestoCreate(PuestoBase):
    pass

class Puesto(PuestoBase):
    id: int

    class Config:
        orm_mode = True

# --------------------- Empleado ---------------------
class EmpleadoBase(BaseModel):
    legajo: str
    apellido: str
    nombre: str
    dni: str
    genero: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    puesto_id: Optional[int] = None
    centro_costo_id: Optional[int] = None
    estado: str

class EmpleadoCreate(EmpleadoBase):
    pass

class Empleado(EmpleadoBase):
    id: int
    puesto: Optional[Puesto] = None   # Añadido para mostrar nombre del puesto
    centro_costo: Optional[CentroCosto] = None  # Añadido para mostrar nombre del centro de costo

    class Config:
        orm_mode = True

# --------------------- Busqueda ---------------------
class BusquedaBase(BaseModel):
    nombre: str
    puesto: str
    descripcion: Optional[str] = None
    fecha_apertura: Optional[date] = None
    fecha_inicio: Optional[date] = None
    estado: Optional[str] = None
    responsable: Optional[str] = None
    centro_costo: Optional[str] = None

class BusquedaCreate(BusquedaBase):
    pass

class Busqueda(BusquedaBase):
    id: int

    class Config:
        orm_mode = True

# --------------------- Postulante ---------------------
class PostulanteBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    busqueda: Optional[str] = None
    cv: Optional[str] = None

class PostulanteCreateForm(PostulanteBase):
    @classmethod
    def as_form(
        cls,
        nombre: str = Form(...),
        email: EmailStr = Form(...),
        telefono: str = Form(None),
        direccion: str = Form(None),
        estado: str = Form(None),
        notas: str = Form(None),
        busqueda: str = Form(...),
        cv: UploadFile = File(None)
    ):
        data = cls(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            estado=estado,
            notas=notas,
            busqueda=busqueda
        )
        return data, cv

class PostulanteCreate(PostulanteBase):
    pass

class Postulante(PostulanteBase):
    id: int

    class Config:
        orm_mode = True

# --------------------- Licencia ---------------------
class LicenciaBase(BaseModel):
    empleado_id: int
    tipo: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None

class LicenciaCreate(LicenciaBase):
    pass

class Licencia(LicenciaBase):
    id: int

    class Config:
        orm_mode = True