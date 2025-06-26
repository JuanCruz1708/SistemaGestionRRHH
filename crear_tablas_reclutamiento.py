import os
from sqlalchemy import create_engine
from models import Base, Busqueda, Postulante

# Ruta actual
ruta_actual = os.getcwd()

# Buscar archivos .db (excepto cuentas.db si estás usando multi-tenant)
archivos_db = [f for f in os.listdir(ruta_actual) if f.endswith(".db") and f != "cuentas.db"]

for archivo in archivos_db:
    print(f"⏳ Procesando base: {archivo}")
    ruta_completa = f"sqlite:///{os.path.join(ruta_actual, archivo)}"
    engine = create_engine(ruta_completa, connect_args={"check_same_thread": False})
    
    # Crear solo las tablas de Reclutamiento si no existen
    Base.metadata.create_all(engine, tables=[Busqueda.__table__, Postulante.__table__])
    print(f"✅ Tablas creadas en {archivo}")
