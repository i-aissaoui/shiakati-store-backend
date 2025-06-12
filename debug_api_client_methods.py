#!/usr/bin/env python3
"""
Debug script to inspect API client methods and identify why they're not being recognized.
This will help diagnose the 'APIClient' object has no attribute issues.
"""

import os
import sys
import inspect

# Add parent directory to path so we can import the API client
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    # Try to import from the desktop_app directory
    from desktop_app.src.utils.api_client import APIClient
    print("Successfully imported APIClient from desktop_app/src/utils/api_client.py")
except ImportError:
    try:
        # If that fails, try the direct import
        sys.path.append(os.path.join(parent_dir, 'desktop_app'))
        from src.utils.api_client import APIClient
        print("Successfully imported APIClient from src/utils/api_client.py")
    except ImportError as e:
        print(f"Error importing APIClient: {e}")
        print("Attempting alternative import paths...")
        
        # Try to locate the file through the filesystem
        api_client_paths = []
        for root, dirs, files in os.walk(parent_dir):
            if 'api_client.py' in files:
                api_client_paths.append(os.path.join(root, 'api_client.py'))
        
        if api_client_paths:
            print(f"Found potential api_client.py files at: {', '.join(api_client_paths)}")
            
            # Try to dynamically import from the first found path
            import importlib.util
            for path in api_client_paths:
                try:
                    module_name = os.path.basename(path).replace('.py', '')
                    spec = importlib.util.spec_from_file_location(module_name, path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    APIClient = module.APIClient
                    print(f"Successfully imported APIClient from {path}")
                    break
                except Exception as e:
                    print(f"Failed to import from {path}: {e}")
        else:
            print("Could not find any api_client.py files in the project.")
            sys.exit(1)

print("\n=== API CLIENT DEBUGGING ===\n")

# Create an instance of the API client
try:
    client = APIClient()
    print("Successfully created APIClient instance")
except Exception as e:
    print(f"Error creating APIClient instance: {e}")
    sys.exit(1)

# Print out all methods of the API client
print("\nAll methods of the APIClient:")
methods = inspect.getmembers(client, predicate=inspect.ismethod)
for name, method in sorted(methods):
    if not name.startswith('__'):  # Exclude dunder methods
        print(f"  - {name}")

# Specifically check for the missing methods
missing_methods = ['get_inventory', 'get_expenses_by_date_range']
print("\nChecking for specific methods that were reported missing:")
for method_name in missing_methods:
    if hasattr(client, method_name):
        print(f"  ✓ Method '{method_name}' exists")
        method = getattr(client, method_name)
        print(f"    Signature: {inspect.signature(method)}")
        print(f"    Is method: {inspect.ismethod(method)}")
    else:
        print(f"  ✗ Method '{method_name}' does NOT exist")

# Check the class definition itself
print("\nChecking APIClient class definition:")
client_class = client.__class__
print(f"  Class name: {client_class.__name__}")
print(f"  Module: {client_class.__module__}")

class_methods = inspect.getmembers(client_class, inspect.isfunction)
print("  Methods defined in the class:")
for name, method in sorted(class_methods):
    if not name.startswith('__'):  # Exclude dunder methods
        print(f"    - {name}")

# Check if there might be import issues
print("\nChecking for potential import issues:")
current_module = inspect.getmodule(client).__name__
print(f"  Current module: {current_module}")

print("\nChecking method implementations:")
with open(inspect.getfile(client.__class__), 'r') as f:
    source_code = f.read()

for method_name in missing_methods:
    method_pattern = f"def {method_name}"
    if method_pattern in source_code:
        print(f"  ✓ Found implementation of '{method_name}' in source code")
        # Get line number of the method definition
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            if method_pattern in line:
                print(f"    Located at approximately line {i+1}")
                # Print a few lines of context
                start = max(0, i-1)
                end = min(len(lines), i+3)
                print("    Code snippet:")
                for j in range(start, end):
                    print(f"      {j+1}: {lines[j]}")
                break
    else:
        print(f"  ✗ Could not find implementation of '{method_name}' in source code")

print("\n=== DEBUGGING COMPLETE ===")
