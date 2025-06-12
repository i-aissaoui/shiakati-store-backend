from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, ProductDetailOut
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, ProductDetailOut
from typing import List
from sqlalchemy.orm import joinedload

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ProductOut])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        # Join load categories and variants with proper relationships
        products = (db.query(models.Product)
                   .options(joinedload(models.Product.category),
                           joinedload(models.Product.variants))
                   .offset(skip)
                   .limit(limit)
                   .all())
        
        # Validate and process products
        validated_products = []
        for product in products:
            try:
                if not product.category:                    continue
                    
                # Add computed fields with proper error handling
                category_name = product.category.name if product.category else None
                variants = product.variants or []
                variants_count = len(variants)
                total_stock = sum(float(v.quantity or 0) for v in variants)
                
                setattr(product, "category_name", category_name)
                setattr(product, "variants_count", variants_count)
                setattr(product, "total_stock", total_stock)
                
                validated_products.append(product)
            except Exception as e:
                continue
        
        return validated_products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products: {str(e)}"
        )

@router.get("/{product_id}", response_model=ProductDetailOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        # Join load variants and category with proper relationships
        db_product = (db.query(models.Product)
                     .options(joinedload(models.Product.variants),
                             joinedload(models.Product.category))
                     .filter(models.Product.id == product_id)
                     .first())
        
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        
        # Add computed fields with proper error handling
        try:
            # Handle category fields
            setattr(db_product, "category_name", db_product.category.name if db_product.category else "Uncategorized")
            
            # Handle variants fields
            variants = db_product.variants or []
            variants_count = len(variants)
            total_stock = sum(float(v.quantity or 0) for v in variants)
            
            setattr(db_product, "variants_count", variants_count)
            setattr(db_product, "total_stock", total_stock)
            
            return db_product
            
        except Exception as e:
            # Set default values on error
            setattr(db_product, "category_name", "Uncategorized")
            setattr(db_product, "variants_count", 0)
            setattr(db_product, "total_stock", 0)
            return db_product
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(e)}"
        )

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        # Verify category exists
        category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product.category_id} not found"
            )
        
        db_product = models.Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # Include category_name in response
        setattr(db_product, "category_name", category.name)
        setattr(db_product, "variants_count", 0)
        setattr(db_product, "total_stock", 0)
        
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        
        if product.category_id is not None:
            # Verify new category exists
            category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {product.category_id} not found"
                )
        
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
        
        # Include computed fields in response
        setattr(db_product, "category_name", db_product.category.name)
        setattr(db_product, "variants_count", len(db_product.variants))
        setattr(db_product, "total_stock", sum(float(v.quantity) for v in db_product.variants))
        
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {str(e)}"
        )

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"ok": True}
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        # Verify category exists
        category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product.category_id} not found"
            )
        
        db_product = models.Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # Include category_name in response
        setattr(db_product, "category_name", category.name)
        setattr(db_product, "variants_count", 0)
        setattr(db_product, "total_stock", 0)
        
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )

@router.get("/", response_model=List[ProductOut])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        # Join load categories and variants with proper relationships
        products = (db.query(models.Product)
                   .options(joinedload(models.Product.category),
                           joinedload(models.Product.variants))
                   .offset(skip)
                   .limit(limit)
                   .all())
        
        # Validate and process products
        validated_products = []
        for product in products:
            try:
                if not product.category:                    continue
                    
                # Add computed fields with proper error handling
                category_name = product.category.name if product.category else None
                variants = product.variants or []
                variants_count = len(variants)
                total_stock = sum(float(v.quantity or 0) for v in variants)
                
                setattr(product, "category_name", category_name)
                setattr(product, "variants_count", variants_count)
                setattr(product, "total_stock", total_stock)
                
                validated_products.append(product)
            except Exception as e:
                continue
        
        return validated_products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products: {str(e)}"
        )

@router.get("/{product_id}", response_model=ProductDetailOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        # Join load variants and category with proper relationships
        db_product = (db.query(models.Product)
                     .options(joinedload(models.Product.variants),
                             joinedload(models.Product.category))
                     .filter(models.Product.id == product_id)
                     .first())
        
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        
        # Add computed fields with proper error handling
        try:
            # Handle category fields
            setattr(db_product, "category_name", db_product.category.name if db_product.category else "Uncategorized")
            
            # Handle variants fields
            variants = db_product.variants or []
            variants_count = len(variants)
            total_stock = sum(float(v.quantity or 0) for v in variants)
            
            setattr(db_product, "variants_count", variants_count)
            setattr(db_product, "total_stock", total_stock)
            
            return db_product
            
        except Exception as e:
            # Set default values on error
            setattr(db_product, "category_name", "Uncategorized")
            setattr(db_product, "variants_count", 0)
            setattr(db_product, "total_stock", 0)
            return db_product
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(e)}"
        )

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_update.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=ProductOut)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return db_product