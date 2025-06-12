#!/usr/bin/env python3
"""
Wrapper script to start the Shiakati Store application with the patched APIClient.
This ensures that the get_inventory method is available before the application starts.
"""
import os
import sys
import importlib

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Applying API client patch...")
# First, apply the patch to add the missing get_inventory method
try:
    import patch_api_client
    print("API client patched successfully!")
except Exception as e:
    print(f"Error applying APIClient patch: {e}")
    sys.exit(1)

print("Starting Shiakati Store application...")
# Import and run the main application
try:
    import main
    main.main()
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
