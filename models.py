from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import Column, String

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./rrhh.db"

Base = declarative_base()

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    legajo = Column(String)
    apellido = Column(String)
    nombre = Column(String)
    genero = Column(String)
    estado_civil = Column(String)
    fecha_nacimiento = Column(String)
    dni = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    centro_costo = Column(String)
    puesto = Column(String)
    remuneracion_bruta = Column(Integer)
    estado = Column(String)
    fecha_alta = Column(String)
    fecha_baja = Column(String)
    jefe_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    jefe = relationship("Empleado", remote_side=[id])

class Licencia(Base):
    __tablename__ = "licencias"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"))
    tipo = Column(String)
    fecha_inicio = Column(String)
    fecha_fin = Column(String)
    observaciones = Column(String)

    empleado = relationship("Empleado")

class Puesto(Base):
    __tablename__ = "puestos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(String, nullable=True)
    jefe_id = Column(Integer, ForeignKey("puestos.id"), nullable=True)

    jefe = relationship("Puesto", remote_side=[id])

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Guardado en texto plano por simplicidad (lo mejor sería hasheado)
    rol = Column(String, nullable=False)  # Ej: "admin", "rh", "consulta"

class CentroCosto(Base):
    __tablename__ = "centros_costo"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

class CuentaEmpresa(Base):
    __tablename__ = "cuentas_empresa"
    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String, unique=True, index=True)
    usuario = Column(String, unique=True, index=True)
    password = Column(String)
    base_datos = Column(String)

# Conexión global para autenticación de cuentas
engine_global = create_engine("sqlite:///./cuentas.db", connect_args={"check_same_thread": False})
SessionGlobal = sessionmaker(autocommit=False, autoflush=False, bind=engine_global)
