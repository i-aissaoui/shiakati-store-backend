#!/usr/bin/env python3

file_path = './src/utils/api_client.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find the problematic lines by content
for i, line in enumerate(lines):
    if "if not variants:" in line and "return []" in line:
        # This is the malformed line
        print(f"Found malformed if statement at line {i+1}: {line.strip()}")
        # Fix the line by splitting it
        parts = line.split("if not variants:")
        indent = parts[0]  # Preserve indentation
        lines[i] = f"{indent}if not variants:\n{indent}    print(\"No variants found in inventory\")\n{indent}    return []\n{indent}print(f\"Retrieved {{len(variants)}} variants\")\n"
    elif "except requests.Timeout:" in line and "return []" in line:
        # This is the malformed except statement
        print(f"Found malformed except statement at line {i+1}: {line.strip()}")
        parts = line.split("except requests.Timeout:")
        indent = parts[0]  # Preserve indentation
        lines[i] = f"{indent}except requests.Timeout:\n{indent}    print(\"Timeout while getting variants - server taking too long to respond\")\n{indent}    return []\n"
    elif "except requests.ConnectionError:" in line and "return []" in line:
        # This is the malformed except statement
        print(f"Found malformed except statement at line {i+1}: {line.strip()}")
        parts = line.split("except requests.ConnectionError:")
        indent = parts[0]  # Preserve indentation
        lines[i] = f"{indent}except requests.ConnectionError:\n{indent}    print(\"Connection error - check if the server is running\")\n{indent}    return []\n"
    elif "except Exception as e:" in line and "return []" in line:
        # This is the malformed except statement
        print(f"Found malformed except statement at line {i+1}: {line.strip()}")
        parts = line.split("except Exception as e:")
        indent = parts[0]  # Preserve indentation
        lines[i] = f"{indent}except Exception as e:\n{indent}    print(f\"Unexpected error getting variants: {{str(e)}}\")\n{indent}    return []\n"

# Write the fixed content back to the file
fixed_file_path = file_path + '.fixed'
with open(fixed_file_path, 'w') as f:
    f.writelines(lines)

print(f"Fixed file saved to {fixed_file_path}")
print("To replace the original file, run:")
print(f"cp {fixed_file_path} {file_path}")
