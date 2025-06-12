#!/usr/bin/env python3
"""
Script to check for method presence directly in the file content.
"""
import os
import re

def check_methods_in_file():
    """Check for method declarations directly in the file content."""
    # Path to the API client file
    api_client_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"
    
    # Required methods that must be implemented
    required_methods = [
        "get_sales_history",
        "get_orders",
        "get_categories", 
        "get_expenses",
        "get_stats",
        "create_sale"
    ]

    print(f"Checking API client at: {api_client_path}")
    
    if not os.path.isfile(api_client_path):
        print(f"❌ API client file not found at {api_client_path}")
        return False

    try:
        # Read the file content
        with open(api_client_path, 'r') as f:
            content = f.read()
        
        # Check for each required method
        missing_methods = []
        found_methods = []
        
        for method_name in required_methods:
            # Look for method declaration pattern
            pattern = rf"def\s+{method_name}\s*\("
            if re.search(pattern, content):
                found_methods.append(method_name)
                print(f"✅ Method '{method_name}' found in file")
            else:
                missing_methods.append(method_name)
                print(f"❌ Method '{method_name}' NOT found in file")
        
        # Summary
        print("\n=== SUMMARY ===")
        print(f"Total required methods: {len(required_methods)}")
        print(f"Methods found: {len(found_methods)}")
        print(f"Methods missing: {len(missing_methods)}")
        
        if missing_methods:
            print(f"\nMissing methods: {', '.join(missing_methods)}")
            return False
        else:
            print("\nAll required methods are found in the file! ✨")
            return True
            
    except Exception as e:
        print(f"❌ Error while checking API client: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_methods_in_file()
    print(f"\nCheck completed with {'success' if success else 'errors'}")
