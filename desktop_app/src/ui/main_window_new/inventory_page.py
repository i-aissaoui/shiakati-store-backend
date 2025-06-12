"""
Inventory Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDialogButtonBox, QHeaderView, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import requests
import traceback
import sys


class InventoryPageMixin:
    """Mixin class for the Inventory page functionality."""
    
    def setup_inventory_page(self):
        """Set up the inventory management page."""
        layout = QVBoxLayout(self.inventory_page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products...")
        self.search_input.textChanged.connect(self.filter_inventory)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                font-size: 14px;
                min-width: 300px;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        search_layout.addStretch()
        
        add_product_btn = QPushButton("➕ Add Product")
        add_product_btn.clicked.connect(self.show_add_product_dialog)
        search_layout.addWidget(add_product_btn)
        
        layout.addLayout(search_layout)
        
        # Product table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Product Name", "Barcode", "Price (DZD)", "Stock", 
            "Category", "Size", "Color", "Actions"
        ])
        
        # Set column widths
        self.inventory_table.setColumnWidth(0, 200)  # Product Name
        self.inventory_table.setColumnWidth(1, 120)  # Barcode
        self.inventory_table.setColumnWidth(2, 100)  # Price
        self.inventory_table.setColumnWidth(3, 80)   # Stock
        self.inventory_table.setColumnWidth(4, 100)  # Category
        self.inventory_table.setColumnWidth(5, 80)   # Size
        self.inventory_table.setColumnWidth(6, 80)   # Color
        self.inventory_table.setColumnWidth(7, 100)  # Actions
        
        self.inventory_table.setMinimumHeight(400)
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f2f6;
                min-height: 20px;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Increase row height for better icon visibility
        self.inventory_table.verticalHeader().setDefaultSectionSize(50)
        layout.addWidget(self.inventory_table)
        
        # Add quick-add product form
        form_layout = QHBoxLayout()
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product Name")
        
        self.product_barcode_input = QLineEdit()
        self.product_barcode_input.setPlaceholderText("Barcode")
        
        self.product_category_combo = QComboBox()
        # Populate with categories
        try:
            categories = self.api_client.get_categories()
            for cat in categories:
                if isinstance(cat, dict):
                    self.product_category_combo.addItem(cat["name"])
        except Exception as e:
            print(f"Failed to load categories: {str(e)}")
        
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setMaximum(9999.99)
        self.apply_spinbox_styling(self.product_price_input)
        
        self.product_stock_input = QDoubleSpinBox()
        self.product_stock_input.setMaximum(9999.99)
        self.product_stock_input.setDecimals(2)
        self.apply_spinbox_styling(self.product_stock_input)
        
        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(self.product_barcode_input)
        form_layout.addWidget(self.product_category_combo)
        form_layout.addWidget(self.product_price_input)
        form_layout.addWidget(self.product_stock_input)
        
        add_button = QPushButton("Add Product")
        add_button.clicked.connect(self.handle_add_product)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Load inventory data
        self.setup_inventory_table()

    def setup_inventory_table(self):
        """Set up the inventory management table with data."""
        try:
            inventory = self.api_client.get_inventory()
            self.inventory_table.setRowCount(0)
            
            for item in inventory:
                row = self.inventory_table.rowCount()
                self.inventory_table.insertRow(row)
                self.inventory_table.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                self.inventory_table.setItem(row, 1, QTableWidgetItem(item["barcode"]))
                self.inventory_table.setItem(row, 2, QTableWidgetItem(self.format_price(item["price"])))
                self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item["quantity"])))
                self.inventory_table.setItem(row, 4, QTableWidgetItem(item["category"]))
                self.inventory_table.setItem(row, 5, QTableWidgetItem(item["size"]))
                self.inventory_table.setItem(row, 6, QTableWidgetItem(item["color"]))
                
                # Create widget for action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 0, 4, 0)
                actions_layout.setSpacing(4)
                
                # Create edit button
                edit_btn = QPushButton("✏️")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.setFixedSize(30, 25)
                edit_btn.setToolTip("Edit product")
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_inventory_item(r))
                
                # Create delete button
                delete_btn = QPushButton("🗑️")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.setFixedSize(30, 25)
                delete_btn.setToolTip("Delete product")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_inventory_item(r))
                
                # Add buttons to layout
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.inventory_table.setCellWidget(row, 7, actions_widget)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load inventory: {str(e)}")

    def filter_inventory(self):
        """Filter the inventory table based on search text."""
        search_text = self.search_input.text().lower()
        for row in range(self.inventory_table.rowCount()):
            match = False
            for col in range(self.inventory_table.columnCount() - 1):  # Exclude actions column
                item = self.inventory_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.inventory_table.setRowHidden(row, not match)

    def show_add_product_dialog(self):
        """Show dialog for adding a new product."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(400)
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        
        # Create input fields
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter product name")
        
        barcode_input = QLineEdit()
        barcode_input.setPlaceholderText("Enter or scan barcode")
        
        price_input = QDoubleSpinBox()
        price_input.setMaximum(999999.99)
        price_input.setSuffix(" DZD")
        price_input.setDecimals(2)
        
        quantity_input = QDoubleSpinBox()
        quantity_input.setMaximum(9999.99)
        quantity_input.setMinimum(0)
        quantity_input.setDecimals(2)
        
        # Create and populate category dropdown
        category_combo = QComboBox()
        try:
            categories = self.api_client.get_categories()
            if not categories:
                QMessageBox.warning(dialog, "Warning", "No categories found. Please create categories first.")
                return

            for cat in enumerate(categories):
                category_combo.addItem(cat["name"])
            
            dialog.categories = categories  # Store for later use
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load categories: {str(e)}")
            return

        size_input = QLineEdit()
        size_input.setPlaceholderText("Size (optional)")
        
        color_input = QLineEdit()
        color_input.setPlaceholderText("Color (optional)")
        
        # Add fields to form
        layout.addRow("Product Name*:", name_input)
        layout.addRow("Barcode*:", barcode_input)
        layout.addRow("Price*:", price_input)
        layout.addRow("Quantity*:", quantity_input)
        layout.addRow("Category*:", category_combo)
        layout.addRow("Size:", size_input)
        layout.addRow("Color:", color_input)
        
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
            # Get form values
            name = name_input.text().strip()
            barcode = barcode_input.text().strip()
            price = price_input.value()
            quantity = quantity_input.value()
            selected_category = category_combo.currentText()
            
            if not name:
                QMessageBox.warning(self, "Error", "Product name is required")
                return
            
            if not barcode:
                QMessageBox.warning(self, "Error", "Barcode is required")
                return
            
            if price <= 0:
                QMessageBox.warning(self, "Error", "Price must be greater than 0")
                return
            
            if quantity < 0:
                QMessageBox.warning(self, "Error", "Quantity cannot be negative")
                return
            
            # Find category id from stored categories
            category_id = None
            for cat in dialog.categories:
                if cat["name"] == selected_category:
                    category_id = cat["id"]
                    break
            
            if not category_id:
                QMessageBox.warning(self, "Error", f"Category '{selected_category}' not found")
                return
                
            # Create product first
            try:
                new_item = {
                    "name": name,
                    "category_id": category_id
                }
                
                product_response = self.api_client.create_product(new_item)
                if not product_response or "id" not in product_response:
                    raise Exception("Invalid response when creating product")
                
                # Then create the initial variant for the product
                variant_data = {
                    "product_id": product_response["id"],
                    "barcode": barcode,
                    "price": price,
                    "quantity": quantity,
                    "size": size_input.text().strip(),
                    "color": color_input.text().strip()
                }
                
                variant_response = self.api_client.create_variant(variant_data)
                if not variant_response:
                    raise Exception("Invalid response when creating variant")
                
                QMessageBox.information(self, "Success", "Product added successfully")
                
                # Refresh tables
                self.setup_inventory_table()
                self.load_product_list()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

    def handle_add_product(self):
        """Handle adding a new product from the quick-add form."""
        try:
            # Get form values
            name = self.product_name_input.text().strip()
            barcode = self.product_barcode_input.text().strip()
            
            # Get selected category
            selected_category = self.product_category_combo.currentText()
            category_id = None
            
            # Get categories to find the ID
            categories = self.api_client.get_categories()
            for cat in categories:
                if cat["name"] == selected_category:
                    category_id = cat["id"]
                    break
            
            if not category_id:
                QMessageBox.warning(self, "Error", f"Category '{selected_category}' not found")
                return
            
            # Get price and quantity
            price = self.product_price_input.value()
            quantity = self.product_stock_input.value()
            
            # Validate input
            if not name:
                QMessageBox.warning(self, "Error", "Product name is required")
                return
            
            if not barcode:
                QMessageBox.warning(self, "Error", "Barcode is required")
                return
            
            if price <= 0:
                QMessageBox.warning(self, "Error", "Price must be greater than 0")
                return
            
            if quantity < 0:
                QMessageBox.warning(self, "Error", "Quantity cannot be negative")
                return
            
            # Create product
            new_item = {
                "name": name,
                "category_id": category_id
            }
            
            product_response = self.api_client.create_product(new_item)
            if not product_response or "id" not in product_response:
                raise Exception("Invalid response when creating product")
            
            # Create variant
            variant_data = {
                "product_id": product_response["id"],
                "barcode": barcode,
                "price": price,
                "quantity": quantity,
                "size": "",  # Empty for quick-add
                "color": ""   # Empty for quick-add
            }
            
            variant_response = self.api_client.create_variant(variant_data)
            if not variant_response:
                raise Exception("Invalid response when creating variant")
            
            QMessageBox.information(self, "Success", "Product added successfully")
            
            # Clear the form
            self.product_name_input.clear()
            self.product_barcode_input.clear()
            self.product_price_input.setValue(0)
            self.product_stock_input.setValue(0)
            
            # Refresh tables
            self.setup_inventory_table()
            
            # Check if method exists before calling (in case POS page is not initialized)
            if hasattr(self, 'load_product_list'):
                self.load_product_list()
            
        except Exception as e:
            print(f"Error in handle_add_product: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")
            
    def edit_inventory_item(self, row: int):
        """Edit an inventory item."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product")
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(350)
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        
        # Get current values
        name = self.inventory_table.item(row, 0).text()
        barcode = self.inventory_table.item(row, 1).text()
        price = self.parse_price(self.inventory_table.item(row, 2).text())
        quantity = float(self.inventory_table.item(row, 3).text())
        current_category = self.inventory_table.item(row, 4).text()
        size = self.inventory_table.item(row, 5).text()
        color = self.inventory_table.item(row, 6).text()
        
        # Create input fields
        name_input = QLineEdit(name)
        barcode_input = QLineEdit(barcode)
        price_input = QDoubleSpinBox()
        price_input.setMaximum(999999.99)
        price_input.setValue(price)
        price_input.setSuffix(" DZD")
        quantity_input = QDoubleSpinBox()
        quantity_input.setMaximum(9999.99)
        quantity_input.setDecimals(2)  # Allow 2 decimal places
        quantity_input.setValue(quantity)

        # Create and populate category dropdown
        category_combo = QComboBox()
        try:
            categories = self.api_client.get_categories()
            if not categories:
                QMessageBox.warning(dialog, "Warning", "No categories found. Please create categories first.")
                return

            current_cat_index = 0
            for i, cat in enumerate(categories):
                category_combo.addItem(cat["name"])
                if cat["name"] == current_category:
                    current_cat_index = i

            category_combo.setCurrentIndex(current_cat_index)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load categories: {str(e)}")
            return

        size_input = QLineEdit(size)
        color_input = QLineEdit(color)
        
        # Add fields to form
        layout.addRow("Product Name:", name_input)
        layout.addRow("Barcode:", barcode_input)
        layout.addRow("Price:", price_input)
        layout.addRow("Quantity:", quantity_input)
        layout.addRow("Category:", category_combo)
        layout.addRow("Size:", size_input)
        layout.addRow("Color:", color_input)
        
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
            try:
                # First, get the variant ID using the barcode
                response = requests.get(
                    f"{self.api_client.base_url}/variants/barcode/{barcode}",
                    headers=self.api_client.get_headers()
                )
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", "Failed to find variant")
                    return
                
                variant = response.json()
                variant_id = variant["id"]
                
                updated_item = {
                    "barcode": barcode_input.text(),
                    "price": price_input.value(),
                    "quantity": quantity_input.value(),
                    "size": size_input.text(),
                    "color": color_input.text()
                }
                
                # Update via API using the variant ID
                response = requests.put(
                    f"{self.api_client.base_url}/variants/{variant_id}",
                    headers=self.api_client.get_headers(),
                    json=updated_item
                )
                
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", f"Failed to update variant: {response.text}")
                    return
                
                # Update table
                self.inventory_table.setItem(row, 0, QTableWidgetItem(name_input.text()))
                self.inventory_table.setItem(row, 1, QTableWidgetItem(updated_item["barcode"]))
                self.inventory_table.setItem(row, 2, QTableWidgetItem(self.format_price(updated_item["price"])))
                self.inventory_table.setItem(row, 3, QTableWidgetItem(str(updated_item["quantity"])))
                self.inventory_table.setItem(row, 4, QTableWidgetItem(category_combo.currentText()))
                self.inventory_table.setItem(row, 5, QTableWidgetItem(updated_item["size"]))
                self.inventory_table.setItem(row, 6, QTableWidgetItem(updated_item["color"]))
                
                # Refresh product list
                self.load_product_list()
                
                QMessageBox.information(self, "Success", "Product updated successfully")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update product: {str(e)}")

    def delete_inventory_item(self, row: int):
        """Delete an inventory item."""
        barcode = self.inventory_table.item(row, 1).text()
        product_name = self.inventory_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "Delete Product",
            f"Are you sure you want to delete '{product_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # First, get the variant ID using the barcode
                response = requests.get(
                    f"{self.api_client.base_url}/variants/barcode/{barcode}",
                    headers=self.api_client.get_headers()
                )
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", "Failed to find variant")
                    return
                
                variant = response.json()
                variant_id = variant["id"]
                
                # Delete the variant using API client method for better error handling
                try:
                    # Use the API client to delete by variant ID directly
                    delete_response = requests.delete(
                        f"{self.api_client.base_url}/variants/{variant_id}", 
                        headers=self.api_client.get_headers(),
                        timeout=10
                    )
                    
                    if delete_response.status_code != 200:
                        error_msg = "Server error"
                        try:
                            error_data = delete_response.json()
                            if isinstance(error_data, dict) and 'detail' in error_data:
                                error_msg = error_data['detail']
                        except:
                            error_msg = delete_response.text if delete_response.text else "Unknown error"
                            
                        QMessageBox.warning(self, "Error", f"Failed to delete variant: {error_msg}")
                        return
                except Exception as delete_err:
                    QMessageBox.warning(self, "Error", f"Failed to delete variant: {str(delete_err)}")
                    return
                
                # Remove row from table
                self.inventory_table.removeRow(row)
                
                # Refresh product list
                self.load_product_list()
                
                QMessageBox.information(self, "Success", "Product deleted successfully")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete product: {str(e)}")
