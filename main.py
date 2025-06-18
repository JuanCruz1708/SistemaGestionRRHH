from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Base, engine, SessionLocal, Empleado, Licencia
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Permitir acceso desde cualquier origen (para conectar con Streamlit)
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