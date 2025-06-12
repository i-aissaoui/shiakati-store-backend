#!/usr/bin/env python3
import os
import re

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find prints
        original = len(re.findall(r'print\(', content))
        
        # Remove common debug prints
        content = re.sub(r'\s*print\([^)]*\)\s*\n', '', content)
        
        # Remove logging
        content = re.sub(r'\s*logging\.(debug|info|warning)\([^)]*\)\s*\n', '', content)
        
        # Count remaining
        remaining = len(re.findall(r'print\(', content))
        
        if original != remaining:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Cleaned {file_path} - Removed {original - remaining} print statements")
            return original - remaining
        return 0
    except Exception as e:
        print(f"Error with {file_path}: {e}")
        return 0

def process_dir(directory):
    total = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != 'cleanup2.py':
                path = os.path.join(root, file)
                total += clean_file(path)
    return total

print("Starting cleanup...")
paths = [
    "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app",
    "/home/ismail/Desktop/projects/shiakati_store/backend/app"
]

total_removed = 0
for path in paths:
    print(f"Processing {path}...")
    total_removed += process_dir(path)

print(f"Cleanup complete! Removed {total_removed} debug statements")
