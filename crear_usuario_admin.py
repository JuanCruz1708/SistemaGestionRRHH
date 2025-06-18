from models import SessionLocal, Usuario

def crear_usuario(username, password, rol):
    db = SessionLocal()
    existente = db.query(Usuario).filter_by(username=username).first()
    if not existente:
        nuevo = Usuario(username=username, password=password, rol=rol)
        db.add(nuevo)
        db.commit()
        print(f"✅ Usuario '{username}' creado correctamente.")
    else:
        print(f"⚠️ El usuario '{username}' ya existe.")
    db.close()

crear_usuario("admin", "admin123", "admin")