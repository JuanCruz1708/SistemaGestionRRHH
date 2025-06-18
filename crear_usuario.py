from models import SessionLocal, Usuario

def crear_usuario(username, password, rol):
    db = SessionLocal()
    nuevo = Usuario(username=username, password=password, rol=rol)
    db.add(nuevo)
    db.commit()
    db.close()

crear_usuario("admin", "admin123", "admin")
print("Usuario creado con éxito.")