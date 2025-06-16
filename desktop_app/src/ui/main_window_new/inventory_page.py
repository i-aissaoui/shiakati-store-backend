"""
Inventory Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDialogButtonBox, QHeaderView, QWidget,
    QFileDialog, QToolButton, QTabWidget, QScrollArea, QListWidget, QListWidgetItem,
    QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPixmap, QImage
import requests
import traceback
import sys
import os
import shutil
import tempfile
from .variant_product_dialog import VariantProductDialog


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
        
        add_variant_product_btn = QPushButton("➕ Add Product with multiple variants")
        add_variant_product_btn.clicked.connect(self.show_variant_product_dialog)
        search_layout.addWidget(add_variant_product_btn)
        
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
        
        # Load inventory data
        self.setup_inventory_table()

    def setup_inventory_table(self):
        """Set up the inventory management table with data."""
        try:
            print("\n\n=========== DEBUG: INVENTORY PAGE ===========")
            print("DEBUG: Calling api_client.get_inventory()...")
            inventory = self.api_client.get_inventory()
            
            print(f"DEBUG: Received inventory data type: {type(inventory)}")
            print(f"DEBUG: Received inventory count: {len(inventory) if inventory else 0}")
            if inventory and len(inventory) > 0:
                print(f"DEBUG: First inventory item keys: {list(inventory[0].keys())}")
                print(f"DEBUG: First inventory item sample: {inventory[0]}")
            
            self.inventory_table.setRowCount(0)
            
            # Process SKU barcodes to ensure they're complete
            for item in inventory:
                # Make sure SKU barcodes are properly formed
                if "barcode" not in item or not item["barcode"]:
                    if "product_id" in item:
                        item["barcode"] = f"SKU{item['product_id']}"
                        print(f"DEBUG: Generated SKU barcode for item: {item['barcode']}")
            
            for item in inventory:
                row = self.inventory_table.rowCount()
                self.inventory_table.insertRow(row)
                
                print(f"DEBUG: Processing item: {item.get('product_name', 'Unknown')}")
                # Check for required fields before using them
                
                try:
                    self.inventory_table.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'product_name': {e}, keys available: {list(item.keys())}")
                    if "name" in item:
                        self.inventory_table.setItem(row, 0, QTableWidgetItem(item["name"]))
                    else:
                        self.inventory_table.setItem(row, 0, QTableWidgetItem("Unknown"))
                        
                try:
                    self.inventory_table.setItem(row, 1, QTableWidgetItem(item["barcode"]))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'barcode': {e}")
                    if "id" in item:
                        sku_barcode = f"SKU{item.get('id', '0000')}"
                        self.inventory_table.setItem(row, 1, QTableWidgetItem(sku_barcode))
                        # Add the barcode to the item for future use
                        item["barcode"] = sku_barcode
                    else:
                        self.inventory_table.setItem(row, 1, QTableWidgetItem("Unknown"))
                    
                try:
                    self.inventory_table.setItem(row, 2, QTableWidgetItem(self.format_price(item["price"])))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'price': {e}")
                    self.inventory_table.setItem(row, 2, QTableWidgetItem("0.00"))
                
                # Use 'stock' as our primary field, but fall back to 'quantity' if it's missing
                if "stock" in item:
                    self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item["stock"])))
                    # Add the quantity field for compatibility
                    item["quantity"] = item["stock"]
                elif "quantity" in item:
                    self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item["quantity"])))
                    # Add the stock field for compatibility
                    item["stock"] = item["quantity"]
                else:
                    # No stock or quantity field found
                    self.inventory_table.setItem(row, 3, QTableWidgetItem("0"))
                    item["quantity"] = 0
                    item["stock"] = 0
                
                try:
                    self.inventory_table.setItem(row, 4, QTableWidgetItem(item["category"]))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'category': {e}")
                    self.inventory_table.setItem(row, 4, QTableWidgetItem(item.get("category_name", "Uncategorized")))
                
                try:
                    self.inventory_table.setItem(row, 5, QTableWidgetItem(item["size"]))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'size': {e}")
                    self.inventory_table.setItem(row, 5, QTableWidgetItem("Standard"))
                    
                try:
                    color = item["color"] if item["color"] and item["color"].strip() else "Default"
                    self.inventory_table.setItem(row, 6, QTableWidgetItem(color))
                except KeyError as e:
                    print(f"DEBUG: KeyError for 'color': {e}")
                    self.inventory_table.setItem(row, 6, QTableWidgetItem("Default"))
                
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
            print(f"ERROR in setup_inventory_table: {str(e)}")
            traceback.print_exc()
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
        """Show a dialog to add a new product with multiple variants and image upload capability."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(700)
        
        layout = QVBoxLayout(dialog)
        
        # Create a tab widget to separate basic info and variants
        tabs = QTabWidget()
        
        # Tab 1: Basic product information
        basic_info_tab = QWidget()
        basic_info_layout = QVBoxLayout(basic_info_tab)
        form_layout = QFormLayout()
        
        # Product name field
        name_input = QLineEdit()
        form_layout.addRow("Product Name:", name_input)
        
        # Base barcode (required)
        barcode_layout = QHBoxLayout()
        barcode_input = QLineEdit()
        barcode_input.setPlaceholderText("Barcode will be auto-generated")
        barcode_gen_btn = QPushButton("Generate")
        barcode_layout.addWidget(barcode_input)
        barcode_layout.addWidget(barcode_gen_btn)
        form_layout.addRow("Barcode:", barcode_layout)
        
        # Base barcode prefix (optional)
        barcode_prefix_layout = QHBoxLayout()
        barcode_prefix_input = QLineEdit()
        barcode_prefix_input.setPlaceholderText("Optional prefix for all variants (e.g. SHIRT)")
        generate_btn = QPushButton("Generate Unique")
        barcode_prefix_layout.addWidget(barcode_prefix_input)
        barcode_prefix_layout.addWidget(generate_btn)
        form_layout.addRow("Barcode Prefix:", barcode_prefix_layout)
        
        # Category dropdown
        category_combo = QComboBox()
        try:
            categories = self.api_client.get_categories()
            for cat in categories:
                if isinstance(cat, dict):
                    category_combo.addItem(cat["name"])
        except Exception as e:
            print(f"Failed to load categories: {str(e)}")
        form_layout.addRow("Category:", category_combo)
        
        # Description field
        description_input = QLineEdit()
        form_layout.addRow("Description:", description_input)
        
        # Price field
        price_input = QDoubleSpinBox()
        price_input.setMaximum(9999.99)
        price_input.setDecimals(2)
        self.apply_spinbox_styling(price_input)
        form_layout.addRow("Price (DZD):", price_input)
        
        # Stock field
        stock_input = QDoubleSpinBox()
        stock_input.setMaximum(9999.99)
        stock_input.setDecimals(2)
        self.apply_spinbox_styling(stock_input)
        form_layout.addRow("Initial Stock:", stock_input)
        
        # Size field
        size_input = QLineEdit()
        size_input.setPlaceholderText("e.g., S, M, L, XL, etc.")
        form_layout.addRow("Size:", size_input)
        
        # Color field
        color_input = QLineEdit()
        color_input.setPlaceholderText("e.g., Red, Blue, Black, etc.")
        form_layout.addRow("Color:", color_input)
        
        # Image upload field
        image_layout = QVBoxLayout()
        main_image_layout = QHBoxLayout()
        image_label = QLabel("No main image selected")
        image_path = None
        additional_image_paths = []
        
        # Add a preview image placeholder for main image
        image_preview = QLabel()
        image_preview.setFixedSize(100, 100)
        image_preview.setStyleSheet("border: 1px solid #dcdde1; background-color: #f7f7f7;")
        image_preview.setAlignment(Qt.AlignCenter)
        image_preview.setText("No Image")
        
        # Browse button for main image
        browse_btn = QPushButton("Browse Main Image...")
        
        main_image_layout.addWidget(image_preview)
        main_image_layout.addWidget(image_label)
        main_image_layout.addWidget(browse_btn)
        
        # Section for additional images
        additional_images_label = QLabel("Additional Images:")
        additional_images_layout = QHBoxLayout()
        
        # Container for additional image previews
        additional_images_container = QWidget()
        additional_images_container_layout = QHBoxLayout(additional_images_container)
        additional_images_container_layout.setContentsMargins(0, 0, 0, 0)
        additional_images_container_layout.setSpacing(5)
        
        # Add button for additional images
        add_image_btn = QPushButton("Add Image...")
        additional_images_layout.addWidget(additional_images_container)
        additional_images_layout.addWidget(add_image_btn)
        
        image_layout.addLayout(main_image_layout)
        image_layout.addWidget(additional_images_label)
        image_layout.addLayout(additional_images_layout)
        
        form_layout.addRow("Product Images:", image_layout)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        # Connect signals
        def generate_barcode():
            try:
                new_barcode = self.api_client.generate_unique_barcode()
                barcode_input.setText(new_barcode)
            except Exception as e:
                QMessageBox.warning(dialog, "Error", f"Failed to generate barcode: {str(e)}")
        
        barcode_gen_btn.clicked.connect(generate_barcode)
        
        def browse_main_image():
            nonlocal image_path
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                dialog, 
                "Select Main Product Image", 
                "", 
                "Image Files (*.png *.jpg *.jpeg)"
            )
            
            if file_path:
                image_path = file_path
                image_label.setText(os.path.basename(file_path))
                
                # Display image preview
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_preview.setPixmap(pixmap)
                image_preview.setText("")  # Clear the "No Image" text
        
        browse_btn.clicked.connect(browse_main_image)
        
        def add_additional_image():
            nonlocal additional_image_paths
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                dialog, 
                "Select Additional Product Image", 
                "", 
                "Image Files (*.png *.jpg *.jpeg)"
            )
            
            if file_path:
                additional_image_paths.append(file_path)
                
                # Create a preview widget for this image
                preview_container = QWidget()
                preview_layout = QVBoxLayout(preview_container)
                preview_layout.setContentsMargins(0, 0, 0, 0)
                
                # Image preview
                image_preview = QLabel()
                image_preview.setFixedSize(70, 70)
                image_preview.setStyleSheet("border: 1px solid #dcdde1;")
                image_preview.setAlignment(Qt.AlignCenter)
                
                # Display image preview
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_preview.setPixmap(pixmap)
                
                # Remove button
                remove_btn = QPushButton("X")
                remove_btn.setFixedSize(20, 20)
                remove_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 10px;")
                
                def remove_image():
                    nonlocal additional_image_paths
                    index = additional_image_paths.index(file_path)
                    additional_image_paths.pop(index)
                    additional_images_container_layout.removeWidget(preview_container)
                    preview_container.deleteLater()
                
                remove_btn.clicked.connect(remove_image)
                
                preview_layout.addWidget(image_preview)
                preview_layout.addWidget(remove_btn, alignment=Qt.AlignRight)
                
                additional_images_container_layout.addWidget(preview_container)
        
        add_image_btn.clicked.connect(add_additional_image)
        
        def add_product():
            try:
                # Validate input
                product_name = name_input.text().strip()
                if not product_name:
                    QMessageBox.warning(dialog, "Error", "Product name is required")
                    return
                
                # Get barcode (generate if empty)
                product_barcode = barcode_input.text().strip()
                if not product_barcode:
                    product_barcode = self.api_client.generate_unique_barcode()
                    
                # Get selected category
                selected_category = category_combo.currentText()
                category_id = None
                
                # Find category ID
                categories = self.api_client.get_categories()
                for cat in categories:
                    if cat["name"] == selected_category:
                        category_id = cat["id"]
                        break
                
                if not category_id:
                    QMessageBox.warning(dialog, "Error", f"Category '{selected_category}' not found")
                    return
                
                # Get other values
                description = description_input.text().strip()
                price = price_input.value()
                stock = stock_input.value()
                size = size_input.text().strip()  # Get size value
                color = color_input.text().strip()  # Get color value
                
                # Validate values
                if price <= 0:
                    QMessageBox.warning(dialog, "Error", "Price must be greater than 0")
                    return
                
                if stock < 0:
                    QMessageBox.warning(dialog, "Error", "Stock cannot be negative")
                    return
                
                # Create product
                new_product = {
                    "name": product_name,
                    "category_id": category_id,
                    "description": description
                }
                
                # First create the product
                product_response = self.api_client.create_product(new_product)
                if not product_response or "id" not in product_response:
                    raise Exception("Invalid response when creating product")
                
                # Create variant
                variant_data = {
                    "product_id": product_response["id"],
                    "barcode": product_barcode,
                    "price": price,
                    "quantity": stock,
                    "size": size,  # Include the size in the variant
                    "color": color  # Include the color in the variant
                }
                
                variant_response = self.api_client.create_variant(variant_data)
                if not variant_response:
                    raise Exception("Invalid response when creating variant")
                
                # Upload images
                success_count = 0
                total_images = (1 if image_path else 0) + len(additional_image_paths)
                
                # If a main image was selected, upload it first
                if image_path:
                    result = self.api_client.upload_product_image(product_barcode, image_path)
                    if result:
                        success_count += 1
                
                # Upload any additional images
                for additional_path in additional_image_paths:
                    result = self.api_client.upload_product_image(product_barcode, additional_path)
                    if result:
                        success_count += 1
                
                if success_count < total_images:
                    QMessageBox.warning(dialog, "Warning", 
                        f"Product was created, but only {success_count} out of {total_images} images were uploaded successfully.")
                
                QMessageBox.information(dialog, "Success", "Product added successfully")
                dialog.accept()  # Close dialog
                
                # Refresh inventory display
                self.setup_inventory_table()
                
            except Exception as e:
                traceback.print_exc()
                QMessageBox.critical(dialog, "Error", f"Failed to add product: {str(e)}")
        
        def reject_dialog():
            dialog.reject()
        
        button_box.accepted.connect(add_product)
        button_box.rejected.connect(reject_dialog)
        
        # Generate a barcode automatically on start
        generate_barcode()
        
        dialog.exec_()

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
            
            # Get size, color, price and quantity
            size = self.product_size_input.text().strip()
            color = self.product_color_input.text().strip()
            price = self.product_price_input.value()
            quantity = self.product_stock_input.value()
            
            # Validate input
            if not name:
                QMessageBox.warning(self, "Error", "Product name is required")
                return
            
            if not barcode:
                # Generate a barcode if empty
                barcode = self.api_client.generate_unique_barcode()
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
            
            # Create variant with the size and color fields
            variant_data = {
                "product_id": product_response["id"],
                "barcode": barcode,
                "price": price,
                "quantity": quantity,
                "size": size,  # Use the size from input
                "color": color  # Use the color from input
            }
            
            variant_response = self.api_client.create_variant(variant_data)
            if not variant_response:
                raise Exception("Invalid response when creating variant")
            
            QMessageBox.information(self, "Success", "Product added successfully")
            
            # Clear the form
            self.product_name_input.clear()
            self.product_barcode_input.clear()
            self.product_size_input.clear()  # Clear size input
            self.product_color_input.clear()  # Clear color input
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
        """Edit an existing inventory item."""
        try:
            # Get the barcode of the selected product - safely handling None cases
            barcode_item = self.inventory_table.item(row, 1)
            
            if barcode_item is None:
                QMessageBox.warning(self, "Error", "Invalid product data. Cannot edit.")
                return
            
            # Safe text extraction with fallback
            try:
                barcode = barcode_item.text().strip() if barcode_item.text() else ""
            except (AttributeError, RuntimeError):
                QMessageBox.warning(self, "Error", "Cannot access product data. Please refresh the table.")
                return
            
            if not barcode:
                QMessageBox.warning(self, "Error", "Product has no barcode. Cannot edit.")
                return
            
            # Find the product in the API client
            for inventory_item in self.api_client.get_inventory():
                if inventory_item.get("barcode") == barcode:
                    # Show product edit dialog
                    self.show_edit_product_dialog(inventory_item)
                    return
                    
            QMessageBox.warning(self, "Error", f"Product with barcode {barcode} not found in inventory.")
        except Exception as e:
            print(f"Error in edit_inventory_item: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to edit product: {str(e)}")
    
    def show_edit_product_dialog(self, product_data):
        """Show dialog to edit an existing product."""
        try:
            # We'll reuse the VariantProductDialog for editing
            if "product_id" in product_data:
                product_id = product_data["product_id"]
                variant_dialog = VariantProductDialog(self, self.api_client, product_id=product_id)
                result = variant_dialog.exec_()
                
                if result == QDialog.Accepted:
                    # Refresh inventory table after editing
                    self.setup_inventory_table()
                    
                    # Refresh product list if it exists
                    if hasattr(self, 'load_product_list'):
                        self.load_product_list()
            else:
                QMessageBox.warning(self, "Error", "Could not find product ID for editing.")
        except Exception as e:
            print(f"Error in show_edit_product_dialog: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to edit product: {str(e)}")
    
    def show_variant_product_dialog(self):
        """Show the dialog for creating multi-variant products."""
        try:
            variant_dialog = VariantProductDialog(self, self.api_client)
            result = variant_dialog.exec_()
            
            if result == QDialog.Accepted:
                # Refresh inventory table after adding new variants
                self.setup_inventory_table()
                
                # Check if method exists before calling (in case POS page is not initialized)
                if hasattr(self, 'load_product_list'):
                    self.load_product_list()
        except Exception as e:
            print(f"Error showing variant product dialog: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to open variant product dialog: {str(e)}")
    
    def delete_inventory_item(self, row: int):
        """Delete an inventory item."""
        try:
            # Get the barcode and name of the selected product - safely handling None cases
            barcode_item = self.inventory_table.item(row, 1)
            product_name_item = self.inventory_table.item(row, 0)
            
            if barcode_item is None or product_name_item is None:
                QMessageBox.warning(self, "Error", "Invalid product data. Cannot delete.")
                return
            
            # Safe text extraction with fallback
            try:
                barcode = barcode_item.text().strip() if barcode_item.text() else ""
                product_name = product_name_item.text().strip() if product_name_item.text() else "Unknown Product"
            except (AttributeError, RuntimeError):
                QMessageBox.warning(self, "Error", "Cannot access product data. Please refresh the table.")
                return
            
            if not barcode:
                QMessageBox.warning(self, "Error", "Product has no barcode. Cannot delete.")
                return
            
            reply = QMessageBox.question(
                self, "Delete Product",
                f"Are you sure you want to delete '{product_name}'?\n\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Find the product and variant ID in the API client
                success = False
                for item in self.api_client.get_inventory():
                    if item.get("barcode") == barcode:
                        # Delete the product through the API
                        if "variant_id" in item:
                            # Delete variant
                            response = self.api_client.delete_variant(item["variant_id"])
                            success = True
                        elif "id" in item:
                            # Delete product
                            response = self.api_client.delete_product(item["id"])
                            success = True
                        break
                
                if success:
                    # Remove the row from the table
                    self.inventory_table.removeRow(row)
                    QMessageBox.information(self, "Success", "Product deleted successfully")
                    
                    # Refresh product list if it exists
                    if hasattr(self, 'load_product_list'):
                        self.load_product_list()
                else:
                    QMessageBox.warning(self, "Error", f"Product with barcode {barcode} not found in inventory")
                    
        except Exception as e:
            print(f"Error in delete_inventory_item: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to delete product: {str(e)}")
