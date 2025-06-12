#!/usr/bin/env python3
"""
Enhanced verification script for API client implementation.
This script provides more detailed output for debugging purposes.
"""
import os
import sys
import traceback

def main():
    """Main verification function with detailed output."""
    print("=== ENHANCED API CLIENT VERIFICATION ===")
    
    # Path to files
    api_client_path = os.path.abspath("desktop_app/src/utils/api_client.py")
    
    print(f"Checking API client at: {api_client_path}")
    
    # Check if file exists
    if not os.path.isfile(api_client_path):
        print(f"ERROR: API client file not found at {api_client_path}")
        return False
    
    # Check file size
    size_bytes = os.path.getsize(api_client_path)
    print(f"API client file size: {size_bytes} bytes")
    
    # Required methods
    required_methods = [
        "get_sales_history",
        "get_orders",
        "get_categories",
        "get_expenses", 
        "get_stats",
        "create_sale"
    ]
    
    # Read file content to check for methods
    try:
        with open(api_client_path, 'r') as f:
            content = f.read()
        
        # Check for method patterns using simple string search
        print("\nChecking for method implementations:")
        missing_methods = []
        
        for method in required_methods:
            method_pattern = f"def {method}"
            if method_pattern in content:
                print(f"✅ {method} - FOUND")
            else:
                missing_methods.append(method)
                print(f"❌ {method} - NOT FOUND")
        
        if missing_methods:
            print(f"\nWARNING: {len(missing_methods)} methods are still missing:")
            for method in missing_methods:
                print(f"  - {method}")
            return False
        else:
            print("\nSUCCESS: All required methods are implemented in the API client!")
            return True
            
    except Exception as e:
        print(f"ERROR checking API client: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    print(f"\nVerification completed with {'SUCCESS' if success else 'ERRORS'}")
    sys.exit(exit_code)
