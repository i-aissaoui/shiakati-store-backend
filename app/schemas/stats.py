from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class TimeSeriesPoint(BaseModel):
    date: datetime
    value: float

class CategoryStats(BaseModel):
    id: int
    name: str
    total_sales: float
    total_revenue: float

class ProductStats(BaseModel):
    id: int
    name: str
    category_name: str
    total_sales: float
    total_revenue: float
    current_stock: float

class StatsSummary(BaseModel):
    total_sales: float
    total_orders: int
    total_revenue: float
    total_profit: float
    sales_over_time: List[TimeSeriesPoint] = []
    top_categories: List[CategoryStats] = []
    top_products: List[ProductStats] = []

class InventorySummary(BaseModel):
    product_id: int
    product_name: str
    category: str
    variant_id: int
    size: str | None
    color: str | None
    barcode: str
    price: float
    quantity: float

class ProductSaleSummary(BaseModel):
    product_id: int
    product_name: str
    total_quantity: float
    total_revenue: float

class SalesOverTime(BaseModel):
    date: date
    revenue: float
    num_sales: int