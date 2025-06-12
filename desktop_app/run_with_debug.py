#!/usr/bin/env python3
"""
Debug wrapper to run the application and capture imports and method calls.
"""
import os
import sys
import importlib
import types

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=== Starting application in debug mode ===")

# Original import hook
orig_import = __import__

# Dictionary to store method calls
method_calls = {}

def patched_method(original_method, class_name, method_name):
    """Wrap a method to log when it's called."""
    def wrapper(*args, **kwargs):
        print(f"CALLED: {class_name}.{method_name}")
        key = f"{class_name}.{method_name}"
        if key not in method_calls:
            method_calls[key] = 0
        method_calls[key] += 1
        try:
            result = original_method(*args, **kwargs)
            print(f"SUCCESS: {class_name}.{method_name} returned {type(result)}")
            return result
        except Exception as e:
            print(f"ERROR: {class_name}.{method_name} raised {type(e).__name__}: {str(e)}")
            raise
    return wrapper

def patch_api_client():
    """Patch the API client class to log method calls."""
    from src.utils import api_client
    
    # Get the original class
    APIClient = api_client.APIClient
    
    # Get the class methods we want to patch
    methods_to_patch = ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']
    
    # Patch each method
    for method_name in methods_to_patch:
        if hasattr(APIClient, method_name):
            original_method = getattr(APIClient, method_name)
            patched = patched_method(original_method, 'APIClient', method_name)
            setattr(APIClient, method_name, patched)
            print(f"Patched: APIClient.{method_name}")
        else:
            print(f"Warning: Method APIClient.{method_name} not found")
            
    print("API client patched successfully")

# Patch the API client before running the application
try:
    patch_api_client()
except Exception as e:
    import traceback
    print(f"Error patching API client: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Run the main application
try:
    print("\nStarting main application...")
    import main
    print("\nApplication exited normally")
except Exception as e:
    import traceback
    print(f"\nApplication error: {str(e)}")
    traceback.print_exc()
    
# Print method call summary at the end
print("\n=== Method Call Summary ===")
for method, count in method_calls.items():
    print(f"{method}: Called {count} times")
