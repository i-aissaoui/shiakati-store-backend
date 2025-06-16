#!/usr/bin/env python3

import requests
import json

# Test updating a product with minimal data (no show_on_website or image_url)
def test_update_product():
    url = "http://localhost:8000/api/products/1"
    
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
    test_update_product()
