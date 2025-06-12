#!/usr/bin/env python3
"""
Quick check for receipt directory permissions and file creation.

This script:
1. Checks if receipt directories exist
2. Tests if we can create a test file in each directory
3. Logs the results to a specific file in the home directory for easy access
"""

import os
import sys
import datetime
import traceback

LOG_FILE = os.path.expanduser("~/receipt_permission_check.log")

def log_message(message):
    """Log a message to both console and file."""
    print(message)
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp}: {message}\n")

def main():
    log_message("\n===== RECEIPT DIRECTORY PERMISSION CHECK =====")
    log_message(f"Log file: {LOG_FILE}")
    
    # Get current directory
    current_dir = os.getcwd()
    log_message(f"Current directory: {current_dir}")
    
    # Define receipt directories
    desktop_app_dir = os.path.join(current_dir, "desktop_app")
    desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
    backend_receipt_dir = os.path.join(current_dir, "receipt")
    
    # Define directories to check
    directories = {
        "Backend Receipt Dir": backend_receipt_dir,
        "Desktop App Receipt Dir": desktop_receipt_dir,
        "Desktop App Dir": desktop_app_dir,
        "Current Dir": current_dir
    }
    
    # Check each directory
    for name, directory in directories.items():
        log_message(f"\nChecking {name}: {directory}")
        
        # Check if directory exists
        if os.path.exists(directory):
            log_message(f"✅ Directory exists")
            
            # Check permissions
            try:
                stat_info = os.stat(directory)
                mode = oct(stat_info.st_mode)[-3:]
                log_message(f"Permissions: {mode}")
                log_message(f"Readable: {os.access(directory, os.R_OK)}")
                log_message(f"Writable: {os.access(directory, os.W_OK)}")
                log_message(f"Executable: {os.access(directory, os.X_OK)}")
            except Exception as e:
                log_message(f"❌ Error checking permissions: {e}")
            
            # Try to create a test file
            test_file = os.path.join(directory, "test_permissions.txt")
            try:
                with open(test_file, "w") as f:
                    f.write(f"Test file created at {datetime.datetime.now()}\n")
                    f.write(f"Python version: {sys.version}\n")
                log_message(f"✅ Successfully created test file: {test_file}")
                
                # Try to read it back
                with open(test_file, "r") as f:
                    content = f.read().strip()
                log_message(f"✅ Successfully read test file: {len(content)} characters")
                
                # Try to remove it
                os.remove(test_file)
                log_message(f"✅ Successfully removed test file")
            except Exception as e:
                log_message(f"❌ Error with test file operations: {e}")
                log_message(traceback.format_exc())
        else:
            log_message(f"❌ Directory does not exist")
            
            # Try to create it
            try:
                os.makedirs(directory)
                log_message(f"✅ Successfully created directory")
                
                # Try to create a test file in the new directory
                test_file = os.path.join(directory, "test_permissions.txt")
                with open(test_file, "w") as f:
                    f.write(f"Test file created at {datetime.datetime.now()}\n")
                log_message(f"✅ Successfully created test file in new directory: {test_file}")
                
                # Try to remove it
                os.remove(test_file)
                log_message(f"✅ Successfully removed test file")
            except Exception as e:
                log_message(f"❌ Error creating directory or test file: {e}")
                log_message(traceback.format_exc())
    
    log_message("\n===== RECEIPT DIRECTORY CHECK COMPLETED =====")
    log_message(f"Full log saved to: {LOG_FILE}")
    log_message("Next steps:")
    log_message("1. Open the POS system")
    log_message("2. Create a test sale")
    log_message("3. Check if the receipt is generated")
    log_message("4. If issues persist, check the log file at ~/receipt_debug.log")

if __name__ == "__main__":
    main()
