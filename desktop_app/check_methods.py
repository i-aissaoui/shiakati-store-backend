from src.utils.api_client import APIClient

def check_methods():
    client = APIClient()
    
    # Check if methods exist
    methods = [
        'get_inventory',
        'get_expenses',
        'get_expenses_by_date_range'
    ]
    
    for method in methods:
        try:
            if hasattr(client, method):
                print(f"✅ Method '{method}' exists")
                # Try to call the method
                try:
                    if method == 'get_inventory':
                        result = client.get_inventory()
                        print(f"   Called successfully, returned {len(result)} items")
                    elif method == 'get_expenses':
                        result = client.get_expenses()
                        print(f"   Called successfully, returned {len(result)} items")
                    elif method == 'get_expenses_by_date_range':
                        # Use dummy dates for testing
                        result = client.get_expenses_by_date_range('2023-01-01', '2023-12-31')
                        print(f"   Called successfully, returned {len(result)} items")
                except Exception as e:
                    print(f"   ⚠️ Error calling method: {str(e)}")
            else:
                print(f"❌ Method '{method}' does not exist")
        except Exception as e:
            print(f"❌ Error checking method '{method}': {str(e)}")

if __name__ == "__main__":
    check_methods()
