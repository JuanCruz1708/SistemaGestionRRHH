from sqlalchemy import create_engine
from models import Base
import sqlite3

# Leer nombres de base de datos desde cuentas.db
conn = sqlite3.connect("cuentas.db")
cursor = conn.cursor()
cursor.execute("SELECT base_datos FROM cuentas_empresa")
bases = cursor.fetchall()
conn.close()

# Crear las tablas en cada base
for base in bases:
    nombre_base = base[0]
    print(f"🛠️ Inicializando tablas en: {nombre_base}")
    engine = create_engine(f"sqlite:///{nombre_base}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

print("✅ Todas las tablas fueron creadas correctamente.")