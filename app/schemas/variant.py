from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VariantBase(BaseModel):
    product_id: int
    size: Optional[str] = None
    color: Optional[str] = None
    price: float = Field(..., ge=0)
    cost_price: Optional[float] = Field(None, ge=0)  # Added cost_price field
    quantity: float = Field(default=0, ge=0)
    barcode: Optional[str] = None

class VariantCreate(VariantBase):
    pass

class VariantUpdate(BaseModel):
    product_id: Optional[int] = None
    size: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[float] = Field(None, ge=0)
    barcode: Optional[str] = None

class VariantOut(BaseModel):
    id: int
    product_id: int
    size: Optional[str]
    color: Optional[str]
    barcode: str
    price: float
    cost_price: Optional[float]  # Added cost_price field
    quantity: float
    created_at: datetime
    product_name: Optional[str] = None  # Added product_name field
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
