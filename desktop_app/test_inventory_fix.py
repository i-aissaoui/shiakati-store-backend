#!/usr/bin/env python3
"""
Test script to verify that the API client's get_inventory method returns data with both 'stock' and 'quantity' fields.
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing API client inventory data...")

try:
    # Import the APIClient class
    from src.utils.api_client import APIClient
    
    # Create an instance
    client = APIClient()
    
    # Check if get_inventory method exists
    if hasattr(client, 'get_inventory'):
        print("✅ get_inventory method exists")
        
        # Try calling the method
        inventory = client.get_inventory()
        print(f"✅ Retrieved {len(inventory)} inventory items")
        
        # Check if the inventory items have both stock and quantity fields
        if inventory:
            print("\nChecking first inventory item:")
            item = inventory[0]
            
            # Check for stock field
            if "stock" in item:
                print(f"✅ 'stock' field exists: {item['stock']}")
            else:
                print("❌ 'stock' field is missing!")
                
            # Check for quantity field
            if "quantity" in item:
                print(f"✅ 'quantity' field exists: {item['quantity']}")
            else:
                print("❌ 'quantity' field is missing!")
                
            print("\nFirst inventory item fields:")
            for key, value in item.items():
                print(f"  {key}: {value}")
            
        print("\nFIX VERIFICATION COMPLETE")
    else:
        print("❌ ERROR: get_inventory method does not exist")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nTest completed")
