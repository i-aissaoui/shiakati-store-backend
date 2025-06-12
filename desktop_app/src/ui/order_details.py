def show_order_details(self, row: int):
    """Show details for a selected order."""
    try:
        # Get orders from the stored data
        orders = self.api_client.get_orders()
        if not orders:
            QMessageBox.warning(self, "Error", "Could not load order details")
            return

        # Get the order ID from the first column of the selected row
        order_id = int(self.orders_table.item(row, 0).text())
        
        # Get detailed order information
        order = self.api_client.get_order(order_id)
        
        if not order or "items" not in order:
            QMessageBox.warning(self, "Error", "Could not load order details")
            return
        
        details_dialog = QDialog(self)
        details_dialog.setWindowTitle(f"Order #{order_id} Details")
        details_dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout(details_dialog)
        layout.setSpacing(10)
        
        # Order header with date and customer info
        header_layout = QHBoxLayout()
        
        # Left side - Date and Order ID
        date_info = QVBoxLayout()
        order_time = QDateTime.fromString(order['order_time'], Qt.ISODateWithMs).toString('yyyy-MM-dd hh:mm')
        date_label = QLabel(f"Date: {order_time}")
        date_label.setStyleSheet("font-weight: bold;")
        date_info.addWidget(date_label)
        
        order_id_label = QLabel(f"Order #: {order_id}")
        order_id_label.setStyleSheet("font-weight: bold;")
        date_info.addWidget(order_id_label)
        
        status_label = QLabel(f"Status: {order.get('status', 'N/A').capitalize()}")
        status_label.setStyleSheet("font-weight: bold;")
        date_info.addWidget(status_label)
        
        header_layout.addLayout(date_info)
        header_layout.addStretch()
        
        # Right side - Customer info
        customer_info = QVBoxLayout()
        customer_name_label = QLabel(f"Customer: {order.get('customer_name', 'N/A')}")
        customer_name_label.setStyleSheet("font-weight: bold;")
        customer_info.addWidget(customer_name_label)
        
        phone_label = QLabel(f"Phone: {order.get('phone_number', 'N/A')}")
        phone_label.setStyleSheet("font-weight: bold;")
        customer_info.addWidget(phone_label)
        
        delivery_label = QLabel(f"Delivery: {order.get('delivery_method', 'N/A').capitalize()}")
        delivery_label.setStyleSheet("font-weight: bold;")
        customer_info.addWidget(delivery_label)
        
        if order.get('wilaya'):
            address_label = QLabel(f"Address: {order.get('wilaya', '')}, {order.get('commune', '')}")
            address_label.setStyleSheet("font-weight: bold;")
            customer_info.addWidget(address_label)
        
        header_layout.addLayout(customer_info)
        layout.addLayout(header_layout)
        
        # Add horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)
        
        # Create items table
        items_label = QLabel("Order Items")
        items_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(items_label)
        
        items_table = QTableWidget()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Product", "Size", "Color", "Quantity", "Price"])
        
        # Set column widths
        items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
        items_table.setColumnWidth(1, 80)   # Size
        items_table.setColumnWidth(2, 80)   # Color
        items_table.setColumnWidth(3, 80)   # Quantity
        items_table.setColumnWidth(4, 100)  # Price
        
        # Style the table
        items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #f1f2f6;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px 4px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
            }
        """)
        
        # Fill table with items
        items = order.get("items", [])
        for i, item in enumerate(items):
            items_table.insertRow(i)
            items_table.setItem(i, 0, QTableWidgetItem(item.get("product_name", "Unknown")))
            items_table.setItem(i, 1, QTableWidgetItem(str(item.get("size", "N/A"))))
            items_table.setItem(i, 2, QTableWidgetItem(str(item.get("color", "N/A"))))
            items_table.setItem(i, 3, QTableWidgetItem(str(item.get("quantity", 0))))
            items_table.setItem(i, 4, QTableWidgetItem(self.format_price(float(item.get("price", 0)))))
            
        layout.addWidget(items_table)
        
        # Total amount
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        
        total_label = QLabel(f"Total: {self.format_price(float(order.get('total', 0)))}")
        total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        total_layout.addWidget(total_label)
        
        layout.addLayout(total_layout)
        
        # Notes section if available
        if order.get('notes'):
            notes_label = QLabel("Notes:")
            notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(notes_label)
            
            notes_text = QTextEdit()
            notes_text.setPlainText(order.get('notes', ''))
            notes_text.setReadOnly(True)
            notes_text.setMaximumHeight(80)
            notes_text.setStyleSheet("border: 1px solid #dcdde1; border-radius: 4px; background-color: #f8f9fa;")
            layout.addWidget(notes_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(details_dialog.accept)
        close_button.setStyleSheet(self.primary_button_style)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Show the dialog
        details_dialog.setLayout(layout)
        details_dialog.exec()
        
    except Exception as e:
        QMessageBox.warning(self, "Error", f"Failed to show order details: {str(e)}")
        import traceback
        traceback.print_exc()
