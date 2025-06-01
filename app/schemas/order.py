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
    size: Optional[str] = None
    color: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            Decimal: lambda v: float(v)
        }
    }
    
    @classmethod
    def from_orm(cls, item):
        # Create a copy of the item.__dict__ to avoid modifying the original
        data = dict(item.__dict__)
        
        # Remove SQLAlchemy internal attributes
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
        
        if hasattr(item, 'variant') and item.variant:
            if hasattr(item.variant, 'product') and item.variant.product:
                data['product_name'] = item.variant.product.name
            else:
                data['product_name'] = "Unknown Product"
            
            data['size'] = item.variant.size
            data['color'] = item.variant.color
        else:
            data['product_name'] = "Unknown Product"
            data['size'] = None
            data['color'] = None
        
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
    status: OrderStatus

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
        data = dict(order.__dict__)
        
        # Remove SQLAlchemy internal attributes
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
        
        # Handle customer info
        if hasattr(order, 'customer') and order.customer:
            data['customer_name'] = order.customer.name
            data['phone_number'] = order.customer.phone_number
        else:
            data['customer_name'] = "Unknown Customer"
            data['phone_number'] = "No Phone"
            
        # Process items separately to use the OrderItemOut.from_orm method
        if hasattr(order, 'items') and order.items:
            data['items'] = [OrderItemOut.from_orm(item) for item in order.items]
        else:
            data['items'] = []
        
        # Clean up sample order notes
        if data.get('notes', '').startswith('Sample order'):
            data['notes'] = None
        
        return cls(**data)
