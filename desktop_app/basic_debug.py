# basic_debug.py
import sys
import traceback

try:
    print("Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
    print("PyQt5 imported successfully!")
    
    def run():
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        
        print("Creating QMainWindow...")
        window = QMainWindow()
        window.setWindowTitle("Debug Test")
        window.setGeometry(100, 100, 300, 200)
        
        print("Creating QLabel...")
        label = QLabel("Hello World!", window)
        label.move(50, 50)
        
        print("Showing window...")
        window.show()
        
        print("Entering event loop...")
        return app.exec_()
    
    if __name__ == "__main__":
        print("Starting debug application...")
        sys.exit(run())
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
