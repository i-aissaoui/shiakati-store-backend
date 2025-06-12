#!/usr/bin/env python3
"""
Simple test to verify the API client fix by directly accessing the get_inventory method.
"""
import os
import sys
import importlib

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Force reload the modules to ensure we get the latest changes
if "src.utils.api_client" in sys.modules:
    print("Reloading API client module")
    importlib.reload(sys.modules["src.utils.api_client"])

print("Testing API client fix...")

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
        
        # Print the first item
        if inventory:
            print("\nFirst inventory item:")
            first_item = inventory[0]
            for key, value in first_item.items():
                print(f"  {key}: {value}")
            
        print("\nFIX VERIFIED: The get_inventory method is working correctly!")
    else:
        print("❌ ERROR: get_inventory method does not exist")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nTest completed")
