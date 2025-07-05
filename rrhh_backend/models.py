from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    legajo = Column(String, unique=True, nullable=False)
    apellido = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    genero = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    puesto_id = Column(Integer, ForeignKey("puestos.id"), nullable=True)
    centro_costo_id = Column(Integer, ForeignKey("centros_costo.id"), nullable=True)
    estado = Column(String, nullable=False)

    puesto = relationship("Puesto")
    centro_costo = relationship("CentroCosto")

class CentroCosto(Base):
    __tablename__ = "centros_costo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

class Puesto(Base):
    __tablename__ = "puestos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String)
    jefe_id = Column(Integer, ForeignKey("puestos.id"), nullable=True)
    jefe = relationship("Puesto", remote_side=[id])

class Busqueda(Base):
    __tablename__ = "busquedas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    puesto = Column(String, nullable=False)
    descripcion = Column(String)
    fecha_apertura = Column(Date)
    fecha_inicio = Column(Date)
    estado = Column(String)
    responsable = Column(String)
    centro_costo = Column(String)

class Postulante(Base):
    __tablename__ = "postulantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String)
    telefono = Column(String)
    direccion = Column(String)
    estado = Column(String)
    notas = Column(String)
    busqueda = Column(String)
    cv = Column(String)

class Licencia(Base):
    __tablename__ = "licencias"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    tipo = Column(String, nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    observaciones = Column(String)

    empleado = relationship("Empleado")

class CuentaEmpresa(Base):
    __tablename__ = "cuentas_empresa"

    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String, nullable=False)
    usuario = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Almacenará hash bcrypt
    base_datos = Column(String, nullable=False)