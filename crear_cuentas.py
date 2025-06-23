from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CuentaEmpresa

# Crear engine global
engine = create_engine("sqlite:///./cuentas.db", connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tabla si no existe
Base.metadata.create_all(bind=engine)

# Crear cuentas ficticias
db = Session()

if not db.query(CuentaEmpresa).filter_by(usuario="empresa1").first():
    db.add(CuentaEmpresa(nombre_empresa="Empresa Uno", usuario="empresa1", password="123", base_datos="empresa1.db"))

if not db.query(CuentaEmpresa).filter_by(usuario="empresa2").first():
    db.add(CuentaEmpresa(nombre_empresa="Empresa Dos", usuario="empresa2", password="123", base_datos="empresa2.db"))

db.commit()
db.close()
print("✅ Cuentas creadas correctamente.")