from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class SaleItemBase(BaseModel):
    variant_id: Optional[int] = None  # Make variant_id optional to handle NULL values
    quantity: Decimal = Field(gt=0)  # Allow any positive number
    price: Decimal = Field(gt=0)  # Allow any positive number

class SaleBase(BaseModel):
    items: List[SaleItemBase]
    total: Decimal = Field(ge=0)  # Total amount must be >= 0

    @validator('total')
    def validate_total(cls, v, values):
        if 'items' in values:
            total = sum(item.price * item.quantity for item in values['items'])
            if abs(v - total) > Decimal('0.01'):  # Allow for small rounding differences
                raise ValueError("Total must match sum of item prices")
        return v

class SaleCreate(SaleBase):
    pass

class SaleItemOut(SaleItemBase):
    id: int
    product_name: str = "Unknown Product"  # Default value if product is missing
    size: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    id: int
    sale_time: datetime
    total: Decimal
    items: List[SaleItemOut]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)  # Convert to float for JSON serialization
        }