# basic_api_client_test.py
import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    print("Importing APIClient...")
    from src.utils.api_client import APIClient
    print("APIClient imported successfully!")
    
    print("Creating APIClient instance...")
    client = APIClient()
    print("APIClient instance created successfully!")
    
    # Try to call a few methods to see if they work
    print("\nTesting get_categories method...")
    try:
        categories = client.get_categories()
        print(f"get_categories returned: {categories}")
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        traceback.print_exc()
    
    print("\nTesting get_products method...")
    try:
        products = client.get_products()
        print(f"get_products returned: {type(products)} with {len(products)} items")
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        traceback.print_exc()
    
    print("\nAPIClient test completed.")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
