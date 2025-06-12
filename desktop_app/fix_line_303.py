#!/usr/bin/env python3

file_path = './src/utils/api_client.py'

# Read the file content
with open(file_path, 'r') as f:
    lines = f.readlines()

# Line 303 (0-indexed as 302) has the syntax error
# Replace this line with the correct version
if len(lines) > 302:
    line_num = 302  # 303-1 for 0-indexing
    if "except requests.Timeout:" in lines[line_num]:
        lines[line_num] = "                except requests.Timeout:\n"
        lines.insert(line_num + 1, "                    print(\"Timeout while getting product data - server taking too long to respond\")\n")
        lines.insert(line_num + 2, "                    return []\n")
        
        # Write the corrected content back to the file
        with open(file_path + '.fixed', 'w') as f:
            f.writelines(lines)
        
        print("Successfully fixed the syntax error on line 303!")
        print(f"Fixed file saved as {file_path}.fixed")
        print("Now replace the original file with the fixed version using:")
        print(f"mv {file_path}.fixed {file_path}")
    else:
        print(f"Line 303 doesn't contain the expected error.")
else:
    print("File doesn't have enough lines.")
