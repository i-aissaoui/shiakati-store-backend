#!/usr/bin/env python3
"""
Script to compare the implementation of the fixed API client with the current one.
This script checks for required methods in both files and shows differences.
"""
import importlib.util
import sys
import os

def import_module_from_path(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def compare_api_clients():
    """Compare the API client implementations."""
    # Set paths
    fixed_api_path = "/home/ismail/Desktop/projects/shiakati_store/backend/fixed_api_client.py"
    current_api_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"
    
    # Required methods that must be implemented
    required_methods = [
        "get_sales_history",
        "get_orders",
        "get_categories", 
        "get_expenses",
        "get_stats",
        "create_sale"
    ]

    # Check if files exist
    if not os.path.isfile(fixed_api_path):
        print(f"❌ Fixed API client file not found at {fixed_api_path}")
        return False
    
    if not os.path.isfile(current_api_path):
        print(f"❌ Current API client file not found at {current_api_path}")
        return False
    
    try:
        # Import modules
        sys.path.append(os.path.dirname(fixed_api_path))
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_api_path)))))
        
        fixed_module = import_module_from_path("fixed_api_client", fixed_api_path)
        current_module = import_module_from_path("api_client", current_api_path)
        
        # Create instances
        fixed_client = fixed_module.APIClient()
        current_client = current_module.APIClient()
        
        # Compare methods
        print("\n=== COMPARISON ===")
        print(f"{'METHOD':<20} | {'FIXED CLIENT':<15} | {'CURRENT CLIENT':<15}")
        print("-" * 55)
        
        missing_methods = []
        
        for method_name in required_methods:
            fixed_has = hasattr(fixed_client, method_name) and callable(getattr(fixed_client, method_name))
            current_has = hasattr(current_client, method_name) and callable(getattr(current_client, method_name))
            
            status_fixed = "✅ Implemented" if fixed_has else "❌ Missing"
            status_current = "✅ Implemented" if current_has else "❌ Missing"
            
            print(f"{method_name:<20} | {status_fixed:<15} | {status_current:<15}")
            
            if not current_has:
                missing_methods.append(method_name)
        
        # Summary
        print("\n=== SUMMARY ===")
        print(f"Total required methods: {len(required_methods)}")
        
        if missing_methods:
            print(f"Methods missing in current implementation: {len(missing_methods)}")
            print(f"\nMissing methods: {', '.join(missing_methods)}")
            return False
        else:
            print("\nAll required methods are implemented in the current API client! ✨")
            return True
            
    except Exception as e:
        print(f"❌ Error during comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = compare_api_clients()
    sys.exit(0 if success else 1)
