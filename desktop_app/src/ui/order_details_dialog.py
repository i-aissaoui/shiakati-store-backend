from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QTextEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QFormLayout, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def format_price(price: float) -> str:
    """Format a price value with the DZD currency."""
    return f"{price:.2f} DZD"

class OrderDetailsDialog(QDialog):
    def __init__(self, parent=None, order_data=None):
        super().__init__(parent)
        self.parent = parent
        self.order_data = order_data
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                font-size: 13px;
            }
            QLabel[heading="true"] {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 5px;
            }
            QGroupBox::title {
                color: #2c3e50;
                padding: 0 10px;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                min-width: 150px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton[primary="true"] {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton[primary="true"]:hover {
                background-color: #2980b9;
            }
            QPushButton[danger="true"] {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton[danger="true"]:hover {
                background-color: #c0392b;
            }
        """)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(f"Order Details #{self.order_data.get('id', 'N/A')}")
        self.setMinimumWidth(700)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Customer Information
        customer_group = QGroupBox("Customer Information")
        customer_layout = QFormLayout()
        customer_layout.addRow("Name:", QLabel(self.order_data.get('customer_name', 'N/A')))
        customer_layout.addRow("Phone:", QLabel(self.order_data.get('phone_number', 'N/A')))
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)

        # Order Items
        order_group = QGroupBox("Order Items")
        order_layout = QVBoxLayout()
        
        # Create items table
        items_table = QTableWidget()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels([
            "Product", "Size", "Color", "Quantity", "Price"
        ])

        # Add items to table
        items = self.order_data.get('items', [])
        items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            items_table.setItem(i, 0, QTableWidgetItem(item.get('product_name', 'N/A')))
            items_table.setItem(i, 1, QTableWidgetItem(item.get('size', 'N/A') or 'N/A'))
            items_table.setItem(i, 2, QTableWidgetItem(item.get('color', 'N/A') or 'N/A'))
            items_table.setItem(i, 3, QTableWidgetItem(str(item.get('quantity', 0))))
            items_table.setItem(i, 4, QTableWidgetItem(format_price(float(item.get('price', 0)))))

        # Set table properties
        header = items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Color
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Price

        order_layout.addWidget(items_table)
        total = float(self.order_data.get('total', 0))
        order_layout.addWidget(QLabel(f"Total: {format_price(total)}"))
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)

        # Delivery Information
        delivery_group = QGroupBox("Delivery Information")
        delivery_layout = QFormLayout()
        delivery_layout.addRow("Method:", QLabel(self.order_data.get('delivery_method', 'N/A')))
        delivery_layout.addRow("Wilaya:", QLabel(self.order_data.get('wilaya', 'N/A')))
        delivery_layout.addRow("Commune:", QLabel(self.order_data.get('commune', 'N/A')))
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)

        # Notes Section
        notes_group = QGroupBox("Additional Notes")
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter order notes here...")
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setText(self.order_data.get('notes', ''))
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Status Section
        status_group = QGroupBox("Order Status")
        status_layout = QVBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Pending", "Confirmed", "Processing", 
            "Shipped", "Delivered", "Cancelled"
        ])
        current_status = self.order_data.get('status', 'pending').capitalize()
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        status_layout.addWidget(self.status_combo)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Button Container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)

        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setProperty("primary", True)
        self.save_btn.clicked.connect(self.accept)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addWidget(button_container)

    def get_status(self) -> str:
        """Get the selected status."""
        return self.status_combo.currentText()

    def get_notes(self) -> str:
        """Get the notes text."""
        return self.notes_text.toPlainText()
