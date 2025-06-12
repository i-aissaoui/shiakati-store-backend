#!/usr/bin/env python3
import re

# The issue is likely in the get_inventory method and possibly other try-except blocks
# Let's create a properly formatted minimum version of these functions

file_path = 'src/utils/api_client.py'

# Read the original file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Check line by line for common syntax patterns that cause issues
fixed_lines = []
i = 0
in_try_block = False

while i < len(lines):
    line = lines[i]
    
    # Fix multi-statement lines with colons using whitespace as separator
    if ':                ' in line:
        parts = line.split(':                ')
        if len(parts) >= 2:
            indent = ' ' * (len(line) - len(line.lstrip(' ')))
            fixed_lines.append(f"{parts[0]}:\n")
            fixed_lines.append(f"{indent}    {parts[1]}")
            i += 1
            continue
    
    # Add the line as is
    fixed_lines.append(line)
    i += 1

# Write the fixed content
with open(f"{file_path}.new", 'w') as f:
    f.writelines(fixed_lines)

print(f"Fixed file saved to {file_path}.new")
