from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api import products, variants, categories, sales, orders, stats, auth, expenses, product_images, customers

app = FastAPI(title="Shiakati Store Backend")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("static/images/products", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(variants.router, prefix="/variants", tags=["variants"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
app.include_router(product_images.router, prefix="/product-images", tags=["product_images"])