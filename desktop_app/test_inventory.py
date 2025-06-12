#!/usr/bin/env python3
from src.utils.api_client import APIClient

# Create an instance of the API client
client = APIClient()

# Test the get_inventory method
print("Testing get_inventory method...")
try:
    inventory = client.get_inventory()
    print(f"Successfully retrieved {len(inventory)} inventory items")
    if inventory:
        print("Sample inventory item:")
        print(inventory[0])
except Exception as e:
    print(f"Error testing get_inventory: {str(e)}")
    import traceback
    traceback.print_exc()
    
print("\nAll tests completed")
