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
        
        # Product list
        self.product_list = QTableWidget()
        self.product_list.setColumnCount(4)
        self.product_list.setHorizontalHeaderLabels(["Name", "Barcode", "Price", "Stock"])
        self.product_list.verticalHeader().setVisible(False)
        self.product_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_list.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing
        self.product_list.itemDoubleClicked.connect(self.add_product_from_list)
        self.product_list.setMinimumHeight(300)
        self.product_list.setStyleSheet("""
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
        
        # Current sale table
        self.sale_table = QTableWidget()
        self.sale_table.setColumnCount(6)
        self.sale_table.setHorizontalHeaderLabels(["Product", "Barcode", "Price", "Quantity", "Total", "Actions"])
        self.sale_table.verticalHeader().setVisible(False)
        self.sale_table.setMinimumHeight(300)
        
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
                padding: 12px 8px;
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
            inventory = self.api_client.get_inventory()
            self.product_list.setRowCount(0)
            
            for item in inventory:
                row = self.product_list.rowCount()
                self.product_list.insertRow(row)
                self.product_list.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                self.product_list.setItem(row, 1, QTableWidgetItem(item["barcode"]))
                self.product_list.setItem(row, 2, QTableWidgetItem(self.format_price(item["price"])))
                self.product_list.setItem(row, 3, QTableWidgetItem(str(item["quantity"])))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load products: {str(e)}")

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
                    name = self.product_list.item(row, 0).text()
                    price = self.parse_price(self.product_list.item(row, 2).text())
                    stock = float(self.product_list.item(row, 3).text())  # Use float instead of int
                    quantity = float(self.quantity_input.value())  # Use float instead of int
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
                            current_qty = float(self.sale_table.item(sale_row, 3).text())
                            new_qty = current_qty + quantity
                            
                            if new_qty > stock:
                                QMessageBox.warning(self, "Error", f"Not enough stock. Only {stock} available.")
                                return
                                
                            self.sale_table.setItem(sale_row, 3, QTableWidgetItem(f"{new_qty:.1f}"))
                            self.sale_table.setItem(sale_row, 4, QTableWidgetItem(self.format_price(price * new_qty)))
                            self.update_sale_totals()
                            return
                    
                    # Add new row to sale
                    row = self.sale_table.rowCount()
                    self.sale_table.insertRow(row)
                    self.sale_table.setItem(row, 0, QTableWidgetItem(name))
                    self.sale_table.setItem(row, 1, QTableWidgetItem(barcode))
                    self.sale_table.setItem(row, 2, QTableWidgetItem(self.format_price(price)))
                    self.sale_table.setItem(row, 3, QTableWidgetItem(f"{quantity:.1f}"))
                    self.sale_table.setItem(row, 4, QTableWidgetItem(self.format_price(price * quantity)))
                    
                    # Add remove button
                    remove_btn = QPushButton("❌")
                    remove_btn.clicked.connect(lambda checked, r=row: self.remove_sale_item(r))
                    self.sale_table.setCellWidget(row, 5, remove_btn)
                    
                    self.update_sale_totals()
                    self.quantity_input.setValue(1)
                    return
            
            QMessageBox.warning(self, "Error", "Product not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")
            pass  # Error adding product

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
            total_cell = self.sale_table.item(row, 4)
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
        
        # Process the sale with the API client
        sale_items = []
        for row in range(self.sale_table.rowCount()):
            try:
                barcode = self.sale_table.item(row, 1).text().strip()
                quantity = float(self.sale_table.item(row, 3).text().strip())
                price = self.parse_price(self.sale_table.item(row, 2).text())
                sale_items.append({
                    "barcode": barcode,
                    "quantity": quantity,
                    "price": price
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
