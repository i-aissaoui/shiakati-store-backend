#!/usr/bin/env python3

def fix_document_print(file_path):
    """Fix the syntax error with document.print in the orders_page.py file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the problematic patterns
    content = content.replace('document.            # Show success message', 'document.print(printer)\n            # Show success message')
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return True

if __name__ == "__main__":
    file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page.py"
    if fix_document_print(file_path):
        print(f"Successfully fixed document.print issue in {file_path}")
    else:
        print(f"Failed to fix document.print issue in {file_path}")
