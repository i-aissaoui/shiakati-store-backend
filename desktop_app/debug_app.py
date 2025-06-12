# debug_app.py
import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 imported successfully")
except Exception as e:
    print(f"Error importing PyQt5: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

try:
    # Try importing from refactored module
    print("Trying to import from main_window_new...")
    from src.ui.main_window_new import MainWindow
    print("Successfully imported MainWindow from main_window_new")
except Exception as e:
    print(f"Error importing from main_window_new: {str(e)}")
    traceback.print_exc()
    
    try:
        # Fall back to original implementation
        print("Falling back to original implementation...")
        from src.ui.main_window import MainWindow
        print("Successfully imported MainWindow from main_window")
    except Exception as e:
        print(f"Error importing from main_window: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

try:
    print("Checking API client...")
    from src.utils.api_client import APIClient
    api_client = APIClient()
    print("API client initialized successfully")
except Exception as e:
    print(f"Error with API client: {str(e)}")
    traceback.print_exc()

def main():
    try:
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        print("Creating MainWindow...")
        window = MainWindow()
        print("Showing window...")
        window.show()
        print("Starting event loop...")
        return app.exec_()
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Starting application...")
    sys.exit(main())
