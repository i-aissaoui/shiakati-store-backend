#!/usr/bin/env python3
"""
Test script for verifying the API client implementation.
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
    
    # Import the module dynamically to check methods
    api_client_dir = os.path.dirname(api_client_path)
    sys.path.append(os.path.dirname(os.path.dirname(api_client_dir)))
    
    try:
        from desktop_app.src.utils.api_client import APIClient
        print("Successfully imported APIClient")
        
        client = APIClient()
        print("Successfully created APIClient instance")
        
        # Check that all required methods exist in the API client
        required_methods = [
            "get_sales_history",
            "get_orders",
            "get_categories",
            "get_expenses",
            "get_stats",
            "create_sale",
            "get_order_details",
            "get_order"
        ]
        
        missing_methods = []
        
        for method in required_methods:
            if hasattr(client, method):
                print(f"✅ Method '{method}' exists")
            else:
                print(f"❌ Method '{method}' is missing")
                missing_methods.append(method)
        
        # Test the implemented methods
        if "get_stats" in required_methods and not method in missing_methods:
            print("\nTesting get_stats method...")
            try:
                stats = client.get_stats()
                print(f"Stats result: {stats}")
                if not stats:
                    print("Warning: get_stats returned empty data")
            except Exception as e:
                print(f"Error testing get_stats: {str(e)}")
                traceback.print_exc()
                
        if "get_categories" in required_methods and not method in missing_methods:
            print("\nTesting get_categories method...")
            try:
                categories = client.get_categories()
                print(f"Categories result: {categories[:2]}...")
                if not categories:
                    print("Warning: get_categories returned empty data")
            except Exception as e:
                print(f"Error testing get_categories: {str(e)}")
                traceback.print_exc()
        
        if missing_methods:
            print(f"\n❌ The following methods are still missing: {', '.join(missing_methods)}")
            return False
        else:
            print("\n✅ All required methods are implemented in the API client.")
            return True
            
    except ImportError as e:
        print(f"Import error: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error checking API client: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if main():
        print("\nVerification completed successfully! All required methods are implemented.")
    else:
        print("\nVerification failed. Some issues still need to be addressed.")
