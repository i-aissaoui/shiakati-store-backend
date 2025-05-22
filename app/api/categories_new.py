# filepath: /home/ismail/Desktop/projects/shiakati_store/desktop/app/api/categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.db.session import SessionLocal
from app.db import models
from app.schemas.category import CategoryOut
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    # Get distinct categories from products table
    categories = db.query(distinct(models.Product.category)).filter(models.Product.category != None).all()
    # Extract category names from result tuples
    return [category[0] for category in categories if category[0]]
