from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine("sqlite:///cuentas.db")
Session = sessionmaker(bind=engine)
session = Session()

usuario = session.query(models.CuentaEmpresa).filter(models.CuentaEmpresa.usuario == "admin").first()
if usuario:
    print("✅ Usuario encontrado:", usuario.usuario)
    print("🔐 Hash de contraseña:", usuario.password)
else:
    print("❌ Usuario no encontrado")