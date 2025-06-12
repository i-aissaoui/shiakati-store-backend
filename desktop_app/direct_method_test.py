#!/usr/bin/env python3
import sys
import os
import importlib.util

# Define path to the API client module
api_client_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src/utils/api_client.py"
)

print(f"API client path: {api_client_path}")
print(f"File exists: {os.path.exists(api_client_path)}")

# Import the module directly from file
spec = importlib.util.spec_from_file_location("api_client", api_client_path)
api_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_client_module)

# Get the APIClient class
APIClient = api_client_module.APIClient
print(f"APIClient class: {APIClient}")

# Create an instance
client = APIClient()
print(f"APIClient instance: {client}")

# List all methods and check for our missing ones
methods = [m for m in dir(client) if not m.startswith('_')]
print(f"Methods: {methods}")

print("\nChecking specific methods:")
target_methods = ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']
for method in target_methods:
    if hasattr(client, method):
        print(f"✓ {method} exists")
        
        # Try to call the method
        try:
            if method == 'get_inventory':
                result = getattr(client, method)()
            elif method == 'get_expenses':
                result = getattr(client, method)()
            elif method == 'get_expenses_by_date_range':
                result = getattr(client, method)('2025-01-01', '2025-06-12')
                
            print(f"  Called successfully, returned {len(result) if result else 0} items")
        except Exception as e:
            print(f"  Error calling method: {e}")
    else:
        print(f"✗ {method} DOES NOT exist")
