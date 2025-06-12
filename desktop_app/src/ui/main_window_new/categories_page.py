"""
Categories Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QHeaderView, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class CategoriesPageMixin:
    """Mixin class for the Categories page functionality."""
    
    def setup_categories_page(self):
        """Set up the Categories management page."""
        layout = QVBoxLayout(self.categories_page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header and add button section
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Product Categories")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        add_category_btn = QPushButton("➕ Add Category")
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #4834d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #686de0;
            }
        """)
        header_layout.addWidget(add_category_btn)
        
        layout.addLayout(header_layout)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)  # ID, Name, Actions
        self.categories_table.setHorizontalHeaderLabels([
            "ID", "Category Name", "Actions"
        ])
        self.categories_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f2f6;
                min-height: 20px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
            }
        """)
        self.categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # ID column
        self.categories_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Name column stretches
        self.categories_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)  # Actions column
        self.categories_table.setColumnWidth(0, 80)   # ID
        self.categories_table.setColumnWidth(2, 200)  # Actions - Make it wider

        # Increase row height for better icon visibility
        self.categories_table.verticalHeader().setDefaultSectionSize(50)
        self.categories_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.categories_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.categories_table)
        
        # Load categories data
        self.load_categories()
    
    def load_categories_data(self):
        """Wrapper for load_categories to match the method name in base.py."""
        self.load_categories()
        
    def load_categories(self):
        """Load categories into the table."""
        try:
            categories = self.api_client.get_categories()
            self.categories_table.setRowCount(0)
            
            if not categories:
                return
                
            for cat in categories:
                row = self.categories_table.rowCount()
                self.categories_table.insertRow(row)
                
                # Add category data
                self.categories_table.setItem(row, 0, QTableWidgetItem(str(cat.get("id", ""))))
                self.categories_table.setItem(row, 1, QTableWidgetItem(cat.get("name", "")))
                
                # Create widget for action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 0, 2, 0)
                actions_layout.setSpacing(4)
                
                # Create edit button - make it compact
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedWidth(40)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                        font-size: 16px;
                        min-height: 25px;
                        max-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.setToolTip("Edit category")
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_category(r))
                
                # Create delete button - make it compact
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedWidth(40)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                        font-size: 16px;
                        min-height: 25px;
                        max-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.setToolTip("Delete category")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_category(r))
                
                # Add buttons to layout
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.categories_table.setCellWidget(row, 2, actions_widget)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load categories: {str(e)}")
            
    def show_add_category_dialog(self):
        """Show dialog for adding a new category."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Category")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        
        # Create input field
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter category name")
        name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                font-size: 14px;
                min-width: 250px;
            }
        """)
        
        # Add field to form
        layout.addRow("Category Name:", name_input)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Category name is required")
                return
                
            try:
                response = self.api_client.create_category({"name": name})
                if response and "id" in response:
                    QMessageBox.information(self, "Success", "Category added successfully")
                    self.load_categories()  # Refresh the categories table
                else:
                    QMessageBox.warning(self, "Error", "Failed to create category")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create category: {str(e)}")
    
    def edit_category(self, row):
        """Edit a category."""
        category_id = self.categories_table.item(row, 0).text()
        current_name = self.categories_table.item(row, 1).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Category")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        
        # Create input field with current value
        name_input = QLineEdit(current_name)
        name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                font-size: 14px;
                min-width: 250px;
            }
        """)
        
        # Add field to form
        layout.addRow("Category Name:", name_input)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Category name is required")
                return
                
            try:
                response = self.api_client.update_category(category_id, {"name": name})
                if response:
                    QMessageBox.information(self, "Success", "Category updated successfully")
                    self.load_categories()  # Refresh the categories table
                    
                    # Also refresh the inventory table and product list since category names may have changed
                    self.setup_inventory_table()
                    self.load_product_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update category")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update category: {str(e)}")
    
    def delete_category(self, row):
        """Delete a category."""
        category_id = self.categories_table.item(row, 0).text()
        category_name = self.categories_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Delete Category",
            f"Are you sure you want to delete the category '{category_name}'?\n\n"
            f"This action may affect products assigned to this category.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = self.api_client.delete_category(category_id)
                if response:
                    QMessageBox.information(self, "Success", "Category deleted successfully")
                    self.load_categories()  # Refresh the categories table
                    
                    # Also refresh the inventory table and product list since products may have been affected
                    self.setup_inventory_table()
                    self.load_product_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete category")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete category: {str(e)}")
