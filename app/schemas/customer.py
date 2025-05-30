from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=8, max_length=20)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    phone_number: Optional[str] = None

class CustomerSummary(BaseModel):
    total_orders: int = 0
    total_spent: Decimal = Decimal('0')
    last_order_date: Optional[datetime] = None

class Customer(CustomerBase):
    id: int
    created_at: datetime
    summary: Optional[CustomerSummary] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: float
        }
