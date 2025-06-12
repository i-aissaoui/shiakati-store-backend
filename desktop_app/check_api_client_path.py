#!/usr/bin/env python3
"""
Check which API client module is actually being imported.
"""
import sys
import os
import inspect

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_api_client_path():
    # Import the API client
    try:
        from src.utils.api_client import APIClient
        client = APIClient()
        
        # Get the module file path
        module_path = inspect.getfile(APIClient)
        print(f"APIClient is being imported from: {module_path}")
        
        # Check if the methods exist
        print("\nChecking methods:")
        for method in ["get_inventory", "get_expenses", "get_expenses_by_date_range"]:
            if hasattr(client, method):
                print(f"✓ {method}: Found")
            else:
                print(f"✗ {method}: Missing")
        
        # Load the file content to check
        with open(module_path, 'r') as f:
            content = f.read()
            
        # Check if the methods are defined in the file
        print("\nChecking file content:")
        for method in ["get_inventory", "get_expenses", "get_expenses_by_date_range"]:
            if f"def {method}" in content:
                print(f"✓ {method}: Defined in file")
            else:
                print(f"✗ {method}: Not defined in file")
                
        # Check if there are any syntax errors
        print("\nChecking for possible syntax errors...")
        try:
            import importlib
            # Try to reload the module
            import src.utils.api_client
            importlib.reload(src.utils.api_client)
            print("✓ No syntax errors detected on reload")
        except SyntaxError as e:
            print(f"✗ Syntax error detected: {str(e)}")
        except Exception as e:
            print(f"! Other error on reload: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_api_client_path()
