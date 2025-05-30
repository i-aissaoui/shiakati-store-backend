from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DeliveryMethod(str, Enum):
    HOME = "home"
    DESK = "desk"

class OrderStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class OrderBase(BaseModel):
    customer_name: str
    phone_number: str
    age: Optional[int] = None
    wilaya: str
    commune: str
    delivery_method: DeliveryMethod
    variant_id: int
    quantity: int = 1
    
class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: OrderStatus

class OrderOut(OrderBase):
    id: int
    order_time: datetime
    status: str
    
    class Config:
        orm_mode = True
