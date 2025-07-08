from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import models

# Cambiar a cliente1.db
engine = create_engine("sqlite:///cliente1.db")
Session = sessionmaker(bind=engine)
session = Session()

usuario = session.query(models.CuentaEmpresa).filter(models.CuentaEmpresa.usuario == "admin").first()
if usuario:
    nueva_password = "admin123"
    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    usuario.password = hashed_password
    session.commit()
    print("✅ Contraseña reseteada correctamente en cliente1.db a 'admin123'")
else:
    print("❌ Usuario no encontrado en cliente1.db. Creando usuario...")

    nueva_password = "admin123"
    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    from models import CuentaEmpresa
    nuevo_usuario = CuentaEmpresa(
        nombre_empresa="empresa_demo",
        usuario="admin",
        password=hashed_password,
        base_datos="cliente1.db"
    )
    session.add(nuevo_usuario)
    session.commit()
    print("✅ Usuario admin creado correctamente en cliente1.db con contraseña 'admin123'")