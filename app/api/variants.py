from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.variant import VariantCreate, VariantOut, VariantUpdate
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[VariantOut])
def list_variants(db: Session = Depends(get_db)):
    return db.query(models.Variant).all()

@router.get("/{variant_id}", response_model=VariantOut)
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

@router.post("/", response_model=VariantOut)
def create_variant(variant: VariantCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == variant.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if barcode is unique
    existing_variant = db.query(models.Variant).filter(models.Variant.barcode == variant.barcode).first()
    if existing_variant:
        raise HTTPException(status_code=400, detail="Barcode already exists")
    
    db_variant = models.Variant(**variant.dict())
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)
    return db_variant

@router.put("/{variant_id}", response_model=VariantOut)
def update_variant(variant_id: int, variant: VariantUpdate, db: Session = Depends(get_db)):
    db_variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    update_data = variant.dict(exclude_unset=True)
    
    # If updating barcode, check uniqueness
    if "barcode" in update_data and update_data["barcode"] != db_variant.barcode:
        existing_variant = db.query(models.Variant).filter(models.Variant.barcode == update_data["barcode"]).first()
        if existing_variant:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    # If updating product_id, check existence
    if "product_id" in update_data and update_data["product_id"] != db_variant.product_id:
        product = db.query(models.Product).filter(models.Product.id == update_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in update_data.items():
        setattr(db_variant, key, value)
    
    db.commit()
    db.refresh(db_variant)
    return db_variant

@router.delete("/{variant_id}")
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    db_variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    db.delete(db_variant)
    db.commit()
    return {"ok": True}
