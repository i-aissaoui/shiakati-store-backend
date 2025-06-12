#!/usr/bin/env python3

file_path = 'src/utils/api_client.py'

# Read the file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Original problematic area is from line 301-312
# We'll replace this whole section with a properly structured try-except block

# First, identify the exact problematic lines
print("Before fixing:")
for i in range(300, 315):
    print(f"{i+1}: {lines[i].rstrip()}")

# Create a fixed version
fixed_lines = lines.copy()

# Fix the problematic section - replace lines 301-312 with corrected code
fixed_section = [
    '                variants = response.json()\n',
    '                if not variants:\n',
    '                    print("No variants found in inventory")\n',
    '                    return []\n',
    '                print(f"Retrieved {len(variants)} variants")\n',
    '\n',
    '            except requests.Timeout:\n',
    '                print("Timeout while getting variants - server taking too long to respond")\n',
    '                return []\n',
    '            except requests.ConnectionError:\n',
    '                print("Connection error - check if the server is running")\n',
    '                return []\n',
    '            except Exception as e:\n',
    '                print(f"Unexpected error getting variants: {str(e)}")\n',
    '                return []\n',
]

# Replace the lines in the copied list
start_line = 301
for i, line in enumerate(fixed_section):
    if start_line + i < len(fixed_lines):
        fixed_lines[start_line + i] = line
    else:
        fixed_lines.append(line)

# Write the fixed file
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

print("\nAfter fixing:")
with open(file_path, 'r') as f:
    lines = f.readlines()
    for i in range(300, 315):
        print(f"{i+1}: {lines[i].rstrip()}")

print("\nFix applied. Let's test for syntax errors.")
import subprocess
result = subprocess.run(['python', '-c', 'import src.utils.api_client'], 
                        capture_output=True, text=True)
if result.returncode == 0:
    print("Success! No syntax errors detected.")
else:
    print("Error still exists:")
    print(result.stderr)
