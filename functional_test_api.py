#!/usr/bin/env python3
"""
Script to test the API client methods directly by instantiating the class and calling the methods.
"""
import os
import sys
import time

# Add the parent directory to the path to import the API client
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

def test_api_client():
    """Test the API client by calling its methods directly."""
    print("=== TESTING API CLIENT METHODS ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    try:
        # Try a direct import
        from desktop_app.src.utils.api_client import APIClient
        print("✅ Successfully imported APIClient")
        
        # Create an instance
        client = APIClient()
        print("✅ Successfully created APIClient instance")
        
        # Test login
        result = client.login("admin", "123")
        print(f"Login result: {result}")
        
        # Test get_sales_history
        print("\nTesting get_sales_history...")
        start_time = time.time()
        sales = client.get_sales_history()
        elapsed = time.time() - start_time
        print(f"get_sales_history returned {len(sales)} items in {elapsed:.2f} seconds")
        if sales:
            print(f"Sample sale: {sales[0]}")
        
        # Test get_orders
        print("\nTesting get_orders...")
        start_time = time.time()
        orders = client.get_orders()
        elapsed = time.time() - start_time
        print(f"get_orders returned {len(orders)} items in {elapsed:.2f} seconds")
        if orders:
            print(f"Sample order: {orders[0]}")
        
        # Test get_categories
        print("\nTesting get_categories...")
        start_time = time.time()
        categories = client.get_categories()
        elapsed = time.time() - start_time
        print(f"get_categories returned {len(categories)} items in {elapsed:.2f} seconds")
        if categories:
            print(f"Sample category: {categories[0]}")
        
        # Test get_expenses
        print("\nTesting get_expenses...")
        start_time = time.time()
        expenses = client.get_expenses()
        elapsed = time.time() - start_time
        print(f"get_expenses returned {len(expenses)} items in {elapsed:.2f} seconds")
        if expenses:
            print(f"Sample expense: {expenses[0]}")
        
        # Test get_stats
        print("\nTesting get_stats...")
        start_time = time.time()
        stats = client.get_stats()
        elapsed = time.time() - start_time
        print(f"get_stats returned data in {elapsed:.2f} seconds")
        print(f"Stats: {stats}")
        
        # Test create_sale (with minimal test data)
        print("\nTesting create_sale...")
        test_items = [
            {"barcode": "TEST123", "quantity": 1, "price": 100.0}
        ]
        start_time = time.time()
        sale_result = client.create_sale(test_items, 100.0)
        elapsed = time.time() - start_time
        print(f"create_sale completed in {elapsed:.2f} seconds")
        print(f"Sale result: {sale_result}")
        
        print("\n✅ All methods are implemented and functional!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_client()
    sys.exit(0 if success else 1)
