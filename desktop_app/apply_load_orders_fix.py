#!/usr/bin/env python3

def replace_method(file_path, method_name, replacement_file):
    """Replace a method in a Python file with a corrected version."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    with open(replacement_file, 'r', encoding='utf-8') as file:
        replacement = file.read()
    
    # Find the method to replace
    start_line = -1
    end_line = -1
    
    for i, line in enumerate(content):
        if f"def {method_name}" in line:
            start_line = i
            break
    
    if start_line == -1:
        print(f"Could not find method {method_name} in {file_path}")
        return False
    
    # Find the next method definition
    for i, line in enumerate(content[start_line+1:], start=start_line+1):
        if line.strip().startswith("def "):
            end_line = i
            break
    
    if end_line == -1:
        # If no next method is found, go to the end of the file
        end_line = len(content)
    
    # Replace the method
    new_content = content[:start_line] + [replacement] + content[end_line:]
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_content)
    
    return True

if __name__ == "__main__":
    file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page.py"
    replacement_file = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/fixed_load_orders_data.txt"
    method_name = "load_orders_data"
    
    if replace_method(file_path, method_name, replacement_file):
        print(f"Successfully replaced method {method_name} in {file_path}")
    else:
        print(f"Failed to replace method {method_name} in {file_path}")
