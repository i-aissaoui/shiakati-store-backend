#!/usr/bin/env python3

import re
import os

def fix_directly():
    file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page.py"
    
    # Create a completely new file with correct syntax
    new_file_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/ui/main_window_new/orders_page_fixed.py"
    
    imports = '''"""
Orders Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox, QDialog,
    QTextEdit, QHeaderView, QFileDialog, QFormLayout, QComboBox,
    QDialogButtonBox, QApplication
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QColor, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPageSize

import os
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
'''
    
    # Read the original file and extract the class content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the class definition and onward
    class_match = re.search(r'class OrdersPageMixin:', content)
    if not class_match:
        print("Could not find the OrdersPageMixin class in the file.")
        return False
    
    # Extract the class content
    class_content = content[class_match.start():]
    
    # Fix any syntax issues in the class content
    class_content = class_content.replace('document.            # Show success message', 'document.print(printer)\n            # Show success message')
    
    # Create the new fixed file
    with open(new_file_path, 'w') as f:
        f.write(imports + "\n\n" + class_content)
    
    print(f"Created fixed file at {new_file_path}")
    
    # Test if the new file compiles correctly
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', new_file_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("New file compiles without errors!")
        # Replace the original file with the fixed one
        os.rename(new_file_path, file_path)
        print(f"Successfully replaced {file_path} with fixed version.")
        return True
    else:
        print(f"Compilation failed: {result.stderr}")
        return False

if __name__ == "__main__":
    fix_directly()
