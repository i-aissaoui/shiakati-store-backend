#!/usr/bin/env python3
"""
Verification script to check for remaining debug prints in the codebase.
"""

import os
import re
import sys

def check_file(file_path):
    """Check a file for any remaining print statements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for remaining prints
        prints = re.findall(r'print\([^)]*\)', content)
        if prints:
            # Skip certain valid print statements
            valid_prints = [
                p for p in prints 
                if "print_sale_ticket" not in p 
                and "print_receipt" not in p
                and "print_invoice" not in p
                and "report" not in p.lower()
            ]
            
            if valid_prints:
                return file_path, valid_prints
        
        # Look for logging statements
        logs = re.findall(r'logging\.(debug|info|warning)\([^)]*\)', content)
        if logs:
            return file_path, [f"logging.{log[0]}(...)" for log in logs]
        
        return None, []
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return None, []

def verify_directory(directory):
    """Check all Python files in a directory and its subdirectories"""
    found_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and "verify_cleanup.py" not in file:
                path = os.path.join(root, file)
                found_file, prints = check_file(path)
                if found_file and prints:
                    found_files.append((found_file, prints))
    
    return found_files

def main():
    print("Verifying cleanup of debug statements...")
    paths = [
        "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app",
        "/home/ismail/Desktop/projects/shiakati_store/backend/app"
    ]
    
    all_findings = []
    for path in paths:
        print(f"Checking {path}...")
        findings = verify_directory(path)
        all_findings.extend(findings)
    
    if all_findings:
        print("\nFound remaining debug statements:")
        for file_path, prints in all_findings:
            print(f"\n{file_path}:")
            for p in prints:
                print(f"  - {p}")
        print(f"\nTotal files with remaining debug statements: {len(all_findings)}")
    else:
        print("\nVerification complete! No debug statements found.")

if __name__ == "__main__":
    main()
