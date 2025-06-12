#!/usr/bin/env python3
"""
File test with logging
"""

import os
import sys
import datetime
import traceback
import logging

# Set up logging
logging.basicConfig(
    filename="file_test.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    try:
        logging.info("===== FILE TEST WITH LOGGING =====")
        
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logging.info(f"Current directory: {current_dir}")
        
        # Define receipt directories
        desktop_app_dir = os.path.join(current_dir, "desktop_app")
        desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
        backend_receipt_dir = os.path.join(current_dir, "receipt")
        
        logging.info(f"Desktop app directory: {desktop_app_dir}")
        logging.info(f"Desktop receipt directory: {desktop_receipt_dir}")
        logging.info(f"Backend receipt directory: {backend_receipt_dir}")
        
        # Check if directories exist
        logging.info(f"Desktop app dir exists: {os.path.exists(desktop_app_dir)}")
        logging.info(f"Desktop receipt dir exists: {os.path.exists(desktop_receipt_dir)}")
        logging.info(f"Backend receipt dir exists: {os.path.exists(backend_receipt_dir)}")
        
        # Create directories if needed
        for directory in [desktop_receipt_dir, backend_receipt_dir]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    logging.info(f"Created directory: {directory}")
                except Exception as e:
                    logging.error(f"Error creating directory {directory}: {e}")
        
        # Create test files
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        test_files = [
            os.path.join(desktop_receipt_dir, f"test-{timestamp}.txt"),
            os.path.join(backend_receipt_dir, f"test-{timestamp}.txt")
        ]
        
        for test_file in test_files:
            try:
                logging.info(f"Writing to file: {test_file}")
                with open(test_file, "w") as f:
                    f.write(f"This is a test file created at {datetime.datetime.now()}")
                    f.write(f"\nPython version: {sys.version}")
                    f.write(f"\nCurrent working directory: {os.getcwd()}")
                
                # Verify file exists
                if os.path.exists(test_file):
                    size = os.path.getsize(test_file)
                    logging.info(f"File created successfully: {test_file} ({size} bytes)")
                else:
                    logging.error(f"File creation failed: {test_file}")
            except Exception as e:
                logging.error(f"Error writing to file: {e}")
                logging.error(traceback.format_exc())
        
        logging.info("File test completed")
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        logging.critical(traceback.format_exc())

if __name__ == "__main__":
    main()
