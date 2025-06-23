from sqlalchemy import create_engine
from models import Base

# Crear la tabla cuentas_empresa en la base cuentas.db
engine = create_engine("sqlite:///cuentas.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

print("✅ Tabla 'cuentas_empresa' creada correctamente.")