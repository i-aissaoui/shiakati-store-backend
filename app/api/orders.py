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
    # Load orders with all relationships
    try:
        # Load all orders first with their relationships
        orders = db.query(models.Order).options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product)
        ).order_by(models.Order.order_time.desc()).all()

        results = []
        for order in orders:
            try:
                # Force load relationships
                for item in order.items:
                    if item.variant:
                        # Access variant attributes to ensure they're loaded
                        _ = item.variant.size
                        _ = item.variant.color
                        if item.variant.product:
                            # Access product name to ensure it's loaded
                            _ = item.variant.product.name

                # Create OrderOut instance
                order_data = OrderOut.from_orm(order)
                results.append(order_data)
                
            except Exception as e:
                print(f"Error processing order {order.id}: {str(e)}")
                # Continue processing other orders
                continue

        return results

    except Exception as e:
        print(f"Error loading orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    print(f"=== BACKEND: Getting individual order {order_id} ===")
    order = _load_order_with_relationships(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    print(f"BACKEND INDIVIDUAL: Loaded order {order_id} with {len(order.items)} items")
    
    # Force load relationships
    if order.items:
        for i, item in enumerate(order.items):
            print(f"BACKEND INDIVIDUAL: Item {i}: {item}")
            if item.variant:
                # Access variant attributes to ensure they're loaded
                size = item.variant.size
                color = item.variant.color
                print(f"BACKEND INDIVIDUAL: Item {i} variant - size: '{size}', color: '{color}'")
                if item.variant.product:
                    # Access product name to ensure it's loaded
                    product_name = item.variant.product.name
                    print(f"BACKEND INDIVIDUAL: Item {i} product name: '{product_name}'")
            else:
                print(f"BACKEND INDIVIDUAL: Item {i} has no variant!")
    
    # Convert to OrderOut schema
    order_out = OrderOut.from_orm(order)
    print(f"BACKEND INDIVIDUAL: OrderOut items: {order_out.items}")
    for i, item in enumerate(order_out.items):
        print(f"BACKEND INDIVIDUAL: OrderOut item {i}: size='{item.size}', color='{item.color}', product_name='{item.product_name}'")
    
    return order_out

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update order details including status, notes, and delivery information."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update only provided fields
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(order, field):
            setattr(order, field, value)
    
    db.commit()
    
    # Load the complete order with relationships
    order = _load_order_with_relationships(db, order_id)
    return order

@router.put("/{order_id}/items/{item_id}", response_model=OrderOut)
def update_order_item(order_id: int, item_id: int, item_update: OrderItemUpdate, db: Session = Depends(get_db)):
    """Update a specific order item."""
    # Check if order exists
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get the order item
    order_item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.order_id == order_id
    ).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    # Update only provided fields
    update_data = item_update.dict(exclude_unset=True)
    old_quantity = order_item.quantity
    
    # If variant_id is being changed, validate the new variant
    if 'variant_id' in update_data:
        new_variant = db.query(models.Variant).filter(models.Variant.id == update_data['variant_id']).first()
        if not new_variant:
            raise HTTPException(status_code=404, detail="New variant not found")
        
        # Restore quantity to old variant
        old_variant = db.query(models.Variant).filter(models.Variant.id == order_item.variant_id).first()
        if old_variant:
            old_variant.quantity += old_quantity
    
    # Apply updates
    for field, value in update_data.items():
        setattr(order_item, field, value)
    
    # Handle inventory updates for quantity changes
    new_quantity = order_item.quantity
    if 'quantity' in update_data or 'variant_id' in update_data:
        current_variant = db.query(models.Variant).filter(models.Variant.id == order_item.variant_id).first()
        if current_variant:
            if 'variant_id' in update_data:
                # New variant, check if we have enough stock
                if current_variant.quantity < new_quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough stock for variant {order_item.variant_id}. Available: {current_variant.quantity}"
                    )
                current_variant.quantity -= new_quantity
            else:
                # Same variant, adjust quantity difference
                quantity_diff = new_quantity - old_quantity
                if current_variant.quantity < quantity_diff:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough stock for variant {order_item.variant_id}. Available: {current_variant.quantity}"
                    )
                current_variant.quantity -= quantity_diff
    
    # Recalculate order total
    total = sum(item.price * item.quantity for item in order.items)
    order.total = total
    
    db.commit()
    
    # Load and return the complete order
    order = _load_order_with_relationships(db, order_id)
    return order

@router.post("/{order_id}/items", response_model=OrderOut)
def add_order_item(order_id: int, item_create: OrderItemCreate, db: Session = Depends(get_db)):
    """Add a new item to an existing order."""
    # Check if order exists
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if variant exists and has enough stock
    variant = db.query(models.Variant).filter(models.Variant.id == item_create.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    if variant.quantity < item_create.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock for variant {item_create.variant_id}. Available: {variant.quantity}"
        )
    
    # Create new order item
    new_item = models.OrderItem(
        order_id=order_id,
        variant_id=item_create.variant_id,
        quantity=item_create.quantity,
        price=item_create.price
    )
    db.add(new_item)
    
    # Update inventory
    variant.quantity -= item_create.quantity
    
    # Recalculate order total
    total = sum(item.price * item.quantity for item in order.items) + (item_create.price * item_create.quantity)
    order.total = total
    
    db.commit()
    
    # Load and return the complete order
    order = _load_order_with_relationships(db, order_id)
    return order

@router.delete("/{order_id}/items/{item_id}", response_model=OrderOut)
def delete_order_item(order_id: int, item_id: int, db: Session = Depends(get_db)):
    """Delete an item from an order."""
    # Check if order exists
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get the order item
    order_item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.order_id == order_id
    ).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    # Restore inventory
    variant = db.query(models.Variant).filter(models.Variant.id == order_item.variant_id).first()
    if variant:
        variant.quantity += order_item.quantity
    
    # Remove the item
    db.delete(order_item)
    
    # Recalculate order total
    total = sum(item.price * item.quantity for item in order.items if item.id != item_id)
    order.total = total
    
    db.commit()
    
    # Load and return the complete order
    order = _load_order_with_relationships(db, order_id)
    return order

@router.get("/date-range", response_model=List[OrderOut])
@router.get("/date-range/", response_model=List[OrderOut])
def get_orders_by_date_range(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get orders between two dates (format: yyyy-MM-dd)."""
    try:
        # Parse dates
        from datetime import datetime, time
        
        # Parse start date with time at beginning of day
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        start_datetime = datetime.combine(start_datetime.date(), time.min)
        
        # Parse end date with time at end of day
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        end_datetime = datetime.combine(end_datetime.date(), time.max)
        
        # Query orders within date range with relationships
        orders = db.query(models.Order).options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.variant).joinedload(models.Variant.product)
        ).filter(
            models.Order.order_time >= start_datetime,
            models.Order.order_time <= end_datetime
        ).order_by(models.Order.order_time.desc()).all()
        
        results = []
        for order in orders:
            try:
                # Force load relationships
                for item in order.items:
                    if item.variant:
                        # Access variant attributes to ensure they're loaded
                        _ = item.variant.size
                        _ = item.variant.color
                        if item.variant.product:
                            # Access product name to ensure it's loaded
                            _ = item.variant.product.name

                # Create OrderOut instance
                order_data = OrderOut.from_orm(order)
                results.append(order_data)
                
            except Exception as e:
                print(f"Error processing order {order.id}: {str(e)}")
                # Continue processing other orders
                continue
                
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders by date range: {str(e)}"
        )

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an entire order."""
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Delete order items first (cascade should handle this, but being explicit)
        db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete()
        
        # Delete the order
        db.delete(order)
        db.commit()
        
        return {"message": f"Order {order_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting order: {str(e)}"
        )
