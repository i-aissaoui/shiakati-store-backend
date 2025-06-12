#!/usr/bin/env python3
import os
import re
import sys

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original prints
        original_prints = len(re.findall(r'print\(', content))
        
        # More specific patterns for exception handling print statements
        patterns = [
            # Handle multiline print statements - preserve necessary code structure
            (r'print\(f"Login error: {str\(e\)}"\)\s*', 'pass  # Login error handled\n            '),
            (r'print\(f"Unexpected error during login: {str\(e\)}"\)\s*', 'pass  # Login error handled\n            '),
            (r'print\(f"Error getting products: {[^}]*}"\)\s*', 'pass  # Error handling\n                    '),
            (r'print\(f"Product {[^}]*} not found"\)\s*', 'pass  # Product not found handling\n                                '),
            (r'print\(f"Error getting product details for ID {[^}]*}: {[^}]*}"\)\s*', 'pass  # Product details error handling\n                                '),
            (r'print\(f"Request error for product {[^}]*}: {str\(e\)}"\)\s*', 'pass  # Request error handling\n                            '),
            
            # General debug prints
            (r'print\(f"[^"]*"\)\s*', ''),
            (r'print\("[^"]*"\)\s*', ''),
            (r'print\(f"[^"]*: [^}]*}"\)\s*', ''),
            (r'print\([^)]*\)\s*', ''),
            
            # Remove logging
            (r'logging\.(debug|info|warning)\([^)]*\)\s*\n', ''),
        ]
        
        # Apply all patterns
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Count remaining prints
        remaining_prints = len(re.findall(r'print\(', content))
        removed = original_prints - remaining_prints
        
        if removed > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Cleaned {file_path} - Removed {removed} print statements")
            return removed
        return 0
    except Exception as e:
        print(f"Error with {file_path}: {e}")
        return 0

def process_dir(directory):
    total = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != 'final_cleanup.py':
                path = os.path.join(root, file)
                total += clean_file(path)
    return total

print("Starting final cleanup...")
paths = [
    "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app",
    "/home/ismail/Desktop/projects/shiakati_store/backend/app"
]

total_removed = 0
for path in paths:
    print(f"Processing {path}...")
    total_removed += process_dir(path)

print(f"Cleanup complete! Removed {total_removed} additional debug statements")
