#!/usr/bin/env python3
"""
Debug API client issues by printing the available methods and tracing calls to them.
"""
import os
import sys
import inspect
import importlib.util

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the API client
from src.utils.api_client import APIClient

print("\n=== DEBUGGING API CLIENT ===")

# Create an instance of the API client
client = APIClient()

# Print out all methods of the API client
print("\nAPI Client Methods:")
methods = inspect.getmembers(client, predicate=inspect.ismethod)
for name, method in methods:
    if not name.startswith('_') or name == '_ensure_authenticated' or name == '_handle_auth_error':
        print(f"  - {name}")

# Check if specific methods exist
print("\nChecking specific methods:")
methods_to_check = [
    "get_inventory", 
    "get_expenses",
    "get_expenses_by_date_range",
    "_generate_dummy_inventory",
    "_generate_dummy_expenses"
]

for method_name in methods_to_check:
    has_method = hasattr(client, method_name)
    print(f"  - {method_name}: {'EXISTS' if has_method else 'MISSING'}")
    
    if has_method:
        # Get the source code of the method
        method = getattr(client, method_name)
        try:
            source = inspect.getsource(method)
            print(f"    First line of source: {source.strip().split('\\n')[0]}")
        except (TypeError, OSError):
            print(f"    Could not get source for {method_name}")

# Try calling the methods to see if they work
print("\nTesting methods:")
try:
    print("  Testing get_inventory...")
    inventory = client.get_inventory()
    print(f"    get_inventory returned {len(inventory)} items")
except Exception as e:
    print(f"    Error calling get_inventory: {str(e)}")

try:
    print("  Testing get_expenses...")
    expenses = client.get_expenses()
    print(f"    get_expenses returned {len(expenses)} items")
except Exception as e:
    print(f"    Error calling get_expenses: {str(e)}")

try:
    print("  Testing get_expenses_by_date_range...")
    expenses = client.get_expenses_by_date_range("2025-01-01", "2025-06-01")
    print(f"    get_expenses_by_date_range returned {len(expenses)} items")
except Exception as e:
    print(f"    Error calling get_expenses_by_date_range: {str(e)}")

print("\nDebug complete!")
