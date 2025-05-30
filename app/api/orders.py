from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from typing import List
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Check if variant exists
    variant = db.query(models.Variant).filter(models.Variant.id == order.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Check inventory
    if variant.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough items in stock")
    
    # Create order
    db_order = models.Order(**order.dict())
    db.add(db_order)
    
    # Update inventory
    variant.quantity -= order.quantity
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderOut)
def update_order_status(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = order_update.status
    db.commit()
    db.refresh(db_order)
    return db_order
