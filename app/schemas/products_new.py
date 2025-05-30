from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .variant import VariantOut

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: int = Field(..., description="ID of the category this product belongs to")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    category_name: str
    created_at: datetime
    variants_count: int = 0
    total_stock: float = 0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductDetailOut(ProductOut):
    variants: List[VariantOut] = []
    
    class Config:
        from_attributes = True
