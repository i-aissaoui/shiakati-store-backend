#!/usr/bin/env python3

import re

file_path = "./src/utils/api_client.py"
output_path = "./src/utils/api_client_new.py"

# Read the original file content
with open(file_path, "r") as f:
    lines = f.readlines()

# Process line by line to fix syntax issues
fixed_lines = []
i = 0
in_try_block = False
try_level = 0

while i < len(lines):
    line = lines[i].rstrip('\n')
    
    # Fix multi-statement lines with problematic syntax
    if re.search(r'if [^:]+:[^\n]+return \[\]', line):
        # Fix "if condition: return []" pattern
        parts = re.split(r'(if [^:]+:)', line, 1)
        if len(parts) >= 3:
            indent = re.match(r'^(\s*)', line).group(1)
            fixed_lines.append(f"{parts[0]}{parts[1]}\n")
            fixed_lines.append(f"{indent}    {parts[2].strip()}\n")
        else:
            fixed_lines.append(line + "\n")
    
    elif re.search(r'except [^:]+:[^\n]+return \[\]', line):
        # Fix "except ExceptionType: return []" pattern
        parts = re.split(r'(except [^:]+:)', line, 1)
        if len(parts) >= 3:
            indent = re.match(r'^(\s*)', line).group(1)
            fixed_lines.append(f"{parts[0]}{parts[1]}\n")
            fixed_lines.append(f"{indent}    {parts[2].strip()}\n")
        else:
            fixed_lines.append(line + "\n")
    
    elif re.search(r'else:[^\n]+except', line):
        # Fix "else: except" invalid syntax
        parts = re.split(r'(else:)', line, 1)
        if len(parts) >= 3:
            indent = re.match(r'^(\s*)', line).group(1)
            fixed_lines.append(f"{parts[0]}{parts[1]}\n")
            except_part = parts[2].strip()
            fixed_lines.append(f"{indent}    pass\n")
            fixed_lines.append(f"{indent}{except_part}\n")
        else:
            fixed_lines.append(line + "\n")
    
    else:
        # Keep the line as is
        fixed_lines.append(line + "\n")
    
    i += 1

# Write the fixed content to the output file
with open(output_path, "w") as f:
    f.writelines(fixed_lines)

print(f"Fixed file written to {output_path}")
print("Testing the fixed file...")

import os
import subprocess
try:
    os.rename(file_path, file_path + ".bak")
    os.rename(output_path, file_path)
    result = subprocess.run(["python", "-c", "import src.utils.api_client"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("Success! The syntax error has been fixed.")
        os.remove(file_path + ".bak")  # Remove the backup if successful
    else:
        print("Error still exists:", result.stderr)
        os.remove(file_path)
        os.rename(file_path + ".bak", file_path)  # Restore the original if there's still an error
except Exception as e:
    print(f"Error during testing: {e}")
    if os.path.exists(file_path + ".bak"):
        os.rename(file_path + ".bak", file_path)  # Restore the original in case of exception
