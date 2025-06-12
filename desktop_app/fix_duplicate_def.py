#!/usr/bin/env python3

file_path = './src/utils/api_client.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find the duplicate function definition
for i, line in enumerate(lines):
    if "def get_inventory(self)def get_inventory(self)" in line:
        print(f"Found duplicate function definition at line {i+1}")
        # Fix the line
        lines[i] = "    def get_inventory(self) -> List[Dict[str, Any]]:\n"
    elif "else:                except Exception as e:" in line:
        print(f"Found malformed except statement at line {i+1}")
        # Fix the line
        lines[i] = "                    else:\n                        print(f\"Warning: Failed to get product {product_id}: {product_response.status_code}\")\n                except Exception as e:\n"

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"Fixed file saved to {file_path}")
