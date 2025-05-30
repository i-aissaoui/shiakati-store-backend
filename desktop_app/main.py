import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

try:
    print("Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication
    print("Importing MainWindow...")
    from src.ui.main_window import MainWindow
except Exception as e:
    print(f"Import error: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)

def main():
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        print("Creating main window...")
        window = MainWindow()
        print("Showing window...")
        window.show()
        print("Entering main loop...")
        return app.exec_()
    except Exception as e:
        print(f"Runtime error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
