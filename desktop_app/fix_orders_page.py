#!/usr/bin/env python3

def fix_imports(file_path):
    """Fix the imports in orders_page.py to make sure all used modules are properly imported."""
    import_block = '''"""
Orders Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox, QDialog,
    QTextEdit, QHeaderView, QFileDialog, QFormLayout, QComboBox,
    QDialogButtonBox, QApplication
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QColor
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument, QPageSize

import datetime
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

'''

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find where the class definition starts
    class_start = content.find('class OrdersPageMixin:')
    if class_start != -1:
        # Replace everything before the class with our new import block
        new_content = import_block + content[class_start:]
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        return True
    
    return False

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
    if fix_imports(file_path):
        print(f"Successfully fixed imports in {file_path}")
    else:
        print(f"Failed to fix imports in {file_path}")
        
    if fix_document_print(file_path):
        print(f"Successfully fixed document.print issue in {file_path}")
    else:
        print(f"Failed to fix document.print issue in {file_path}")
