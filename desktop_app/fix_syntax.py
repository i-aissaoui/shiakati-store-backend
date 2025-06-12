#!/usr/bin/env python3
import sys
import re

# Get the file path from the command line
file_path = sys.argv[1]

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Fix the syntax error on line 292
pattern1 = r'if response.status_code != 200:\s+if response.status_code == 401:\s+elif response.status_code == 404:\s+else:\s+return \[\]'
replacement1 = '''if response.status_code != 200:
                    if response.status_code == 401:
                        print("Authentication error - please log in again")
                    elif response.status_code == 404:
                        print("Variants endpoint not found - check server URL")
                    else:
                        print(f"Server response: {response.text}")
                    return []'''

content = re.sub(pattern1, replacement1, content)

# Fix the syntax error on line 411
pattern2 = r'if response.status_code != 200:\s+if response.status_code != 500:\s+return \{\}'
replacement2 = '''if response.status_code != 200:
                print(f"Error getting stats: {response.status_code}")
                if response.status_code != 500:
                    print(f"Error response: {response.text}")
                return {}'''

content = re.sub(pattern2, replacement2, content)

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.write(content)

print(f"Fixed syntax errors in {file_path}")
