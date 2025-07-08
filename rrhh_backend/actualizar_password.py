import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine("sqlite:///cuentas.db")
Session = sessionmaker(bind=engine)
session = Session()

usuario = session.query(models.CuentaEmpresa).filter(models.CuentaEmpresa.usuario == "admin").first()
if usuario:
    nueva_password = "admin123"
    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    usuario.password = hashed_password
    session.commit()
    print("✅ Contraseña actualizada correctamente")
else:
    print("❌ Usuario no encontrado")