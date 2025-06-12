# step_by_step_debug.py
import os
import sys
import traceback

def log(message):
    """Write message both to stdout and to the log file"""
    print(message)
    with open('step_by_step_log.txt', 'a') as f:
        f.write(message + '\n')

# Start with a clean log
with open('step_by_step_log.txt', 'w') as f:
    f.write("Starting step-by-step debugging\n")

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
log(f"Set project root: {project_root}")

# Step 1: Import PyQt5
try:
    log("Step 1: Importing PyQt5 components...")
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt
    log("PyQt5 imports successful!")
except Exception as e:
    log(f"ERROR in Step 1: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 2: Import APIClient
try:
    log("Step 2: Importing APIClient...")
    from src.utils.api_client import APIClient
    log("APIClient import successful!")
except Exception as e:
    log(f"ERROR in Step 2: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 3: Create an APIClient instance
try:
    log("Step 3: Creating APIClient instance...")
    api_client = APIClient()
    log("APIClient instance created successfully!")
except Exception as e:
    log(f"ERROR in Step 3: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 4: Import the original main window
try:
    log("Step 4: Importing original MainWindow...")
    from src.ui.main_window import MainWindow as OriginalMainWindow
    log("Original MainWindow import successful!")
except Exception as e:
    log(f"ERROR in Step 4: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 5: Try importing the new main window
try:
    log("Step 5: Importing new MainWindow...")
    from src.ui.main_window_new import MainWindow as NewMainWindow
    log("New MainWindow import successful!")
    use_new_window = True
except Exception as e:
    log(f"WARNING in Step 5: {str(e)}")
    log(traceback.format_exc())
    use_new_window = False
    log("Will use original MainWindow implementation.")

# Step 6: Create a QApplication instance
try:
    log("Step 6: Creating QApplication...")
    app = QApplication(sys.argv)
    log("QApplication created successfully!")
except Exception as e:
    log(f"ERROR in Step 6: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 7: Create a MainWindow instance
try:
    log("Step 7: Creating MainWindow instance...")
    if use_new_window:
        log("Using new MainWindow implementation...")
        window = NewMainWindow()
    else:
        log("Using original MainWindow implementation...")
        window = OriginalMainWindow()
    log("MainWindow created successfully!")
except Exception as e:
    log(f"ERROR in Step 7: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)

# Step 8: Show the window and run the app
try:
    log("Step 8: Showing window and starting event loop...")
    window.show()
    log("Window displayed, entering event loop...")
    sys.exit(app.exec_())
except Exception as e:
    log(f"ERROR in Step 8: {str(e)}")
    log(traceback.format_exc())
    sys.exit(1)
