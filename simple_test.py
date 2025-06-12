import sys
sys.path.append('/home/ismail/Desktop/projects/shiakati_store/backend')
from desktop_app.src.utils.api_client import APIClient

print("Module imported successfully")
client = APIClient()
print("Client created successfully")

# Test the get_inventory method
try:
    inventory = client.get_inventory()
    print(f"Successfully retrieved {len(inventory)} inventory items")
    if inventory:
        print("First inventory item:")
        print(inventory[0])
except Exception as e:
    print(f"Error: {e}")
