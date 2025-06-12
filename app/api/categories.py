from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[Category])
def list_categories(db: Session = Depends(get_db)):
    try:
        categories = db.query(models.Category).all()
        # Calculate products_count for each category
        for category in categories:
            products_count = db.query(models.Product).filter(models.Product.category_id == category.id).count()
            setattr(category, "products_count", products_count)
        # Explicitly serialize to dicts to avoid tuple/dict mismatch
        return [Category.model_validate(category).model_dump() for category in categories]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )

@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        # Check if category with same name exists
        existing = db.query(models.Category).filter(
            models.Category.name == category.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category.name}' already exists"
            )
        
        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        # Set products_count for new category (will be 0)
        setattr(db_category, "products_count", 0)
        
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )

@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        
        # Calculate products_count for this category
        products_count = db.query(models.Product).filter(models.Product.category_id == category.id).count()
        setattr(category, "products_count", products_count)
        
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving category: {str(e)}"
        )

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        
        # Check if updated name conflicts with existing category
        existing = db.query(models.Category).filter(
            models.Category.name == category.name,
            models.Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category.name}' already exists"
            )
        
        for key, value in category.model_dump().items():
            setattr(db_category, key, value)
        
        db.commit()
        db.refresh(db_category)
        
        # Calculate products_count for updated category
        products_count = db.query(models.Product).filter(models.Product.category_id == db_category.id).count()
        setattr(db_category, "products_count", products_count)
        
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating category: {str(e)}"
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        
        # Check if category has associated products - fix the relationship check
        products = db.query(models.Product).filter(models.Product.category_id == category_id).count()
        if products > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category: {products} products are associated with it"
            )
        
        db.delete(db_category)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )
