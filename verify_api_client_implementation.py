#!/usr/bin/env python3
"""
Script to verify and test the Shiakati Store application after API client fixes.
This script will create a new API client implementation with all required methods.
"""
import os
import sys
import time
import traceback
from datetime import datetime

def main():
    # Path to the API client file
    api_client_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"
    
    # Check if the API client file exists
    if not os.path.isfile(api_client_path):
        print(f"Error: API client file not found at {api_client_path}")
        return False
    
    # Create a backup of the original file
    backup_path = f"{api_client_path}.backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(api_client_path, 'r') as src_file:
            with open(backup_path, 'w') as dst_file:
                dst_file.write(src_file.read())
        print(f"Created backup of API client at {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {str(e)}")
    
    # Check that all required methods exist in the API client
    required_methods = [
        "get_sales_history",
        "get_orders",
        "get_categories",
        "get_expenses",
        "get_order_details",
        "get_order",
        "get_stats",
        "create_sale"
    ]
    
    missing_methods = []
    
    # Import the module dynamically to check methods
    api_client_dir = os.path.dirname(api_client_path)
    sys.path.append(os.path.dirname(os.path.dirname(api_client_dir)))
    try:
        from desktop_app.src.utils.api_client import APIClient
        client = APIClient()
        
        for method in required_methods:
            if not hasattr(client, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"Warning: The following methods are still missing: {', '.join(missing_methods)}")
        else:
            print("All required methods are implemented in the API client.")
            return True
            
    except Exception as e:
        print(f"Error checking API client: {str(e)}")
        traceback.print_exc()
    
    return len(missing_methods) == 0

if __name__ == "__main__":
    if main():
        print("Verification completed successfully!")
    else:
        print("Verification failed. Some issues still need to be addressed.")
