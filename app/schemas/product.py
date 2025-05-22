from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .variant import VariantOut

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductDetailOut(ProductOut):
    variants: List[VariantOut] = []
    
    class Config:
        orm_mode = True 