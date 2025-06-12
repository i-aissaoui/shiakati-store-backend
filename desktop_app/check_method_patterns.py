#!/usr/bin/env python3
import os
import re

# Path to the API client file
api_client_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src/utils/api_client.py"
)

print(f"API client path: {api_client_path}")
print(f"File exists: {os.path.exists(api_client_path)}")

if not os.path.exists(api_client_path):
    print("Error: API client file not found")
    exit(1)

# Read the file
with open(api_client_path, 'r') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Check for method definitions
method_patterns = {
    'get_inventory': r'def\s+get_inventory\s*\(',
    'get_expenses': r'def\s+get_expenses\s*\(',
    'get_expenses_by_date_range': r'def\s+get_expenses_by_date_range\s*\('
}

print("\nChecking for method definitions:")
for method, pattern in method_patterns.items():
    matches = re.findall(pattern, content)
    if matches:
        line_num = 0
        for i, line in enumerate(content.split('\n')):
            if re.search(pattern, line):
                line_num = i + 1
                break
                
        print(f"✓ {method} found {len(matches)} time(s) at line {line_num}")
        
        # Show context (3 lines before and after)
        lines = content.split('\n')
        start = max(0, line_num - 4)
        end = min(len(lines), line_num + 3)
        
        print("\nContext:")
        for i in range(start, end):
            prefix = "  > " if i == line_num - 1 else "    "
            print(f"{prefix}{i + 1}: {lines[i]}")
    else:
        print(f"✗ {method} NOT found")
