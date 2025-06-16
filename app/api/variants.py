from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.db import models
from app.schemas.variant import VariantCreate, VariantOut, VariantUpdate
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[VariantOut])
@router.get("/", response_model=List[VariantOut])
def list_variants(db: Session = Depends(get_db)):
    return db.query(models.Variant).all()

@router.get("/{variant_id}", response_model=VariantOut)
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

@router.get("/barcode/{barcode}", response_model=VariantOut)
@router.get("/barcode/{barcode}/", response_model=VariantOut)
def get_variant_by_barcode(barcode: str, db: Session = Depends(get_db)):
    variant = db.query(models.Variant).options(
        joinedload(models.Variant.product)
    ).filter(models.Variant.barcode == barcode).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Add product name to the response
    if variant.product:
        setattr(variant, "product_name", variant.product.name)
    else:
        setattr(variant, "product_name", "Unknown Product")
    
    return variant

@router.post("", response_model=VariantOut)
@router.post("/", response_model=VariantOut)
def create_variant(variant: VariantCreate, db: Session = Depends(get_db)):
    try:
        # Verify product exists
        product = db.query(models.Product).filter(models.Product.id == variant.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Use provided barcode if any, otherwise generate one
        barcode = variant.barcode
        if not barcode:
            from app.utils.barcode import generate_unique_barcode
            barcode = generate_unique_barcode(db, prefix=str(variant.product_id).zfill(3))
        else:
            # Check if barcode is unique
            existing_variant = db.query(models.Variant).filter(models.Variant.barcode == barcode).first()
            if existing_variant:
                raise HTTPException(status_code=400, detail="Barcode already exists")

        # Convert decimal values for precision
        from decimal import Decimal, ROUND_HALF_UP
        price = Decimal(str(variant.price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        quantity = Decimal(str(variant.quantity)).quantize(Decimal('0.003'), rounding=ROUND_HALF_UP)

        # Create variant
        db_variant = models.Variant(
            product_id=variant.product_id,
            size=variant.size,
            color=variant.color,
            barcode=barcode,
            price=price,
            quantity=quantity
        )
        
        db.add(db_variant)
        db.commit()
        db.refresh(db_variant)
        
        # Load relationships for response
        db_variant = db.query(models.Variant).options(
            joinedload(models.Variant.product).joinedload(models.Product.category)
        ).filter(models.Variant.id == db_variant.id).first()
        
        return db_variant
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating variant: {str(e)}")

@router.put("/{variant_id}", response_model=VariantOut)
def update_variant(variant_id: int, variant: VariantUpdate, db: Session = Depends(get_db)):
    db_variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    update_data = variant.dict(exclude_unset=True)
    
    # If updating barcode, check uniqueness
    if "barcode" in update_data and update_data["barcode"] != db_variant.barcode:
        existing_variant = db.query(models.Variant).filter(models.Variant.barcode == update_data["barcode"]).first()
        if existing_variant:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    # If updating product_id, check existence
    if "product_id" in update_data and update_data["product_id"] != db_variant.product_id:
        product = db.query(models.Product).filter(models.Product.id == update_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in update_data.items():
        setattr(db_variant, key, value)
    
    db.commit()
    db.refresh(db_variant)
    return db_variant

@router.delete("/{variant_id}")
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    db_variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Check if variant is referenced in any sale items
    sale_items = db.query(models.SaleItem).filter(models.SaleItem.variant_id == variant_id).count()
    if sale_items > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete: Variant is used in {sale_items} sales. Delete related sales first."
        )
    
    try:
        db.delete(db_variant)
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search/", response_model=List[VariantOut])
@router.get("/search", response_model=List[VariantOut])
def search_variants(barcode: str = None, name: str = None, product_id: int = None, db: Session = Depends(get_db)):
    """Search for variants by barcode, name, or product id."""
    query = db.query(models.Variant)
    
    if barcode:
        # Check if this is an SKU barcode format
        if barcode.startswith("SKU"):
            try:
                # Extract the numeric part after 'SKU'
                sku_product_id = int(barcode[3:])
                print(f"Extracted product_id {sku_product_id} from SKU barcode: {barcode}")
                
                # Add a filter for product_id
                query = query.filter(models.Variant.product_id == sku_product_id)
            except ValueError:
                # If we can't extract a number, just use the regular LIKE search
                print(f"Could not extract product_id from SKU barcode: {barcode}")
                query = query.filter(models.Variant.barcode.ilike(f"%{barcode}%"))
        else:
            # Regular barcode search with LIKE
            query = query.filter(models.Variant.barcode.ilike(f"%{barcode}%"))
    
    if product_id:
        query = query.filter(models.Variant.product_id == product_id)
        
    if name:
        # Join with Product to search by product name
        query = query.join(models.Product).filter(models.Product.name.ilike(f"%{name}%"))
    
    if not barcode and not name and not product_id:
        raise HTTPException(status_code=400, detail="At least one search parameter (barcode, name, or product_id) is required")
    
    # Limit results to prevent overloading    
    results = query.limit(100).all()
    
    # If no results found with LIKE search and barcode is provided, try exact match as fallback
    if not results and barcode:
        exact_match = db.query(models.Variant).filter(models.Variant.barcode == barcode).first()
        if exact_match:
            return [exact_match]
            
    return results

@router.get("/product/{product_id}", response_model=List[VariantOut])
@router.get("/product/{product_id}/", response_model=List[VariantOut])
def get_variants_by_product_id(product_id: int, db: Session = Depends(get_db)):
    """Get all variants for a specific product ID."""
    variants = db.query(models.Variant).filter(models.Variant.product_id == product_id).all()
    if not variants:
        # Return empty list rather than 404 to simplify client handling
        return []
    return variants
