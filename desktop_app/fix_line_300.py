#!/usr/bin/env python3
import sys
import os
import re

def fix_line_300_onwards(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # First, fix the "if not variants: return []" pattern at line 300
    pattern1 = r'if not variants:\s+return \[]'
    replacement1 = 'if not variants:\n                    print("No variants found in inventory")\n                    return []\n                print(f"Retrieved {len(variants)} variants")'
    content = re.sub(pattern1, replacement1, content)
    
    # Fix the "else: except Exception as e:" issue at line 318
    pattern2 = r'else:\s+except Exception as e:'
    replacement2 = 'else:\n                        print(f"Warning: Failed to get product {product_id}: {product_response.status_code}")\n                except Exception as e:'
    content = re.sub(pattern2, replacement2, content)
    
    # Save fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed lines in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix_line_300.py <file_path>")
        sys.exit(1)
    
    fix_line_300_onwards(sys.argv[1])
