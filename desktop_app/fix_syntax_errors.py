#!/usr/bin/env python3

import sys

def fix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Fix for line 292
    line_292_fixed = False
    for i in range(len(lines)):
        if "if response.status_code != 200:" in lines[i] and "if response.status_code == 401:" in lines[i]:
            parts = lines[i].split("if response.status_code != 200:")
            prefix = parts[0] + "if response.status_code != 200:\n"
            
            remaining = parts[1].strip()
            if_parts = remaining.split("if response.status_code == 401:")
            if len(if_parts) > 1:
                if_content = if_parts[1]
                
                # Check for elif and else parts
                elif_parts = if_content.split("elif response.status_code == 404:")
                if len(elif_parts) > 1:
                    elif_content = elif_parts[1]
                    
                    # Check for else part
                    else_parts = elif_content.split("else:")
                    if len(else_parts) > 1:
                        else_content = else_parts[1]
                        
                        # Now rebuild the line properly
                        new_lines = [
                            prefix,
                            parts[0] + "    if response.status_code == 401:\n",
                            parts[0] + "        print(\"Authentication error - please log in again\")\n",
                            parts[0] + "    elif response.status_code == 404:\n",
                            parts[0] + "        print(\"Variants endpoint not found - check server URL\")\n",
                            parts[0] + "    else:\n",
                            parts[0] + "        print(f\"Server response: {response.text}\")\n",
                            parts[0] + "    return []\n"
                        ]
                        lines[i:i+1] = new_lines
                        line_292_fixed = True
                        break
    
    # Fix for line 411
    line_411_fixed = False
    for i in range(len(lines)):
        if "if response.status_code != 200:" in lines[i] and "if response.status_code != 500:" in lines[i]:
            parts = lines[i].split("if response.status_code != 200:")
            prefix = parts[0] + "if response.status_code != 200:\n"
            
            remaining = parts[1].strip()
            if_parts = remaining.split("if response.status_code != 500:")
            if len(if_parts) > 1:
                if_content = if_parts[1]
                
                # Now rebuild the line properly
                new_lines = [
                    prefix,
                    parts[0] + "    print(f\"Error getting stats: {response.status_code}\")\n",
                    parts[0] + "    if response.status_code != 500:\n",
                    parts[0] + "        print(f\"Error response: {response.text}\")\n",
                    parts[0] + "    return {}\n"
                ]
                lines[i:i+1] = new_lines
                line_411_fixed = True
                break
    
    # Fix for data.json() issues
    for i in range(len(lines)):
        if "data = response.json()" in lines[i] and "if not isinstance(data, dict):" in lines[i]:
            parts = lines[i].split("data = response.json()")
            prefix = parts[0] + "data = response.json()\n"
            
            new_lines = [
                prefix,
                parts[0] + "if not isinstance(data, dict):\n",
                parts[0] + "    print(f\"Unexpected response type: {type(data)}\")\n",
                parts[0] + "    return {}\n"
            ]
            lines[i:i+1] = new_lines
            break
    
    print(f"Fixed lines: 292={line_292_fixed}, 411={line_411_fixed}")
    
    # Look for any if statement with multiple statements on the same line
    for i in range(len(lines)):
        if "if " in lines[i] and ":" in lines[i] and "    if " in lines[i]:
            # This line might have multiple if statements
            print(f"Potential issue on line {i+1}: {lines[i].strip()}")
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
        
    print(f"Fixed file: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix_syntax_errors.py <file_path>")
        sys.exit(1)
    
    fix_file(sys.argv[1])
