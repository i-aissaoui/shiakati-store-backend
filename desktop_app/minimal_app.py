# minimal_app.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("If you see this, PyQt5 is working correctly")
        layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MinimalWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    print("Starting minimal test application...")
    sys.exit(main())
