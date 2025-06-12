import sys
sys.path.insert(0, ".")
from src.utils.api_client import APIClient
client = APIClient()
print("Methods in APIClient:")
for m in dir(client):
    if not m.startswith("__"):
        print(f"- {m}")
