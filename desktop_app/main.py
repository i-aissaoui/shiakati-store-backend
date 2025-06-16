#!/usr/bin/env python3
# filepath: /home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/main.py
import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import QApplication
    try:
        # First attempt to import from the new refactored module
        from src.ui.main_window_new import MainWindow
        print("Successfully imported from main_window_new")
    except ImportError as e:
        print(f"Import error from main_window_new: {str(e)}")
        print("Falling back to original implementation")
        # Fall back to the original implementation if the refactored one is not ready
        from src.ui.main_window import MainWindow
except Exception as e:
    print(f"Critical error during imports: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec_()
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        traceback.print_exc()
        return 1

def fix_communes_dict():
    """Fix the duplicate communes dictionary entries in api_client.py."""
    try:
        import os
        import re
        
        print("Fixing communes dictionary duplicates in api_client.py...")
        api_client_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'src', 'utils', 'api_client.py')
        
        # Read the file
        with open(api_client_path, 'r') as f:
            content = f.read()
            
        # Define the fixed communes dictionary
        replacement = '''        communes = {
            "Alger": ["Bab Ezzouar", "Hydra", "El Biar", "Kouba"],
            "Oran": ["Bir El Djir", "Es Senia", "Arzew"],
            "Constantine": ["El Khroub", "Ain Smara"],
            "Annaba": ["El Bouni", "Sidi Amar"],
            "Batna": ["Tazoult", "Timgad"],
            "Blida": ["Boufarik", "Beni Mered"]
        }'''
        
        # Fix all instances of duplicate or incomplete dictionaries
        lines = content.split('\n')
        fixed_lines = []
        skip_mode = False
        communes_dict_complete = False
        
        for i, line in enumerate(lines):
            if '"Blida": ["Boufarik", "Beni Mered"]' in line and not communes_dict_complete:
                fixed_lines.append(line)
                fixed_lines.append("        }")
                communes_dict_complete = True
                skip_mode = True
                continue
            
            if skip_mode and '"Constantine": ["El Khroub", "Ain Smara"],' in line:
                # We're in the duplicate part, skip until we reach the closing brace
                continue
                
            if skip_mode and 'product_names' in line:
                # We've reached the end of the duplicate section
                skip_mode = False
                fixed_lines.append(line)
                continue
                
            if not skip_mode:
                fixed_lines.append(line)
        
        # Write the fixed content back
        with open(api_client_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
            
        print("Fixed communes dictionary in api_client.py")
        return True
    except Exception as e:
        print(f"Error fixing communes dictionary: {str(e)}")
        return False

def apply_inventory_patch():
    """Apply the inventory patch to ensure API client has all necessary methods."""
    try:
        # First, fix the syntax error in the communes dictionary
        fix_communes_dict()
        
        print("Applying complete API client fixes...")
        
        # Use the complete API client fix that handles all issues
        from api_client_complete_fix import apply_fixes
        apply_fixes()
        print("Complete API client fixes successfully applied")
        
        # Then apply the enhancement to show all products (including those without variants)
        print("Applying enhancement to show all products in inventory...")
        from add_missing_products_fix import apply_fix
        apply_fix()
        print("All products will now be displayed in inventory (with and without variants)")
    except Exception as e:
        print(f"Error applying API client fixes: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        print("Starting Shiakati Store POS application...")
        
        # Apply the API patches
        apply_inventory_patch()
        
        # Start the application
        main_app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        print("Application window created and shown")
        sys.exit(main_app.exec_())
    except Exception as e:
        print(f"Fatal application error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)