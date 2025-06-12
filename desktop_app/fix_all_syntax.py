#!/usr/bin/env python3

import re

def fix_all_syntax(file_path):
    # Read in the imports
    with open('/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/orders_imports.txt', 'r') as f:
        new_imports = f.read()

    # Read the target file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the class start
    class_pattern = r'class OrdersPageMixin:'
    match = re.search(class_pattern, content)
    if match:
        class_start = match.start()
        # Replace everything before the class definition
        new_content = new_imports + '\n\n' + content[class_start:]
        
        # Fix document.print issues
        new_content = new_content.replace('document.            # Show success message', 'document.print(printer)\n            # Show success message')

        # Fix any remaining malformed/incomplete lines
        lines = new_content.split("\n")
        for i, line in enumerate(lines):
            if "QMessageBox.warning(self, " in line and line.endswith(","):
                # If a line ends with a comma but is supposed to be the end of a statement
                lines[i] = line.rstrip(",")
        
        # Join back and write the result
        with open(file_path, 'w') as f:
            f.write("\n".join(lines))
        
        return True
    
    return False

if __name__ == "__main__":
    file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page.py"
    if fix_all_syntax(file_path):
        print("Successfully fixed all syntax issues in the file!")
    else:
        print("Failed to fix syntax issues.")
