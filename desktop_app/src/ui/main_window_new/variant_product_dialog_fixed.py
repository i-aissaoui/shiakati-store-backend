"""
Fixed variant product dialog module with better dialog handling.
This module includes enhancements to fix persistent popup issues,
especially for products with no images like P7111001 and THM1101.
"""

import os
import re
import time
import traceback
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import socket
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QSpinBox, 
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QFileDialog, QInputDialog, QCheckBox, QProgressDialog,
    QScrollArea, QWidget, QGridLayout, QApplication, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer
from PyQt5.QtGui import QPixmap, QImage, QColor, QIntValidator

class VariantProductDialog(QDialog):
    """
    Dialog for creating or editing variant products.
    Contains special handling for problematic products (P7111001, THM1101)
    and improved dialog management to prevent UI hangs.
    """
    
    def __init__(self, parent, api_client, product_id=None):
        super().__init__(parent)
        self.api_client = api_client
        self.parent = parent
        self.variants = []
        self.image_paths = []
        self.product_id = product_id  # Store product_id for editing existing products
        self.server_images = []  # List of dicts: {"url": ..., "filename": ...}
        self.active_loading_dialogs = []  # Track all loading dialogs created
        self.problematic_products = ["P7111001", "THM1101"]  # Known problematic products
        self.dialog_closure_attempts = 0  # Track number of attempts to close dialogs
        self.last_image_refresh_time = 0  # Track when last image refresh happened
        self.setup_ui()
        
        # If we have a product ID, load that product's data and update UI elements for edit mode
        if self.product_id:
            # Update button text now that the UI is set up
            self.create_btn.setText("Update Product & Variants")
            self.load_product_data()
        
        # Apply network timeout patch to API client
        self.add_network_timeout_to_api_client()
    
    def add_network_timeout_to_api_client(self):
        """Add reasonable network timeouts to the API client if the methods exist."""
        # Check if method exists and is callable
        if hasattr(self.api_client, 'set_connect_timeout') and callable(getattr(self.api_client, 'set_connect_timeout')):
            self.api_client.set_connect_timeout(10)  # 10 seconds connect timeout
            
        if hasattr(self.api_client, 'set_read_timeout') and callable(getattr(self.api_client, 'set_read_timeout')):
            self.api_client.set_read_timeout(15)  # 15 seconds read timeout
    
    def setup_ui(self):
        """Set up the user interface."""
        # Implementation continues here, unchanged...
        # Replace this with your actual setup_ui code
        pass
    
    def delayed_image_refresh(self, barcode, timeout=10):
        """
        Refresh server images after a delay to ensure they're available.
        
        Args:
            barcode: The product barcode to fetch images for
            timeout: Timeout in seconds for API call
        """
        # Record the time of this refresh attempt
        self.last_image_refresh_time = int(time.time())
        
        # Skip entire loading process if barcode is None or empty
        if not barcode:
            print("No barcode provided to delayed_image_refresh, skipping")
            self.server_images = []
            self.update_image_preview()
            # Make sure any existing dialogs are closed
            self.ensure_loading_dialogs_closed()
            return
            
        # Special handling for known problematic products (P7111001, THM1101, etc.)
        # These products often have issues with empty image arrays
        is_problematic = (barcode in self.problematic_products or 
                         barcode.startswith("P711") or 
                         barcode.startswith("THM"))
                         
        if is_problematic:
            print(f"Special handling for known problematic product: {barcode}")
            # For these products, we'll be extra cautious and set a shorter timeout
            timeout = min(timeout, 3)  # Reduce timeout to 3 seconds max for these products
            
            # Schedule multiple cleanup attempts with increasing delays
            QTimer.singleShot(1000, lambda: self.ensure_loading_dialogs_closed())
            QTimer.singleShot(2000, lambda: self.ensure_loading_dialogs_closed())
            QTimer.singleShot(3000, lambda: self.ensure_loading_dialogs_closed())
        
        loading_label = None
        loading_msg = None
        
        try:
            print(f"Performing delayed refresh of product images for barcode {barcode}")
            
            # Start with clean server images
            self.server_images = []
            
            # First add network timeout to API client to prevent hanging
            self.add_network_timeout_to_api_client()
            
            # FIRST CHECK: Do a preliminary check to see if the product has ANY images at all
            # This prevents the dialog from showing up in the first place for products with no images
            try:
                print(f"Pre-checking if product {barcode} has any existing images...")
                check_images = self.api_client.get_product_images(barcode)
                
                # If there are no images, don't even show a loading dialog
                if not check_images or len(check_images) == 0:
                    print(f"Product {barcode} has NO images - skipping loading dialog completely")
                    self.server_images = []
                    self.update_image_preview()
                    self.ensure_loading_dialogs_closed()  # Extra safety check to close any existing dialogs
                    return
                else:
                    print(f"Product {barcode} has {len(check_images)} existing images")
            except Exception as pre_check_err:
                print(f"Error during image pre-check: {str(pre_check_err)}")
                # If pre-check fails, we'll proceed with the normal flow but be cautious
            
            # SECOND CHECK: Try a fast check for response timing
            try:
                # Start timer for tracking response time
                start_time = QElapsedTimer()
                start_time.start()
                
                # Make fast API call first to check if images exist
                images = self.api_client.get_product_images(barcode)
                
                # If response is fast and empty, don't show loading dialog at all
                if start_time.elapsed() < 300 and (not images or len(images) == 0):
                    print(f"Fast empty response ({start_time.elapsed()}ms), skipping loading dialog")
                    self.server_images = []
                    self.update_image_preview()
                    self.ensure_loading_dialogs_closed()
                    return
            except Exception:
                # If the fast check fails, we'll continue with the normal flow
                pass
            
            # Only create loading dialog for products if we know they have existing images
            # First, make sure any previous dialogs are closed
            self.ensure_loading_dialogs_closed()
            
            # Now create the new dialog with a unique identifier in the title
            # This will help us find and close it specifically if needed
            dialog_id = f"{barcode}-{int(time.time())}"
            loading_msg = QMessageBox(self)
            loading_msg.setWindowTitle(f"Refreshing Images ({dialog_id})")
            loading_msg.setText(f"Refreshing product images for {barcode}...")
            loading_msg.setStandardButtons(QMessageBox.NoButton)
            
            # Add dialog to tracking list before showing it
            if hasattr(self, 'active_loading_dialogs'):
                self.active_loading_dialogs.append(loading_msg)
            
            loading_msg.show()
            QApplication.processEvents()  # Ensure UI updates
            
            # Create a loading indicator in the image grid as well
            loading_label = QLabel(f"Refreshing product images for {barcode}...")
            loading_label.setAlignment(Qt.AlignCenter)
            loading_label.setStyleSheet("""
                background-color: #e8f5e9; 
                color: #2e7d32; 
                padding: 10px; 
                border-radius: 5px;
                border: 1px solid #c8e6c9;
                font-weight: bold;
            """)
            
            # Add the loading label to the UI if images_grid exists
            if hasattr(self, 'images_grid'):
                self.images_grid.addWidget(loading_label, 0, 0, 1, 4)
                QApplication.processEvents()  # Ensure UI updates
            else:
                print("Warning: images_grid not found, cannot display loading indicator")
                
            # Set a safety timer to automatically close the dialog after 5 seconds
            # This ensures it never gets stuck, even if there's an error in the code below
            QTimer.singleShot(5000, lambda: self.ensure_loading_dialogs_closed())
            
            # Start a timer for timeout handling
            start_time = QElapsedTimer()
            start_time.start()
            
            # Get images with timeout handling
            images = None
            error_occurred = False
            
            # Try to get images from API with explicit timeout
            try:
                # Make API call
                images = self.api_client.get_product_images(barcode)
                
                # Check if we've exceeded our own timeout (separate from API timeout)
                if start_time.elapsed() > timeout * 1000:  # Convert to milliseconds
                    print(f"Image refresh operation timed out after {timeout} seconds")
                    error_occurred = True
            except Exception as timeout_err:
                print(f"Error or timeout in image refresh: {str(timeout_err)}")
                import traceback
                traceback.print_exc()
                error_occurred = True
            
            # Process returned images (even if None or empty)
            print(f"Received {len(images) if images else 0} images from server after upload")
            
            # Reset server images
            self.server_images = []
            
            # Process images if they exist
            if images:
                for img in images:
                    if isinstance(img, dict) and "url" in img:
                        # Make sure we have a filename
                        if "filename" not in img:
                            img["filename"] = os.path.basename(img["url"])
                        self.server_images.append(img)
                    elif img is not None:  # Skip None values
                        try:
                            # If only URL as string, convert to proper format
                            img_url = str(img)
                            fname = os.path.basename(img_url)
                            self.server_images.append({"url": img_url, "filename": fname})
                        except Exception as e:
                            print(f"Error processing image data: {str(e)}")
            else:
                # Handle case where images is None or empty
                print("No images found or images is None, updating preview with empty list")
                
                # For empty responses, make sure to close any loading dialogs immediately
                # This is especially important for products that have no images yet like THM1101
                self.ensure_loading_dialogs_closed()
                
                # For better UX, add a 'No images' label to the image grid
                if hasattr(self, 'images_grid'):
                    try:
                        no_images_label = QLabel(f"No images available for {barcode}")
                        no_images_label.setAlignment(Qt.AlignCenter)
                        no_images_label.setStyleSheet("""
                            background-color: #f5f5f5; 
                            color: #757575; 
                            padding: 15px; 
                            border-radius: 5px;
                            font-style: italic;
                        """)
                        self.images_grid.addWidget(no_images_label, 0, 0, 1, 4)
                        QApplication.processEvents()
                        
                        # Auto-remove after 5 seconds to clean up UI
                        QTimer.singleShot(5000, no_images_label.deleteLater)
                    except Exception as label_err:
                        print(f"Error adding 'No images' label: {str(label_err)}")
            
            # Show error if needed (after processing images, before updating UI)
            if error_occurred:
                # Show error message to user (if images_grid exists)
                if hasattr(self, 'images_grid'):
                    error_label = QLabel("Error loading images. Please try again.")
                    error_label.setStyleSheet("color: red; font-weight: bold;")
                    self.images_grid.addWidget(error_label, 0, 0, 1, 4)
                    QApplication.processEvents()
                    # Automatically remove after 3 seconds
                    QTimer.singleShot(3000, error_label.deleteLater)
            
            # Update the preview with the fresh server images
            self.update_image_preview()
            print(f"Image preview updated with {len(self.server_images)} server images")
        except Exception as e:
            print(f"Error in delayed image refresh: {str(e)}")
            import traceback
            traceback.print_exc()
            # Update UI anyway to avoid hanging
            self.server_images = []  # Ensure we have empty list in case of error
            self.update_image_preview()
        finally:
            # Clean up UI elements regardless of outcome
            print("Cleaning up loading UI elements in delayed_image_refresh")
            
            try:
                # First try targeted cleanup of our specific widgets
                # Close loading message dialog with robust checks
                if loading_msg:
                    try:
                        if hasattr(loading_msg, 'reject') and callable(loading_msg.reject):
                            loading_msg.reject()  # Force rejection first
                        
                        if hasattr(loading_msg, 'isVisible') and callable(loading_msg.isVisible) and loading_msg.isVisible():
                            loading_msg.close()
                            
                        if hasattr(loading_msg, 'deleteLater') and callable(loading_msg.deleteLater):
                            loading_msg.deleteLater()
                            
                        QApplication.processEvents()
                    except Exception as msg_err:
                        print(f"Error closing specific loading message: {str(msg_err)}")
                
                # Remove loading label with robust checks
                if loading_label:
                    try:
                        if hasattr(loading_label, 'hide') and callable(loading_label.hide):
                            loading_label.hide()
                            
                        if hasattr(loading_label, 'parent') and loading_label.parent():
                            loading_label.setParent(None)
                            
                        if hasattr(loading_label, 'deleteLater') and callable(loading_label.deleteLater):
                            loading_label.deleteLater()
                            
                        QApplication.processEvents()
                    except Exception as label_err:
                        print(f"Error cleaning up specific loading label: {str(label_err)}")
                
                # Finally, use our aggressive cleanup method to catch ANY remaining dialogs
                # This ensures nothing gets left behind even if specific cleanup fails
                self.ensure_loading_dialogs_closed()
                
            except Exception as cleanup_err:
                print(f"Error in delayed_image_refresh cleanup: {str(cleanup_err)}")
                
                # Last resort - still try to call ensure_loading_dialogs_closed
                try:
                    self.ensure_loading_dialogs_closed()
                except:
                    pass
    
    def update_image_preview(self, include_local=False):
        """
        Update the image preview area using self.images_grid.
        
        Args:
            include_local: If True, include locally added images too (not just server images)
        """
        # Check if the dialog is still valid (not being destroyed)
        if not hasattr(self, 'images_grid') or self.images_grid is None:
            print("update_image_preview: images_grid not available, likely widget is being destroyed")
            return
            
        # Safety check for C++ object deleted situations
        try:
            # Check if the layout is still valid by trying to access count()
            # This will raise RuntimeError if layout has been deleted
            count = self.images_grid.count()
        except RuntimeError as e:
            if "C/C++ object" in str(e) and "deleted" in str(e):
                print("update_image_preview: images_grid has been deleted, skipping update")
                return
            # If it's a different RuntimeError, re-raise it
            raise

        # ------------------------
        # Clear the grid layout of all widgets
        # ------------------------
        # First, save reference to widgets that need cleanup
        widgets_to_remove = []
        for i in range(self.images_grid.count()):
            item = self.images_grid.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())
        
        # Then clear the grid by removing all widgets
        for widget in widgets_to_remove:
            try:
                self.images_grid.removeWidget(widget)
                # Don't delete the widgets immediately as this can cause crashes
                # during layout updates. Just schedule deletion.
                widget.setParent(None)  # Detach from parent
                widget.deleteLater()    # Schedule for deletion
            except Exception as e:
                print(f"Error removing widget from grid: {str(e)}")
        
        # Reset our tracking list and ensure no references to deleted widgets remain
        self.image_widgets_preview = []
        
        # ------------------------
        # Always recreate the "No images" message label to avoid C++ deleted object issues
        # ------------------------
        # Create a fresh "no images" label every time to avoid keeping references to deleted widgets
        self.no_images_label_preview = QLabel("No images available for this product.")
        self.no_images_label_preview.setAlignment(Qt.AlignCenter)
        self.no_images_label_preview.setStyleSheet("font-style: italic; color: #555; padding: 20px;")

        # ------------------------
        # Determine which images to display
        # ------------------------
        all_images = []
        
        # Track if we're showing server images that might be loading
        is_loading_server_images = False
        
        # Safely check and add server images
        if hasattr(self, 'server_images') and isinstance(self.server_images, list):
            all_images.extend(self.server_images)
            if self.server_images:
                is_loading_server_images = True
            
        # Add local images if requested and they exist
        if include_local and hasattr(self, 'local_images') and isinstance(self.local_images, list):
            all_images.extend(self.local_images)
            
        # ------------------------
        # Display images or "No images" message
        # ------------------------
        try:
            if not all_images:
                print("update_image_preview: No images to display.")
                # Add the 'no images' label to the grid
                self.images_grid.addWidget(self.no_images_label_preview, 0, 0, 1, 4)  # span 4 columns
                self.no_images_label_preview.setVisible(True)
                self.image_widgets_preview.append(self.no_images_label_preview)
            else:
                print(f"update_image_preview: Displaying {len(all_images)} images.")
                
                # Add loading indicator at the top if we have server images
                if is_loading_server_images:
                    try:
                        loading_indicator = QLabel("Loading server images... Please wait")
                        loading_indicator.setAlignment(Qt.AlignCenter)
                        loading_indicator.setStyleSheet("""
                            background-color: #fff3cd; 
                            color: #856404; 
                            font-weight: bold; 
                            padding: 5px; 
                            border: 1px solid #ffeeba;
                            border-radius: 4px;
                        """)
                        self.images_grid.addWidget(loading_indicator, 0, 0, 1, 4)  # span 4 columns
                        self.image_widgets_preview.append(loading_indicator)
                        row_offset = 1  # Start images from next row
                    except Exception as e:
                        print(f"Error adding loading indicator: {str(e)}")
                        row_offset = 0  # No loading indicator, start from row 0
                else:
                    row_offset = 0  # No loading indicator, start from row 0
                
                images_per_row = 4
                row, col = row_offset, 0
                
                for img_data in all_images:
                    if not isinstance(img_data, dict):
                        print(f"Skipping invalid image data: {img_data}")
                        continue
                        
                    url = img_data.get("url", "")
                    filename = img_data.get("filename", "image.png")
                    is_local = "local_path" in img_data  # Flag for local images
                    
                    if not url:
                        print(f"Skipping image with no URL: {filename}")
                        continue
                    
                    try:
                        # Create a container widget to hold both the image and delete button
                        container = QWidget()
                        container_layout = QVBoxLayout(container)
                        container_layout.setContentsMargins(4, 4, 4, 4)
                        container_layout.setSpacing(2)
                        
                        # Create label with image or filename
                        temp_label = QLabel()
                        
                        if is_local:
                            # For local images, try to load from filesystem with QPixmap
                            local_path = img_data.get("local_path")
                            if os.path.exists(local_path):
                                pixmap = QPixmap(local_path)
                                if not pixmap.isNull():
                                    pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                    temp_label.setPixmap(pixmap)
                                else:
                                    # Fallback if image can't be loaded
                                    temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Local file: {local_path}")
                            else:
                                temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Local file not found: {local_path}")
                        else:
                            # For server images, try to load but with fallback to display text
                            try:
                                # Properly handle URLs
                                if url.startswith(("http://", "https://", "file://")):
                                    server_path = url
                                else:
                                    # Try to construct a valid URL from relative path
                                    api_base_url = getattr(self.api_client, 'base_url', 'http://127.0.0.1:8000').rstrip('/')
                                    if url.startswith('/'):
                                        server_path = f"{api_base_url}{url}"
                                    else:
                                        server_path = f"{api_base_url}/{url}"
                                
                                # Show filename as text while we wait
                                temp_label.setText(f"Loading {filename[:10]}...")
                                temp_label.setAlignment(Qt.AlignCenter)
                                
                                # Try to load the image from the server (in a production app, this would be asynchronous)
                                if self.check_network_status():
                                    # For a full implementation, we would load images asynchronously
                                    # But for now, we'll just show the filename
                                    temp_label.setText(f"{filename[:15]}...")
                                    temp_label.setToolTip(f"Server image: {server_path}")
                                else:
                                    # Network is not available
                                    temp_label.setText("Network Error")
                                    temp_label.setToolTip(f"Cannot access server image: {server_path}")
                                    temp_label.setStyleSheet(temp_label.styleSheet() + "border-color: #e74c3c;")
                            except Exception as url_error:
                                print(f"Error processing server image URL '{url}': {str(url_error)}")
                                temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Error loading image: {str(url_error)}")
                        
                        # Style the label
                        temp_label.setFixedSize(90, 90)
                        temp_label.setAlignment(Qt.AlignCenter)
                        border_color = "#4CAF50" if is_local else "#cccccc"  # Green for local, gray for server
                        bg_color = "#e8f5e9" if is_local else "#f0f0f0"      # Light green for local
                        temp_label.setStyleSheet(f"""
                            border: 2px solid {border_color}; 
                            background-color: {bg_color}; 
                            margin: 2px; 
                            font-size: 9px;
                            border-radius: 3px;
                            padding: 2px;
                        """)
                        
                        # Add the image label to the container
                        container_layout.addWidget(temp_label)
                        
                        # Add a delete button
                        delete_btn = QPushButton("Remove")
                        delete_btn.setFixedHeight(20)
                        delete_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #f44336;
                                color: white;
                                border: none;
                                border-radius: 2px;
                                font-size: 8px;
                                padding: 2px;
                            }
                            QPushButton:hover {
                                background-color: #d32f2f;
                            }
                        """)
                        
                        # Capture image data for the delete function
                        delete_btn.image_data = img_data
                        delete_btn.is_local = is_local
                        
                        # Connect delete button to appropriate function
                        if is_local:
                            delete_btn.clicked.connect(lambda checked, data=img_data: self.remove_local_image(data))
                        else:
                            delete_btn.clicked.connect(lambda checked, data=img_data: self.remove_server_image(data))
                            
                        container_layout.addWidget(delete_btn)
                        
                        # Add the container to the grid
                        self.images_grid.addWidget(container, row, col)
                        self.image_widgets_preview.append(container)
                        
                        # Move to next grid position
                        col += 1
                        if col >= images_per_row:
                            col = 0
                            row += 1
                    except Exception as e:
                        print(f"Error displaying image {filename}: {str(e)}")
                
            # ------------------------
            # Update scroll area view if needed
            # ------------------------
            try:
                if hasattr(self, 'images_content') and self.images_content:
                    self.images_content.adjustSize()
                elif hasattr(self, 'images_scroll') and self.images_scroll and hasattr(self.images_scroll, 'widget') and callable(self.images_scroll.widget):
                    scroll_widget = self.images_scroll.widget()
                    if scroll_widget:
                        scroll_widget.adjustSize()
            except Exception as e:
                print(f"Error adjusting scroll area: {str(e)}")
                
        except Exception as e:
            print(f"Error updating image preview: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # In case of error, try to show the "No images" message as a fallback
            try:
                # Clear any existing widgets first
                for i in reversed(range(self.images_grid.count())):
                    widget = self.images_grid.itemAt(i).widget()
                    if widget:
                        self.images_grid.removeWidget(widget)
                        widget.setParent(None)
                        widget.deleteLater()
                
                error_label = QLabel("Error loading images")
                error_label.setStyleSheet("color: red; font-weight: bold;")
                self.images_grid.addWidget(error_label, 0, 0)
                self.image_widgets_preview = [error_label]
            except Exception:
                # If even this fails, just log it and continue
                print("Critical error in image preview update - could not show error message")
                
    def check_network_status(self):
        """Check if network is available."""
        # Simple implementation - in production, implement a real check
        return True
    
    def ensure_loading_dialogs_closed(self):
        """
        Safety method to ensure all loading dialogs are closed.
        This is a fail-safe to prevent hanging dialogs, especially when there are no images
        or when operations fail with exceptions.
        
        This method is EXTREMELY aggressive in finding and closing dialogs to prevent UI hangs.
        It will find and close ALL dialogs related to loading, refreshing, or product images.
        """
        try:
            # Increment the closure attempt counter
            self.dialog_closure_attempts += 1
            print(f"EMERGENCY: Forcing closure of loading dialogs (attempt #{self.dialog_closure_attempts})")
            
            # First, ensure no events are pending that might interfere
            QApplication.processEvents()
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()  # Double process to catch everything
            
            # First, check our tracked dialog list for direct cleanup
            if hasattr(self, 'active_loading_dialogs') and self.active_loading_dialogs:
                print(f"Found {len(self.active_loading_dialogs)} tracked loading dialogs to close")
                for dialog in self.active_loading_dialogs[:]:  # Use a copy of the list to safely modify during iteration
                    try:
                        # Check if the dialog is still valid (not deleted)
                        if dialog and hasattr(dialog, 'isVisible'):
                            if dialog.isVisible():
                                print(f"Closing tracked dialog: {dialog.windowTitle() if hasattr(dialog, 'windowTitle') else 'unknown'}")
                                
                                # Try all closure methods
                                for close_method in ['reject', 'done', 'close', 'hide']:
                                    try:
                                        if hasattr(dialog, close_method) and callable(getattr(dialog, close_method)):
                                            if close_method == 'done':
                                                getattr(dialog, close_method)(0)  # done(0) for rejection
                                            else:
                                                getattr(dialog, close_method)()
                                    except Exception:
                                        pass
                                
                                # Schedule deletion
                                try:
                                    dialog.deleteLater()
                                except Exception:
                                    pass
                                
                                QApplication.processEvents()  # Process events after each closure
                    except Exception:
                        pass
                
                # Clear the list completely after attempting to close all dialogs
                self.active_loading_dialogs = []
            
            # Multiple attempts loop to ensure we catch everything
            # Sometimes one pass isn't enough due to event loop timing
            for attempt in range(4):  # Increased to 4 attempts for more reliability
                # AGGRESSIVELY find and close any QMessageBox or QDialog with loading-related text
                closed_count = 0
                for widget in QApplication.topLevelWidgets():
                    try:
                        # Check for QMessageBox dialogs
                        if isinstance(widget, QMessageBox):
                            # Try to get title and text with robust error handling
                            title = ""
                            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                                title = widget.windowTitle()
                                
                            text = ""
                            if hasattr(widget, 'text') and callable(widget.text):
                                text = widget.text()
                            
                            # ULTRA aggressive checks - even more conditions to match ANY loading dialog
                            # Include P7111001 as a specific match since that's giving us trouble
                            if (('loading' in title.lower() or 'loading' in text.lower()) or
                                ('refresh' in title.lower() or 'refresh' in text.lower()) or
                                ('image' in title.lower() or 'image' in text.lower()) or
                                ('p7111' in title.lower() or 'p7111' in text.lower()) or
                                ('thm' in title.lower() or 'thm' in text.lower()) or
                                ('uploading' in title.lower() or 'uploading' in text.lower()) or
                                ('processing' in title.lower() or 'processing' in text.lower())):
                                
                                print(f"FORCE CLOSING QMessageBox: {title} ({text})")
                                
                                # Try all possible ways to close this widget
                                for close_method in ['reject', 'done', 'close', 'hide']:
                                    try:
                                        if hasattr(widget, close_method) and callable(getattr(widget, close_method)):
                                            if close_method == 'done':
                                                getattr(widget, close_method)(0)  # done(0) for rejection
                                            else:
                                                getattr(widget, close_method)()
                                    except Exception:
                                        pass
                                
                                try:
                                    widget.deleteLater()  # Always try to schedule deletion
                                except Exception:
                                    pass
                                    
                                closed_count += 1
                                QApplication.processEvents()  # Process each close immediately
                        
                        # Also check for QDialog instances with loading-related titles
                        elif isinstance(widget, QDialog):
                            title = ""
                            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                                title = widget.windowTitle()
                                
                            # Check for ANY dialog that might be related to loading or images
                            if ('Loading' in title or 'Refreshing' in title or 'Images' in title or
                                'Processing' in title or 'Upload' in title or 'Product' in title):
                                print(f"FORCE CLOSING QDialog: {title}")
                                
                                # Try all possible ways to close this widget
                                for close_method in ['reject', 'done', 'close', 'hide']:
                                    try:
                                        if hasattr(widget, close_method) and callable(getattr(widget, close_method)):
                                            if close_method == 'done':
                                                getattr(widget, close_method)(0)  # done(0) for rejection
                                            else:
                                                getattr(widget, close_method)()
                                    except Exception:
                                        pass
                                
                                try:
                                    widget.deleteLater()  # Always try to schedule deletion
                                except Exception:
                                    pass
                                    
                                closed_count += 1
                                QApplication.processEvents()  # Process each close immediately
                    except Exception as widget_err:
                        print(f"Error processing widget during cleanup: {str(widget_err)}")
                
                # If nothing was closed in this attempt, no need for more attempts
                if closed_count == 0 and attempt > 0:
                    break
                    
                # Process events between attempts
                QApplication.processEvents()
            
            # Aggressively clean the images grid - find ANYTHING with loading text
            if hasattr(self, 'images_grid') and self.images_grid:
                # Safety check for C++ object deleted situations
                try:
                    # Check if the layout is still valid by trying to access count()
                    # This will raise RuntimeError if layout has been deleted
                    grid_count = self.images_grid.count()
                except RuntimeError as e:
                    print(f"Warning: images_grid has been deleted or is invalid: {str(e)}")
                    # Skip all grid operations
                    grid_count = 0
                
                # Only proceed if grid is still valid
                if grid_count > 0:
                    # First pass: remove any labels with loading text
                    try:
                        for i in range(grid_count):
                            try:
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widget = item.widget()
                                    
                                    # Check for loading indicators in QLabels
                                    if isinstance(widget, QLabel):
                                        try:
                                            label_text = widget.text().lower()
                                            if ('loading' in label_text or 'refreshing' in label_text or 
                                                'product image' in label_text):
                                                print(f"Removing grid widget: {widget.text()}")
                                                widget.setParent(None)
                                                widget.deleteLater()
                                                QApplication.processEvents()
                                        except Exception:
                                            # If we can't get text, try to remove it anyway
                                            widget.setParent(None)
                                            widget.deleteLater()
                                            QApplication.processEvents()
                            except Exception as item_err:
                                print(f"Error cleaning grid item: {str(item_err)}")
                    except Exception as e:
                        print(f"Error in first grid cleaning pass: {str(e)}")
                    
                    # Second pass: complete clearance if needed - prepare list first
                    try:
                        # Verify layout is still valid before second pass
                        try:
                            current_count = self.images_grid.count()
                        except RuntimeError:
                            print("Grid layout was deleted during cleanup, skipping second pass")
                            current_count = 0
                            
                        if current_count > 0:
                            # Get all widgets to be removed
                            widgets_to_remove = []
                            for i in range(current_count):
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widgets_to_remove.append(item.widget())
                            
                            # Now actually remove them
                            for widget in widgets_to_remove:
                                try:
                                    self.images_grid.removeWidget(widget)
                                    widget.setParent(None)
                                    widget.deleteLater()
                                    QApplication.processEvents()
                                except Exception:
                                    # If we can't remove it one way, try other ways
                                    try:
                                        widget.hide()
                                    except Exception:
                                        pass
                    except Exception as grid_err:
                        print(f"Error in complete grid cleaning: {str(grid_err)}")
            
            # Update image preview to refresh the UI state
            try:
                self.update_image_preview()
            except Exception as update_err:
                print(f"Error updating image preview after cleanup: {str(update_err)}")
            
            # Force process all events to update UI - multiple passes for reliability
            QApplication.processEvents()
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()
            
        except Exception as e:
            print(f"Error in ensure_loading_dialogs_closed: {str(e)}")

    # Rest of methods like refresh_server_images, remove_server_image, etc. go here...
    # They remain unchanged from your original implementation
