#!/usr/bin/env python3

import requests
import json

def create_test_product():
    """Create a test product first"""
    url = "http://localhost:8000/api/products/"
    
    # First, let's create a category
    category_url = "http://localhost:8000/api/categories/"
    category_data = {
        "name": "Test Category",
        "description": "Test category for products"
    }
    
    print("Creating test category...")
    try:
        cat_response = requests.post(category_url, json=category_data)
        print(f"Category response: {cat_response.status_code} - {cat_response.text}")
        
        if cat_response.status_code == 201:
            category_id = cat_response.json()["id"]
            print(f"✅ Category created with ID: {category_id}")
        else:
            # Try to get existing categories
            categories_response = requests.get(category_url)
            if categories_response.status_code == 200:
                categories = categories_response.json()
                if categories:
                    category_id = categories[0]["id"]
                    print(f"Using existing category ID: {category_id}")
                else:
                    print("❌ No categories available")
                    return None
            else:
                print("❌ Failed to create or get categories")
                return None
    except Exception as e:
        print(f"Error with category: {e}")
        return None
    
    # Now create a product
    product_data = {
        "name": "Test Product",
        "description": "A test product for update testing",
        "category_id": category_id
    }
    
    print(f"Creating test product with data: {product_data}")
    try:
        response = requests.post(url, json=product_data)
        print(f"Product response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Product created with ID: {product['id']}")
            return product["id"]
        else:
            print("❌ Failed to create product")
            return None
            
    except Exception as e:
        print(f"Error creating product: {e}")
        return None

def test_update_product(product_id):
    """Test updating a product with minimal data"""
    url = f"http://localhost:8000/api/products/{product_id}"
    
    # This is what the desktop app is likely sending - minimal data
    update_data = {
        "name": "Updated Product Name",
        "description": "Updated description"
    }
    
    print(f"Sending update request with data: {update_data}")
    
    try:
        response = requests.put(url, json=update_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Update successful!")
        else:
            print("❌ Update failed!")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    product_id = create_test_product()
    if product_id:
        print(f"\nTesting update on product ID: {product_id}")
        test_update_product(product_id)
    else:
        print("Could not create test product")
