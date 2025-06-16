from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
from pathlib import Path

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ImageResponse(BaseModel):
    """Response model for image operations"""
    image_url: str
    is_main: bool = False


@router.post("/upload/{product_id}", response_model=ImageResponse)
async def upload_product_image(
    product_id: int, 
    file: UploadFile = File(...), 
    set_as_main: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload an image for a product.
    All variants of this product will share the same images.
    """
    try:
        # Check if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {product_id} not found"
            )
            
        # Create directory for this product's images
        product_dir = f"static/images/products/product_{product_id}"
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
            
        # Update the product image URL if it's the first image or set_as_main is True
        image_url = f"/{file_path}"  
        
        if set_as_main or image_number == 1:
            product.image_url = image_url
            db.commit()
        
        return {"image_url": image_url, "is_main": set_as_main or image_number == 1}
    except HTTPException:
        raise
    except Exception as e:
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )


@router.get("/list/{product_id}", response_model=List[ImageResponse])
async def get_product_images(product_id: int, db: Session = Depends(get_db)):
    """Get all images for a product with the specified ID."""
    try:
        # Check if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {product_id} not found"
            )
            
        # Check the product's image directory
        product_dir = f"static/images/products/product_{product_id}"
        
        # If no directory, return empty list
        if not os.path.exists(product_dir):
            return []
            
        # Get all image files from the directory
        image_files = []
        
        image_files = [f for f in os.listdir(product_dir) 
                      if os.path.isfile(os.path.join(product_dir, f)) and 
                      f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
        # Create response objects for all images
        response_images = []
        for img in image_files:
            image_url = f"/{os.path.join(product_dir, img)}"
            is_main = (product.image_url == image_url)
            response_images.append({"image_url": image_url, "is_main": is_main})
            
        return response_images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product images: {str(e)}"
        )


@router.post("/set-main/{product_id}")
async def set_main_product_image(product_id: int, image_url: str, db: Session = Depends(get_db)):
    """Set a specific image as the main image for a product."""
    try:
        # Check if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {product_id} not found"
            )
        
        # Check if the image exists
        if not image_url.startswith("/"):
            image_url = f"/{image_url}"
            
        file_path = image_url[1:]  # Remove leading slash
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {image_url}"
            )
            
        # Set as main image
        product.image_url = image_url
        db.commit()
        
        return {"message": "Main image set successfully", "image_url": image_url}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting main image: {str(e)}"
        )


@router.delete("/delete/{product_id}")
async def delete_product_image(product_id: int, image_url: str = Query(..., description="URL of the image to delete"), db: Session = Depends(get_db)):
    """Delete a specific image for a product."""
    try:
        # Check if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {product_id} not found"
            )
        
        # Check if the image exists
        if not image_url.startswith("/"):
            image_url = f"/{image_url}"
            
        file_path = image_url[1:]  # Remove leading slash
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {image_url}"
            )
            
        # Check if it's the main image
        if product.image_url == image_url:
            # Get product directory
            product_dir = f"static/images/products/product_{product_id}"
            
            # Find other images that could be used as main
            other_images = [f for f in os.listdir(product_dir) 
                            if os.path.isfile(os.path.join(product_dir, f)) 
                            and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                            and f"/{os.path.join(product_dir, f)}" != image_url]
            
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


class VisibilityUpdate(BaseModel):
    show_on_website: int

@router.put("/website-visibility/{product_id}")
async def update_product_visibility(product_id: int, visibility_data: VisibilityUpdate, db: Session = Depends(get_db)):
    """Update whether a product is visible on the website."""
    try:
        # Check if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {product_id} not found"
            )
            
        # Validate value
        show_on_website = visibility_data.show_on_website
        if show_on_website not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="show_on_website must be either 0 (hidden) or 1 (visible)"
            )
        
        # Update visibility
        product.show_on_website = show_on_website
        db.commit()
        
        return {"message": f"Product visibility updated to {'visible' if show_on_website == 1 else 'hidden'}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product visibility: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product visibility: {str(e)}"
        )