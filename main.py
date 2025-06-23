from fastapi import FastAPI, Depends
from models import Base, CuentaEmpresa
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_global = create_engine("sqlite:///./cuentas.db", connect_args={"check_same_thread": False})
SessionGlobal = sessionmaker(autocommit=False, autoflush=False, bind=engine_global)
Base.metadata.create_all(bind=engine_global)

def get_engine_for_user(nombre_archivo_db):
    db_url = f"sqlite:///./{nombre_archivo_db}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, Session

app = FastAPI()

# Permitir CORS para conexión con Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/empleados")
def listar_empleados(db: Session = Depends(get_db)):
    return db.query(Empleado).all()

@app.post("/empleados")
def agregar_empleado(empleado: dict, db: Session = Depends(get_db)):
    nuevo = Empleado(**empleado)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/licencias")
def listar_licencias(db: Session = Depends(get_db)):
    return db.query(Licencia).all()

@app.post("/licencias")
def agregar_licencia(licencia: dict, db: Session = Depends(get_db)):
    nueva = Licencia(**licencia)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def get_engine_for_user(empresa_id):
    db_url = f"sqlite:///./{empresa_id}.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, Session

def inicializar_base_cliente(engine):
    Base.metadata.create_all(bind=engine)