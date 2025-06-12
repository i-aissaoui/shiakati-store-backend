#!/usr/bin/env python3
"""
Check if the APIClient classes and methods are accessible directly.
This file should be run from the root of the project.
"""

import os
import sys
import inspect

print("[DEBUG] Checking API client class and methods")

# Add project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print(f"[DEBUG] Project root: {project_root}")
print(f"[DEBUG] Python path: {sys.path}")

try:
    from src.utils.api_client import APIClient
    print("[DEBUG] Successfully imported APIClient from src.utils.api_client")

    # Create an instance
    client = APIClient()
    print(f"[DEBUG] Created APIClient instance: {client}")
    
    # Check if the methods exist
    methods = [m for m in dir(client) if not m.startswith('_')]
    print(f"[DEBUG] Available methods: {methods}")
    
    # Check for specific methods
    print(f"[DEBUG] Has get_inventory: {'get_inventory' in methods}")
    print(f"[DEBUG] Has get_expenses: {'get_expenses' in methods}")
    print(f"[DEBUG] Has get_expenses_by_date_range: {'get_expenses_by_date_range' in methods}")
    
    # Try to call the methods
    print("\n[DEBUG] Testing method calls:")
    
    if 'get_inventory' in methods:
        print("[DEBUG] Calling get_inventory()...")
        inventory = client.get_inventory()
        print(f"[DEBUG] get_inventory returned {len(inventory) if inventory else 0} items")
    else:
        print("[DEBUG] get_inventory method not found")
    
    if 'get_expenses' in methods:
        print("[DEBUG] Calling get_expenses()...")
        expenses = client.get_expenses()
        print(f"[DEBUG] get_expenses returned {len(expenses) if expenses else 0} items")
    else:
        print("[DEBUG] get_expenses method not found")
    
    if 'get_expenses_by_date_range' in methods:
        print("[DEBUG] Calling get_expenses_by_date_range()...")
        expenses = client.get_expenses_by_date_range('2025-01-01', '2025-06-12')
        print(f"[DEBUG] get_expenses_by_date_range returned {len(expenses) if expenses else 0} items")
    else:
        print("[DEBUG] get_expenses_by_date_range method not found")

    # Print method signatures
    print("\n[DEBUG] Method details:")
    for method_name in ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']:
        if hasattr(client, method_name):
            method = getattr(client, method_name)
            print(f"[DEBUG] {method_name} signature: {inspect.signature(method)}")
            print(f"[DEBUG] {method_name} source file: {inspect.getfile(method.__class__)}")
        else:
            print(f"[DEBUG] {method_name} not found")

except ImportError as e:
    print(f"[DEBUG] ImportError: {e}")
except Exception as e:
    print(f"[DEBUG] Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n[DEBUG] Checking if there are multiple API client implementations")

api_client_files = []
for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith('.py') and ('api_client' in file.lower()):
            api_client_files.append(os.path.join(root, file))

print(f"[DEBUG] Found {len(api_client_files)} API client files:")
for file in api_client_files:
    print(f"  - {file}")
