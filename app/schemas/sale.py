from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SaleBase(BaseModel):
    variant_id: int
    quantity: int = 1

class SaleCreate(SaleBase):
    pass

class SaleOut(SaleBase):
    id: int
    sale_time: datetime
    
    class Config:
        orm_mode = True 