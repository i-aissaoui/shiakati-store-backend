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
    """Helper function to load a sale with all its relationships, with improved error handling"""
    try:
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
            if sale is None or not hasattr(sale, 'id'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sale object provided"
                )
            sale = query.filter(models.Sale.id == sale.id).first()
            
        if not hasattr(sale, 'items'):
            return sale
            
        # Validate relationships are properly loaded but don't fail if product data is missing
        # Just log a warning instead of raising an exception
        for item in sale.items:
            try:
                variant = getattr(item, 'variant', None)
                if variant and not getattr(variant, 'product', None):
                    print(f"Warning: Variant {variant.id} has no associated product")
            except Exception as e:
                print(f"Warning: Error processing sale item: {str(e)}")
        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load sale relationships: {str(e)}"
        )

@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db)):
    try:
        # First get basic sale data without eager loading relationships
        sales_basic = db.query(models.Sale).order_by(models.Sale.sale_time.desc()).all()
        
        # Prepare properly formatted results
        result_sales = []
        
        # Process each sale individually
        for sale in sales_basic:
            try:
                # Create manually validated sale object with safe defaults
                sale_dict = {
                    "id": sale.id,
                    "sale_time": sale.sale_time,
                    "total": sale.total,
                    "items": []
                }
                
                # Get sale items separately
                sale_items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale.id).all()
                
                # Process each item individually
                for item in sale_items:
                    item_dict = {
                        "id": item.id,
                        "quantity": item.quantity,
                        "price": item.price,
                        "variant_id": item.variant_id if item.variant_id is not None else 0,
                        "product_name": "Unknown Product",
                        "size": None,
                        "color": None
                    }
                    
                    # Only try to add variant/product data if the relationship exists
                    if item.variant_id is not None:
                        variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
                        if variant:
                            # Add variant data
                            item_dict["size"] = variant.size
                            item_dict["color"] = variant.color
                            
                            # Add product data if available
                            if variant.product_id and variant.product:
                                item_dict["product_name"] = variant.product.name
                    
                    sale_dict["items"].append(item_dict)
                
                # Add the fully processed sale to results
                result_sales.append(sale_dict)
                
            except Exception as e:
                # Continue with next sale instead of failing completely
                continue
                
        return result_sales
        
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
        sale = _load_sale_with_relationships(db, sale_id=sale_id)
        
        # Manually construct the response to ensure product names are included
        sale_dict = {
            "id": sale.id,
            "sale_time": sale.sale_time,
            "total": sale.total,
            "items": []
        }
        
        for item in sale.items:
            item_dict = {
                "id": item.id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": item.price,
                "product_name": "Unknown Product",
                "size": None,
                "color": None
            }
            
            # Get product name and variant info from relationships
            if item.variant:
                item_dict["size"] = item.variant.size
                item_dict["color"] = item.variant.color
                
                if item.variant.product:
                    item_dict["product_name"] = item.variant.product.name
                    print(f"Sale item {item.id}: Found product name = {item.variant.product.name}")
                else:
                    print(f"Sale item {item.id}: Variant has no product")
            else:
                print(f"Sale item {item.id}: No variant found")
                
            sale_dict["items"].append(item_dict)
        
        return sale_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sale: {str(e)}"
        )

@router.delete("/clear-all", status_code=status.HTTP_200_OK)
def clear_all_sales(db: Session = Depends(get_db)):
    """Clear all sales from the database."""
    try:
        # Delete all sale items first to avoid foreign key constraints
        db.query(models.SaleItem).delete()
        
        # Then delete all sales
        num_deleted = db.query(models.Sale).delete()
        
        db.commit()
        return {"message": f"Successfully cleared {num_deleted} sales from database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing sales: {str(e)}"
        )
