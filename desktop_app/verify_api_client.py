#!/usr/bin/env python3
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the API client module to check if it loads without syntax errors
print("Importing API client module...")
from src.utils import api_client
print("API client module loaded successfully.")

# Verify the methods are present
print("\nVerifying methods in API client...")
methods = [m for m in dir(api_client.APIClient) if not m.startswith('__')]

# Check for our target methods
missing_methods = []
required_methods = ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']
for method in required_methods:
    if method in methods:
        print(f"✓ Method '{method}' found")
    else:
        missing_methods.append(method)
        print(f"✗ Method '{method}' NOT found")

print("\nSummary:")
if missing_methods:
    print(f"The following methods are still missing: {', '.join(missing_methods)}")
    sys.exit(1)
else:
    print("All required methods have been added successfully!")
    sys.exit(0)
