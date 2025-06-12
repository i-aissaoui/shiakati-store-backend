from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

class DeliveryMethod(str, Enum):
    HOME = "home"
    DESK = "desk"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    variant_id: int
    quantity: int = Field(ge=1)
    price: Decimal = Field(ge=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    product_name: str = "Unknown Product" 
    size: str = "N/A"  # Changed from Optional[str] = None to ensure JSON always has a string
    color: str = "N/A"  # Changed from Optional[str] = None to ensure JSON always has a string
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            Decimal: lambda v: float(v)
        }
    }
    
    @classmethod
    def from_orm(cls, item):
        # Start with a fresh dict instead of copying __dict__
        data = {
            'id': item.id,
            'variant_id': item.variant_id,
            'quantity': item.quantity,
            'price': item.price,
            'product_name': "Unknown Product",
            'size': "N/A",  # Default to N/A instead of None
            'color': "N/A"  # Default to N/A instead of None
        }
        
        # Get variant info and product name
        variant = getattr(item, 'variant', None)
        
        if variant is not None:  # Check using 'is not None' to handle falsy values
            # Get product info
            product = getattr(variant, 'product', None)
            if product is not None:
                data['product_name'] = product.name
                
            # Get variant details - checking explicitly for None
            if hasattr(variant, 'size') and variant.size is not None and variant.size != "" and variant.size.lower() != "none":
                data['size'] = variant.size
            else:
                data['size'] = "N/A"
                
            if hasattr(variant, 'color') and variant.color is not None and variant.color != "" and variant.color.lower() != "none":
                data['color'] = variant.color
            else:
                data['color'] = "N/A"
        
        return cls(**data)

class OrderBase(BaseModel):
    customer_id: int
    wilaya: str = Field(..., min_length=1)
    commune: str = Field(..., min_length=1)
    delivery_method: DeliveryMethod
    notes: Optional[str] = None
    total: Decimal = Field(ge=0)
    
class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @validator('total')
    def validate_total(cls, v, values):
        if 'items' in values:
            # Calculate total from items
            total = sum(item.price * item.quantity for item in values['items'])
            if abs(v - total) > Decimal('0.01'):  # Allow for small rounding differences
                raise ValueError("Total must match sum of item prices")
        return v

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    wilaya: Optional[str] = None
    commune: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None

class OrderItemUpdate(BaseModel):
    variant_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=1)
    price: Optional[Decimal] = Field(None, ge=0)

class OrderOut(BaseModel):
    id: int
    customer_id: int
    customer_name: str = "Unknown Customer"
    phone_number: str = "No Phone"
    wilaya: str
    commune: str
    delivery_method: DeliveryMethod
    order_time: datetime
    status: str
    notes: Optional[str] = None
    total: Decimal
    items: List[OrderItemOut] = []
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    }

    @classmethod
    def from_orm(cls, order):
        # Start with a fresh dict instead of copying __dict__
        data = {
            'id': order.id,
            'customer_id': order.customer_id,
            'wilaya': order.wilaya,
            'commune': order.commune,
            'delivery_method': order.delivery_method,
            'order_time': order.order_time,
            'status': order.status,
            'notes': order.notes,
            'total': order.total
        }
        
        # Explicitly handle customer info by accessing the relationship directly
        if order.customer:  # This forces SQLAlchemy to load the relationship
            data['customer_name'] = order.customer.name
            data['phone_number'] = order.customer.phone_number
        else:
            data['customer_name'] = "Unknown Customer"
            data['phone_number'] = "No Phone"
            
        # Process items separately to use the OrderItemOut.from_orm method
        items = getattr(order, 'items', None)
        if items is not None:  # Check using 'is not None' to handle empty lists
            data['items'] = [OrderItemOut.from_orm(item) for item in items]
        else:
            data['items'] = []
        
        # Clean up sample order notes
        notes = data.get('notes')
        if notes and isinstance(notes, str) and notes.startswith('Sample order'):
            data['notes'] = None
        
        # Validate and create the order
        try:
            return cls(**data)
        except Exception as e:
            raise
