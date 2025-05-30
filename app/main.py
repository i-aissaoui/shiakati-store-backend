from fastapi import FastAPI
from app.api import products, variants, categories, sales, orders, stats, auth

app = FastAPI(title="Shiakati Store Backend")

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(variants.router, prefix="/variants", tags=["variants"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(stats.router, prefix="/stats", tags=["stats"]) 