#!/usr/bin/env python3
"""
Script to list unnecessary test and development files in the project.
"""

import os
import sys

def list_files_to_clean():
    """List unnecessary files in the project without removing them."""
    print("===== FILES TO CLEAN UP =====")
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Base directory: {base_dir}")
    
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
        
        # This script and the cleanup script
        "cleanup_project.py",
        "list_files_to_clean.py",
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
    
    files_to_delete = []
    files_to_keep = []
    
    print("\nScanning files...")
    
    # Get list of all files in the directory
    all_files = os.listdir(base_dir)
    print(f"Found {len(all_files)} files/directories in base directory")
    
    # Process all files in the base directory
    for item in all_files:
        item_path = os.path.join(base_dir, item)
        
        # Skip essential directories
        if os.path.isdir(item_path) and item in essential_dirs:
            print(f"Will keep directory: {item}")
            continue
        
        # Keep essential files
        if item in essential_files:
            files_to_keep.append(item)
            continue
        
        # Check if it's a test file
        is_test_file = any(pattern in item for pattern in test_file_patterns)
        
        # Check if it's a log file
        is_log_file = any(pattern in item for pattern in log_file_patterns)
        
        # Check if it's in explicit removal list
        is_unwanted = item in files_to_remove
        
        # Check if it's a backup file
        is_backup = any(pattern in item for pattern in backup_patterns)
        
        # Mark for deletion if any condition is met
        if is_test_file or is_log_file or is_unwanted or is_backup:
            files_to_delete.append((item, "test file" if is_test_file else
                                         "log file" if is_log_file else 
                                         "unwanted file" if is_unwanted else
                                         "backup file"))
        else:
            files_to_keep.append(item)
    
    # Summary
    print("\n===== FILES MARKED FOR DELETION =====")
    if len(files_to_delete) > 0:
        for file, reason in sorted(files_to_delete):
            print(f" - {file} ({reason})")
    else:
        print("No files marked for deletion")
    
    print("\n===== FILES TO KEEP =====")
    for file in sorted(files_to_keep):
        print(f" - {file}")
    
    print(f"\nTotal: {len(files_to_delete)} files to delete, {len(files_to_keep)} files to keep")
    print("\nTo delete these files, run: python cleanup_project.py")
    
    return True

if __name__ == "__main__":
    try:
        success = list_files_to_clean()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
