from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VariantBase(BaseModel):
    product_id: int
    size: Optional[str] = None
    color: Optional[str] = None
    barcode: str
    price: float
    quantity: int = 0

class VariantCreate(VariantBase):
    pass

class VariantUpdate(VariantBase):
    product_id: Optional[int] = None
    barcode: Optional[str] = None

class VariantOut(VariantBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
