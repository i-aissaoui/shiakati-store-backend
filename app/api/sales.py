from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.db import models
from app.schemas.sale import SaleCreate, SaleOut, SaleItemBase
from typing import List
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _load_sale_with_relationships(db: Session, sale_id: int = None, sale: models.Sale = None) -> models.Sale:
    """Helper function to load a sale with all its relationships"""
    query = db.query(models.Sale).options(
        joinedload(models.Sale.items).joinedload(models.SaleItem.variant).joinedload(models.Variant.product)
    )
    
    if sale_id is not None:
        sale = query.filter(models.Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sale with id {sale_id} not found"
            )
    else:
        sale = query.filter(models.Sale.id == sale.id).first()
        
    # Validate relationships are properly loaded
    for item in sale.items:
        if item.variant and not item.variant.product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Product data missing for sale item {item.id}"
            )
    
    return sale

@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db)):
    try:
        # Get all sales with relationships loaded
        sales = db.query(models.Sale).options(
            joinedload(models.Sale.items).joinedload(models.SaleItem.variant).joinedload(models.Variant.product)
        ).order_by(models.Sale.sale_time.desc()).all()
        
        # Verify data integrity
        for sale in sales:
            for item in sale.items:
                if item.variant and not hasattr(item.variant, 'product'):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Product data missing for sale item in sale {sale.id}"
                    )
        
        return sales
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sales: {str(e)}"
        )

@router.post("/", response_model=SaleOut)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        # Convert total to Decimal for precision
        total = Decimal(str(sale.total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Create the sale record
        db_sale = models.Sale(total=total)
        db.add(db_sale)
        db.flush()  # Get the sale.id
        
        # Process each item
        for item in sale.items:
            # Get the variant with product preloaded
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
                    detail=f"Product data missing for variant {item.variant_id}"
                )
            
            # Convert quantity and check inventory
            quantity = Decimal(str(item.quantity)).quantize(Decimal('0.003'), rounding=ROUND_HALF_UP)
            if variant.quantity < quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough items in stock for variant {item.variant_id}. Available: {variant.quantity}"
                )
            
            # Convert price to Decimal with proper precision
            price = Decimal(str(item.price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Create sale item record
            db_sale_item = models.SaleItem(
                sale_id=db_sale.id,
                variant_id=item.variant_id,
                quantity=quantity,
                price=price
            )
            db.add(db_sale_item)
            
            # Update inventory with proper decimal handling
            variant.quantity = (variant.quantity - quantity).quantize(Decimal('0.003'), rounding=ROUND_HALF_UP)
        
        db.commit()
        
        # Load all relationships for response
        return _load_sale_with_relationships(db, sale=db_sale)
        
    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid numeric value: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sale: {str(e)}"
        )

@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    try:
        return _load_sale_with_relationships(db, sale_id=sale_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sale: {str(e)}"
        )
