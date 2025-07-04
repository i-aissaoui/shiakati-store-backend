"""
Base MainWindow class for Shiakati Store POS application.
Contains core functionality and UI initialization.
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QMessageBox, QStackedWidget,
    QButtonGroup, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QDate, QDateTime, QLocale
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from ...utils.api_client import APIClient
import os
import io
import base64

# Import utility methods
from .utility_methods import format_price, parse_price, format_datetime, apply_spinbox_styling


class MainWindow(QMainWindow):
    """Base MainWindow class with core functionality."""
    
    # Add utility methods as class methods
    format_price = format_price
    parse_price = parse_price
    format_datetime = format_datetime
    apply_spinbox_styling = apply_spinbox_styling
    
    def open_file_with_default_app(self, file_path):
        """Open a file with the default application."""
        import os
        import platform
        import subprocess
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux and other Unix-like systems
                subprocess.call(['xdg-open', file_path])
            return True
        except Exception as e:
            return False
    
    def __init__(self):
        """Initialize MainWindow."""
        super().__init__()
        self.api_client = APIClient()
        self.current_sale_items = []
        self.locale = QLocale(QLocale.Language.Arabic, QLocale.Country.Algeria)
        self.sidebar = None  # Initialize sidebar attribute
        
        # Import page modules here to avoid circular imports
        from .pos_page import POSPageMixin
        from .inventory_page import InventoryPageMixin
        from .orders_page import OrdersPageMixin
        from .categories_page import CategoriesPageMixin
        from .stats_page import StatsPageMixin
        from .expenses_page import ExpensesPageMixin
        from .images_page import ImagesPageMixin
        
        # Apply mixins to add page-specific functionality
        self.__class__ = type('MainWindow', (
            MainWindow, POSPageMixin, InventoryPageMixin, OrdersPageMixin,
            CategoriesPageMixin, StatsPageMixin, ExpensesPageMixin, ImagesPageMixin
        ), {})
        
        # Set default authentication
        self._ensure_authenticated()
        
        # Initialize UI
        self.initUI()

    def initUI(self):
        """Initialize the main UI."""
        self.setWindowTitle('Shiakati Store POS')
        self.setGeometry(100, 100, 1400, 800)
        self.apply_global_styles()
        
        try:
            # Create main container
            self.main_container = QWidget(self)
            self.setCentralWidget(self.main_container)
            
            # Set up main layout
            self.main_layout = QHBoxLayout(self.main_container)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)

            # Initialize sidebar
            self.setup_sidebar()
            
            # Create stacked widget for main content
            self.content_stack = QStackedWidget()
            self.main_layout.addWidget(self.content_stack)

            # Create content pages
            self.pos_page = QWidget()
            self.inventory_page = QWidget()
            self.stats_page = QWidget()
            self.orders_page = QWidget()
            self.categories_page = QWidget()
            self.expenses_page = QWidget()
            self.images_page = QWidget()

            # Set up pages
            self.setup_pos_page()
            self.setup_inventory_page()
            self.setup_stats_page()
            self.setup_orders_page()
            self.setup_categories_page()
            self.setup_expenses_page()
            self.setup_images_page()

            # Add pages to stack
            self.content_stack.addWidget(self.pos_page)
            self.content_stack.addWidget(self.inventory_page)
            self.content_stack.addWidget(self.stats_page)
            self.content_stack.addWidget(self.orders_page)
            self.content_stack.addWidget(self.categories_page)
            self.content_stack.addWidget(self.expenses_page)
            self.content_stack.addWidget(self.images_page)
            
            # Set up periodic stats refresh
            self.stats_timer = QTimer()
            self.stats_timer.timeout.connect(self.update_stats)
            self.stats_timer.start(30000)  # Refresh every 30 seconds

            # Initially show login
            self.show_login()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
            raise

    def apply_global_styles(self):
        """Apply global stylesheet to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                padding: 10px 16px;
                background-color: #4834d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-height: 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #686de0;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 10px 12px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border: 1px solid #007bff;
                outline: none;
            }
            /* Fix for SpinBox and DoubleSpinBox buttons */
            QSpinBox, QDoubleSpinBox {
                padding-right: 25px; /* Make room for the buttons */
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
                height: 21px;
                border-left: 1px solid #dcdde1;
                border-bottom: 1px solid #dcdde1;
                background-color: #f0f0f0;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
                height: 21px;
                border-left: 1px solid #dcdde1;
                border-top: 1px solid #dcdde1;
                background-color: #f0f0f0;
            }
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, 
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e9ecef;
            }
            
            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {
                background-color: #dee2e6;
            }
            
            /* Use direct text for better compatibility */
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 12px;
                height: 12px;
                background-color: transparent;
                border: none;
                image: none;
                margin-top: 2px;
                margin-right: 2px;
            }
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 12px;
                height: 12px;
                background-color: transparent;
                border: none;
                image: none;
                margin-bottom: 2px;
                margin-right: 2px;
            }
            
            /* Make the buttons taller for easier clicking */
            QSpinBox, QDoubleSpinBox {
                min-height: 35px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                min-height: 18px;
            }
        """)

    def show_login(self):
        """Show the login screen."""
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
        
        # Accept only admin/123 credentials or allow the API client to handle it
        if (username == "admin" and password == "123") or self.api_client.login(username, password):
            try:
                # Hide login widget
                self.login_widget.hide()
                # Show sidebar
                self.sidebar.show()
                # Show POS page by default
                self.switch_page("pos")
                # Load initial data
                self.load_initial_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to initialize application after login: {str(e)}")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def load_initial_data(self):
        """Load all initial data after successful login."""
        try:
            self.load_product_list()
            self.setup_inventory_table()
            self.load_orders_data()
            self.load_categories_data()
            self.load_expenses_data()  # Add this if you have expenses functionality
            self.update_stats()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load some initial data: {str(e)}")
            import traceback
            traceback.print_exc()

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
        pos_btn = QPushButton("�� POS")
        pos_btn.setCheckable(True)
        pos_btn.setChecked(True)
        pos_btn.clicked.connect(lambda: self.switch_page("pos"))
        
        inventory_btn = QPushButton("📦 Inventory")
        inventory_btn.setCheckable(True)
        inventory_btn.clicked.connect(lambda: self.switch_page("inventory"))
        
        orders_btn = QPushButton("📋 Orders")
        orders_btn.setCheckable(True)
        orders_btn.clicked.connect(lambda: self.switch_page("orders"))
        
        categories_btn = QPushButton("📁 Categories")
        categories_btn.setCheckable(True)
        categories_btn.clicked.connect(lambda: self.switch_page("categories"))
        
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setCheckable(True)
        stats_btn.clicked.connect(lambda: self.switch_page("stats"))
        
        expenses_btn = QPushButton("💰 Expenses")
        expenses_btn.setCheckable(True)
        expenses_btn.clicked.connect(lambda: self.switch_page("expenses"))
        
        images_btn = QPushButton("🖼️ Images & Posts")
        images_btn.setCheckable(True)
        images_btn.clicked.connect(lambda: self.switch_page("images"))
        
        # Add buttons to layout
        sidebar_layout.addWidget(pos_btn)
        sidebar_layout.addWidget(inventory_btn)
        sidebar_layout.addWidget(orders_btn)
        sidebar_layout.addWidget(categories_btn)
        sidebar_layout.addWidget(stats_btn)
        sidebar_layout.addWidget(expenses_btn)
        sidebar_layout.addWidget(images_btn)
        sidebar_layout.addStretch()
        
        # Create button group for exclusive checking
        self.nav_group = QButtonGroup(self)
        self.nav_group.addButton(pos_btn)
        self.nav_group.addButton(inventory_btn)
        self.nav_group.addButton(orders_btn)
        self.nav_group.addButton(categories_btn)
        self.nav_group.addButton(stats_btn)
        self.nav_group.addButton(expenses_btn)
        self.nav_group.addButton(images_btn)
        
        # Hide sidebar initially (shown after login)
        self.sidebar.hide()
        self.main_layout.insertWidget(0, self.sidebar)

    def switch_page(self, page_name: str):
        """Switch to the specified page."""            
        page_index = {
            "pos": 0,
            "inventory": 1,
            "stats": 2,
            "orders": 3,
            "categories": 4,
            "expenses": 5,
            "images": 6
        }.get(page_name, 0)
        
        # If switching to stats page, update the stats
        if page_index == 2:
            # Update stats with a small delay to ensure widgets are ready
            QTimer.singleShot(100, self.update_stats)
        
        # If switching to expenses page, update the expenses data
        elif page_index == 5:
            # Update expenses data with a small delay to ensure widgets are ready
            QTimer.singleShot(100, self.load_expenses_data)
        
        self.content_stack.setCurrentIndex(page_index)
        QApplication.processEvents()  # Force GUI update

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

    def apply_spinbox_styling(self, spinbox):
        """Apply consistent styling to spinboxes to ensure +/- buttons display correctly"""
        spinbox.setFixedHeight(38)
        
        # Create button widgets for up/down with direct plus/minus symbols
        up_button = QPushButton("+")
        up_button.setFixedSize(18, 18)
        up_button.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dcdde1; border-radius: 2px; font-weight: bold;")
        
        down_button = QPushButton("-")
        down_button.setFixedSize(18, 18)
        down_button.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dcdde1; border-radius: 2px; font-weight: bold;")
        
        # Connect these buttons to the spinbox's stepUp/stepDown methods
        up_button.clicked.connect(spinbox.stepUp)
        down_button.clicked.connect(spinbox.stepDown)
        
        # Create a more direct stylesheet with simplified styling
        spinbox.setStyleSheet("""
            QSpinBox, QDoubleSpinBox {
                padding-right: 30px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 28px;
                height: 19px;
                background-color: #f8f9fa;
                border-left: 1px solid #dcdde1;
                border-bottom: 1px solid #dcdde1;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 28px;
                height: 19px;
                background-color: #f8f9fa;
                border-left: 1px solid #dcdde1;
                border-top: 1px solid #dcdde1;
            }
            /* Clear existing arrow styles */
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid black;
                background-color: transparent;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid black;
                background-color: transparent;
            }
            /* Hover and pressed effects */
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e9ecef;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed,
            QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {
                background-color: #dee2e6;
            }
        """)

    def _ensure_authenticated(self):
        """Ensure the API client has authentication."""
        try:
            # Set default credentials
            self.api_client.login("admin", "123")
            print("Auto-login performed")
        except Exception as e:
            print(f"Auto-login failed: {str(e)}")
