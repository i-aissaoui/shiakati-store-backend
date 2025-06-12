import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import QApplication
    try:
        # First attempt to import from the new refactored module
        from src.ui.main_window_new import MainWindow
        print("Successfully imported from main_window_new")
    except ImportError as e:
        print(f"Import error from main_window_new: {str(e)}")
        print("Falling back to original implementation")
        # Fall back to the original implementation if the refactored one is not ready
        from src.ui.main_window import MainWindow
except Exception as e:
    print(f"Critical error during imports: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec_()
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        print("Starting Shiakati Store POS application...")
        main_app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        print("Application window created and shown")
        sys.exit(main_app.exec_())
    except Exception as e:
        print(f"Fatal application error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
