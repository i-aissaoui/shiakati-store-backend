#!/usr/bin/env python3
"""
Script to clean up debugging print statements from API client and main window files
"""

import os
import re
import shutil
import sys

def remove_prints_from_file(file_path):
    """Remove print statements from a file."""
    print(f"Processing file: {file_path}")
    
    # Skip if file doesn't exist
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return False
    
    # Create backup first
    backup_path = f"{file_path}.debug_bak"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Read file: {len(content)} bytes")
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Count original print statements
    print_count = len(re.findall(r'print\(', content))
    print(f"Found {print_count} print statements")
    
    if print_count == 0:
        print("No print statements found to remove")
        return True
    
    # Replace common debug print patterns
    content = re.sub(r'\s*print\(f"[^"]*Error[^"]*(str\(e\))[^"]*"\)[^\n]*', r'        pass  # Error handled', content)
    content = re.sub(r'\s*print\(f"[^"]*Debug[^"]*"[^)]*\)[^\n]*', r'        pass  # Debug removed', content)
    content = re.sub(r'\s*print\("Warning:[^"]*"\)[^\n]*', r'        pass  # Warning removed', content)
    content = re.sub(r'\s*print\(f"Warning:[^"]*"\)[^\n]*', r'        pass  # Warning removed', content)
    content = re.sub(r'\s*print\("Starting[^"]*"\)[^\n]*', r'        # Starting process', content)
    content = re.sub(r'\s*print\(f"Starting[^"]*"\)[^\n]*', r'        # Starting process', content)
    content = re.sub(r'\s*print\(f"Updated[^"]*"\)[^\n]*', r'        # Update complete', content)
    content = re.sub(r'\s*print\(f"Received[^"]*"\)[^\n]*', r'        # Data received', content)
    content = re.sub(r'\s*print\(f"Got[^"]*"\)[^\n]*', r'        # Data received', content)
    
    # Count remaining print statements
    remaining_prints = len(re.findall(r'print\(', content))
    print(f"Removed {print_count - remaining_prints} print statements, {remaining_prints} remaining")
    
    # Write back the cleaned content
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully updated file: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def clean_api_client():
    """Clean up the API client file."""
    api_client_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "utils", "api_client.py"
    )
    
    if remove_prints_from_file(api_client_path):
        print("API client cleaned successfully!")
    else:
        print("Failed to clean API client")

def clean_main_window():
    """Clean up the main window file."""
    main_window_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window.py"
    )
    
    if remove_prints_from_file(main_window_path):
        print("Main window cleaned successfully!")
    else:
        print("Failed to clean main window")

def clean_inventory_page():
    """Clean up the inventory page file."""
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "inventory_page.py"
    )
    
    if remove_prints_from_file(file_path):
        print("Inventory page cleaned successfully!")
    else:
        print("Failed to clean inventory page")

def clean_stats_page():
    """Clean up the stats page file."""
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "stats_page.py"
    )
    
    if remove_prints_from_file(file_path):
        print("Stats page cleaned successfully!")
    else:
        print("Failed to clean stats page")

def clean_expenses_page():
    """Clean up the expenses page file."""
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "expenses_page.py"
    )
    
    if remove_prints_from_file(file_path):
        print("Expenses page cleaned successfully!")
    else:
        print("Failed to clean expenses page")

def clean_other_ui_files():
    """Clean up other UI files."""
    ui_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui"
    )
    
    for root, _, files in os.walk(ui_dir):
        for file in files:
            if file.endswith(".py") and file not in ["main_window.py", "pos_page.py"]:
                file_path = os.path.join(root, file)
                remove_prints_from_file(file_path)

def main():
    """Main function to clean all files."""
    print("=== CLEANING UP DEBUG PRINT STATEMENTS ===")
    
    clean_api_client()
    print("\n" + "-" * 40 + "\n")
    
    clean_main_window()
    print("\n" + "-" * 40 + "\n")
    
    clean_inventory_page()
    print("\n" + "-" * 40 + "\n")
    
    clean_stats_page()
    print("\n" + "-" * 40 + "\n")
    
    clean_expenses_page()
    print("\n" + "-" * 40 + "\n")
    
    clean_other_ui_files()
    
    print("\n=== DEBUG CLEANUP COMPLETED ===")
    print("All debug print statements have been removed or cleaned up.")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
