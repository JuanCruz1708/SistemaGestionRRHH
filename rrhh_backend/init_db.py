# init_db.py
from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite:///cuentas.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

print("✅ Tabla 'cuentas_empresa' creada correctamente.")
