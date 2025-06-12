from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, extract
from app.db.session import SessionLocal
from app.db import models
from app.schemas.stats import StatsSummary, InventorySummary, ProductSaleSummary, SalesOverTime, ProductStats
from typing import List
from decimal import Decimal
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=StatsSummary)
@router.get("/", response_model=StatsSummary)
@router.get("/summary", response_model=StatsSummary)
def get_stats_summary(db: Session = Depends(get_db)):
    try:
        # Calculate stats
        
        # Calculate total sales items and revenue with explicit joins
        sales_stats = db.query(
            func.count(distinct(models.Sale.id)).label('total_transactions'),
            func.coalesce(func.sum(models.SaleItem.quantity), 0).label('total_items'),
            func.coalesce(func.sum(models.SaleItem.quantity * models.SaleItem.price), 0).label('total_revenue')
        ).select_from(models.Sale).join(
            models.SaleItem, models.SaleItem.sale_id == models.Sale.id
        ).first()
        
        total_transactions = sales_stats.total_transactions if sales_stats else 0
        total_items = float(sales_stats.total_items or 0)
        total_revenue = float(sales_stats.total_revenue or 0)

        # Get top products with explicit joins
        top_products_query = (
            db.query(
                models.Product.id,
                models.Product.name,
                func.sum(models.SaleItem.quantity).label('total_sales'),
                func.sum(models.SaleItem.quantity * models.SaleItem.price).label('total_revenue')
            )
            .select_from(models.Product)
            .join(models.Variant, models.Variant.product_id == models.Product.id)
            .join(models.SaleItem, models.SaleItem.variant_id == models.Variant.id)
            .group_by(models.Product.id, models.Product.name)
            .order_by(func.sum(models.SaleItem.quantity * models.SaleItem.price).desc())
            .limit(5)
            .all()
        )
        
        top_products = [
            ProductStats(
                id=p.id,
                name=p.name,
                category_name="",  # We'll add this later if needed
                total_sales=float(p.total_sales or 0),
                total_revenue=float(p.total_revenue or 0),
                current_stock=0
            )
            for p in top_products_query
        ]

        response = StatsSummary(
            total_sales=total_items,
            total_orders=total_transactions,
            total_revenue=total_revenue,
            total_profit=total_revenue * 0.3,  # Using 30% profit margin
            top_products=top_products
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}"
        )

@router.get("/sales-over-time", response_model=List[SalesOverTime])
def get_sales_over_time(db: Session = Depends(get_db)):
    try:
        # Get daily sales for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        daily_sales = db.query(
            func.date(models.Sale.sale_time).label('date'),
            func.sum(models.SaleItem.quantity * models.SaleItem.price).label('revenue'),
            func.count(distinct(models.Sale.id)).label('num_sales')
        ).join(
            models.SaleItem
        ).filter(
            models.Sale.sale_time >= thirty_days_ago
        ).group_by(
            func.date(models.Sale.sale_time)
        ).order_by(
            func.date(models.Sale.sale_time)
        ).all()
        
        return [
            SalesOverTime(
                date=day.date,
                revenue=float(day.revenue or 0),
                num_sales=day.num_sales
            )
            for day in daily_sales
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sales over time: {str(e)}"
        )

@router.get("/inventory", response_model=List[InventorySummary])
def get_inventory_summary(db: Session = Depends(get_db)):
    try:
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
        
        return [
            InventorySummary(
                product_id=item.product_id,
                product_name=item.product_name,
                category=item.category,
                variant_id=item.variant_id,
                size=item.size,
                color=item.color,
                barcode=item.barcode,
                price=float(item.price),
                quantity=float(item.quantity)
            )
            for item in inventory_items
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting inventory summary: {str(e)}"
        )

@router.get("/top-products", response_model=List[ProductSaleSummary])
def get_top_products(db: Session = Depends(get_db)):
    try:
        # Get sales data for products
        product_sales = db.query(
            models.Product.id,
            models.Product.name,
            func.coalesce(func.sum(models.SaleItem.quantity), 0).label('total_quantity'),
            func.coalesce(func.sum(models.SaleItem.quantity * models.SaleItem.price), 0).label('total_revenue')
        ).join(
            models.Variant
        ).join(
            models.SaleItem
        ).group_by(
            models.Product.id,
            models.Product.name
        ).order_by(
            func.sum(models.SaleItem.quantity).desc()
        ).limit(10).all()
        
        return [
            ProductSaleSummary(
                product_id=item.id,
                product_name=item.name,
                total_quantity=float(item.total_quantity),
                total_revenue=float(item.total_revenue)
            )
            for item in product_sales
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting top products: {str(e)}"
        )