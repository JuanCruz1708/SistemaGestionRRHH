# crear_bases.py
import sqlite3
from sqlalchemy import create_engine
from models import Base

# Conectamos a la base global para obtener las cuentas
conn = sqlite3.connect("cuentas.db")
cursor = conn.cursor()
cursor.execute("SELECT base_datos FROM cuentas_empresa")
bases = [fila[0] for fila in cursor.fetchall()]
conn.close()

# Crear las tablas en cada base individual
for base in bases:
    print(f"🛠️ Inicializando base: {base}")
    engine = create_engine(f"sqlite:///{base}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

print("✅ Todas las bases fueron inicializadas correctamente.")