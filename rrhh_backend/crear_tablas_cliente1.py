from sqlalchemy import create_engine
from models import Base

nombre_base = "cliente1.db"

def crear_tablas_si_faltan():
    engine = create_engine(f"sqlite:///./{nombre_base}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print(f"✅ Tablas necesarias creadas/verificadas en '{nombre_base}'.")

if __name__ == "__main__":
    crear_tablas_si_faltan()