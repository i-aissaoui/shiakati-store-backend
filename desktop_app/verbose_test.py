#!/usr/bin/env python3
import os
import sys
import traceback

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Starting API client test...")

try:
    print("Importing APIClient...")
    from src.utils.api_client import APIClient
    print("Successfully imported APIClient")

    # Check if the get_inventory method exists
    print("\nChecking if get_inventory method exists...")
    if hasattr(APIClient, 'get_inventory'):
        print("get_inventory method exists in the APIClient class")
    else:
        print("ERROR: get_inventory method does NOT exist in the APIClient class")
        print("Available methods:", [m for m in dir(APIClient) if not m.startswith('_') and callable(getattr(APIClient, m))])

    # Create an instance
    print("\nCreating APIClient instance...")
    client = APIClient()
    print("Successfully created APIClient instance")

    # Check if the _ensure_authenticated method exists
    print("\nChecking if _ensure_authenticated method exists...")
    if hasattr(client, '_ensure_authenticated'):
        print("_ensure_authenticated method exists")
    else:
        print("ERROR: _ensure_authenticated method does NOT exist")

    # Check if the get_inventory method exists on the instance
    print("\nChecking if get_inventory method exists on the instance...")
    if hasattr(client, 'get_inventory'):
        print("get_inventory method exists on the instance")
    else:
        print("ERROR: get_inventory method does NOT exist on the instance")
        print("Available methods:", [m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m))])

    # Test the get_inventory method
    print("\nTesting get_inventory method...")
    try:
        inventory = client.get_inventory()
        print(f"Successfully retrieved {len(inventory)} inventory items")
        if inventory:
            print("Sample inventory item:")
            print(inventory[0])
    except AttributeError as e:
        print(f"AttributeError: {str(e)}")
        print("This suggests the method might be missing or there's a typo in the method name")
    except Exception as e:
        print(f"Error testing get_inventory: {str(e)}")
        traceback.print_exc()

except Exception as e:
    print(f"Error during testing: {str(e)}")
    traceback.print_exc()

print("\nTest completed")
