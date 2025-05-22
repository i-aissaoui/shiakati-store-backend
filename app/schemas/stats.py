from pydantic import BaseModel
from typing import Optional

class StatsSummary(BaseModel):
    total_sales: int
    total_orders: int
    total_profit: float
    total_revenue: float

class InventorySummary(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    variant_id: int
    size: Optional[str] = None
    color: Optional[str] = None
    barcode: str
    price: float
    quantity: int

class ProductSaleSummary(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int
    total_revenue: float 