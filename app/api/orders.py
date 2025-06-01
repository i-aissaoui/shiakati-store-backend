from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.db import models
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from typing import List
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from decimal import Decimal, ROUND_HALF_UP

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _load_order_with_relationships(db: Session, order_id: int) -> models.Order:
    """Helper function to load an order with all its relationships"""
    return db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product)
    ).filter(models.Order.id == order_id).first()

@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # Verify customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {order.customer_id} not found"
            )
        
        # Extract items data
        items_data = order.items
        order_dict = order.dict(exclude={'items'})
        
        # Create order
        db_order = models.Order(**order_dict)
        db.add(db_order)
        db.flush()  # Get order ID without committing
        
        # Process each item
        for item in items_data:
            # Get variant with product preloaded for validation
            variant = db.query(models.Variant).options(
                joinedload(models.Variant.product)
            ).filter(models.Variant.id == item.variant_id).first()
            
            if not variant:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Variant {item.variant_id} not found"
                )
            
            if not variant.product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Variant {item.variant_id} has no associated product"
                )
            
            # Check inventory
            if variant.quantity < item.quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Not enough stock for {variant.product.name} - {variant.size or ''} {variant.color or ''}. Available: {variant.quantity}, Requested: {item.quantity}"
                )
            
            # Create order item
            db_item = models.OrderItem(
                order_id=db_order.id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                price=Decimal(str(item.price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            db.add(db_item)
            
            # Update inventory
            variant.quantity -= item.quantity
        
        db.commit()
        
        # Load and return the complete order
        db_order = _load_order_with_relationships(db, db_order.id)
        return db_order
        
    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product),
        joinedload(models.Order.items).joinedload(models.OrderItem.variant),
    ).order_by(models.Order.order_time.desc()).all()
    
    # Ensure all relationships are loaded
    for order in orders:
        if order.items:
            for item in order.items:
                _ = item.variant  # Force load variant
                if item.variant:
                    _ = item.variant.product  # Force load product
    
    return orders

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = _load_order_with_relationships(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderOut)
def update_order_status(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = order_update.status
    db.commit()
    
    # Load the complete order with relationships
    order = _load_order_with_relationships(db, order_id)
    return order
