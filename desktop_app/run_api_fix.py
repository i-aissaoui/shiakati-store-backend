#!/usr/bin/env python3
"""
Simple script to directly add the missing methods to the APIClient class.
This will run the patch and test if the fix works.
"""
import os
import sys
import importlib

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing APIClient before patching...")
# First, test if the get_inventory method exists
try:
    from src.utils.api_client import APIClient
    client = APIClient()
    if hasattr(client, 'get_inventory'):
        print("get_inventory method already exists, no need to patch")
    else:
        print("get_inventory method is missing, applying patch...")
        
        # Apply the patch
        try:
            import patch_api_client
            print("Patch applied successfully")
            
            # Add the methods directly to the APIClient class
            from src.utils.inventory_api import EnhancedAPIClient
            
            # Monkey patch the methods directly into APIClient
            APIClient.get_inventory = EnhancedAPIClient.get_inventory
            APIClient._generate_dummy_inventory = EnhancedAPIClient._generate_dummy_inventory
            APIClient._ensure_authenticated = EnhancedAPIClient._ensure_authenticated
            APIClient._handle_auth_error = EnhancedAPIClient._handle_auth_error
            
            print("Methods added to APIClient class")
            
            # Test if the methods are now available
            client = APIClient()
            if hasattr(client, 'get_inventory'):
                try:
                    inventory = client.get_inventory()
                    print(f"SUCCESS: Retrieved {len(inventory)} inventory items")
                    if inventory:
                        print("First inventory item:")
                        print(inventory[0])
                except Exception as e:
                    print(f"Error calling get_inventory: {e}")
            else:
                print("ERROR: get_inventory method still missing after patch")
        except Exception as e:
            print(f"Error applying patch: {e}")
except ImportError as e:
    print(f"Error importing APIClient: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

print("Done!")
