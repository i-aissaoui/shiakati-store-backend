# test_api_client_syntax.py
import sys
import ast
import os

# Get the path to the API client file
api_client_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "src", "utils", "api_client.py"
)

print(f"Checking syntax of {api_client_path}")

try:
    # Open the file and read the contents
    with open(api_client_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Parse the code using ast
    parsed = ast.parse(code)
    print("File syntax is valid! No syntax errors found.")
    
    # Count methods in the APIClient class
    class_methods = []
    for node in ast.walk(parsed):
        if isinstance(node, ast.ClassDef) and node.name == 'APIClient':
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_methods.append(item.name)
    
    print(f"Found {len(class_methods)} methods in APIClient class:")
    for method in sorted(class_methods):
        print(f"- {method}")
    
except SyntaxError as e:
    line_no = e.lineno
    col_no = e.offset
    print(f"Syntax error at line {line_no}, column {col_no}:")
    print(f"  {e.text.strip() if e.text else ''}")
    print(f"  {' ' * (col_no - 1)}^")
    print(e)
    
    # Get a few lines around the error for context
    with open(api_client_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start_line = max(0, line_no - 5)
    end_line = min(len(lines), line_no + 5)
    
    print("\nContext:")
    for i in range(start_line, end_line):
        prefix = "-> " if i + 1 == line_no else "   "
        print(f"{prefix}{i + 1}: {lines[i].rstrip()}")
    
    sys.exit(1)
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
