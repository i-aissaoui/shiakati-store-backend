#!/usr/bin/env python3
"""
Comprehensive cleanup script for removing all debugging prints 
and logging statements from the Shiakati Store POS system.
"""

import os
import re
import sys
from pathlib import Path
import fnmatch

# Skip these files when cleaning
SKIP_FILES = [
    "cleanup_debug_prints.py", 
    "clean_print_function.py",
    "direct_fix_pos.py", 
    "remove_debugging.py",
    "comprehensive_cleanup.py",
    "list_files_to_clean.py"
]

# Function to clean a single file
def clean_debug_statements(file_path):
    """
    Remove debug print statements and logging from a Python file.
    Returns: (cleaned_content, changes_made_count)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original debug statements
        original_print_count = len(re.findall(r'print\(', content))
        original_logging_count = len(re.findall(r'logging\.(debug|info|warning)', content))
        
        # Patterns for common debug prints
        patterns = [
            # Basic print statements with strings
            (r'\s*print\("Debug[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Debug[^"]*"\)\s*\n', ''),
            (r'\s*print\("Starting[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Starting[^"]*"\)\s*\n', ''),
            
            # Error reports
            (r'\s*print\(f"Error[^"]*: {[^}]+}"\)\s*\n', ''),
            (r'\s*print\(f"Error[^"]*: {str\(e\)}"\)\s*\n', ''),
            (r'\s*print\("Error[^"]*"\)\s*\n', ''),
            
            # Status updates
            (r'\s*print\(f"Attempting[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Processing[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Loading[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Updating[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Creating[^"]*"\)\s*\n', ''),
            (r'\s*print\("Processing[^"]*"\)\s*\n', ''),
            
            # API response debugging
            (r'\s*print\(f"[^"]*response[^"]*: {[^}]+}"\)\s*\n', ''),
            (r'\s*print\(f"[^"]*status[^"]*: {[^}]+}"\)\s*\n', ''),
            (r'\s*print\(f"[^"]*body[^"]*: {[^}]+}"\)\s*\n', ''),
            
            # Login/auth debugging
            (r'\s*print\(f"Login[^"]*"\)\s*\n', ''),
            (r'\s*print\(f"Auth[^"]*"\)\s*\n', ''),
            
            # Variable inspection
            (r'\s*print\(f"[^"]*: {[^}]+}"\)\s*\n', ''),
            
            # Exception reports
            (r'\s*print\(f"[^"]*exception[^"]*: {[^}]+}"\)\s*\n', ''),
            (r'\s*print\(f"[^"]*error[^"]*: {[^}]+}"\)\s*\n', ''),
            (r'\s*print\(f"Unexpected[^"]*: {str\(e\)}"\)\s*\n', ''),
            
            # Warning messages
            (r'\s*print\(f"Warning[^"]*"\)\s*\n', ''),
            (r'\s*print\("Warning[^"]*"\)\s*\n', ''),
            
            # Logging statements
            (r'\s*logging\.debug\([^)]*\)\s*\n', ''),
            (r'\s*logging\.info\([^)]*\)\s*\n', ''),
            (r'\s*logging\.warning\([^)]*\)\s*\n', ''),
        ]
        
        # Apply all patterns
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Count remaining debug statements
        remaining_prints = len(re.findall(r'print\(', content))
        remaining_logging = len(re.findall(r'logging\.(debug|info|warning)', content))
        
        changes_made = (original_print_count - remaining_prints) + (original_logging_count - remaining_logging)
        
        return content, changes_made
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None, 0

def process_directory(directory_path):
    """
    Process all Python files in a directory and its subdirectories.
    """
    total_changes = 0
    total_files_changed = 0
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py') and file not in SKIP_FILES:
                file_path = os.path.join(root, file)
                
                # Clean the file
                clean_content, changes = clean_debug_statements(file_path)
                
                if clean_content is not None and changes > 0:
                    # Write changes back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(clean_content)
                    
                    print(f"Cleaned {file_path} - Removed {changes} debug statements")
                    total_changes += changes
                    total_files_changed += 1
    
    return total_files_changed, total_changes

def main():
    # Paths to clean
    paths_to_clean = [
        "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app",
        "/home/ismail/Desktop/projects/shiakati_store/backend/app"
    ]
    
    print("Starting comprehensive cleanup of debug statements...")
    total_files = 0
    total_changes = 0
    
    for path in paths_to_clean:
        print(f"\nProcessing directory: {path}")
        files_changed, changes = process_directory(path)
        total_files += files_changed
        total_changes += changes
        
    print(f"\nCleanup complete!")
    print(f"Total files changed: {total_files}")
    print(f"Total debug statements removed: {total_changes}")

if __name__ == "__main__":
    main()
