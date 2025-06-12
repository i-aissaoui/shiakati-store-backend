#!/usr/bin/env python3
import re

file_path = "./src/utils/api_client.py"
clean_method_path = "clean_inventory.py"

# Read the original file content
with open(file_path, "r") as f:
    file_content = f.read()

# Read the clean method
with open(clean_method_path, "r") as f:
    clean_method = f.read()

# Define a regex pattern to match the entire get_inventory method
pattern = r"    def get_inventory\(self\)(.*?)\n    def parse_price_string"
replacement = clean_method + "\n\n    def parse_price_string"

# Replace the method
fixed_content = re.sub(pattern, replacement, file_content, flags=re.DOTALL)

# Write the fixed content back to the file
with open(file_path, "w") as f:
    f.write(fixed_content)

print(f"Fixed {file_path}")

# Test if the fix worked
import subprocess
try:
    result = subprocess.run(["python", "-c", "import src.utils.api_client"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("Success! The syntax error has been fixed.")
    else:
        print("Error still exists:", result.stderr)
except Exception as e:
    print(f"Error testing the fix: {e}")
