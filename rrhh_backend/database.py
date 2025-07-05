from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Conexión directa a cliente1.db para estabilidad
db_url = "sqlite:///./cliente1.db"
engine = create_engine(db_url, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_cliente():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_global():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()