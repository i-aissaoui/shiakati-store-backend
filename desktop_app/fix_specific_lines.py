#!/usr/bin/env python3

file_path = './src/utils/api_client.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Fix specific problematic lines
problematic_lines = [
    84, 85, 516, 529, 530, 532, 566, 579, 580, 582, 615, 628, 629,
    663, 713, 721, 768, 770, 816, 818, 967, 980, 981
]

for i in problematic_lines:
    line_index = i - 1  # Adjust for 0-based indexing
    if line_index < len(lines):
        line = lines[line_index]
        
        if ':                ' in line:
            parts = line.split(':                ')
            if len(parts) >= 2:
                indent = ' ' * (len(line) - len(line.lstrip(' ')))
                lines[line_index] = f"{parts[0]}:\n{indent}    {parts[1]}"
                print(f"Fixed line {i}")

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"Fixed specific problematic lines in {file_path}")
