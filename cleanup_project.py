#!/usr/bin/env python3
"""
Script to clean up unnecessary test and development files from the project.
"""

import os
import shutil
import time
import sys

def cleanup_project():
    """Remove unnecessary files from the project."""
    print("===== CLEANING UP PROJECT FILES =====")
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to keep (essential files)
    essential_files = [
        # Core files
        "alembic.ini",
        "README.md",
        "requirements.txt",
        "schema.sql",
        ".env",
        "main.py",
        
        # The solution files we want to keep
        "final_receipt_fix.py",
        "RECEIPT_FIX_SUMMARY.md",
        
        # This cleanup script
        "cleanup_project.py",
    ]

    # Directories to keep (always)
    essential_dirs = [
        "alembic",
        "app",
        "desktop_app",
        "receipt",
        "__pycache__",
        ".git",
    ]
    
    # Test files pattern to be removed
    test_file_patterns = [
        "test_",
        "fix_",
        "debug_",
        "check_",
        "verify_",
        "diagnose_",
        "manual_",
        "direct_",
        "create_test_",
        "simple_test_",
        "simple_fix",
    ]
    
    # Log files to remove
    log_file_patterns = [
        ".log",
        "output",
    ]
    
    # Files to remove (by exact name)
    files_to_remove = [
        "auth_output.log",
        "auth_output2.log",
        "auth_response.json",
        "hello_test.py",
        "output.log",
        "server_output.log",
        "z-note-creating order.txt",
        "hiakati psql -h localhost -U shiakati -d shiakati -c \""
    ]
    
    # Temporary backup files
    backup_patterns = [
        ".bak_",
        ".backup",
        "~"
    ]
    
    removed_files = []
    kept_files = []
    
    print("\nScanning files...")
    
    # Process all files in the base directory
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        
        # Skip essential directories
        if os.path.isdir(item_path) and item in essential_dirs:
            print(f"✓ Keeping directory: {item}")
            continue
        
        # Keep essential files
        if item in essential_files:
            print(f"✓ Keeping essential file: {item}")
            kept_files.append(item)
            continue
        
        # Check if it's a test file
        is_test_file = any(pattern in item for pattern in test_file_patterns)
        
        # Check if it's a log file
        is_log_file = any(pattern in item for pattern in log_file_patterns)
        
        # Check if it's in explicit removal list
        is_unwanted = item in files_to_remove
        
        # Check if it's a backup file
        is_backup = any(pattern in item for pattern in backup_patterns)
        
        # Remove if any condition is met
        if is_test_file or is_log_file or is_unwanted or is_backup:
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    removed_files.append(item)
                    print(f"✓ Removed file: {item}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    removed_files.append(item)
                    print(f"✓ Removed directory: {item}")
            except Exception as e:
                print(f"✗ Failed to remove {item}: {e}")
        else:
            kept_files.append(item)
            print(f"? Keeping file (not identified as unnecessary): {item}")
    
    # Clean up backup files from desktop_app/src/ui/main_window_new
    ui_dir = os.path.join(base_dir, "desktop_app", "src", "ui", "main_window_new")
    if os.path.exists(ui_dir):
        print("\nCleaning backup files in UI directory...")
        for item in os.listdir(ui_dir):
            if any(pattern in item for pattern in backup_patterns):
                try:
                    item_path = os.path.join(ui_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"✓ Removed backup file from UI directory: {item}")
                except Exception as e:
                    print(f"✗ Failed to remove backup {item}: {e}")
    
    # Summary
    print("\n===== CLEANUP SUMMARY =====")
    print(f"Removed {len(removed_files)} unnecessary files")
    print(f"Kept {len(kept_files)} files")
    
    print("\nRemoved files:")
    for file in sorted(removed_files):
        print(f" - {file}")
    
    print("\nKept files (excluding directories):")
    for file in sorted(kept_files):
        if os.path.isfile(os.path.join(base_dir, file)):
            print(f" - {file}")
    
    print("\nCleanup completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = cleanup_project()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
