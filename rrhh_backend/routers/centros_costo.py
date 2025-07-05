from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CentroCosto

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_centros(db: Session = Depends(get_db)):
    return db.query(CentroCosto).all()

@router.post("/")
def create_centro(centro: dict, db: Session = Depends(get_db)):
    nuevo = CentroCosto(**centro)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.delete("/{centro_id}")
def delete_centro(centro_id: int, db: Session = Depends(get_db)):
    centro = db.query(CentroCosto).filter(CentroCosto.id == centro_id).first()
    if centro is None:
        raise HTTPException(status_code=404, detail="Centro de costo no encontrado")
    db.delete(centro)
    db.commit()
    return {"ok": True}