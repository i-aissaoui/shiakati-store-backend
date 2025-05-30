# filepath: /home/ismail/Desktop/projects/shiakati_store/desktop/app/api/sales.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.sale import SaleCreate, SaleOut
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SaleOut)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    # Get the variant to update inventory
    variant = db.query(models.Variant).filter(models.Variant.id == sale.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Check inventory
    if variant.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Not enough items in stock")
    
    # Create sale record
    db_sale = models.Sale(**sale.dict())
    db.add(db_sale)
    
    # Update inventory
    variant.quantity -= sale.quantity
    
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).all()

@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale
