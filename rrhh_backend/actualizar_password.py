from sqlalchemy.orm import Session
from database import SessionGlobal
import models
import bcrypt

# Configuración
usuario_a_actualizar = "admin"
nueva_contraseña = "admin123"

def actualizar_password():
    db: Session = SessionGlobal()
    try:
        cuenta = db.query(models.CuentaEmpresa).filter(models.CuentaEmpresa.usuario == usuario_a_actualizar).first()
        if not cuenta:
            print(f"❌ El usuario '{usuario_a_actualizar}' no existe.")
            return
        hashed_password = bcrypt.hashpw(nueva_contraseña.encode('utf-8'), bcrypt.gensalt())
        cuenta.password = hashed_password.decode('utf-8')
        db.commit()
        print(f"✅ Contraseña de '{usuario_a_actualizar}' actualizada correctamente a '{nueva_contraseña}'.")
    except Exception as e:
        print(f"❌ Error al actualizar la contraseña: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    actualizar_password()