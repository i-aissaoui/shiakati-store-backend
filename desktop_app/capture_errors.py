# capture_errors.py
import os
import sys
import traceback

def run_with_error_capture():
    try:
        # Add the project root directory to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        print("Starting import of PyQt5...")
        from PyQt5.QtWidgets import QApplication
        print("PyQt5 imported successfully!")
        
        print("Attempting to import MainWindow...")
        try:
            from src.ui.main_window_new import MainWindow
            print("Imported MainWindow from main_window_new")
            main_window_source = "new"
        except Exception as e:
            print(f"Error importing from main_window_new: {str(e)}")
            print(traceback.format_exc())
            print("Trying original implementation...")
            
            from src.ui.main_window import MainWindow
            print("Imported MainWindow from main_window")
            main_window_source = "original"
        
        print(f"Creating QApplication instance...")
        app = QApplication(sys.argv)
        
        print(f"Creating MainWindow instance from {main_window_source} implementation...")
        window = MainWindow()
        
        print("MainWindow created successfully!")
        window.show()
        
        print("Window shown, entering application event loop...")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    with open('detailed_error_log.txt', 'w') as f:
        # Redirect both stdout and stderr to the file
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f
        
        try:
            run_with_error_capture()
        finally:
            # Restore stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    # Print the error log to the console
    print("Application execution completed. Error log:")
    with open('detailed_error_log.txt', 'r') as f:
        print(f.read())
