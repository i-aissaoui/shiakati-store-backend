#!/usr/bin/env python3
import sys
import os
import re

def rewrite_api_client(file_path):
    try:
        # Create a fixed file path
        fixed_file_path = file_path + ".fixed"
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Process line by line to fix issues
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Fix specific syntax errors we know about
            # Case 1: Multiple statements on one line with "if response.status_code != 200:"
            if "if response.status_code != 200:" in line and "if response.status_code ==" in line:
                # Extract the base indentation
                indentation = re.match(r'^(\s*)', line).group(1)
                
                # Split the first if statement
                parts = line.split("if response.status_code != 200:")
                first_part = parts[0] + "if response.status_code != 200:\n"
                
                # Process the remaining parts with proper indentation
                remaining = parts[1].strip()
                
                # Handle nested if
                if "if response.status_code == 401:" in remaining:
                    nested_parts = remaining.split("if response.status_code == 401:")
                    if_line = indentation + "    if response.status_code == 401:\n"
                    
                    # Check if there's an elif
                    if "elif response.status_code == 404:" in nested_parts[1]:
                        elif_parts = nested_parts[1].split("elif response.status_code == 404:")
                        
                        # Add appropriate print statements
                        fixed_lines.extend([
                            first_part,
                            indentation + "    print(f\"Error: {response.status_code}\")\n",
                            if_line,
                            indentation + "        print(\"Authentication error - please log in again\")\n",
                            indentation + "    elif response.status_code == 404:\n",
                            indentation + "        print(\"API endpoint not found\")\n"
                        ])
                        
                        # Check for else
                        if "else:" in elif_parts[1]:
                            else_parts = elif_parts[1].split("else:")
                            fixed_lines.extend([
                                indentation + "    else:\n",
                                indentation + "        print(f\"Server response: {response.text}\")\n",
                            ])
                            
                            # Check for return
                            if "return" in else_parts[1]:
                                return_parts = else_parts[1].split("return")
                                return_val = return_parts[1].strip()
                                fixed_lines.append(indentation + "    return " + return_val + "\n")
                    
                    # If no elif, just add the closing
                    else:
                        fixed_lines.append(indentation + "    return []\n")
                
                # Move past this problematic line
                i += 1
                continue
            
            # Case 2: if statement combined with except
            if "if not variants:" in line and "return" in line and len(line.strip()) > 30:
                indentation = re.match(r'^(\s*)', line).group(1)
                fixed_lines.extend([
                    indentation + "if not variants:\n",
                    indentation + "    print(\"No variants found in inventory\")\n",
                    indentation + "    return []\n",
                    indentation + "print(f\"Retrieved {len(variants)} variants\")\n"
                ])
                i += 1
                continue
                
            # Case 3: except statement merged with return
            if "except" in line and "return" in line and len(line.strip()) > 25:
                parts = line.split("except")
                first = parts[0] + "except"
                indentation = re.match(r'^(\s*)', line).group(1)
                
                # Extract the exception type
                exception_parts = parts[1].split(":")
                exception_type = exception_parts[0]
                fixed_lines.extend([
                    first + exception_type + ":\n",
                    indentation + "    print(f\"Error: {str(e)}\")\n",
                    indentation + "    return []\n"
                ])
                i += 1
                continue
            
            # Case 4: else statement merged with except
            if "else:" in line and "except" in line:
                indentation = re.match(r'^(\s*)', line).group(1)
                fixed_lines.extend([
                    indentation + "else:\n",
                    indentation + "    print(f\"Warning: Status code {response.status_code}\")\n"
                ])
                
                # Extract the exception part
                parts = line.split("except")
                exception_line = indentation + "except" + parts[1]
                fixed_lines.append(exception_line)
                i += 1
                continue
            
            # Default - keep the line as is
            fixed_lines.append(line)
            i += 1
        
        # Write the fixed content to the new file
        with open(fixed_file_path, 'w') as f:
            f.writelines(fixed_lines)
        
        # Replace the original file with the fixed version
        os.rename(fixed_file_path, file_path)
        
        print(f"Successfully fixed {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing file: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix_api_client.py <file_path>")
        sys.exit(1)
    
    success = rewrite_api_client(sys.argv[1])
    sys.exit(0 if success else 1)
