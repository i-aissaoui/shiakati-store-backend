#!/usr/bin/env python3
# filepath: /home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/run_app.py
"""
Comprehensive entry point for the Shiakati Store POS application.
This script provides multiple options to run the application with different fixes.
"""

import os
import sys
import traceback
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_with_standalone_client():
    """Run the application using the standalone fixed API client."""
    try:
        # Import and apply the standalone fixed API client
        print("Loading standalone fixed API client...")
        import api_client_fixed_standalone
        api_client_fixed_standalone.apply_fixed_client()
        
        # Now import and run the application
        from PyQt5.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        print("Starting Shiakati Store POS application with standalone API client...")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Application window displayed successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error when running with standalone client: {e}")
        traceback.print_exc()
        return False
    return True

def run_with_patched_client():
    """Run the application using the patched original API client."""
    try:
        # Apply the complete fix patch
        from api_client_complete_fix import apply_fixes
        print("Applying complete API client fixes...")
        apply_fixes()
        
        # Now import and run the application
        from PyQt5.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        print("Starting Shiakati Store POS application with patched API client...")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Application window displayed successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error when running with patched client: {e}")
        traceback.print_exc()
        return False
    return True

def run_with_fixed_original():
    """Run the application after fixing the syntax error in the original API client."""
    try:
        # Fix the syntax error in the original API client
        from fix_communes_dict import fix_api_client_syntax
        print("Fixing syntax error in original API client...")
        if not fix_api_client_syntax():
            print("Failed to fix syntax error in original API client")
            return False
        
        # Now import and run the application
        from PyQt5.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        print("Starting Shiakati Store POS application with fixed original API client...")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Application window displayed successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error when running with fixed original client: {e}")
        traceback.print_exc()
        return False
    return True

def run_original():
    """Run the application using the original main.py entry point."""
    try:
        print("Running original main.py entry point...")
        # We'll use os.system to run the main.py script
        import os
        main_script = os.path.join(project_root, "main.py")
        os.system(f"python {main_script}")
        return True
    except Exception as e:
        print(f"Error when running original entry point: {e}")
        traceback.print_exc()
        return False

def main():
    """Parse arguments and run the application with the selected fix."""
    parser = argparse.ArgumentParser(description="Run Shiakati Store POS application with different API client fixes.")
    parser.add_argument("--mode", choices=["auto", "standalone", "patched", "fixed-original", "original"], 
                        default="auto", help="Fix mode to use")
    
    args = parser.parse_args()
    
    if args.mode == "auto":
        print("Auto-selecting best API client fix...")
        # Try each method in order of preference
        if run_with_standalone_client():
            return
        print("\nStandalone client failed, trying patched client...")
        if run_with_patched_client():
            return
        print("\nPatched client failed, trying to fix original client...")
        if run_with_fixed_original():
            return
        print("\nAll fix methods failed, falling back to original entry point...")
        run_original()
    
    elif args.mode == "standalone":
        run_with_standalone_client()
    
    elif args.mode == "patched":
        run_with_patched_client()
    
    elif args.mode == "fixed-original":
        run_with_fixed_original()
    
    elif args.mode == "original":
        run_original()

if __name__ == "__main__":
    main()