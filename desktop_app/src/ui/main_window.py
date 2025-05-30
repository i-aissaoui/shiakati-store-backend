from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, 
    QTableWidgetItem, QMessageBox, QTabWidget, QStackedWidget,
    QComboBox, QSpinBox, QDoubleSpinBox, QDialog, QFormLayout, 
    QTextEdit, QGroupBox, QDialogButtonBox, QDateEdit, QButtonGroup,
    QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDate, QDateTime, QLocale, QSizeF, QMarginsF
from PyQt5.QtGui import QFont, QColor, QTextDocument, QPageSize
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from ..utils.api_client import APIClient
from typing import Dict, List, Optional
import json
import PIL.Image
import requests
import os  # Add os module import

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_sale_items = []
        self.locale = QLocale(QLocale.Language.Arabic, QLocale.Country.Algeria)
        self.sidebar = None  # Initialize sidebar attribute
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Shiakati Store POS')
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4834d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #686de0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        try:
            # Create main container widget
            self.main_container = QWidget()
            self.setCentralWidget(self.main_container)
            self.main_layout = QHBoxLayout(self.main_container)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)

            # Initialize sidebar (but don't show it yet)
            self.setup_sidebar()
            
            # Create stacked widget for main content
            self.content_stack = QStackedWidget()
            self.main_layout.addWidget(self.content_stack)

            # Create content pages
            self.pos_page = QWidget()
            self.inventory_page = QWidget()
            self.stats_page = QWidget()
            self.orders_page = QWidget()  # Orders management page

            # Set up pages
            self.setup_pos_page()
            self.setup_inventory_page()
            self.setup_stats_page()
            self.setup_orders_page()

            # Add pages to stack
            self.content_stack.addWidget(self.pos_page)
            self.content_stack.addWidget(self.inventory_page)
            self.content_stack.addWidget(self.stats_page)
            self.content_stack.addWidget(self.orders_page)
            
            # Set up periodic stats refresh
            self.stats_timer = QTimer()
            self.stats_timer.timeout.connect(self.update_stats)
            self.stats_timer.start(30000)  # Refresh every 30 seconds

            # Initially show login
            self.show_login()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
            print(f"Error initializing UI: {str(e)}")
            raise

            # Initially show login
            self.show_login()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
            print(f"Error initializing UI: {str(e)}")
            raise

    def show_login(self):
        self.login_widget = QWidget()
        self.login_widget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #2f3640;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: #4834d4;
            }
            QPushButton {
                background-color: #4834d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #686de0;
            }
        """)
        
        # Create a container for centering
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Login form
        form_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Logo/Title
        title = QLabel("Shiakati Store")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2f3640;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Username input
        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(login_button)
        
        form_widget.setLayout(layout)
        container_layout.addWidget(form_widget)
        container.setLayout(container_layout)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.login_widget.setLayout(main_layout)
        self.main_layout.addWidget(self.login_widget)

    def handle_login(self):
        """Handle login form submission."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if self.api_client.login(username, password):
            try:
                # Remove login widget
                if hasattr(self, 'login_widget'):
                    self.login_widget.hide()
                    self.main_layout.removeWidget(self.login_widget)
                    self.login_widget.deleteLater()
                
                # Make sure sidebar is set up
                if not self.sidebar:
                    self.setup_sidebar()
                    
                # Show sidebar and switch to POS page
                self.sidebar.show()
                self.switch_page("pos")
                
                # Load initial data
                self.load_product_list()
                self.setup_inventory_table()
                self.load_orders_data()
            except Exception as e:
                print(f"Error setting up main interface: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to initialize interface: {str(e)}")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def setup_pos_page(self):
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
        self.product_list.itemDoubleClicked.connect(self.add_product_from_list)
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
        
        # Enable editing only for quantity column
        self.sale_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.sale_table.itemChanged.connect(self.handle_sale_item_change)
        
        # Improve table styling
        self.sale_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0984e3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 8px;
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

    def setup_inventory_page(self):
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
        self.inventory_table.setColumnCount(7)  # Added Actions column
        self.inventory_table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Variant Barcode", 
            "Category", "Price", "Stock", "Actions"
        ])
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.inventory_table)
        
        # Add product section
        form_layout = QHBoxLayout()
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product Name")
        self.product_barcode_input = QLineEdit()
        self.product_barcode_input.setPlaceholderText("Barcode")
        self.product_category_combo = QComboBox()
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setMaximum(9999.99)
        self.product_stock_input = QDoubleSpinBox()  # Changed from QSpinBox to QDoubleSpinBox
        self.product_stock_input.setMaximum(9999.99)
        
        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(self.product_barcode_input)
        form_layout.addWidget(self.product_category_combo)
        form_layout.addWidget(self.product_price_input)
        form_layout.addWidget(self.product_stock_input)
        
        add_button = QPushButton("Add Product")
        add_button.clicked.connect(self.handle_add_product)
        form_layout.addWidget(add_button)
        
        layout.addWidget(self.inventory_table)
        layout.addLayout(form_layout)

    def parse_price(self, price_str: str) -> float:
        """Parse price string into float, handling different formats."""
        try:
            # Remove currency symbol and whitespace
            price_str = price_str.replace('DZD', '').strip()
            
            # Handle both comma and dot as decimal separators
            price_str = price_str.replace(',', '.')
            
            # Remove any remaining non-numeric chars except decimal point
            price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
            
            # Convert to float
            price = float(price_str)
            
            return round(price, 2)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid price format: {price_str}")

    def format_price(self, price: float) -> str:
        """Format price with DZD currency."""
        try:
            return f"{price:.2f} DZD"
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid price value: {price}")

    def setup_stats_page(self):
        """Set up the statistics page."""
        # Main layout for stats page with history sidebar
        main_layout = QHBoxLayout(self.stats_page)
        
        # Create left panel for main stats
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create cards layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)  # Minimal spacing between cards
        
        # Total Sales Card
        sales_card = QWidget()
        sales_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #4b6cb7, stop:1 #182848);
                border-radius: 4px;
                padding: 4px;
                color: white;
                min-height: 30px;
            }
            QLabel {
                background: transparent;
            }
        """)
        sales_layout = QVBoxLayout(sales_card)
        sales_layout.setContentsMargins(8, 4, 8, 4)
        sales_layout.setSpacing(0)  # Minimal spacing between elements
        
        sales_icon = QLabel("🛍️")
        sales_icon.setStyleSheet("font-size: 16px;")
        sales_layout.addWidget(sales_icon)
        
        sales_title = QLabel("Total Sales")
        sales_title.setStyleSheet("font-size: 14px; color: #e2e8f0;")
        sales_layout.addWidget(sales_title)
        
        self.total_sales_label = QLabel("0")
        self.total_sales_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0;
        """)
        self.total_sales_label.setObjectName("total_sales_label")
        sales_layout.addWidget(self.total_sales_label)
        
        sales_subtitle = QLabel("Total number of transactions")
        sales_subtitle.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        sales_layout.addWidget(sales_subtitle)
        
        cards_layout.addWidget(sales_card)
        
        # Revenue Card
        revenue_card = QWidget()
        revenue_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #11998e, stop:1 #38ef7d);
                border-radius: 4px;
                padding: 4px;
                color: white;
                min-height: 30px;
            }
            QLabel {
                background: transparent;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_card)
        revenue_layout.setContentsMargins(8, 4, 8, 4)
        revenue_layout.setSpacing(0)  # Minimal spacing between elements
        
        revenue_icon = QLabel("💰")
        revenue_icon.setStyleSheet("font-size: 16px;")
        revenue_layout.addWidget(revenue_icon)
        
        revenue_title = QLabel("Total Revenue")
        revenue_title.setStyleSheet("font-size: 14px; color: #e2e8f0;")
        revenue_layout.addWidget(revenue_title)
        
        self.revenue_label = QLabel("0 DZD")
        self.revenue_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0;
        """)
        self.revenue_label.setObjectName("revenue_label")
        revenue_layout.addWidget(self.revenue_label)
        
        revenue_subtitle = QLabel("Total earnings from all sales")
        revenue_subtitle.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        revenue_layout.addWidget(revenue_subtitle)
        
        cards_layout.addWidget(revenue_card)
        
        # Add cards layout to left panel
        left_layout.addLayout(cards_layout)
        
        # Top Products Section
        top_products_container = QWidget()
        top_products_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                color: #1e293b;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
            }
            QTableWidget {
                border: none;
                gridline-color: #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #475569;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        top_products_layout = QVBoxLayout(top_products_container)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_label = QLabel("📊 Top Performing Products")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        top_products_layout.addLayout(header_layout)
        
        # Table
        self.top_products_table = QTableWidget()
        self.top_products_table.setObjectName("top_products_table")
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            "Product", "Quantity Sold", "Revenue (DZD)", "Profit (DZD)"
        ])
        self.top_products_table.horizontalHeader().setStretchLastSection(True)
        self.top_products_table.setAlternatingRowColors(True)
        self.top_products_table.verticalHeader().setVisible(False)
        self.top_products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        header = self.top_products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.top_products_table.setColumnWidth(1, 150)  # Quantity
        self.top_products_table.setColumnWidth(2, 150)  # Revenue
        self.top_products_table.setColumnWidth(3, 150)  # Profit
        
        top_products_layout.addWidget(self.top_products_table)
        left_layout.addWidget(top_products_container)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel, stretch=2)
        
        # Create right panel for sales history
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sales History Title
        history_title = QLabel("Sales History")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        right_layout.addWidget(history_title)
        
        # Sales History Table
        self.sales_history_table = QTableWidget()
        self.sales_history_table.setObjectName("sales_history_table")
        self.sales_history_table.setColumnCount(3)
        self.sales_history_table.setHorizontalHeaderLabels([
            "Date", "Items", "Total"
        ])
        self.sales_history_table.horizontalHeader().setStretchLastSection(True)
        self.sales_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        right_layout.addWidget(self.sales_history_table)
        
        # Style the right panel
        right_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #dcdde1;
            }
        """)
        
        # Add right panel to main layout
        main_layout.addWidget(right_panel, stretch=1)
        
        # Connect double click event for sales history
        self.sales_history_table.cellDoubleClicked.connect(self.show_sale_details)
        
        # Initial load of sales history
        self.load_sales_history()

    def load_sales_history(self):
        """Load and display sales history in the sidebar table."""
        try:
            if not hasattr(self, 'sales_history_table') or not self.sales_history_table:
                return
                
            sales_history = self.api_client.get_sales_history()
            self.sales_history_table.setRowCount(0)
            
            for sale in reversed(sales_history):  # Show newest first
                row = self.sales_history_table.rowCount()
                self.sales_history_table.insertRow(row)
                
                # Format date
                sale_date = QDateTime.fromString(sale["sale_time"], Qt.ISODateWithMs)
                formatted_date = sale_date.toString("yyyy-MM-dd hh:mm")
                
                # Calculate total quantity from all items, handling floating point display
                total_quantity = sum(float(item["quantity"]) for item in sale["items"])
                items_summary = f"{total_quantity:.1f} items"
                
                # Calculate total from items to ensure consistency
                items_total = sum(float(item["quantity"]) * float(item["price"]) for item in sale["items"])
                
                # Set table items
                self.sales_history_table.setItem(row, 0, QTableWidgetItem(formatted_date))
                self.sales_history_table.setItem(row, 1, QTableWidgetItem(items_summary))
                self.sales_history_table.setItem(row, 2, QTableWidgetItem(self.format_price(items_total)))
                
        except Exception as e:
            print(f"Error loading sales history: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load sales history: {str(e)}")
            
    def show_sale_details(self, row: int):
        """Show details for a selected sale."""
        try:
            # Get sale from the stored data
            sales_history = self.api_client.get_sales_history()
            if not sales_history:
                QMessageBox.warning(self, "Error", "Could not load sale details")
                return

            # Get the current sale since we store them in reverse order (newest first)
            current_sale = sales_history[-(row + 1)]  # Simple negative indexing to get the correct sale
            current_sale_id = current_sale["id"]
            sale = self.api_client.get_sale_details(current_sale_id)
            
            if not sale or "items" not in sale:
                QMessageBox.warning(self, "Error", "Could not load sale details")
                return
            
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Sale Details - #{current_sale_id}")
            details_dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(details_dialog)
            layout.setSpacing(10)
            
            # Date and time info
            date_label = QLabel(f"Date: {QDateTime.fromString(sale['sale_time'], Qt.ISODateWithMs).toString('yyyy-MM-dd hh:mm')}")
            date_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(date_label)
            
            # Create items table
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Product", "Price", "Quantity", "Total"])
            
            # Set column widths
            items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
            items_table.setColumnWidth(1, 100)  # Price
            items_table.setColumnWidth(2, 80)   # Quantity
            items_table.setColumnWidth(3, 100)  # Total
            
            # Style the table
            items_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #f1f2f6;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }
            """)
            
            # Disable editing
            items_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Add sale items
            total_items = 0
            items_total = 0
            for item in sale["items"]:
                row = items_table.rowCount()
                items_table.insertRow(row)
                
                price = float(item["price"])
                quantity = float(item["quantity"])
                total = price * quantity
                items_total += total
                
                items_table.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                items_table.setItem(row, 1, QTableWidgetItem(self.format_price(price)))
                items_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.1f}"))  # Display 1 decimal place
                items_table.setItem(row, 3, QTableWidgetItem(self.format_price(total)))
                
                total_items += quantity
        
            layout.addWidget(items_table)
            
            # Summary section
            summary_widget = QWidget()
            summary_layout = QVBoxLayout(summary_widget)
            summary_layout.setSpacing(5)
            
            items_count = QLabel(f"Total Items: {total_items}")
            items_count.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(items_count)
            
            total_label = QLabel(f"Total Amount: {self.format_price(float(sale['total']))}")
            total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3436; margin-top: 5px;")
            summary_layout.addWidget(total_label)
            
            layout.addWidget(summary_widget)
            
            # Button container
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            
            # Print button
            print_button = QPushButton("🖨️ Print Ticket")
            print_button.clicked.connect(lambda: self.print_sale_ticket(sale))
            print_button.setStyleSheet("""
                QPushButton {
                    background-color: #00b894;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00a885;
                }
            """)
            button_layout.addWidget(print_button)
            
            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(details_dialog.close)
            close_button.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    font-weight: bold;
                }
            """)
            button_layout.addWidget(close_button)
            
            layout.addWidget(button_container)
            
            details_dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load sale details: {str(e)}")
            print(f"Error showing sale details: {str(e)}")  # Debug logging

    def print_sale_ticket(self, sale_data):
        """Print a sale ticket."""
        try:
            # Create receipts directory if it doesn't exist
            if not os.path.exists("receipt"):
                os.makedirs("receipt")

            printer = QPrinter()
            custom_page_size = QPageSize(QSizeF(80, 200), QPageSize.Unit.Millimeter)
            printer.setPageSize(custom_page_size)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(f"receipt/Sale-{sale_data['id']}.pdf")
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
                            font-size: 7pt;
                            line-height: 1.1;
                            white-space: pre;
                        }
                        .content {
                            width: 100%;
                            text-align: center;
                        }
                        .store-name {
                            font-size: 10pt;
                            margin-bottom: 6mm;
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

            # Store name - centered
            html += '<div class="store-name">Shiakati Store</div>'

            # Add date and sale number - centered in header section
            date_str = QDateTime.fromString(sale_data['sale_time'], Qt.ISODateWithMs).toString('yyyy-MM-dd HH:mm')
            html += '<div class="header">'
            html += f"Date: {date_str}\n"
            html += f"Sale {sale_data['id']}\n\n"  # Added extra newline
            html += '</div>'

            # Start items section
            html += '<div class="items-section">'
            
            # Add separator line at top
            html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n'
            
            # Add header for items with proper alignment
            html += "Item            Qty  Price  Total\n"
            html += '<span style="font-weight: bold;">───────────────────────────────────</span>\n'

            # Add items with proper spacing
            total_items = 0
            total_amount = 0
            for item in sale_data["items"]:
                product_name = item.get("product_name", "Unknown Product")
                quantity = float(item.get("quantity", 1))
                price = float(item.get("price", 0))
                total = price * quantity
                total_items += quantity
                total_amount += total
                
                # Handle long product names with line wrapping
                name_width = 16
                if len(product_name) > name_width:
                    # Split into multiple lines
                    first_line = product_name[:name_width]
                    remaining = product_name[name_width:]
                    # Format the first line with values
                    qty_str = f"{quantity:3.1f}".rjust(4)
                    price_str = f"{price:6.2f}".rjust(6)
                    total_str = f"{total:6.2f}".rjust(6)
                    html += f"{first_line.ljust(14)}{qty_str}  {price_str}  {total_str}\n"
                    
                    # Add remaining text on next line
                    while remaining:
                        line = remaining[:name_width]
                        remaining = remaining[name_width:]
                        html += f"{line.ljust(name_width + 16)}\n"  # Add padding to align with first line
                else:
                    # Single line format
                    qty_str = f"{quantity:3.1f}".rjust(4)
                    price_str = f"{price:6.2f}".rjust(6)
                    total_str = f"{total:6.2f}".rjust(6)
                    html += f"{product_name.ljust(14)}{qty_str}  {price_str}  {total_str}\n"

            # Add separator line
            html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n\n'
            html += '</div>'

            # Add centered total
            html += f'<div class="total">Total: {total_amount:.2f} DZD</div>'

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
                f"Receipt has been saved to receipt/Sale-{sale_data['id']}.pdf"
            )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to print ticket: {str(e)}")
            print(f"Error printing ticket: {str(e)}")  # Debug logging
            
            # Create the receipt directory if it doesn't exist
            if not os.path.exists("receipt"):
                try:
                    os.makedirs("receipt")
                except Exception as mkdir_error:
                    print(f"Failed to create receipt directory: {str(mkdir_error)}")
                    return

    def update_stats(self):
        """Update statistics display."""
        print("Starting stats update...")
        QApplication.processEvents()  # Process any pending events
        
        try:
            # Get stats from API
            stats = self.api_client.get_stats()
            if not stats:
                print("No stats data received from API")
                return
                
            print(f"Received stats: {stats}")
            
            # Update total sales (using total_orders from API)
            total_sales = stats.get("total_orders", 0)
            sales_text = str(int(float(total_sales)))
            self.total_sales_label.setText(sales_text)
            QApplication.processEvents()  # Force update
            print(f"Updated total sales to: {sales_text}")
            
            # Update total revenue    
            total_revenue = stats.get("total_revenue", 0)
            revenue_text = self.format_price(float(total_revenue))
            self.revenue_label.setText(revenue_text)
            QApplication.processEvents()  # Force update
            print(f"Updated total revenue to: {revenue_text}")

            # Update top products table
            self.top_products_table.setRowCount(0)
            top_products = stats.get("top_products", [])
            print(f"Got {len(top_products)} top products")
            
            try:
                for product in top_products:
                    row = self.top_products_table.rowCount()
                    self.top_products_table.insertRow(row)
                    
                    # Get product data with fallbacks
                    name = product.get("name", "Unknown")
                    sales = float(product.get("total_sales", 0))
                    revenue = float(product.get("total_revenue", 0))
                    profit = revenue * 0.3  # Assuming 30% profit margin
                    
                    # Add items to row
                    self.top_products_table.setItem(row, 0, QTableWidgetItem(str(name)))
                    self.top_products_table.setItem(row, 1, QTableWidgetItem(str(int(sales))))
                    self.top_products_table.setItem(row, 2, QTableWidgetItem(self.format_price(revenue)))
                    self.top_products_table.setItem(row, 3, QTableWidgetItem(self.format_price(profit)))
                    QApplication.processEvents()  # Update after each row
                
            except Exception as e:
                print(f"Error processing top products: {str(e)}")
            
            # Update sales history
            self.load_sales_history()
                
        except Exception as e:
            print(f"Stats update error: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging

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
                self.product_list.setItem(row, 4, QTableWidgetItem(item["category"]))
                self.product_list.setItem(row, 5, QTableWidgetItem(item["size"]))
                self.product_list.setItem(row, 6, QTableWidgetItem(item["color"]))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load products: {str(e)}")
            
    def setup_inventory_table(self):
        """Set up the inventory management table."""
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
        
        # Increase row height for better icon visibility
        self.inventory_table.verticalHeader().setDefaultSectionSize(36)
        
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

    def setup_orders_page(self):
        layout = QVBoxLayout(self.orders_page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.order_search_input = QLineEdit()
        self.order_search_input.setPlaceholderText("🔍 Search orders...")
        self.order_search_input.textChanged.connect(self.filter_orders)
        self.order_search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                font-size: 14px;
                min-width: 300px;
            }
        """)
        search_layout.addWidget(self.order_search_input)
        
        search_layout.addStretch()
        
        # Date range filters
        date_label = QLabel("Date Range:")
        search_layout.addWidget(date_label)
        
        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Default to last month
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        search_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())  # Default to today
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        search_layout.addWidget(self.end_date)
        
        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.filter_orders_by_date)
        search_layout.addWidget(filter_button)
        
        layout.addLayout(search_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Date", "Customer", "Total", "Status"])
        self.orders_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.orders_table)
        
        # Order details section
        self.order_details = QTextEdit()
        self.order_details.setReadOnly(True)
        self.order_details.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.order_details)
        
        # Load initial orders data
        self.load_orders_data()

    def load_orders_data(self):
        """Load orders data into the orders table."""
        try:
            orders = self.api_client.get_orders()
            self.orders_table.setRowCount(0)
            
            for order in orders:
                row = self.orders_table.rowCount()
                self.orders_table.insertRow(row)
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order["id"])))
                self.orders_table.setItem(row, 1, QTableWidgetItem(order["date"]))
                self.orders_table.setItem(row, 2, QTableWidgetItem(order["customer"] or "N/A"))
                self.orders_table.setItem(row, 3, QTableWidgetItem(self.format_price(order["total"])))
                self.orders_table.setItem(row, 4, QTableWidgetItem(order["status"]))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load orders: {str(e)}")

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

    def filter_orders(self):
        """Filter the orders table based on search text."""
        search_text = self.order_search_input.text().lower()
        for row in range(self.orders_table.rowCount()):
            match = False
            for col in range(self.orders_table.columnCount()):
                item = self.orders_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.orders_table.setRowHidden(row, not match)

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
            
    def filter_orders_by_date(self):
        """Filter orders by the selected date range."""
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        
        for row in range(self.orders_table.rowCount()):
            order_date = QDate.fromString(self.orders_table.item(row, 1).text(), "yyyy-MM-dd")
            if start_date <= order_date <= end_date:
                self.orders_table.setRowHidden(row, False)
            else:
                self.orders_table.setRowHidden(row, True)

    def setup_sidebar(self):
        """Set up the sidebar with navigation buttons."""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #2f3640;
                color: white;
            }
            QPushButton {
                padding: 15px;
                text-align: left;
                border: none;
                border-radius: 0;
                background-color: transparent;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #353b48;
            }
            QPushButton:checked {
                background-color: #40739e;
                border-left: 4px solid #74b9ff;
            }
        """)
        
        # Create sidebar layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add navigation buttons
        pos_btn = QPushButton("🛒 POS")
        pos_btn.setCheckable(True)
        pos_btn.setChecked(True)
        pos_btn.clicked.connect(lambda: self.switch_page("pos"))
        
        inventory_btn = QPushButton("📦 Inventory")
        inventory_btn.setCheckable(True)
        inventory_btn.clicked.connect(lambda: self.switch_page("inventory"))
        
        orders_btn = QPushButton("📋 Orders")
        orders_btn.setCheckable(True)
        orders_btn.clicked.connect(lambda: self.switch_page("orders"))
        
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setCheckable(True)
        stats_btn.clicked.connect(lambda: self.switch_page("stats"))
        
        # Add buttons to layout
        sidebar_layout.addWidget(pos_btn)
        sidebar_layout.addWidget(inventory_btn)
        sidebar_layout.addWidget(orders_btn)
        sidebar_layout.addWidget(stats_btn)
        sidebar_layout.addStretch()
        
        # Create button group for exclusive checking
        self.nav_group = QButtonGroup(self)
        self.nav_group.addButton(pos_btn)
        self.nav_group.addButton(inventory_btn)
        self.nav_group.addButton(orders_btn)
        self.nav_group.addButton(stats_btn)
        
        # Hide sidebar initially (shown after login)
        self.sidebar.hide()
        self.main_layout.insertWidget(0, self.sidebar)

    def switch_page(self, page_name: str):
        """Switch to the specified page."""            
        page_index = {
            "pos": 0,
            "inventory": 1,
            "stats": 2,
            "orders": 3
        }.get(page_name, 0)
        
        # If switching to stats page, update the stats
        if page_index == 2:
            # Update stats with a small delay to ensure widgets are ready
            QTimer.singleShot(100, self.update_stats)
        
        self.content_stack.setCurrentIndex(page_index)
        print(f"Switched to page {page_name} (index {page_index})")
        QApplication.processEvents()  # Force GUI update

    def cleanup_stats_widgets(self):
        """Safely clean up stats page widgets."""
        try:
            if hasattr(self, 'total_sales_label'):
                self.total_sales_label.deleteLater()
                self.total_sales_label = None
            if hasattr(self, 'revenue_label'):
                self.revenue_label.deleteLater()
                self.revenue_label = None
            if hasattr(self, 'top_products_table'):
                self.top_products_table.deleteLater()
                self.top_products_table = None
        except Exception as e:
            print(f"Error cleaning up stats widgets: {str(e)}")

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

    def create_sale(self):
        """Process the current sale with proper error handling."""
        try:
            if self.sale_table.rowCount() == 0:
                QMessageBox.warning(self, "Error", "No items in the sale")
                return

            # Prepare sale items
            sale_items = []
            total_amount = 0.0
            
            for row in range(self.sale_table.rowCount()):
                try:
                    # Get values with proper parsing
                    barcode = self.sale_table.item(row, 1).text().strip()
                    if not barcode:
                        raise ValueError("Missing barcode")
                        
                    quantity_str = self.sale_table.item(row, 3).text().strip()
                    quantity = float(quantity_str.replace(',', '.'))
                    if quantity <= 0:
                        raise ValueError("Quantity must be greater than 0")
                        
                    price = self.parse_price(self.sale_table.item(row, 2).text())
                    if price <= 0:
                        raise ValueError("Price must be greater than 0")
                        
                    # Verify against inventory
                    available_stock = 0
                    for product_row in range(self.product_list.rowCount()):
                        if self.product_list.item(product_row, 1).text().strip() == barcode:
                            available_stock = float(self.product_list.item(product_row, 3).text())
                            break
                            
                    if quantity > available_stock:
                        raise ValueError(f"Not enough stock for product {barcode}. Only {available_stock} available.")
                    
                    item = {
                        'barcode': barcode,
                        'quantity': quantity,
                        'price': price
                    }
                    sale_items.append(item)
                    total_amount += price * quantity
                    
                except (ValueError, AttributeError) as e:
                    raise Exception(f"Invalid data in row {row + 1}: {str(e)}")

            if not sale_items:
                raise Exception("No valid items in sale")

            # Create sale through API
            response = self.api_client.create_sale(sale_items, total_amount)
            
            if response is None:
                raise Exception("No response from server")
                
            if isinstance(response, dict) and response.get('id'):
                QMessageBox.information(self, "Success", "Sale completed successfully!")
                self.sale_table.setRowCount(0)  # Clear the sale table
                self.update_sale_totals()  # Update totals after clearing
                self.load_product_list()  # Refresh inventory
            else:
                error_msg = response.get('error', 'Unknown error') if isinstance(response, dict) else "Invalid response from server"
                raise Exception(error_msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process sale: {str(e)}")
            print(f"Sale processing error: {str(e)}")

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
            print(f"Error adding product: {str(e)}")  # Add debug logging

    def add_product_from_list(self, item):
        """Add a product to the sale when double-clicked in the product list."""
        row = item.row()
        barcode = self.product_list.item(row, 1).text()
        self.add_product_to_sale(barcode)
            
    def edit_inventory_item(self, row: int):
        """Edit an inventory item."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product")
        layout = QFormLayout(dialog)
        
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

    def show_add_product_dialog(self):
        """Show dialog for adding a new product."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        layout = QFormLayout(dialog)
        
        # Create input fields
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter product name")
        
        barcode_input = QLineEdit()
        barcode_input.setPlaceholderText("Enter or scan barcode")
        
        price_input = QDoubleSpinBox()
        price_input.setMaximum(999999.99)
        price_input.setSuffix(" DZD")
        price_input.setDecimals(2)
        
        quantity_input = QDoubleSpinBox()  # Changed to QDoubleSpinBox
        quantity_input.setMaximum(9999.99)
        quantity_input.setMinimum(0)
        quantity_input.setDecimals(2)  # Allow 2 decimal places
        
        # Create and populate category dropdown
        category_combo = QComboBox()
        try:
            categories = self.api_client.get_categories()
            if not categories:
                QMessageBox.warning(dialog, "Warning", "No categories found. Please create categories first.")
                return
            
            # Store category data for later use
            dialog.categories = categories
            for cat in categories:
                category_combo.addItem(cat["name"])
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load categories: {str(e)}")
            return
        
        # Optional fields
        size_input = QLineEdit()
        size_input.setPlaceholderText("Enter size (optional)")
        
        color_input = QLineEdit()
        color_input.setPlaceholderText("Enter color (optional)")
        
        # Add fields to form with validation messages
        layout.addRow("Product Name*:", name_input)
        layout.addRow("Barcode*:", barcode_input)
        layout.addRow("Price* (DZD):", price_input)
        layout.addRow("Quantity*:", quantity_input)
        layout.addRow("Category*:", category_combo)
        layout.addRow("Size:", size_input)
        layout.addRow("Color:", color_input)
        
        # Add note about required fields
        note = QLabel("* Required fields")
        note.setStyleSheet("color: #666;")
        layout.addRow(note)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        # Store input references for validation
        dialog.name_input = name_input
        dialog.barcode_input = barcode_input
        dialog.price_input = price_input
        dialog.quantity_input = quantity_input
        dialog.category_combo = category_combo
        dialog.size_input = size_input
        dialog.color_input = color_input
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Validate required fields
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
                    
                except Exception as variant_error:
                    # Get the error message
                    error_msg = str(variant_error)
                    if "Failed to create variant:" in error_msg:
                        error_msg = error_msg.split("Failed to create variant:", 1)[1].strip()
                    
                    QMessageBox.warning(self, "Error", f"Failed to create variant: {error_msg}")
                    
                    # Clean up the product since variant creation failed
                    try:
                        if 'product_response' in locals() and product_response and 'id' in product_response:
                            self.api_client.delete_product(product_response['id'])
                    except Exception as cleanup_error:
                        print(f"Error during cleanup: {cleanup_error}")  # Log cleanup error
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

    def handle_barcode_scan(self):
        """Handle a barcode scan by getting the barcode from the input field and adding the product to sale."""
        barcode = self.barcode_input.text().strip()
        if barcode:
            self.add_product_to_sale(barcode)
            self.barcode_input.clear()  # Clear the input field after processing

    def handle_sale_item_change(self, item):
        """Handle changes to items in the sale table, particularly quantity changes."""
        # Only handle changes to the quantity column (index 3)
        if item.column() != 3:
            return

        try:
            row = item.row()
            new_quantity = float(item.text())
            if new_quantity <= 0:
                QMessageBox.warning(self, "Error", "Quantity must be greater than 0")
                item.setText('1')
                new_quantity = 1.0

            # Get product info
            barcode = self.sale_table.item(row, 1).text().strip()
            price = self.parse_price(self.sale_table.item(row, 2).text())

            # Check available stock
            available_stock = 0
            for product_row in range(self.product_list.rowCount()):
                if self.product_list.item(product_row, 1).text().strip() == barcode:
                    available_stock = float(self.product_list.item(product_row, 3).text())
                    break

            if new_quantity > available_stock:
                QMessageBox.warning(self, "Error", f"Not enough stock. Only {available_stock:.1f} available.")
                item.setText(f"{min(available_stock, 1.0):.1f}")
                new_quantity = min(available_stock, 1.0)

            # Update total for this row
            self.sale_table.setItem(row, 4, QTableWidgetItem(self.format_price(price * new_quantity)))
            self.update_sale_totals()

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid quantity value")
            item.setText('1.0')
    
    def handle_add_product(self):
        """Handle adding a new product from the inventory page form."""
        try:
            # Get values from form fields
            name = self.product_name_input.text().strip()
            barcode = self.product_barcode_input.text().strip()
            category = self.product_category_combo.currentText()
            price = float(self.product_price_input.value())
            quantity = float(self.product_stock_input.value())

            # Validate required fields
            if not name or not barcode or not category:
                QMessageBox.warning(self, "Error", "Please fill in all required fields")
                return

            # Add the product and variant through the API
            product_data = {
                "name": name,
                "description": name,  # Using name as description for now
                "category_id": self.get_category_id(category)
            }

            try:
                # Create the product first
                response = requests.post(
                    f"{self.api_client.base_url}/products",
                    headers=self.api_client.get_headers(),
                    json=product_data                )
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", f"Failed to create product: {response.text}")
                    return
                
                product = response.json()
                
                # Then create a variant for it
                variant_data = {
                    "product_id": product["id"],
                    "barcode": barcode,
                    "price": price,
                    "quantity": stock,
                    "size": "",  # Default empty size
                    "color": ""  # Default empty color
                }
                
                response = requests.post(
                    f"{self.api_client.base_url}/variants",
                    headers=self.api_client.get_headers(),
                    json=variant_data
                )
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", f"Failed to create variant: {response.text}")
                    return

                # Clear the form
                self.product_name_input.clear()
                self.product_barcode_input.clear()
                self.product_price_input.setValue(0)
                self.product_stock_input.setValue(0)

                # Refresh the inventory table and product list
                self.setup_inventory_table()
                self.load_product_list()

                QMessageBox.information(self, "Success", "Product added successfully")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process form: {str(e)}")
    
    def delete_inventory_item(self, row: int):
        """Delete an inventory item."""
        try:
            # Get the barcode of the item to delete
            barcode = self.inventory_table.item(row, 1).text().strip()
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, "Delete Product",
                "Are you sure you want to delete this product?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
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
                
                # Delete the variant through the API using its ID
                response = requests.delete(
                    f"{self.api_client.base_url}/variants/{variant_id}",
                                       headers=self.api_client.get_headers()
                )
                
                if response.status_code != 200:
                    QMessageBox.warning(self, "Error", f"Failed to delete product: {response.text}")
                    return
                
                # Remove the row from the table
                self.inventory_table.removeRow(row)
                
                # Refresh the product list
                self.load_product_list()
                
                QMessageBox.information(self, "Success", "Product deleted successfully")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete product: {str(e)}")