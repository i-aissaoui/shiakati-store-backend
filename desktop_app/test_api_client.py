# test_api_client.py
import sys
import os
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.utils.api_client import APIClient
    
    # Create an instance of the API client
    api_client = APIClient()
    print("API client initialized")
    
    # Try logging in (this will fail but should not crash)
    try:
        result = api_client.login("test", "test")
        print(f"Login result: {result}")
    except Exception as e:
        print(f"Login attempt failed (expected): {str(e)}")
    
    # Test a few methods
    try:
        categories = api_client.get_categories()
        print(f"Categories: {categories}")
    except Exception as e:
        print(f"get_categories failed: {str(e)}")
        traceback.print_exc()
    
    print("API client testing complete")

except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
