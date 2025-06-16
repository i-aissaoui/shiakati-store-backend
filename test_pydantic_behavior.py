#!/usr/bin/env python3

from app.schemas.product import ProductUpdate
import json

def test_pydantic_behavior():
    """Test how Pydantic handles the ProductUpdate schema"""
    
    print("=== Testing Pydantic ProductUpdate behavior ===")
    
    # Test 1: Empty dict (simulating no data sent)
    print("\n1. Empty dict:")
    empty_data = {}
    product_update = ProductUpdate(**empty_data)
    print(f"   Raw object: {product_update}")
    print(f"   model_dump(): {product_update.model_dump()}")
    print(f"   model_dump(exclude_unset=True): {product_update.model_dump(exclude_unset=True)}")
    print(f"   model_dump(exclude_none=True): {product_update.model_dump(exclude_none=True)}")
    print(f"   model_dump(exclude_unset=True, exclude_none=True): {product_update.model_dump(exclude_unset=True, exclude_none=True)}")
    
    # Test 2: Partial data (simulating desktop app request)
    print("\n2. Partial data (name and description only):")
    partial_data = {"name": "Test Product", "description": "Test description"}
    product_update = ProductUpdate(**partial_data)
    print(f"   Raw object: {product_update}")
    print(f"   model_dump(): {product_update.model_dump()}")
    print(f"   model_dump(exclude_unset=True): {product_update.model_dump(exclude_unset=True)}")
    print(f"   model_dump(exclude_none=True): {product_update.model_dump(exclude_none=True)}")
    print(f"   model_dump(exclude_unset=True, exclude_none=True): {product_update.model_dump(exclude_unset=True, exclude_none=True)}")
    
    # Test 3: Full data
    print("\n3. Full data:")
    full_data = {
        "name": "Test Product",
        "description": "Test description", 
        "category_id": 1,
        "image_url": "http://example.com/image.jpg",
        "show_on_website": 1
    }
    product_update = ProductUpdate(**full_data)
    print(f"   Raw object: {product_update}")
    print(f"   model_dump(): {product_update.model_dump()}")
    print(f"   model_dump(exclude_unset=True): {product_update.model_dump(exclude_unset=True)}")
    print(f"   model_dump(exclude_none=True): {product_update.model_dump(exclude_none=True)}")
    print(f"   model_dump(exclude_unset=True, exclude_none=True): {product_update.model_dump(exclude_unset=True, exclude_none=True)}")

if __name__ == "__main__":
    test_pydantic_behavior()
