#!/usr/bin/env python3

def fix_syntax_error(file_path):
    """Fix the syntax error in the orders_page.py file by ensuring the correct indentation and proper syntax."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    # Find the load_orders_data method
    start_line = -1
    end_line = -1
    for i, line in enumerate(content):
        if "def load_orders_data(self):" in line:
            start_line = i
        elif start_line != -1 and "def filter_orders" in line:
            end_line = i
            break
    
    if start_line != -1 and end_line != -1:
        # Fix the try-except block
        method_content = content[start_line:end_line]
        fixed_content = []
        indent = "    "  # Base indentation for class methods
        
        # Add the method signature
        fixed_content.append(method_content[0])
        
        # Add docstring if present
        if '"""' in method_content[1]:
            fixed_content.append(method_content[1])
            start_idx = 2
        else:
            start_idx = 1
        
        # Create fixed try-except block
        fixed_content.append(f"{indent}    try:\n")
        
        # Find the except block
        in_except = False
        for line in method_content[start_idx:]:
            if 'except Exception as e:' in line:
                in_except = True
                fixed_content.append(f"{indent}    except Exception as e:\n")
            elif in_except and 'def filter_orders' in line:
                break
            elif in_except:
                fixed_content.append(line)
            elif 'try:' not in line:  # Skip the original try line
                fixed_content.append(line)
        
        # Replace the original method with the fixed one
        content[start_line:end_line] = fixed_content
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(content)
        
        return True
    
    return False

if __name__ == "__main__":
    file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page.py"
    if fix_syntax_error(file_path):
        print(f"Successfully fixed syntax error in {file_path}")
    else:
        print(f"Failed to fix syntax error in {file_path}")
