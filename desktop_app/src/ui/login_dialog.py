from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class LoginDialog(QDialog):
    """Login dialog for Shiakati Store POS application."""
    
    login_successful = pyqtSignal()
    
    def __init__(self, api_client):
        """Initialize the login dialog."""
        super().__init__()
        self.api_client = api_client
        self.initUI()
        
    def initUI(self):
        """Set up the UI components."""
        self.setWindowTitle('Shiakati Store Login')
        self.setFixedSize(400, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel('Login to Shiakati Store')
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel('Username')
        username_label.setStyleSheet("font-size: 14px; color: #555;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel('Password')
        password_label.setStyleSheet("font-size: 14px; color: #555;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Login button
        buttons_layout = QHBoxLayout()
        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.login_button)
        layout.addLayout(buttons_layout)
        
        # Set dialog layout
        self.setLayout(layout)
        
        # Set focus to username field
        self.username_input.setFocus()
        
        # Connect enter key to login
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self.attempt_login)
        
        # Set default username if available (for testing)
        self.username_input.setText("admin")
        
    def attempt_login(self):
        """Attempt to log in with provided credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validate input
        if not username or not password:
            QMessageBox.warning(self, 'Login Error', 'Username and password are required')
            return
        
        # Show a loading state
        self.login_button.setEnabled(False)
        self.login_button.setText('Logging in...')
        QApplication.processEvents()
        
        # Attempt login
        success = self.api_client.login(username, password)
        
        # Handle result
        if success:
            self.login_successful.emit()
            self.accept()
        else:
            QMessageBox.critical(self, 'Login Failed', 'Invalid username or password')
            self.login_button.setEnabled(True)
            self.login_button.setText('Login')
