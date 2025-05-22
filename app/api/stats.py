from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.db.session import SessionLocal
from app.db import models
from app.schemas.stats import StatsSummary, InventorySummary, ProductSaleSummary
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


@router.get("/summary", response_model=StatsSummary)
def get_stats_summary(db: Session = Depends(get_db)):
    # Count total sales
    total_sales = db.query(func.sum(models.Sale.quantity)).scalar() or 0
    
    # Calculate total in-store revenue
    sales_revenue = db.query(
        func.sum(models.Sale.quantity * models.Variant.price)
    ).join(
        models.Variant, models.Sale.variant_id == models.Variant.id
    ).scalar() or 0
    
    # Calculate total online orders 
    total_orders = db.query(models.Order).count()
    
    # Calculate total online revenue
    orders_revenue = db.query(
        func.sum(models.Order.quantity * models.Variant.price)
    ).join(
        models.Variant, models.Order.variant_id == models.Variant.id
    ).scalar() or 0
    
    # Total revenue from both sales and orders
    total_revenue = float(sales_revenue) + float(orders_revenue)
    
    # For profit, assume profit = revenue - cost (cost not tracked, so just return revenue for now)
    total_profit = total_revenue * 0.3  # Placeholder: assuming 30% profit margin
    
    return StatsSummary(
        total_sales=total_sales, 
        total_orders=total_orders,
        total_profit=total_profit, 
        total_revenue=total_revenue
    )

@router.get("/inventory", response_model=List[InventorySummary])
def get_inventory_summary(db: Session = Depends(get_db)):
    # Get product and variant information
    inventory_items = db.query(
        models.Product.id.label("product_id"),
        models.Product.name.label("product_name"),
        models.Product.category,
        models.Variant.id.label("variant_id"),
        models.Variant.size,
        models.Variant.color,
        models.Variant.barcode,
        models.Variant.price,
        models.Variant.quantity
    ).join(
        models.Variant, models.Product.id == models.Variant.product_id
    ).all()
    
    # Convert to Pydantic models
    result = []
    for item in inventory_items:
        result.append(InventorySummary(
            product_id=item.product_id,
            product_name=item.product_name,
            category=item.category,
            variant_id=item.variant_id,
            size=item.size,
            color=item.color,
            barcode=item.barcode,
            price=float(item.price),
            quantity=item.quantity
        ))
    
    return result

@router.get("/top-products", response_model=List[ProductSaleSummary])
def get_top_products(db: Session = Depends(get_db)):
    # Combine sales and orders to find top products by total quantity sold
    product_sales = db.query(
        models.Product.id,
        models.Product.name,
        func.sum(models.Sale.quantity + models.Order.quantity).label("total_quantity"),
        func.sum((models.Sale.quantity + models.Order.quantity) * models.Variant.price).label("total_revenue")
    ).join(
        models.Variant, models.Product.id == models.Variant.product_id
    ).outerjoin(
        models.Sale, models.Variant.id == models.Sale.variant_id
    ).outerjoin(
        models.Order, models.Variant.id == models.Order.variant_id
    ).group_by(
        models.Product.id
    ).order_by(
        func.sum(models.Sale.quantity + models.Order.quantity).desc()
    ).limit(10).all()
    
    # Convert to Pydantic models
    result = []
    for item in product_sales:
        result.append(ProductSaleSummary(
            product_id=item.id,
            product_name=item.name,
            total_quantity=item.total_quantity or 0,
            total_revenue=float(item.total_revenue or 0)
        ))
    
    return result 