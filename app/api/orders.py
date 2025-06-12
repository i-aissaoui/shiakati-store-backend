from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.db import models
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate, OrderItemCreate, OrderItemUpdate
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
    # Query with explicit eager loading of all needed relationships
    order = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product)
    ).filter(models.Order.id == order_id).first()
    
    # Force load variant details to ensure they're accessible
    if order and order.items:
        for item in order.items:
            if hasattr(item, 'variant') and item.variant:
                _ = getattr(item.variant, 'size', None)  # Force load size
                _ = getattr(item.variant, 'color', None)  # Force load color
                if hasattr(item.variant, 'product'):
                    _ = getattr(item.variant.product, 'name', None)  # Force load product name
    
    return order

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
        
        # Create order
        db_order = models.Order(
            customer_id=order.customer_id,
            order_date=order.order_date,
            status=order.status
        )
        db.add(db_order)
        db.flush()  # Flush to get the order ID
        
        # Create order items
        for item_data in items_data:
            # Verify variant exists
            variant = db.query(models.Variant).filter(models.Variant.id == item_data.variant_id).first()
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Variant {item_data.variant_id} not found"
                )
            
            # Check if there's enough stock
            if variant.stock < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for variant {variant.id}. Available: {variant.stock}, Requested: {item_data.quantity}"
                )
            
            # Create order item
            db_order_item = models.OrderItem(
                order_id=db_order.id,
                variant_id=item_data.variant_id,
                quantity=item_data.quantity,
                price=item_data.price
            )
            db.add(db_order_item)
            
            # Update variant stock
            variant.stock -= item_data.quantity
            db.add(variant)
        
        db.commit()
        
        # Reload the order with all relationships
        return _load_order_with_relationships(db, db_order.id)
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

@router.get("/", response_model=List[OrderOut])
def get_orders(
    start_date: str = None, 
    end_date: str = None, 
    limit: int = 100, 
    skip: int = 0, 
    db: Session = Depends(get_db)
):
    try:
        # Base query with preloaded relationships
        query = db.query(models.Order).options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product)
        )
        
        # Filter by date range if specified
        if start_date or end_date:
            from datetime import datetime, time
            
            try:
                # Parse dates
                if start_date:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    start_datetime = datetime.combine(start_datetime.date(), time.min)
                    query = query.filter(models.Order.order_date >= start_datetime)
                
                if end_date:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    end_datetime = datetime.combine(end_datetime.date(), time.max)
                    query = query.filter(models.Order.order_date <= end_datetime)
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid date format. Expected yyyy-MM-dd, received: start_date='{start_date}', end_date='{end_date}'"
                )
        
        # Apply offset and limit for pagination
        query = query.order_by(models.Order.order_date.desc()).offset(skip).limit(limit)
        
        # Execute query
        results = query.all()
        
        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error when querying orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = _load_order_with_relationships(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Force load relationships
    if order.items:
        for i, item in enumerate(order.items):
            if item.variant:
                # Access variant attributes to ensure they're loaded
                size = item.variant.size
                color = item.variant.color
                if item.variant.product:
                    # Access product name to ensure it's loaded
                    name = item.variant.product.name
    
    return order

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    try:
        # Check if order exists
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order fields
        if order_update.status is not None:
            order.status = order_update.status
        
        if order_update.order_date is not None:
            order.order_date = order_update.order_date
        
        if order_update.customer_id is not None:
            # Verify customer exists
            customer = db.query(models.Customer).filter(models.Customer.id == order_update.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer {order_update.customer_id} not found"
                )
            order.customer_id = order_update.customer_id
        
        # Update items if provided
        if order_update.items:
            # Keep track of existing items
            existing_item_ids = [item.id for item in order.items]
            updated_item_ids = []
            
            for item_update in order_update.items:
                if item_update.id:  # Update existing item
                    updated_item_ids.append(item_update.id)
                    item = db.query(models.OrderItem).filter(models.OrderItem.id == item_update.id).first()
                    
                    if not item:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Order item {item_update.id} not found"
                        )
                    
                    # Adjust inventory if quantity changes
                    old_quantity = item.quantity
                    new_quantity = item_update.quantity if item_update.quantity is not None else old_quantity
                    
                    if old_quantity != new_quantity:
                        variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
                        if variant:
                            # Return old quantity to stock
                            variant.stock += old_quantity
                            
                            # Take new quantity from stock
                            if variant.stock < new_quantity:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Not enough stock for variant {variant.id}. Available: {variant.stock}, Requested: {new_quantity}"
                                )
                            
                            variant.stock -= new_quantity
                            db.add(variant)
                    
                    # Update the item
                    if item_update.quantity is not None:
                        item.quantity = item_update.quantity
                    
                    if item_update.price is not None:
                        item.price = item_update.price
                    
                    if item_update.variant_id is not None:
                        # Verify variant exists
                        variant = db.query(models.Variant).filter(models.Variant.id == item_update.variant_id).first()
                        if not variant:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Variant {item_update.variant_id} not found"
                            )
                        item.variant_id = item_update.variant_id
                    
                    db.add(item)
                
                else:  # Add new item
                    # Verify variant exists
                    variant = db.query(models.Variant).filter(models.Variant.id == item_update.variant_id).first()
                    if not variant:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Variant {item_update.variant_id} not found"
                        )
                    
                    # Check if there's enough stock
                    if variant.stock < item_update.quantity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Not enough stock for variant {variant.id}. Available: {variant.stock}, Requested: {item_update.quantity}"
                        )
                    
                    # Create new order item
                    new_item = models.OrderItem(
                        order_id=order_id,
                        variant_id=item_update.variant_id,
                        quantity=item_update.quantity,
                        price=item_update.price
                    )
                    db.add(new_item)
                    
                    # Update variant stock
                    variant.stock -= item_update.quantity
                    db.add(variant)
            
            # Remove items that weren't updated
            items_to_delete = [item_id for item_id in existing_item_ids if item_id not in updated_item_ids]
            for item_id in items_to_delete:
                item = db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()
                if item:
                    # Return quantity to stock
                    variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
                    if variant:
                        variant.stock += item.quantity
                        db.add(variant)
                    
                    # Delete the item
                    db.delete(item)
        
        db.commit()
        
        # Reload the order with all relationships
        return _load_order_with_relationships(db, order_id)
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order: {str(e)}"
        )

@router.delete("/{order_id}", response_model=OrderOut)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        # Check if order exists
        order = _load_order_with_relationships(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Store order data for return
        order_data = OrderOut.from_orm(order)
        
        # Return items to inventory
        for item in order.items:
            variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
            if variant:
                variant.stock += item.quantity
                db.add(variant)
        
        # Delete order (this will cascade delete order items)
        db.delete(order)
        db.commit()
        
        return order_data
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting order: {str(e)}"
        )
