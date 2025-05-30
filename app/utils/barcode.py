import random
import string
from sqlalchemy.orm import Session
from app.db import models

def generate_unique_barcode(db: Session, prefix: str = '') -> str:
    """Generate a unique barcode with optional prefix.
    Format: PREFIX + PRODUCTID + RANDOM + CHECKSUM
    """
    while True:
        # Generate random part (8 digits)
        random_part = ''.join(random.choices(string.digits, k=8))
        
        # Combine parts
        barcode = f"{prefix}{random_part}"
        
        # Add checksum digit
        total = sum((3 if i % 2 else 1) * int(d) for i, d in enumerate(barcode))
        checksum = (10 - (total % 10)) % 10
        barcode = f"{barcode}{checksum}"
        
        # Check if barcode exists
        exists = db.query(models.Variant).filter(
            models.Variant.barcode == barcode
        ).first()
        
        if not exists:
            return barcode
