#!/usr/bin/env python3
import os
import sys

api_file = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"
fixed_file = "/home/ismail/Desktop/projects/shiakati_store/backend/fixed_api_client.py"

if os.path.exists(api_file):
    size = os.path.getsize(api_file)
    print(f"API client file exists, size: {size} bytes")
else:
    print(f"API client file does not exist at {api_file}")

if os.path.exists(fixed_file):
    size = os.path.getsize(fixed_file)
    print(f"Fixed API client file exists, size: {size} bytes")
else:
    print(f"Fixed API client file does not exist at {fixed_file}")

# List the API client directory
dir_path = os.path.dirname(api_file)
print(f"\nListing files in {dir_path}:")
for f in os.listdir(dir_path):
    if f.startswith("api_client"):
        file_path = os.path.join(dir_path, f)
        size = os.path.getsize(file_path)
        print(f"  {f}: {size} bytes")

print("\nDone.")
