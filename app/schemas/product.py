from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from .variant import VariantOut

class ProductBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product name (supports Unicode characters)",
        example="تيشيرت قطن"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Product description (supports Unicode characters)",
        example="قميص قطني بجودة عالية"
    )
    category_id: int = Field(
        ...,
        description="ID of the category this product belongs to"
    )

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
    category_id: Optional[int] = None
    category_name: str = "Uncategorized"
    created_at: datetime
    variants_count: int = 0
    total_stock: float = 0
    
    model_config = ConfigDict(from_attributes=True)

class ProductDetailOut(ProductOut):
    variants: List[VariantOut] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)