from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.db import models
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, ProductDetailOut
from typing import List, Optional
import shutil
import os
from pathlib import Path
import uuid

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
                # # if not product.category: continue # Commented out to show all products # Commented out to show all products
                    
                # Add computed fields with proper error handling
                category_name = product.category.name if product.category else "Uncategorized"
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
                # # if not product.category: continue # Commented out to show all products # Commented out to show all products
                    
                # Add computed fields with proper error handling
                category_name = product.category.name if product.category else "Uncategorized"
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

# Create an endpoint to handle file uploads for product images
@router.post("/upload-image/{barcode}")
async def upload_product_image(barcode: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an image for a product variant with the specified barcode.
    The image will be stored in a directory named after the barcode.
    """
    try:
        # Find the variant with this barcode
        variant = db.query(models.Variant).filter(models.Variant.barcode == barcode).first()
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Variant with barcode {barcode} not found"
            )
        
        # Get the product for this variant
        product_id = variant.product_id
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product not found for variant with barcode {barcode}"
            )
            
        # Create directory for this product's images
        product_dir = f"static/images/products/{barcode}"
        os.makedirs(product_dir, exist_ok=True)
        
        # Check how many images already exist for this product
        existing_files = os.listdir(product_dir) if os.path.exists(product_dir) else []
        image_number = len(existing_files) + 1
        
        # Generate a unique filename for the image
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"product_{image_number}{file_extension}"
        file_path = os.path.join(product_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update the product image URL
        # If it's the first image, update the main image_url
        # Ensure consistent forward slashes for URL paths
        image_url = f"/{product_dir}/{unique_filename}".replace('\\', '/')
        
        print(f"[API DEBUG] Created image URL: {image_url}")
        
        if image_number == 1:
            product.image_url = image_url
        
        db.commit()
        
        return {"filename": unique_filename, "image_url": image_url}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )

# Also add a utility endpoint to generate a unique barcode
@router.get("/generate-barcode")
async def generate_unique_barcode(db: Session = Depends(get_db)):
    """Generate a unique barcode that doesn't exist in the database."""
    try:
        while True:
            # Generate a random barcode with "SKU" prefix
            new_barcode = f"SKU{uuid.uuid4().hex[:8].upper()}"
            
            # Check if it exists in the database
            exists = db.query(models.Variant).filter(models.Variant.barcode == new_barcode).first()
            if not exists:
                return {"barcode": new_barcode}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating barcode: {str(e)}"
        )

@router.get("/product-images/{barcode}")
async def get_product_images(barcode: str, db: Session = Depends(get_db)):
    """Get all images for a product with the specified barcode."""
    try:
        # Find the variant with this barcode
        variant = db.query(models.Variant).filter(models.Variant.barcode == barcode).first()
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Variant with barcode {barcode} not found"
            )
        
        # Get the product for this variant
        product_id = variant.product_id
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product not found for variant with barcode {barcode}"
            )
            
        # Check the product's image directory
        product_dir = f"static/images/products/{barcode}"
        if not os.path.exists(product_dir):
            print(f"[API DEBUG] Image directory not found for barcode {barcode}: {product_dir}")
            return {"images": []}
            
        # Get all image files in this directory
        image_files = [f for f in os.listdir(product_dir) 
                      if os.path.isfile(os.path.join(product_dir, f)) and 
                      f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        print(f"[API DEBUG] Found {len(image_files)} images for barcode {barcode} in {product_dir}")
        print(f"[API DEBUG] Image files: {image_files}")
        
        # Create URLs for all images with proper forward slashes
        # Replace os.path.join with explicit path construction using forward slashes
        image_urls = [f"/{product_dir}/{img}".replace('\\', '/') for img in image_files]
        
        print(f"[API DEBUG] Returning {len(image_urls)} image URLs")
        # Add debugging to see actual URLs being returned
        if image_urls:
            print(f"[API DEBUG] Sample URL: {image_urls[0]}")
        return {"images": image_urls, "main_image": product.image_url}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[API ERROR] Error getting product images: {str(e)}")
        print(f"[API ERROR] Traceback: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product images: {str(e)}"
        )

@router.delete("/product-image/{barcode}/{filename}")
async def delete_product_image(barcode: str, filename: str, db: Session = Depends(get_db)):
    """Delete a specific image for a product with the specified barcode."""
    try:
        # Find the variant with this barcode
        variant = db.query(models.Variant).filter(models.Variant.barcode == barcode).first()
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Variant with barcode {barcode} not found"
            )
        
        # Get the product for this variant
        product_id = variant.product_id
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product not found for variant with barcode {barcode}"
            )
            
        # Check the product's image directory
        product_dir = f"static/images/products/{barcode}"
        if not os.path.exists(product_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No image directory found for product with barcode {barcode}"
            )
            
        # Create full file path
        file_path = os.path.join(product_dir, filename)
        
        # Ensure the file exists and is within the product directory
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found"
            )
            
        # Check if it's the main image
        image_url = f"/{file_path}"
        if product.image_url == image_url:
            # If deleting the main image, check if there are other images to set as main
            other_images = [f for f in os.listdir(product_dir) 
                           if os.path.isfile(os.path.join(product_dir, f)) 
                           and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                           and f != filename]
            
            if other_images:
                # Set first alternative as the main image
                product.image_url = f"/{os.path.join(product_dir, other_images[0])}"
            else:
                # No other images, clear the image URL
                product.image_url = None
                
            db.commit()
        
        # Delete the file
        os.remove(file_path)
        
        return {"message": "Image deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product image: {str(e)}"
        )