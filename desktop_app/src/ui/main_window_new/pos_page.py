"""
POS Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class POSPageMixin:
    """Mixin class for the POS page functionality."""
    
    def setup_pos_page(self):
        """Set up the Point of Sale page."""
        layout = QVBoxLayout()
        
        # Top section with search and barcode
        top_section = QHBoxLayout()
        
        # Product search
        search_layout = QVBoxLayout()
        search_label = QLabel("Product Search")
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search products by name...")
        self.product_search.textChanged.connect(self.filter_product_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.product_search)
        
        # Product list with variant columns
        self.product_list = QTableWidget()
        self.product_list.setColumnCount(6)  # Columns for Name, Barcode, Price, Stock, Size, Color
        self.product_list.setHorizontalHeaderLabels(["Name", "Barcode", "Price", "Stock", "Size", "Color"])
        self.product_list.verticalHeader().setVisible(False)
        self.product_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_list.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing
        self.product_list.itemDoubleClicked.connect(self.add_product_from_list)
        self.product_list.setMinimumHeight(300)
        self.product_list.verticalHeader().setDefaultSectionSize(50)  # Match the row height of other tables
        self.product_list.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 16px 8px;
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
        search_layout.addWidget(self.product_list)
        
        # Barcode scanner input
        scanner_layout = QVBoxLayout()
        scanner_label = QLabel("Barcode Scanner")
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan or enter barcode")
        self.barcode_input.returnPressed.connect(self.handle_barcode_scan)
        scanner_layout.addWidget(scanner_label)
        scanner_layout.addWidget(self.barcode_input)
        
        # Quick add quantity
        quantity_layout = QHBoxLayout()
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(999)
        self.quantity_input.setValue(1)
        # Apply consistent styling using our helper method
        self.apply_spinbox_styling(self.quantity_input)
        quantity_layout.addWidget(QLabel("Quantity:"))
        quantity_layout.addWidget(self.quantity_input)
        scanner_layout.addLayout(quantity_layout)
        
        # Add search and scanner to top section
        top_section.addLayout(search_layout, stretch=2)
        top_section.addLayout(scanner_layout, stretch=1)
        
        # Current sale table with variant columns
        self.sale_table = QTableWidget()
        self.sale_table.setColumnCount(8)  # Increased columns to include variant information
        self.sale_table.setHorizontalHeaderLabels(["Product", "Barcode", "Size", "Color", "Price", "Quantity", "Total", "Actions"])
        self.sale_table.verticalHeader().setVisible(False)
        self.sale_table.setMinimumHeight(300)
        
        # Set row height to match the variant table (50px)
        self.sale_table.verticalHeader().setDefaultSectionSize(50)
        
        # Disable editing for all columns
        self.sale_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Remove the itemChanged connection since editing is disabled
        # self.sale_table.itemChanged.connect(self.handle_sale_item_change)
        
        # Improve table styling
        self.sale_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 16px 8px;
                border-bottom: 1px solid #f1f2f6;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #0984e3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
            }
        """)

        # Sale controls
        controls_layout = QHBoxLayout()
        
        # Customer info (optional)
        customer_layout = QVBoxLayout()
        customer_label = QLabel("Customer Info (Optional)")
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Customer Phone")
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_name)
        customer_layout.addWidget(self.customer_phone)
        controls_layout.addLayout(customer_layout)
        
        # Totals section
        totals_layout = QVBoxLayout()
        self.subtotal_label = QLabel("Subtotal: 0.00 DZD")
        self.total_label = QLabel("Total: 0.00 DZD")
        self.total_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(self.total_label)
        controls_layout.addLayout(totals_layout)
        
        # Action buttons
        buttons_layout = QVBoxLayout()
        self.clear_sale_button = QPushButton("Clear Sale")
        self.clear_sale_button.clicked.connect(self.clear_current_sale)
        self.checkout_button = QPushButton("Complete Sale")
        self.checkout_button.clicked.connect(self.handle_checkout)
        buttons_layout.addWidget(self.clear_sale_button)
        buttons_layout.addWidget(self.checkout_button)
        controls_layout.addLayout(buttons_layout)
        
        # Add all widgets to main layout
        layout.addLayout(top_section)
        layout.addWidget(self.sale_table)
        layout.addLayout(controls_layout)
        
        self.pos_page.setLayout(layout)
        
        # Load initial product list
        self.load_product_list()

    def handle_barcode_scan(self):
        """Handle barcode scanner input."""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        # Add product to sale
        self.add_product_to_sale(barcode)
            
        # Clear barcode input
        self.barcode_input.clear()

    def filter_product_list(self):
        """Filter the product list based on search text."""
        search_text = self.product_search.text().lower()
        for row in range(self.product_list.rowCount()):
            match = False
            for col in range(self.product_list.columnCount()):
                item = self.product_list.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.product_list.setRowHidden(row, not match)

    def load_product_list(self):
        """Load all products into the product list table."""
        try:
            print("Loading product list from API client...")
            print(f"API client type: {type(self.api_client).__name__}")
            print(f"Available methods: {[m for m in dir(self.api_client) if not m.startswith('_') and callable(getattr(self.api_client, m))]}")
            
            # Try multiple methods in sequence until one works
            inventory = None
            
            methods_to_try = [
                'get_inventory_safe', 
                'get_inventory',
                'get_products_safe',
                'get_products'
            ]
            
            # Try each method in order until one works
            for method_name in methods_to_try:
                if hasattr(self.api_client, method_name):
                    try:
                        print(f"Trying method: {method_name}")
                        method = getattr(self.api_client, method_name)
                        inventory = method()
                        print(f"SUCCESS: Got {len(inventory)} products using {method_name}")
                        break
                    except Exception as method_err:
                        print(f"Error calling {method_name}: {str(method_err)}")
            
            # If no methods worked, generate dummy data
            if inventory is None:
                print("All inventory methods failed, generating dummy data")
                inventory = self._generate_dummy_products()
                print(f"Generated {len(inventory)} dummy products")
            
            # Clear existing table
            self.product_list.setRowCount(0)                # Populate table with inventory data including variant columns
            for item in inventory:
                row = self.product_list.rowCount()
                self.product_list.insertRow(row)
                
                # Product name - only show the base product name
                # Extract just the base name without size/color information
                product_name = item.get("product_name", "Unknown")
                
                # Split at common size/color separators to remove any extra information
                if " - " in product_name:
                    product_name = product_name.split(" - ")[0]
                elif ", " in product_name:
                    product_name = product_name.split(", ")[0]
                
                self.product_list.setItem(row, 0, QTableWidgetItem(product_name))
                
                # Barcode
                self.product_list.setItem(row, 1, QTableWidgetItem(str(item.get("barcode", f"SKU{row}"))))
                
                # Price
                self.product_list.setItem(row, 2, QTableWidgetItem(self.format_price(item["price"])))
                
                # Stock - Handle case where quantity might be named "stock" instead
                quantity = item.get("quantity", item.get("stock", 0))
                self.product_list.setItem(row, 3, QTableWidgetItem(str(quantity)))
                
                # Size - Display in its own column
                size = item.get("size", item.get("variant_size", "N/A"))
                self.product_list.setItem(row, 4, QTableWidgetItem(str(size)))
                
                # Color - Display in its own column
                color = item.get("color", item.get("variant_color", "N/A"))
                self.product_list.setItem(row, 5, QTableWidgetItem(str(color)))
                
                # Store variant_id as item data for reference, but don't show in a column
                variant_id = item.get("variant_id", "N/A")
                self.product_list.item(row, 0).setData(Qt.UserRole, variant_id)
            
            print(f"Successfully loaded {self.product_list.rowCount()} products into the table")
                
        except Exception as e:
            print(f"ERROR in load_product_list: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            QMessageBox.warning(self, "Error", f"Failed to load products: {str(e)}")
    
    def _generate_dummy_products(self, count=15):
        """Generate dummy products for testing when API fails."""
        import random
        import datetime
        
        print("Generating dummy products for POS page")
        dummy_products = []
        
        for i in range(count):
            dummy_products.append({
                "id": i,
                "product_name": f"Product {i}",
                "description": f"Test product {i} description",
                "category_id": random.randint(1, 7),
                "category_name": f"Category {random.randint(1, 7)}",
                "price": round(random.uniform(20, 200), 2),
                "barcode": f"TEST{i}".upper(),
                "stock": random.randint(0, 50),
                "created_at": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 100))).strftime("%Y-%m-%dT%H:%M:%S")
            })
        
        return dummy_products

    def add_product_from_list(self, item):
        """Add a product to the sale when double-clicked in the product list."""
        row = item.row()
        barcode = self.product_list.item(row, 1).text()
        self.add_product_to_sale(barcode)
            
    def add_product_to_sale(self, barcode: str):
        """Add a product to the current sale by barcode."""
        try:
            # Find product in the list
            for row in range(self.product_list.rowCount()):
                if self.product_list.item(row, 1).text().strip() == barcode.strip():
                    # Get base product name
                    name = self.product_list.item(row, 0).text()
                    price = self.parse_price(self.product_list.item(row, 2).text())
                    stock = float(self.product_list.item(row, 3).text())  # Use float instead of int
                    quantity = float(self.quantity_input.value())  # Use float instead of int
                    
                    # Get variant information
                    size = self.product_list.item(row, 4).text()
                    color = self.product_list.item(row, 5).text()
                    
                    if quantity <= 0:
                        QMessageBox.warning(self, "Error", "Quantity must be greater than 0")
                        return
                    if quantity > stock:
                        QMessageBox.warning(self, "Error", f"Not enough stock. Only {stock} available.")
                        return
                    
                    # Check if already in sale
                    for sale_row in range(self.sale_table.rowCount()):
                        if self.sale_table.item(sale_row, 1).text().strip() == barcode.strip():
                            # Item already in cart, update quantity
                            current_qty = float(self.sale_table.item(sale_row, 5).text())
                            new_qty = current_qty + quantity
                            
                            if new_qty > stock:
                                QMessageBox.warning(self, "Error", f"Not enough stock. Only {stock} available.")
                                return
                                
                            self.sale_table.setItem(sale_row, 5, QTableWidgetItem(f"{new_qty:.1f}"))
                            self.sale_table.setItem(sale_row, 6, QTableWidgetItem(self.format_price(price * new_qty)))
                            self.update_sale_totals()
                            return
                    
                    # Add new row to sale with variant information
                    row = self.sale_table.rowCount()
                    self.sale_table.insertRow(row)
                    self.sale_table.setItem(row, 0, QTableWidgetItem(name))
                    self.sale_table.setItem(row, 1, QTableWidgetItem(barcode))
                    self.sale_table.setItem(row, 2, QTableWidgetItem(size))
                    self.sale_table.setItem(row, 3, QTableWidgetItem(color))
                    self.sale_table.setItem(row, 4, QTableWidgetItem(self.format_price(price)))
                    self.sale_table.setItem(row, 5, QTableWidgetItem(f"{quantity:.1f}"))
                    self.sale_table.setItem(row, 6, QTableWidgetItem(self.format_price(price * quantity)))
                    
                    # Add remove button (using same style as variant table)
                    remove_btn = QPushButton("🗑️")
                    remove_btn.setFixedSize(25, 22)  # Smaller button consistent with variant table
                    remove_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            padding: 2px;
                            border-radius: 2px;
                            font-size: 10px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    remove_btn.clicked.connect(lambda checked, r=row: self.remove_sale_item(r))
                    self.sale_table.setCellWidget(row, 7, remove_btn)  # Updated column index for the Actions column
                    
                    self.update_sale_totals()
                    self.quantity_input.setValue(1)
                    return
            
            QMessageBox.warning(self, "Error", "Product not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")
            print(f"Error adding product: {str(e)}")  # Add debug logging

    def clear_current_sale(self):
        """Clear the current sale."""
        reply = QMessageBox.question(
            self, "Clear Sale",
            "Are you sure you want to clear the current sale?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sale_table.setRowCount(0)
            self.update_sale_totals()
            self.customer_name.clear()
            self.customer_phone.clear()
            self.quantity_input.setValue(1)

    def remove_sale_item(self, row: int):
        """Remove an item from the current sale."""
        reply = QMessageBox.question(
            self, "Remove Item",
            "Are you sure you want to remove this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sale_table.removeRow(row)
            self.update_sale_totals()

    def update_sale_totals(self):
        """Update the subtotal and total labels."""
        subtotal = 0.0
        for row in range(self.sale_table.rowCount()):
            total_cell = self.sale_table.item(row, 6)  # Updated column index for Total
            if total_cell:
                subtotal += self.parse_price(total_cell.text())
        
        # Update labels with DZD format
        self.subtotal_label.setText(f"Subtotal: {self.format_price(subtotal)}")
        self.total_label.setText(f"Total: {self.format_price(subtotal)}")  # Add tax calculation if needed

    def handle_checkout(self):
        """Process the checkout."""
        if self.sale_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No items in cart")
            return
            
        total = self.parse_price(self.total_label.text().split(': ')[1])
        
        # Process the sale with the API client including variant information
        sale_items = []
        for row in range(self.sale_table.rowCount()):
            try:
                product_name = self.sale_table.item(row, 0).text().strip()
                barcode = self.sale_table.item(row, 1).text().strip()
                size = self.sale_table.item(row, 2).text().strip()
                color = self.sale_table.item(row, 3).text().strip()
                price = self.parse_price(self.sale_table.item(row, 4).text())
                quantity = float(self.sale_table.item(row, 5).text().strip())
                sale_items.append({
                    "product_name": product_name,  # Include product name in sale items
                    "barcode": barcode,
                    "quantity": quantity,
                    "price": price,
                    "size": size,
                    "color": color
                })
            except (ValueError, AttributeError) as e:
                QMessageBox.warning(self, "Error", f"Invalid data in row {row + 1}")
                return
            
        try:
            response = self.api_client.create_sale(sale_items, total)
            
            if response is None:
                QMessageBox.warning(self, "Error", "No response from server")
                return
                
            if isinstance(response, dict):
                if response.get('id') or response.get('success'):
                    # Ask if user wants to print the ticket
                    reply = QMessageBox.question(
                        self,
                        "Sale Complete",
                        f"Sale completed successfully!\nTotal: {self.format_price(total)}\n\nWould you like to print the receipt?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        # Get the complete sale details for printing
                        sale_details = self.api_client.get_sale_details(response['id'])
                        if sale_details:
                            self.print_sale_ticket(sale_details)
                    
                    # Clear the sale table
                    self.sale_table.setRowCount(0)
                    self.update_sale_totals()
                    self.load_product_list()  # Refresh product list
                    
                    # Only update stats if stats page is currently visible
                    if self.content_stack.currentIndex() == 2:
                        self.update_stats()  # Refresh statistics
                else:
                    error_msg = response.get('error', 'Unknown error')
                    QMessageBox.warning(self, "Error", f"Failed to process sale: {error_msg}")
            else:
                QMessageBox.warning(self, "Error", "Invalid response from server")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process sale: {str(e)}")

    def print_sale_ticket(self, sale_data):
        """Print a sale ticket."""
        try:
            import os
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtGui import QTextDocument, QPageSize
            from PyQt5.QtCore import QSizeF, QMarginsF, QDateTime, Qt
            
            # Create receipts directory if it doesn't exist
            if not os.path.exists("receipt"):
                os.makedirs("receipt")

            # Extract just the sale number for simpler naming
            sale_id = str(sale_data['id'])
            # Remove any prefix if there is one
            if '-' in sale_id:
                sale_id = sale_id.split('-')[-1]
                
            file_name = f"receipt/sale-{sale_id}.pdf"

            printer = QPrinter()
            custom_page_size = QPageSize(QSizeF(80, 200), QPageSize.Unit.Millimeter)
            printer.setPageSize(custom_page_size)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_name)
            printer.setPageMargins(2.0, 2.0, 2.0, 2.0, QPrinter.Unit.Millimeter)
            
            document = QTextDocument()
            document.setDocumentMargin(0)

            # Create HTML receipt with monospace font and better alignment
            html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @page { 
                            size: 80mm 200mm;
                            margin: 0mm;
                        }
                        body { 
                            font-family: "Courier", monospace;
                            width: 72mm;
                            margin: 0;
                            padding: 2mm;
                            font-size: 6.5pt;
                            line-height: 1.1;
                            white-space: pre;
                        }
                        .content {
                            width: 100%;
                            text-align: center;
                        }
                        .store-logo {
                            width: 15mm !important;
                            max-width: 15mm !important;
                            height: 15mm !important;
                            max-height: 15mm !important;
                            margin-bottom: 3mm;
                            display: block;
                            margin-left: auto;
                            margin-right: auto;
                        }
                        .header {
                            text-align: center;
                            margin-bottom: 6mm;
                        }
                        .items-section {
                            text-align: left;
                            margin: 0;
                        }
                        .items-header {
                            margin: 1mm 0;
                            font-weight: normal;
                        }
                        .item-row {
                            margin: 0.5mm 0;
                        }
                        .item-name {
                            margin-left: 2mm;
                            color: #000;
                        }
                        .separator {
                            margin: 1mm 0;
                        }
                        .total {
                            text-align: center;
                            margin: 3mm 0;
                            font-size: 10pt;
                            font-weight: bold;
                        }
                        .footer {
                            text-align: center;
                            margin-top: 6mm;
                            line-height: 1.5;
                        }
                    </style>
                </head>
                <body>
                    <div class="content">"""

            # Convert ICO to base64 for reliable embedding
            from PIL import Image
            import io
            import base64
            
            try:
                # Try to load and resize the ICO file
                logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'images', 'logo.ico'))
                img = Image.open(logo_path)
                # Set to a larger size for better visibility
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Add logo
                html += f'<img src="data:image/png;base64,{img_str}" class="store-logo" />'
            except Exception as e:
                # If logo can't be loaded, skip it
                print(f"Could not load logo: {e}")
                
            # Add store name
            html += '<div style="text-align: center; font-weight: bold; margin-bottom: 2mm; font-size: 9pt;">Shiakati شياكتي</div></br>'

            # Add date and sale number - centered in header section
            date_str = QDateTime.fromString(sale_data['sale_time'], Qt.ISODate).toString('yyyy-MM-dd HH:mm')
            
            # Clean up sale ID display - remove any prefix and show just the number
            display_sale_id = str(sale_data['id'])
            if '-' in display_sale_id:
                display_sale_id = display_sale_id.split('-')[-1]
            
            html += '<div class="header">'
            html += f"Date: {date_str}\n"
            html += f"Sale : {display_sale_id}\n\n"  # Use cleaned sale ID
            html += '</div>'

            # Start items section
            html += '<div class="items-section">'
            
            # Add separator line at top
            html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n'
            
            # Add header with spacings matching the data format - make column headers clearer
            html += '<span style="font-weight: bold;">Product Name      Qty   Price  Total</span>\n'
            html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n'

            # Add items with proper spacing
            total_items = 0
            total_amount = 0
            for item in sale_data["items"]:
                # Try multiple approaches to get the product name
                product_name = None
                
                # First try: Use product_name from the item if available
                if item.get("product_name") and item.get("product_name") != "Unknown Product":
                    product_name = item.get("product_name")
                
                # Second try: Use name field from the item
                if not product_name and item.get("name") and item.get("name") != "Unknown Product":
                    product_name = item.get("name")
                
                # Third try: Look up the product name from the current inventory using barcode
                if not product_name:
                    barcode = item.get("barcode", "")
                    if barcode:
                        try:
                            for row in range(self.product_list.rowCount()):
                                if self.product_list.item(row, 1) and self.product_list.item(row, 1).text().strip() == barcode.strip():
                                    product_name = self.product_list.item(row, 0).text()
                                    break
                        except Exception as e:
                            print(f"Error looking up product name: {e}")
                
                # Fourth try: Create a descriptive name from available data
                if not product_name:
                    barcode = item.get("barcode", "")
                    size = item.get("size", "")
                    color = item.get("color", "")
                    
                    if barcode:
                        # Try to create a meaningful name
                        if size or color:
                            parts = []
                            if color:
                                parts.append(color)
                            if size:
                                parts.append(size)
                            product_name = f"Item {' '.join(parts)} ({barcode[-6:] if len(barcode) > 6 else barcode})"
                        else:
                            product_name = f"Item {barcode[-6:] if len(barcode) > 6 else barcode}"
                    else:
                        product_name = "Unknown Product"
                
                # Extract size and color if available
                size = item.get("size", "")
                color = item.get("color", "")
                
                quantity = float(item.get("quantity", 1))
                price = float(item.get("price", 0))
                total = price * quantity
                total_items += quantity
                total_amount += total
                
                # Clean up the product name to ensure it's only the base name without extra details
                # Remove any size/color info if it's included in the name (in parentheses)
                base_product_name = product_name.split(" (")[0] if " (" in product_name else product_name
                
                # Format numbers with consistent decimal places and spacing
                name_width = 16  # Width for product name
                qty_str = f"{int(quantity)}".rjust(3)     # Width for quantity
                price_str = f"{price:.2f}".rjust(7)      # Width for price
                total_str = f"{total:.2f}".rjust(6)      # Width for total - pulled in
                
                # Handle long product names by breaking into multiple lines
                if len(base_product_name) > name_width:
                    # Split product name into words
                    words = base_product_name.split()
                    current_line = ""
                    first_line = True
                    
                    for word in words:
                        if len(current_line) + len(word) + 1 <= name_width or len(current_line) == 0:
                            if len(current_line) > 0:
                                current_line += " "
                            current_line += word
                        else:
                            if first_line:
                                # Print first line with values
                                html += f"{current_line.ljust(name_width)}{qty_str}   {price_str}  {total_str}\n"
                                first_line = False
                            else:
                                # Print continuation line
                                html += f"{current_line.ljust(name_width)}\n"
                            current_line = word
                    
                    # Print any remaining text
                    if current_line:
                        if first_line:
                            html += f"{current_line.ljust(name_width)}{qty_str}   {price_str}  {total_str}\n"
                        else:
                            html += f"{current_line.ljust(name_width)}\n"
                else:
                    # Single line format with consistent spacing
                    html += f"{base_product_name.ljust(name_width)}{qty_str}   {price_str}  {total_str}\n"

            # Add separator line
            html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n\n'
            html += '</div>'
            
            # Add centered total with proper spacing
            html += f'<div class="total">Total: {total_amount:>8.2f} DZD</div>'

            # Add centered footer
            html += '<div class="footer">'
            html += "Thank you"
            html += '</div>'

            # Close HTML tags
            html += """
                    </div>
                </body>
                </html>
            """
            
            document.setHtml(html)
            document.setMetaInformation(QTextDocument.DocumentTitle, f"Sale-{sale_data['id']}")
            rect = printer.pageRect(QPrinter.Unit.Point)
            document.setPageSize(QSizeF(rect.width(), rect.height()))
            
            # Print the document
            document.print_(printer)
                
            QMessageBox.information(
                self,
                "Success",
                f"Receipt has been saved to {file_name}"
            )
            
            return True
        except Exception as e:
            QMessageBox.warning(self, "Print Error", f"Failed to print receipt: {str(e)}")
            print(f"Error printing receipt: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
