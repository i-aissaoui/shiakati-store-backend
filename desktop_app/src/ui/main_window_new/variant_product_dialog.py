"""
Product variant dialog for multi-variant product creation.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDialogButtonBox, QHeaderView, QWidget,
    QFileDialog, QToolButton, QTabWidget, QScrollArea, QListWidget, QListWidgetItem,
    QCheckBox, QGroupBox, QGridLayout, QRadioButton, QSizePolicy, QFrame, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer, QSize, QEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont, QImage
import os
import traceback
import time
import sip
import sip

# Custom event to handle QPixmap updates from threads
class QPixmapEvent(QEvent):
    """Custom event for updating pixmaps from threads."""
    # Define a custom event type
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, label, pixmap):
        """Initialize with label to update and pixmap to set."""
        super().__init__(QPixmapEvent.EVENT_TYPE)
        self.label = label  # The QLabel to update
        self.pixmap = pixmap  # The QPixmap to set

class VariantProductDialog(QDialog):
    def event(self, event):
        # Handle custom QPixmapEvent for updating pixmaps from threads
        if event.type() == QPixmapEvent.EVENT_TYPE:
            try:
                if hasattr(event, 'label') and not sip.isdeleted(event.label) and hasattr(event, 'pixmap'):
                    event.label.setPixmap(event.pixmap)
                    return True
            except Exception as e:
                print(f"Error handling QPixmapEvent: {e}")
        return super().event(event)
        
    """Dialog for creating products with multiple variants."""
    
    def __init__(self, parent, api_client, product_id=None):
        super().__init__(parent)
        self.api_client = api_client
        self.parent = parent
        self.variants = []
        self.image_paths = []
        self.product_id = product_id  # Store product_id for editing existing products
        self.server_images = []  # List of dicts: {"url": ..., "filename": ...}
        self.local_images = []   # List of local images: {"url":..., "filename":..., "local_path":...}
        self._last_local_images = []  # Persistent backup of local images to prevent loss during refresh
        self.deleted_images = [] # Track deleted images for backend sync
        self.active_loading_dialogs = []  # Track all loading dialogs created
        self.problematic_products = ["P7111001", "THM1101"]  # Known problematic products
        self.dialog_closure_attempts = 0  # Track number of attempts to close dialogs
        self.last_image_refresh_time = 0  # Track when last image refresh happened
        
        # Add persistent references to prevent garbage collection
        self._pixmaps = []  # Keep persistent references to pixmaps
        self._images = []   # Keep persistent references to QImages
        self._delete_buttons = []  # Keep persistent references to delete buttons
        self._image_labels = []  # Keep persistent references to image labels
        
        self.setup_ui()
        
        # If we have a product ID, load that product's data and update UI elements for edit mode
        if self.product_id:
            # Update button text now that the UI is set up
            self.create_btn.setText("Update Product & Variants")
            self.load_product_data()
        
        # Apply network timeout patch to API client
        self.add_network_timeout_to_api_client()
        
    def setup_ui(self):
        """Set up the user interface for the dialog."""
        title = "Edit Product with Variants" if self.product_id else "Create Product with Variants"
        self.setWindowTitle(title)
        self.setMinimumWidth(1200)  # Increased width from 880 to 1200 for wider table
        self.setMinimumHeight(750)  # Increased height from 650 to 750 for longer table
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full-width header
        main_layout.setSpacing(15)
        
        # Title header removed to save space
        main_layout.addSpacing(1)
        
        # Create a horizontal layout to split into two columns
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)
        
        # Create left and right columns
        left_column = QVBoxLayout()
        left_column.setSpacing(15)  # Increased spacing between sections
        
        right_column = QVBoxLayout()
        right_column.setSpacing(15)  # Increased spacing between sections
        
        # === Basic Product Information ===
        product_group = QGroupBox("Product Information")
        product_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 15px; }")
        product_layout = QFormLayout()
        product_layout.setLabelAlignment(Qt.AlignRight)
        product_layout.setSpacing(8)  # Increased spacing between form rows
        product_layout.setContentsMargins(10, 10, 10, 10)  # Increased margins
        
        # Product name field with compact input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setMinimumHeight(30)  # Increased height
        self.name_input.setStyleSheet("font-size: 12px; padding: 5px 8px; margin-bottom: 3px;")  # Added margin
        product_layout.addRow("<b>Product Name:</b>", self.name_input)
        
        # Barcode prefix
        self.barcode_prefix = QLineEdit()
        self.barcode_prefix.setPlaceholderText("Optional (SHIRT, PANT, etc.)")
        self.barcode_prefix.setMinimumHeight(30)  # Increased height
        self.barcode_prefix.setStyleSheet("font-size: 12px; padding: 5px 8px; margin-bottom: 3px;")  # Added margin
        self.barcode_prefix_btn = QPushButton("Generate Unique")
        self.barcode_prefix_btn.setMinimumHeight(30)  # Increased height
        self.barcode_prefix_btn.setStyleSheet("padding: 5px 8px; margin-bottom: 3px;")  # Added margin
        self.barcode_prefix_btn.clicked.connect(self.generate_unique_prefix)
        
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(self.barcode_prefix)
        prefix_layout.addWidget(self.barcode_prefix_btn)
        product_layout.addRow("<b>Barcode Prefix:</b>", prefix_layout)
        
        # Description field
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter product description (optional)")
        self.description_input.setMinimumHeight(30)  # Increased height
        self.description_input.setStyleSheet("font-size: 12px; padding: 5px 8px; margin-bottom: 3px;")  # Added margin
        product_layout.addRow("<b>Description:</b>", self.description_input)
        
        # Category dropdown with compact styling
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(30)  # Increased height
        self.category_combo.setStyleSheet("font-size: 12px; padding: 5px 8px; margin-bottom: 3px;")  # Added margin
        
        # Populate with categories
        try:
            categories = self.api_client.get_categories()
            for cat in categories:
                if isinstance(cat, dict):
                    self.category_combo.addItem(cat["name"])
        except Exception as e:
            print(f"Failed to load categories: {str(e)}")
            
        product_layout.addRow("<b>Category:</b>", self.category_combo)
        
        product_group.setLayout(product_layout)
        left_column.addWidget(product_group)
         # === Variant Options (Single Variant Entry) ===
        variant_group = QGroupBox("Variant Options")
        variant_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 12px; 
                padding-top: 10px;
                border: 1px solid #c0d0e0;
                border-radius: 4px;
                margin-top: 2px;
                background-color: #fafbfc;
            }
        """)
        variant_group.setMinimumHeight(260)  # Reduced height to make it compact
        variant_layout = QVBoxLayout()
        variant_layout.setSpacing(8)  # Increased spacing between elements
        variant_layout.setContentsMargins(10, 10, 10, 10)  # Increased margins
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(8)  # Increased space between form elements
        form_layout.setContentsMargins(10, 10, 10, 10)  # Increased padding
        form_layout.setVerticalSpacing(8)  # Increased vertical spacing
        
        # Remove heading to save space

        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Enter size (example: S, M, L, XL, 40, 42)")
        self.size_input.setMinimumHeight(30)  # Increased height
        self.size_input.setStyleSheet("""
            font-size: 12px; 
            padding: 5px 8px; 
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: #ffffff;
            margin-bottom: 3px;
        """)
        form_layout.addRow("<b>Size:</b>", self.size_input)

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Enter color (example: Red, Blue, Black)")
        self.color_input.setMinimumHeight(30)  # Increased height
        self.color_input.setStyleSheet("""
            font-size: 12px; 
            padding: 5px 8px; 
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: #ffffff;
            margin-bottom: 3px;
        """)
        form_layout.addRow("<b>Color:</b>", self.color_input)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(9999)
        self.quantity_input.setDecimals(1)
        self.quantity_input.setValue(0.0)  # Start with zero
        self.quantity_input.setMinimumHeight(30)  # Increased height
        self.quantity_input.setStyleSheet("""
            font-size: 12px; 
            padding: 5px 8px; 
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: #f8f9fa;
            margin-bottom: 3px;
        """)
        form_layout.addRow("<b>Quantity:</b>", self.quantity_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999)
        self.price_input.setDecimals(2)
        self.price_input.setValue(0.00)  # Start with zero
        self.price_input.setSuffix(" DZD")
        self.price_input.setMinimumHeight(30)  # Increased height
        self.price_input.setStyleSheet("""
            font-size: 12px; 
            padding: 5px 8px; 
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: #f8f9fa;
            margin-bottom: 3px;
        """)
        form_layout.addRow("<b>Price:</b>", self.price_input)
        
        # Add the form to the variant layout with minimal spacing
        variant_layout.addLayout(form_layout)
        variant_layout.addSpacing(8)  # Spacing after form

        # Generate Variants Button
        self.generate_variants_btn = QPushButton("🔄 Generate Variants")
        self.generate_variants_btn.setMinimumHeight(35)
        self.generate_variants_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.generate_variants_btn.clicked.connect(self.generate_variants)
        variant_layout.addWidget(self.generate_variants_btn)
        
        variant_layout.addSpacing(5)  # Minimal spacing after button
        variant_layout.addStretch(1)  # Add stretch at the bottom to push content up
        
        variant_group.setLayout(variant_layout)
        # Ensure variant section takes proper space in the layout
        variant_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        left_column.addWidget(variant_group)
        
        # === Variants Preview ===
        variants_group = QGroupBox("Variants Preview")
        variants_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 15px; 
                padding-top: 12px;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)
        variants_layout = QVBoxLayout()
        variants_layout.setSpacing(10)  # Reduced spacing from 18 to 10
        variants_layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins from 20,25,20,20 to 15,15,15,15
        
        # Add variant count label with enhanced styling
        self.variant_count_label = QLabel("No variants added yet. Use 'Generate Variants' to create multiple variants.")
        self.variant_count_label.setStyleSheet("""
            font-weight: bold; 
            color: #e74c3c; 
            font-size: 14px;
            padding: 10px;
            background-color: #fdf2f0;
            border-radius: 6px;
            border: 1px solid #fadbd8;
            margin-bottom: 5px;
        """)
        self.variant_count_label.setAlignment(Qt.AlignCenter)
        self.variant_count_label.setMinimumHeight(60)  # Increased height
        self.variant_count_label.setWordWrap(True)  # Enable word wrap for better display
        variants_layout.addWidget(self.variant_count_label)
        
        # Better table with enhanced styling
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(6)  # Added column for delete button
        self.variants_table.setMinimumHeight(400)  # Increased height from 250 to 400 for longer table
        self.variants_table.setHorizontalHeaderLabels(
            ["Size", "Color", "Barcode", "Price", "Stock (Editable)", "Actions"]
        )
        
        # Set wider column widths to utilize the increased window width
        self.variants_table.setColumnWidth(0, 120)  # Size column (increased from 100)
        self.variants_table.setColumnWidth(1, 140)  # Color column (increased from 120)
        self.variants_table.setColumnWidth(2, 200)  # Barcode column (increased from 150)
        self.variants_table.setColumnWidth(3, 120)  # Price column (increased from 100)
        self.variants_table.setColumnWidth(4, 150)  # Stock column (increased from 120)
        self.variants_table.setColumnWidth(5, 100)  # Actions column (increased from 80)
        
        # Increase row height for better visibility
        self.variants_table.verticalHeader().setDefaultSectionSize(65)
        
        # Enhanced table styling with improved visuals and higher rows
        self.variants_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                font-size: 15px;
                alternate-background-color: #f8f9fa;
                gridline-color: #e6e6e6;
            }
            QTableWidget::item {
                padding: 16px 8px;  /* Increased vertical padding for taller rows */
                border-bottom: 1px solid #f1f2f6;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 14px 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:last {
                background-color: #2980b9;  /* Darker blue for Stock column header */
            }
        """)
        
        # Set alternating row colors
        self.variants_table.setAlternatingRowColors(True)
        
        # Make the horizontal header more visible
        header = self.variants_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        variants_layout.addWidget(self.variants_table)
        
        # Add a spacing widget after the table with increased height
        spacer = QWidget()
        spacer.setMinimumHeight(20)  # Increased height
        variants_layout.addWidget(spacer)
        
        # Add spacer after the table for better positioning of stock controls
        variants_layout.addSpacing(20)  # Increased spacing
        
        # Add stock management controls with better styling
        stock_controls_layout = QVBoxLayout()  # Changed to vertical layout
        stock_controls_layout.setSpacing(15)  # Increased spacing
        
        # Add spacer for proper bottom padding
        stock_controls_layout.addSpacing(10)
        stock_controls_layout.addStretch()
        
        variants_layout.addLayout(stock_controls_layout)
        variants_group.setLayout(variants_layout)
        right_column.addWidget(variants_group)
        
        # Add columns to content layout
        content_layout.addLayout(left_column, 1) # 40% width
        content_layout.addLayout(right_column, 2) # 60% width
        
        # Add the content layout to the main layout
        main_layout.addLayout(content_layout)
        
        # Setup additional UI enhancements
        self.setupInputFocusHighlights()
        
        # === Action Buttons ===
        # Add a separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        separator.setStyleSheet("background-color: #ddd;")
        main_layout.addWidget(separator)
        
        # Button container with enhanced styling - full width
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #f5f7fa; border-top: 1px solid #e5e8ec; padding: 5px;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(50)  # Increased height
        self.cancel_btn.setMinimumWidth(160)  # Increased width
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Create button will be dynamically renamed after setup_ui() if in edit mode
        self.create_btn = QPushButton("Create Product & Variants")
        self.create_btn.setMinimumHeight(50)  # Increased height
        self.create_btn.setMinimumWidth(280)  # Increased width
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.create_btn.clicked.connect(self.create_product)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.create_btn)
        
        main_layout.addWidget(button_container)
    
    def add_image(self):
        """Add a product image to the collection."""
        file_dialog = QFileDialog()
        # Make the file dialog larger for better visibility
        file_dialog.setMinimumWidth(800)
        file_dialog.setMinimumHeight(600)
        file_dialog.setWindowTitle("Select High-Quality Product Image")
        # Set view mode to detail for better information display
        file_dialog.setViewMode(QFileDialog.Detail)
        # Allow selection of multiple images if needed in the future
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Product Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.webp)"  # Added webp support
        )
        
        if file_path:
            # Create image storage directory if it doesn't exist
            # Use a more robust folder structure with product-specific subdirectories
            base_image_dir = os.path.join(os.path.expanduser("~"), ".shiakati_images")
            if not os.path.exists(base_image_dir):
                os.makedirs(base_image_dir)
                
            # Create a product-specific directory if we have a product ID or barcode
            product_id = getattr(self, 'product_id', None)
            barcode = ""
            if self.variants and len(self.variants) > 0:
                barcode = self.variants[0].get('barcode', '')
                
            if product_id:
                image_dir = os.path.join(base_image_dir, f"product_{product_id}")
            elif barcode:
                image_dir = os.path.join(base_image_dir, f"barcode_{barcode}")
            else:
                image_dir = os.path.join(base_image_dir, "new_products")
                
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            
            # Copy the image to our storage location with a unique name
            import shutil
            from datetime import datetime
            
            # Generate a unique filename based on timestamp and original name
            original_filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{original_filename}"
            new_file_path = os.path.join(image_dir, unique_filename)
            
            # Copy the file to our storage directory
            try:
                shutil.copy2(file_path, new_file_path)
                file_path = new_file_path  # Use the new path for further processing
                print(f"Copied image to storage directory: {new_file_path}")
            except Exception as e:
                print(f"Error copying image to storage: {str(e)}")
                # Continue with the original path if copy fails
                pass
            
            # Initialize tracking lists if they don't exist
            if not hasattr(self, 'image_paths'):
                self.image_paths = []
                
            if not hasattr(self, 'local_images'):
                self.local_images = []
                
            if not hasattr(self, 'deleted_images'):
                self.deleted_images = []
            
            # Store the file path in self.image_paths (avoid duplicates)
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
            
            # Create an image structure similar to server_images
            filename = os.path.basename(file_path)
            
            # Add more metadata to track image status for syncing with backend
            self.local_images.append({
                "url": f"file://{file_path}",  # Local file URL scheme
                "filename": filename,
                "local_path": file_path,  # Store local path for uploading later
                "added_time": timestamp,  # Track when it was added
                "new": True,  # Flag as new for syncing with backend
                "size": os.path.getsize(file_path),
                "status": "pending_upload",  # Track image status
                "sync_status": "not_synced"  # Track sync status with backend
            })
            
            print(f"Added local image: {filename} at {file_path}")
            
            # Make a backup copy of the local images list before refresh
            if hasattr(self, '_last_local_images'):
                # If we already have a backup, append this new one to it
                found = False
                for img in self._last_local_images:
                    if img.get('filename') == filename:
                        found = True
                        break
                if not found:
                    self._last_local_images.append(self.local_images[-1])
            else:
                self._last_local_images = self.local_images.copy()
            
            # First ensure local images are preserved by creating a backup
            if hasattr(self, 'ensure_local_images_preserved'):
                self.ensure_local_images_preserved()
            else:
                # Fallback if method doesn't exist
                if hasattr(self, 'local_images') and self.local_images:
                    # Always update the backup even if it already exists
                    if not hasattr(self, '_last_local_images'):
                        self._last_local_images = []
                    self._last_local_images = self.local_images.copy()
            
            # Update the preview with both server and local images
            self.update_image_preview()  # include_local=True by default

    def update_image_preview(self, include_local=True):
        """
        Update the image preview area using self.images_grid.
        
        Args:
            include_local: If True, include locally added images too (not just server images).
                          ALWAYS default to True to prevent images from disappearing.
                          This is the root cause of the image disappearance issue when
                          it's called with include_local=False elsewhere in the code.
        """
        # Make sure we close any lingering loading dialogs first
        self.ensure_loading_dialogs_closed()
        
        # Schedule a second cleanup attempt after this method completes, in case we create new indicators
        QTimer.singleShot(500, self.ensure_loading_dialogs_closed)
        
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
            
        # Process any pending events to make sure UI stays responsive
        QApplication.processEvents()

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
            self.images_grid.removeWidget(widget)
            # Don't delete the widgets immediately as this can cause crashes
            # during layout updates. Just schedule deletion.
            widget.setParent(None)  # Detach from parent
            widget.deleteLater()    # Schedule for deletion
        
        # Reset our tracking list to clear references to old widgets
        self.image_widgets_preview = []
        
        # Clear persistent storage but don't delete objects yet (they'll be garbage collected when no longer needed)
        if hasattr(self, '_image_labels'):
            self._image_labels = []
        else:
            self._image_labels = []
            
        # Make sure we have persistent storage for delete buttons
        if not hasattr(self, '_delete_buttons'):
            self._delete_buttons = []
        
        # Process events after clearing to ensure smooth UI updates
        QApplication.processEvents()
        
        # Initialize or clear persistent reference lists to prevent garbage collection
        if not hasattr(self, '_pixmaps'):
            self._pixmaps = []
        else:
            self._pixmaps = []
            
        if not hasattr(self, '_images'):
            self._images = []
        else:
            self._images = []
            
        if not hasattr(self, '_image_labels'):
            self._image_labels = []
        else:
            self._image_labels = []
            
        if not hasattr(self, '_delete_buttons'):
            self._delete_buttons = []
        else:
            self._delete_buttons = []
        
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
                print(f"Using {len(self.server_images)} server images")
                
                # Debug the first server image to check its format
                if self.server_images and len(self.server_images) > 0:
                    first_img = self.server_images[0]
                    print(f"First server image type: {type(first_img)}")
                    if isinstance(first_img, dict):
                        print(f"First server image keys: {list(first_img.keys())}")
                        for key, value in first_img.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"First server image value: {first_img}")
        
        # Always include local images unless explicitly excluded - fixing image disappearing issue
        if include_local != False:
            # First try to use the current local_images list
            if hasattr(self, 'local_images') and isinstance(self.local_images, list) and self.local_images:
                valid_local_images = []
                for img in self.local_images:
                    if isinstance(img, dict) and 'local_path' in img and os.path.exists(img['local_path']):
                        valid_local_images.append(img)
                
                if valid_local_images:
                    print(f"Adding {len(valid_local_images)} local images to display")
                    all_images.extend(valid_local_images)
                else:
                    print("No valid local images found in current list")
                    
                    # If current local_images is empty but we have a backup, restore from backup
                    if hasattr(self, '_last_local_images') and self._last_local_images:
                        backup_valid_images = []
                        for img in self._last_local_images:
                            if isinstance(img, dict) and 'local_path' in img and os.path.exists(img['local_path']):
                                backup_valid_images.append(img)
                        
                        if backup_valid_images:
                            print(f"Restoring {len(backup_valid_images)} local images from backup")
                            self.local_images = backup_valid_images.copy()
                            all_images.extend(backup_valid_images)
                        else:
                            print("No valid local images found in backup")
            
            # If we don't have local_images or it's empty but we have a backup, use that
            elif hasattr(self, '_last_local_images') and self._last_local_images:
                valid_backup_images = []
                for img in self._last_local_images:
                    if isinstance(img, dict) and 'local_path' in img and os.path.exists(img['local_path']):
                        valid_backup_images.append(img)
                
                if valid_backup_images:
                    print(f"Using {len(valid_backup_images)} local images from backup")
                    # Restore the local_images list from backup
                    self.local_images = valid_backup_images.copy()
                    all_images.extend(valid_backup_images)
                else:
                    print("No valid local images found to display")
            
        # ------------------------
        # Display images or "no images" message
        # ------------------------
        if not all_images:
            print("update_image_preview: No images to display.")
            # Add the 'no images' label to the grid
            try:
                # Use a nicer styled "no images" label
                no_images_label = QLabel("No images available for this product")
                no_images_label.setAlignment(Qt.AlignCenter)
                no_images_label.setStyleSheet("""
                    background-color: #f5f5f5; 
                    color: #757575; 
                    padding: 15px; 
                    border-radius: 5px;
                    font-style: italic;
                """)
                self.images_grid.addWidget(no_images_label, 0, 0, 1, 4)  # span 4 columns
                self.image_widgets_preview.append(no_images_label)
                # Store reference to prevent garbage collection
                self._image_labels.append(no_images_label)
                self._image_labels.append(no_images_label)  # Keep reference to prevent GC
                
            except Exception as e:
                print(f"Error displaying no images message: {str(e)}")
        else:
            try:
                print(f"update_image_preview: Displaying {len(all_images)} images.")
                images_per_row = 3  # Reduced from 4 to accommodate larger image sizes
                row, col = 0, 0
                
                # Clear existing delete button references before creating new ones
                self._delete_buttons = []
                
                for img_data in all_images:
                    # --- FIX: handle both dict and string formats ---
                    if isinstance(img_data, dict):
                        url = img_data.get("url", "")
                        filename = img_data.get("filename") or os.path.basename(url)
                        is_local = "local_path" in img_data
                    elif isinstance(img_data, str):
                        url = img_data
                        filename = os.path.basename(url)
                        is_local = False
                    else:
                        print(f"Skipping invalid image data: {img_data}")
                        continue
                    if not url:
                        print(f"Skipping image with no URL: {filename}")
                        continue

                    try:
                        # Create a container widget to hold both the image and delete button
                        container = QWidget()
                        container.setMinimumSize(220, 240)  # Further increased container size for better visibility
                        container.setProperty("class", "image-container")  # Add CSS class for styling
                        container_layout = QVBoxLayout(container)
                        container_layout.setContentsMargins(6, 6, 6, 6)  # Increased margins
                        container_layout.setSpacing(4)  # Increased spacing
                        
                        # Create label with image or filename
                        temp_label = QLabel()
                        
                        if is_local and isinstance(img_data, dict):
                            # For local images, try to load from filesystem with QPixmap
                            local_path = img_data.get("local_path")
                            if os.path.exists(local_path):
                                pixmap = QPixmap(local_path)
                                # Always store persistent references
                                self._pixmaps.append(pixmap)  # Keep QPixmap alive
                                
                                if not pixmap.isNull():
                                    # Immediately show local images at larger size
                                    scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                    # Store the scaled pixmap too
                                    self._pixmaps.append(scaled_pixmap)
                                    temp_label.setPixmap(scaled_pixmap)
                                    # Ensure UI updates immediately
                                    QApplication.processEvents()
                                else:
                                    # Fallback if image can't be loaded
                                    temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Local file: {local_path}")
                            else:
                                temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Local file not found: {local_path}")
                                # Mark as problematic
                                img_data["status"] = "file_missing"
                                img_data["error_message"] = f"File not found: {local_path}"
                        else:
                            # For server images, try to load but with fallback to display text
                            try:
                                # Properly handle URLs
                                if url.startswith(("http://", "https://", "file://")):
                                    server_path = url
                                else:
                                    # Try to construct a valid URL from relative path with improved handling
                                    api_base_url = getattr(self.api_client, 'base_url', 'http://127.0.0.1:8000').rstrip('/')
                                    if url.startswith('/'):
                                        server_path = f"{api_base_url}{url}"
                                    else:
                                        server_path = f"{api_base_url}/{url}"
                                    
                                    # Add debug output to help diagnose URL issues
                                    print(f"Constructed server path: {server_path} from URL: {url}")
                                    
                                    # Additional check for static/ prefix to ensure proper path handling
                                    if 'static/' in url and not url.startswith('/static/'):
                                        # Alternative URL with /static/ prefix
                                        alt_path = f"{api_base_url}/static/{url.split('static/', 1)[1]}"
                                        print(f"Trying alternative path: {alt_path}")
                                        # Store both paths to try
                                        server_path = [server_path, alt_path]
                                
                                # Show filename as text while we wait
                                temp_label.setText(f"Loading {filename[:10]}...")
                                temp_label.setAlignment(Qt.AlignCenter)
                                
                                # Try to load the image from the server asynchronously
                                def load_image_async():
                                    try:
                                        from urllib.request import Request, urlopen
                                        from urllib.error import URLError, HTTPError
                                        import socket
                                        
                                        # Debug print the URL we're attempting to load
                                        print(f"Attempting to load image from: {server_path}")
                                        
                                        # Handle both single path and list of paths to try
                                        paths_to_try = [server_path] if isinstance(server_path, str) else server_path
                                        success = False
                                        last_error = None
                                        
                                        for path in paths_to_try:
                                            try:
                                                print(f"Attempting to fetch from: {path}")
                                                req = Request(path)
                                                req.add_header('User-Agent', 'Mozilla/5.0')
                                                
                                                with urlopen(req, timeout=10) as response:  # Increased timeout
                                                    data = response.read()
                                                    image = QImage()
                                                    if image.loadFromData(data):
                                                        pixmap = QPixmap.fromImage(image)
                                                        # Always store persistent references
                                                        self._images.append(image)  # Keep QImage alive
                                                        self._pixmaps.append(pixmap)  # Keep QPixmap alive
                                                        
                                                        # Scale the pixmap to larger size and keep a reference to it as well
                                                        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                                        self._pixmaps.append(scaled_pixmap)  # Keep scaled pixmap alive
                                                        # Use a safe method to update UI from thread - use scaled_pixmap instead of full pixmap
                                                        QApplication.postEvent(self, QPixmapEvent(temp_label, scaled_pixmap))
                                                        # Mark as successful
                                                        if isinstance(img_data, dict):
                                                            img_data["loaded"] = True
                                                        success = True  # Mark success for multi-path approach
                                                        break  # Exit the loop on success
                                                    else:
                                                        # Image data couldn't be loaded
                                                        print(f"Failed to load image data: {filename}")
                                                        if isinstance(img_data, dict):
                                                            img_data["error"] = "Invalid image data"
                                                            img_data["loaded"] = False
                                            except HTTPError as e:
                                                print(f"HTTP Error loading server image: {e.code} {e.reason}")
                                                last_error = f"HTTP Error: {e.code}"
                                            except URLError as e:
                                                print(f"URL Error loading server image: {e.reason}")
                                                last_error = f"URL Error: {e.reason}"
                                            except socket.timeout:
                                                print(f"Socket timeout loading server image")
                                                last_error = "Timeout loading image"
                                        
                                        # Only set error if all paths failed
                                        if not success and isinstance(img_data, dict):
                                            img_data["error"] = last_error or "Failed to load image"
                                            img_data["loaded"] = False
                                    except Exception as load_err:
                                        print(f"Error loading image {filename}: {str(load_err)}")
                                        if isinstance(img_data, dict):
                                            img_data["error"] = f"Error: {str(load_err)}"
                                            img_data["loaded"] = False
                                
                                # Check network before attempting to load
                                if self.check_network_status():
                                    # Use a thread to load the image asynchronously
                                    from threading import Thread
                                    image_thread = Thread(target=load_image_async)
                                    image_thread.daemon = True
                                    image_thread.start()
                                    
                                    # Meanwhile, show the filename
                                    temp_label.setText(f"{filename[:15]}...")
                                    temp_label.setToolTip(f"Loading server image: {server_path}")
                                else:
                                    # Network is not available
                                    temp_label.setText("Network Error")
                                    temp_label.setToolTip(f"Cannot access server image: {server_path}")
                                    temp_label.setStyleSheet(temp_label.styleSheet() + "border-color: #e74c3c;")
                                    # Mark image as having network error 
                                    if isinstance(img_data, dict):
                                        img_data["error"] = "Network unavailable"
                                        img_data["loaded"] = False
                            except Exception as url_error:
                                print(f"Error processing server image URL '{url}': {str(url_error)}")
                                temp_label.setText(f"{filename[:15]}...")
                                temp_label.setToolTip(f"Error loading image: {str(url_error)}")
                                # Mark as error
                                if isinstance(img_data, dict):
                                    img_data["error"] = str(url_error)
                                    img_data["loaded"] = False
                        
                        # Add the image label to the container
                        container_layout.addWidget(temp_label)
                        
                        # Store reference to prevent garbage collection
                        self._image_labels.append(temp_label)
                        
                        # Keep reference to prevent garbage collection
                        self._image_labels.append(temp_label)
                        
                        # Add status indicator (local vs server)
                        status_label = QLabel(is_local and "Local" or "Server")
                        status_label.setAlignment(Qt.AlignCenter)
                        status_label.setStyleSheet(f"""
                            background-color: {is_local and "#e8f5e9" or "#e3f2fd"}; 
                            color: {is_local and "#2e7d32" or "#1565c0"}; 
                            border-radius: 2px;
                            padding: 2px 5px;
                            font-size: 8px;
                            font-weight: bold;
                            margin-top: 2px;
                        """)
                        container_layout.addWidget(status_label)
                        
                        # Add a horizontally centered trash icon delete button
                        delete_container = QWidget()
                        delete_layout = QHBoxLayout(delete_container)
                        delete_layout.setContentsMargins(0, 0, 0, 0)
                        
                        delete_btn = QPushButton()
                        delete_btn.setFixedSize(24, 24)
                        
                        # Use trash icon if available, otherwise text
                        try:
                            trash_icon = QIcon.fromTheme("user-trash")
                            if trash_icon.isNull():
                                # Create a simple trash icon if theme icon not available
                                delete_btn.setText("🗑️")  # Unicode trash emoji
                                delete_btn.setFont(QFont("Arial", 10))
                            else:
                                delete_btn.setIcon(trash_icon)
                                delete_btn.setIconSize(QSize(16, 16))
                        except:
                            # Fallback to text if icon loading fails
                            delete_btn.setText("🗑️")
                        
                        delete_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #f44336;
                                color: white;
                                border: none;
                                border-radius: 12px;
                                padding: 2px;
                            }
                            QPushButton:hover {
                                background-color: #d32f2f;
                            }
                            QPushButton:pressed {
                                background-color: #b71c1c;
                            }
                        """)
                        delete_btn.setToolTip("Delete this image")
                        
                        # Center the button horizontally
                        delete_layout.addStretch()
                        delete_layout.addWidget(delete_btn)
                        delete_layout.addStretch()
                        
                        # Capture image data for the delete function
                        delete_btn.image_data = img_data
                        delete_btn.is_local = is_local
                        
                        # Connect delete button to appropriate function with persistent connection
                        if is_local:
                            # Save reference to avoid garbage collection
                            delete_btn._callback = lambda checked, data=img_data: self.remove_local_image(data)
                            delete_btn.clicked.connect(delete_btn._callback)
                        else:
                            # Save reference to avoid garbage collection
                            delete_btn._callback = lambda checked, data=img_data: self.remove_server_image(data)
                            delete_btn.clicked.connect(delete_btn._callback)
                            
                        # Store button reference in the class to prevent GC
                        self._delete_buttons.append(delete_btn)
                            
                        # Add delete button container to the main container
                        container_layout.addWidget(delete_container)
                            
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
            except Exception as e:
                print(f"Error in update_image_preview while processing images: {str(e)}")
                # If we fail during image processing, show the no images message
                self.images_grid.addWidget(self.no_images_label_preview, 0, 0, 1, 4)
                self.no_images_label_preview.setVisible(True)
                self.image_widgets_preview.append(self.no_images_label_preview)
        
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
    
    def force_refresh_images(self):
        """Force a complete refresh of all images to ensure they are visible."""
        print("\n===== FORCING IMAGE REFRESH =====")
        
        # Clear cached images first
        if hasattr(self, "_pixmaps"):
            self._pixmaps.clear()
        if hasattr(self, "_images"):
            self._images.clear()
            
        # Reset image widgets to force recreation
        self.image_widgets_preview = []
        
        # Use a short delay to ensure UI is ready
        QTimer.singleShot(100, lambda: self.update_image_preview(include_local=True))
        
        # Schedule another refresh after a longer delay to ensure loading completes
        QTimer.singleShot(500, lambda: self.update_image_preview(include_local=True))
        
        # One final refresh after everything should be loaded
        QTimer.singleShot(1000, lambda: self.update_image_preview(include_local=True))

    def check_network_status(self):
        """
        Check if the network/API is available.
        Returns True if network is available, False otherwise.
        """
        try:
            # Apply timeout settings to avoid blocking API calls
            self.add_network_timeout_to_api_client()
            
            # Simple check to see if we can reach the API server
            success = False
            try:
                # Use a timer to track response time
                start_time = QElapsedTimer()
                start_time.start()
                
                # Try a lightweight call as a network check
                categories = self.api_client.get_categories()
                success = categories is not None
                
                # If it took too long, consider it a failure
                if start_time.elapsed() > 5000:  # 5 seconds max
                    print(f"Network check: API response was too slow ({start_time.elapsed()}ms)")
                    success = False
            except Exception as api_err:
                print(f"Network check: API error - {str(api_err)}")
                success = False
                
            if not success:
                print("Network check: API server is not accessible")
                return False
                
            print("Network check: API server is accessible")
            return True
        except Exception as e:
            print(f"Network check: Error connecting to API server - {str(e)}")
            return False
    
    def generate_unique_prefix(self):
        """Generate a unique barcode prefix."""
        # Try to generate a prefix based on the product name
        product_name = self.name_input.text().strip()
        if product_name:
            # Convert the name to all caps and keep only letters
            prefix = ''.join(c for c in product_name.upper() if c.isalpha())
            # Take the first 3-5 characters
            prefix = prefix[:min(5, len(prefix))]
            if len(prefix) >= 2:
                self.barcode_prefix.setText(prefix)
                return
        
        # If no valid prefix could be generated, use a timestamp-based approach
        import time
        timestamp = int(time.time()) % 10000
        self.barcode_prefix.setText(f"P{timestamp}")
    
    def generate_variants(self, silent=False):
        """Generate variant combinations based on size and color options."""
        # Get sizes and colors
        sizes = [s.strip() for s in self.size_input.text().split(',') if s.strip()]
        colors = [c.strip() for c in self.color_input.text().split(',') if c.strip()]
        
        if not sizes and not colors:
            if not silent:  # Only show warning if not in silent mode
                QMessageBox.warning(self, "Input Required", "Please enter at least one size or color.")
            return
        
        # If one is empty, use a placeholder
        if not sizes:
            sizes = [""]
        if not colors:
            colors = [""]
        
        # Get price and stock from current inputs
        price = self.price_input.value()
        stock = self.quantity_input.value()
        
        # Generate barcode prefix if needed
        prefix = self.barcode_prefix.text().strip()
        if not prefix:
            self.generate_unique_prefix()
            prefix = self.barcode_prefix.text().strip()
        
        # Open manual entry dialog for variant quantities
        self.edit_variants_dialog(sizes, colors, price, stock, prefix)
        
    def edit_variants_dialog(self, sizes, colors, base_price, base_stock, prefix):
        """Open dialog to edit individual variant quantities before generating."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Individual Quantities for Each Variant")
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(650)
        
        # Dialog layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions
        instructions_container = QWidget()
        instructions_container.setStyleSheet("background-color: #eaf2fc; border-radius: 6px; border: 1px solid #c5d8ef;")
        instructions_layout = QVBoxLayout(instructions_container)
        instructions_layout.setContentsMargins(15, 15, 15, 15)
        
        instructions_title = QLabel("Set Different Quantities for Each Size & Color")
        instructions_title.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        instructions_layout.addWidget(instructions_title)
        
        instructions_text = QLabel(
            "• Each row represents a unique size/color combination\n"
            "• You can set different stock quantities for each variant\n"
            "• Select multiple rows to update them together"
        )
        instructions_text.setStyleSheet("font-size: 14px; color: #34495e; margin-top: 5px;")
        instructions_layout.addWidget(instructions_text)
        
        layout.addWidget(instructions_container)
        
        # Table of variants
        variants_table = QTableWidget()
        variants_table.setColumnCount(5)
        variants_table.setHorizontalHeaderLabels(
            ["Size", "Color", "Barcode", "Price", "Stock Quantity"]
        )
        
        # Add variants to table
        variant_count = 1
        variant_data = []
        
        for size in sizes:
            for color in colors:
                row = variants_table.rowCount()
                variants_table.insertRow(row)
                
                # Create a unique barcode for this variant
                barcode = f"{prefix}{variant_count:03d}"
                
                # Add size item
                size_item = QTableWidgetItem(size)
                size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                variants_table.setItem(row, 0, size_item)
                
                # Add color item
                color_item = QTableWidgetItem(color)
                color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                variants_table.setItem(row, 1, color_item)
                
                # Add barcode item
                barcode_item = QTableWidgetItem(barcode)
                barcode_item.setFlags(barcode_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                variants_table.setItem(row, 2, barcode_item)
                
                # Add price item with SpinBox
                price_spinbox = QDoubleSpinBox()
                price_spinbox.setMaximum(99999.99)
                price_spinbox.setDecimals(2)
                price_spinbox.setValue(base_price)
                price_spinbox.setSuffix(" DZD")
                price_spinbox.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #fcfcfc;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        padding: 3px;
                        min-height: 30px;
                    }
                    QDoubleSpinBox:hover {
                        border-color: #3498db;
                    }
                """)
                variants_table.setCellWidget(row, 3, price_spinbox)
                
                # Add stock item with SpinBox
                stock_spinbox = QDoubleSpinBox()
                stock_spinbox.setMaximum(9999.99)
                stock_spinbox.setDecimals(1)
                stock_spinbox.setValue(base_stock)
                stock_spinbox.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #f0f7fc;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        padding: 3px;
                        min-height: 30px;
                    }
                    QDoubleSpinBox:hover {
                        border-color: #3498db;
                        background-color: #e1f0fa;
                    }
                """)
                variants_table.setCellWidget(row, 4, stock_spinbox)
                
                # Store variant data
                variant_data.append({
                    'size': size,
                    'color': color,
                    'barcode': barcode,
                    'price_spinbox': price_spinbox,
                    'stock_spinbox': stock_spinbox,
                    'row': row
                })
                
                variant_count += 1
        
        # Apply styling to the table
        variants_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Set alternating row colors
        variants_table.setAlternatingRowColors(True)
        
        # Set column widths
        variants_table.setColumnWidth(0, 100)  # Size
        variants_table.setColumnWidth(1, 120)  # Color
        variants_table.setColumnWidth(2, 150)  # Barcode
        variants_table.setColumnWidth(3, 150)  # Price
        variants_table.setColumnWidth(4, 150)  # Stock
        
        # Make the table resizable and fill space
        variants_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        variants_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(variants_table)
        
        # Quick-set buttons
        quick_set_box = QHBoxLayout()
        quick_set_label = QLabel("Quick set stock for selected rows:")
        quick_set_label.setStyleSheet("font-weight: bold;")
        quick_set_box.addWidget(quick_set_label)
        
        # Stock value input
        quick_stock = QDoubleSpinBox()
        quick_stock.setMaximum(9999.99)
        quick_stock.setDecimals(1)
        quick_stock.setValue(base_stock)
        quick_stock.setMinimumWidth(100)
        quick_set_box.addWidget(quick_stock)
        
        # Set stock button
        set_stock_btn = QPushButton("Apply to Selected")
        set_stock_btn.setStyleSheet("""
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
        """)
        
        def apply_stock_to_selected():
            value = quick_stock.value()
            selected_rows = []
            
            # Check for selected rows
            for idx in range(variants_table.rowCount()):
                if variants_table.item(idx, 0).isSelected() or variants_table.item(idx, 1).isSelected() or variants_table.item(idx, 2).isSelected():
                    selected_rows.append(idx)
            
            # If no rows are selected, ask if user wants to apply to all
            if not selected_rows:
                apply_to_all = QMessageBox.question(dialog, 
                                                   "No Selection", 
                                                   "No rows are selected. Do you want to apply this stock value to all variants?",
                                                   QMessageBox.Yes | QMessageBox.No)
                
                if apply_to_all == QMessageBox.Yes:
                    selected_rows = list(range(variants_table.rowCount()))
            
            # Apply the stock value to selected rows
            for idx in selected_rows:
                stock_spinbox = variants_table.cellWidget(idx, 4)
                if stock_spinbox:
                    stock_spinbox.setValue(value)
                    
                    # Get size and color for visual feedback
                    size = variants_table.item(idx, 0).text()
                    color = variants_table.item(idx, 1).text() 
                    
                    # Briefly highlight the row for visual feedback
                    for col in range(variants_table.columnCount()):
                        item = variants_table.item(idx, col)
                        if item:
                            item.setBackground(QColor("#d5f5e3"))  # Light green highlight
            
            # If rows were updated, show a brief confirmation
            if selected_rows:
                QTimer.singleShot(800, lambda: variants_table.clearSelection())
        
        set_stock_btn.clicked.connect(apply_stock_to_selected)
        quick_set_box.addWidget(set_stock_btn)
        quick_set_box.addStretch()
        
        layout.addLayout(quick_set_box)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        # Style the OK button
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Generate Variants")
        ok_button.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            min-width: 150px;
        """)
        
        # Style the Cancel button
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("padding: 10px 20px;")
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addSpacing(10)
        layout.addWidget(button_box)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Add variants to existing ones (instead of replacing them)
            # Keep track of existing variants by size, color, and price to avoid duplicates
            existing_variants = {
                (variant.get('size', '').strip().lower(), 
                 variant.get('color', '').strip().lower(), 
                 float(variant.get('price', 0)))
                for variant in self.variants
            }
            
            for var in variant_data:
                # Get values from spinboxes
                price = var['price_spinbox'].value()
                stock = var['stock_spinbox'].value()
                
                # Create variant with custom values
                variant = {
                    'size': var['size'],
                    'color': var['color'],
                    'barcode': var['barcode'],
                    'price': price,
                    'stock': stock
                }
                
                # Check if this variant combination already exists (size, color, price)
                variant_key = (
                    variant['size'].strip().lower(),
                    variant['color'].strip().lower(), 
                    float(variant['price'])
                )
                
                if variant_key not in existing_variants:
                    self.variants.append(variant)
                    existing_variants.add(variant_key)
                    print(f"Added new variant: {variant['size']} {variant['color']} - {variant['price']} DZD")
                else:
                    print(f"Skipping duplicate variant: {variant['size']} {variant['color']} - {variant['price']} DZD (already exists)")
            
            # Update table view
            self.update_variants_table()
    
    def update_variants_table(self):
        """Update the variants table with current variant data."""
        self.variants_table.setRowCount(0)
        
        for i, variant in enumerate(self.variants):
            row = self.variants_table.rowCount()
            self.variants_table.insertRow(row)
            
            # Set table items
            self.variants_table.setItem(row, 0, QTableWidgetItem(variant['size']))
            self.variants_table.setItem(row, 1, QTableWidgetItem(variant['color']))
            self.variants_table.setItem(row, 2, QTableWidgetItem(variant['barcode']))
            
            # Price is editable and shows with 2 decimal places
            price_item = QTableWidgetItem(f"{variant['price']:.2f}")
            price_item.setToolTip(f"Edit price for {variant['size']} {variant['color']}")
            self.variants_table.setItem(row, 3, price_item)
            
            # Stock is editable and shows with 1 decimal place
            stock_item = QTableWidgetItem(f"{variant['stock']:.1f}")
            stock_item.setToolTip(f"Edit stock quantity for {variant['size']} {variant['color']}")
            # Make stock cells more noticeable 
            stock_item.setBackground(QColor("#f1f8ff"))  # Light blue background
            self.variants_table.setItem(row, 4, stock_item)
            
            # Create delete button for this variant
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)
            
            # Create delete button (smaller trash icon)
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 2px;
                    border-radius: 2px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.setFixedSize(25, 22)
            delete_btn.setToolTip(f"Delete variant {variant['size']} {variant['color']}")
            
            # Connect delete button with current index
            current_index = i  # Store the current index for this button
            delete_btn.clicked.connect(lambda checked, idx=current_index: self.delete_variant(idx))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            # Add the widget to the actions column
            self.variants_table.setCellWidget(row, 5, actions_widget)
        
        # Update variant count label
        count = len(self.variants)
        if count > 0:
            self.variant_count_label.setText(f"{count} variant{'s' if count > 1 else ''} added - You can edit price and stock levels directly in the table")
            self.variant_count_label.setStyleSheet("""
                font-weight: bold; 
                color: #27ae60; 
                font-size: 16px;
                padding: 15px;
                background-color: #d5f5e3;
                border-radius: 6px;
                border: 1px solid #abebc6;
                min-height: 50px;
                margin-bottom: 5px;
            """)
        else:
            self.variant_count_label.setText("No variants added yet. Use 'Generate Variants' to create multiple variants.")
            self.variant_count_label.setStyleSheet("""
                font-weight: bold; 
                color: #e74c3c; 
                font-size: 16px;
                padding: 12px;
                background-color: #fdf2f0;
                border-radius: 4px;
                border: 1px solid #fadbd8;
                margin-bottom: 5px;
            """)
        
        # Resize columns to content
        self.variants_table.resizeColumnsToContents()
    
    def validate_input(self):
        """Validate all input fields."""
        product_name = self.name_input.text().strip()
        if not product_name:
            QMessageBox.warning(self, "Validation Error", "Product name is required")
            return False
        
        if not self.variants:
            QMessageBox.warning(self, "Validation Error", "No variants have been generated. Please generate variants first.")
            return False
        
        # Update variants with table values (in case user edited them)
        for row in range(self.variants_table.rowCount()):
            try:
                price = float(self.variants_table.item(row, 3).text())
                stock = float(self.variants_table.item(row, 4).text())
                
                # Update variant data
                self.variants[row]['price'] = price
                self.variants[row]['stock'] = stock
            except (ValueError, IndexError) as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid price or stock value at row {row+1}")
                return False
        
        return True
    
    def create_product(self):
        """Create or update a product with variants."""
        # Validate input first
        if not self.validate_input():
            return
        
        # FIX: Remove blocking progress dialog - use print instead
        print("Creating/updating product and variants...")
        QApplication.processEvents()  # Allow UI to remain responsive
        
        # Get the values from the input fields
        product_name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        category = self.category_combo.currentText()
        
        # Determine if we're creating a new product or updating an existing one
        is_update_mode = self.product_id is not None
        
        try:
            if is_update_mode:
                # Update the existing product
                print(f"Updating product {self.product_id}: {product_name}")
                
                # Get category_id from category name
                category_id = None
                if category:
                    try:
                        categories = self.api_client.get_categories()
                        for cat in categories:
                            if isinstance(cat, dict) and cat.get("name") == category:
                                category_id = cat.get("id")
                                break
                    except Exception as e:
                        print(f"Error getting category ID: {str(e)}")
                
                product_data = {
                    "name": product_name,
                    "description": description,
                }
                
                # Always include category_id - None for no category, or the found category ID
                product_data["category_id"] = category_id
                
                print(f"DEBUG: Updating product {self.product_id} with data: {product_data}")
                
                # Clear any cache before updating to ensure fresh data
                if hasattr(self.api_client, 'clear_cache'):
                    self.api_client.clear_cache()
                
                # Update the product in the database
                updated_product = self.api_client.update_product(self.product_id, product_data)
                
                if not updated_product:
                    # Get more details about what went wrong from the logs
                    raise Exception(f"Failed to update product ID {self.product_id}. Check console for detailed error information.")
                
                print(f"Successfully updated product ID: {self.product_id}")
                
                # Combine existing variants with any updates or additions
                # Variants from edit mode already have variant_id if they exist in DB
                first_barcode = None
                for idx, variant in enumerate(self.variants):
                    variant_data = {
                        "size": variant.get("size", ""),
                        "color": variant.get("color", ""),
                        "barcode": variant.get("barcode"),
                        "price": float(variant.get("price", 0)),
                        "stock": float(variant.get("stock", 0)),
                        "product_id": self.product_id
                    }
                    
                    if idx == 0:
                        first_barcode = variant_data["barcode"]
                    
                    variant_id = variant.get("variant_id")
                    if variant_id:  # Existing variant, update it
                        updated_variant = self.api_client.update_variant(variant_id, variant_data)
                        if not updated_variant:
                            print(f"Warning: Failed to update variant ID {variant_id}")
                    else:  # New variant, create it
                        new_variant = self.api_client.create_variant(variant_data)
                        if not new_variant:
                            print(f"Warning: Failed to create new variant for product {self.product_id}")
                
                # Handle image uploads - Now supporting both local and server images
                # We use the first variant's barcode for images
                if first_barcode:
                    # Handle local image uploads
                    if hasattr(self, 'local_images') and self.local_images:
                        # FIX: Remove blocking dialog text update - use print instead
                        print(f"Uploading {len(self.local_images)} local images for barcode {first_barcode}")
                        QApplication.processEvents()  # Ensure UI updates during upload
                        
                        for img_data in self.local_images:
                            try:
                                local_path = img_data.get('local_path')
                                if local_path and os.path.exists(local_path):
                                    print(f"Uploading local image: {local_path}")
                                    success = self.api_client.upload_product_image(first_barcode, local_path)
                                    if success:
                                        print(f"Successfully uploaded image for {first_barcode}: {local_path}")
                                    else:
                                        print(f"Failed to upload image for {first_barcode}: {local_path}")
                                else:
                                    print(f"Image file not found: {local_path}")
                            except Exception as upload_err:
                                print(f"Error uploading image: {str(upload_err)}")
                        
                        # Update server images after upload
                        try:
                            print("Refreshing server images after upload...")
                            # Instead of just calling delayed_image_refresh, we'll use a custom approach
                            # that preserves local images during the refresh
                            
                            # First, save the local images to preserve them
                            QTimer.singleShot(1000, lambda b=first_barcode: self.delayed_image_refresh_with_local_preservation(b))
                            
                            # Set a backup timer to ensure popup gets closed if refresh fails or hangs
                            QTimer.singleShot(6000, lambda: self.ensure_loading_dialogs_closed())
                        except Exception as refresh_err:
                            print(f"Error scheduling image refresh: {str(refresh_err)}")
                            # Still try to close any loading dialogs in case of error
                            self.ensure_loading_dialogs_closed()
                
                success_msg = "Product and variants updated successfully!"
                
            else:
                # Create a new product
                print(f"Creating new product: {product_name}")
                
                # Get category_id from category name
                category_id = None
                if category:
                    try:
                        categories = self.api_client.get_categories()
                        for cat in categories:
                            if isinstance(cat, dict) and cat.get("name") == category:
                                category_id = cat.get("id")
                                break
                    except Exception as e:
                        print(f"Error getting category ID: {str(e)}")
                
                product_data = {
                    "name": product_name,
                    "description": description,
                }
                
                # Always include category_id - None for no category, or the found category ID
                product_data["category_id"] = category_id
                
                # Create the product first
                new_product = self.api_client.create_product(product_data)
                if not new_product or "id" not in new_product:
                    raise Exception("Failed to create product")
                
                product_id = new_product["id"]
                print(f"Created product with ID: {product_id}")
                
                # Then create all variants
                first_barcode = None
                for idx, variant in enumerate(self.variants):
                    variant_data = {
                        "size": variant.get("size", ""),
                        "color": variant.get("color", ""),
                        "barcode": variant.get("barcode", ""),
                        "price": float(variant.get("price", 0)),
                        "stock": float(variant.get("stock", 0)),
                        "product_id": product_id
                    }
                    
                    if idx == 0:
                        first_barcode = variant_data["barcode"]
                    
                    new_variant = self.api_client.create_variant(variant_data)
                    if not new_variant:
                        print(f"Warning: Failed to create variant for product {product_id}")
                
                # Handle image synchronization (uploads and deletions)
                if first_barcode:
                    # First, check network connectivity
                    if not self.check_network_status():
                        QMessageBox.warning(
                            self, 
                            "Network Error", 
                            "Cannot connect to server. Images won't be synchronized. You can try again later."
                        )
                    else:
                        # Handle image uploads if we have local images
                        # Initialize variables at the beginning of the scope
                        success_count = 0
                        failed_images = []
                        
                        if hasattr(self, 'local_images') and self.local_images:
                            # FIX: Remove blocking dialog text update - use print instead  
                            print(f"Uploading {len(self.local_images)} local images for barcode {first_barcode}")
                            QApplication.processEvents()  # Ensure UI updates
                            
                            upload_count = len(self.local_images) 
                            
                            print(f"Uploading {upload_count} local images for barcode {first_barcode}")
                            
                        # Handle image deletions if we have tracked deleted images
                        deleted_count = 0
                        deletion_failures = []
                        if hasattr(self, 'deleted_images') and self.deleted_images:
                            print(f"Synchronizing {len(self.deleted_images)} deleted images for barcode {first_barcode}")
                            
                            for deleted_img in self.deleted_images:
                                # Only process images that haven't been synced yet
                                if deleted_img.get("sync_status") == "not_synced":
                                    try:
                                        filename = deleted_img.get("filename")
                                        print(f"Reporting deletion of image {filename} to server")
                                        
                                        # Delete from server if needed
                                        if not deleted_img.get("server_image", False):
                                            success = self.delete_product_image_with_timeout(first_barcode, filename)
                                            if success:
                                                deleted_img["sync_status"] = "synced"
                                                deleted_count += 1
                                            else:
                                                deletion_failures.append(filename)
                                        
                                    except Exception as e:
                                        print(f"Error synchronizing deleted image: {str(e)}")
                                        deletion_failures.append(deleted_img.get("filename", "unknown"))
                            
                            if deletion_failures:
                                print(f"Failed to synchronize {len(deletion_failures)} deleted images")
                        for i, img_data in enumerate(self.local_images):
                            try:
                                # Show detailed progress with percentage in console
                                percent_complete = int((i / upload_count) * 100)
                                print(f"Uploading image {i+1} of {upload_count} ({percent_complete}%)...")
                                QApplication.processEvents()  # Ensure UI updates
                                
                                local_path = img_data.get('local_path')
                                filename = img_data.get('filename', os.path.basename(local_path) if local_path else "Unknown")
                                
                                if local_path and os.path.exists(local_path):
                                    print(f"Starting upload for image {i+1}: {local_path}")
                                    
                                    # Set a timeout for this upload
                                    timeout_timer = QTimer()
                                    timeout_timer.setSingleShot(True)
                                    timeout_timer.start(15000)  # 15 seconds timeout for upload
                                    
                                    # Update status before upload
                                    img_data["status"] = "uploading"                                   
                                    # Upload the image
                                    success = self.api_client.upload_product_image(first_barcode, local_path)
                                    
                                    # Cancel timeout timer
                                    timeout_timer.stop()
                                    
                                    if success:
                                        success_count += 1
                                        print(f"Successfully uploaded image {i+1} for {first_barcode}: {local_path}")
                                                    # Update image status after successful upload
                                        img_data["status"] = "uploaded"
                                        img_data["sync_status"] = "synced"
                                        img_data["new"] = False
                                        img_data["upload_time"] = time.time()
                                        img_data["server_barcode"] = first_barcode
                                        
                                        # Make sure we keep a backup of the local image data
                                        # even though it's now on the server
                                        if not hasattr(self, '_last_local_images'):
                                            self._last_local_images = []
                                        
                                        # Check if we already have this image in our backup
                                        existing_filename = False
                                        for backup_img in self._last_local_images:
                                            if backup_img.get('filename') == img_data.get('filename'):
                                                existing_filename = True
                                                break
                                                
                                        # If not in backup, add it
                                        if not existing_filename:
                                            self._last_local_images.append(dict(img_data))
                                    else:
                                        failed_images.append(filename)
                                        img_data["status"] = "upload_failed"
                                        img_data["sync_status"] = "not_synced"
                                        print(f"Failed to upload image {i+1} for {first_barcode}: {local_path}")
                                else:
                                    failed_images.append(filename)
                                    img_data["status"] = "file_missing"
                                    img_data["sync_status"] = "not_synced"
                                    print(f"Image file not found: {local_path}")
                            except Exception as upload_err:
                                print(f"Error uploading image {i+1}: {str(upload_err)}")
                                img_data["status"] = "upload_error"
                                img_data["sync_status"] = "not_synced"
                                img_data["error_message"] = str(upload_err)
                                failed_images.append(filename)
                        
                        # Update server images after upload to ensure proper display
                        try:
                            print("Refreshing server images after new product image upload...")
                            # Instead of just calling delayed_image_refresh, we'll use the custom approach
                            # that preserves local images during the refresh
                            QTimer.singleShot(1000, lambda b=first_barcode: self.delayed_image_refresh_with_local_preservation(b))
                            
                            # Set a backup timer to ensure popup gets closed if refresh fails or hangs
                            QTimer.singleShot(6000, lambda: self.ensure_loading_dialogs_closed())
                        except Exception as refresh_err:
                            print(f"Error scheduling image refresh for new product: {str(refresh_err)}")
                            # Still try to close any loading dialogs in case of error
                            self.ensure_loading_dialogs_closed()

                        # Show upload summary if there were any failures
                        if failed_images:
                            failed_msg = f"Successfully uploaded {success_count} of {upload_count} images.\n\n"
                            failed_msg += "The following images failed to upload:\n"
                            for fail in failed_images[:5]:  # Show only first 5 failures
                                failed_msg += f"- {fail}\n"
                            
                            if len(failed_images) > 5:
                                failed_msg += f"...and {len(failed_images) - 5} more."
                                
                            # Show warning after the progress dialog is closed
                            QTimer.singleShot(500, lambda: QMessageBox.warning(self, "Upload Issues", failed_msg))
                
                success_msg = "Product and variants created successfully!"
            
            # FIX: Emergency cleanup for any other loading dialogs
            self.ensure_loading_dialogs_closed()
            
            # Ensure the inventory cache is cleared so the product appears in the main window
            try:
                if hasattr(self.api_client, 'clear_cache'):
                    print("Clearing API cache to refresh inventory...")
                    self.api_client.clear_cache()
            except Exception as cache_err:
                print(f"Error clearing cache: {str(cache_err)}")
            
            # Show success message
            QMessageBox.information(self, "Success", success_msg)
            
            # Signal to main window that data has changed
            self.accept()
            
        except Exception as e:
            # FIX: Emergency cleanup for any other loading dialogs
            self.ensure_loading_dialogs_closed()
            
            QMessageBox.critical(self, "Error", f"Failed to {('update' if is_update_mode else 'create')} product: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_product_data(self):
        """Load data for an existing product."""
        try:
            # Change dialog title for edit mode
            self.setWindowTitle("Edit Product with Variants")
            
            # Get product data from API
            product = self.api_client.get_product_by_id(self.product_id)
            if not product:
                QMessageBox.warning(self, "Error", "Could not load product data.")
                return
            
            # Fill basic product information
            self.name_input.setText(product.get("name", ""))
            self.description_input.setText(product.get("description", ""))
            
            # Set category if it exists
            if "category_name" in product:
                category_name = product.get("category_name")
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemText(i) == category_name:
                        self.category_combo.setCurrentIndex(i)
                        break
            
            # Get variants for this product
            variants = self.api_client.get_variants_by_product_id(self.product_id)
            if variants:
                # Load existing variants into our data model
                self.variants = []
                for variant in variants:
                    self.variants.append({
                        'size': variant.get("size", ""),
                        'color': variant.get("color", ""),
                        'barcode': variant.get("barcode", ""),
                        'price': float(variant.get("price", 0)),
                        'stock': float(variant.get("quantity", 0)),
                        'variant_id': variant.get("id")  # Store variant ID for updating
                    })
                
                # Extract prefix from first variant barcode if possible
                if self.variants:
                    first_barcode = self.variants[0].get('barcode', '')
                    if first_barcode:
                        # Extract prefix (non-numeric part)
                        import re
                        prefix_match = re.match(r'^([A-Za-z]+)', first_barcode)
                        if prefix_match:
                            self.barcode_prefix.setText(prefix_match.group(1))
                            
                    # Set size and color inputs with unique values from variants
                    sizes = set()
                    colors = set()
                    for variant in self.variants:
                        if variant['size']:
                            sizes.add(variant['size'])
                        if variant['color']:
                            colors.add(variant['color'])
                    
                    self.size_input.setText(", ".join(sizes))
                    self.color_input.setText(", ".join(colors))
                
                # Update the variants table
                self.update_variants_table()
                
                # Fetch and display server images for the first variant's barcode
                first_variant = self.variants[0] if self.variants else None
                first_barcode = first_variant.get("barcode") if first_variant else None
                
                # Initialize server_images to an empty list regardless of outcome
                self.server_images = []
                if first_barcode:
                    try:
                        print(f"Initial check for images for product with barcode: {first_barcode}")
                        # Only perform a quick check without showing UI - showEvent will handle the full loading
                        
                        # Add network timeout to API client
                        self.add_network_timeout_to_api_client()
                        
                        # Set a timeout for the image loading operation (5 seconds)
                        timeout = 5  # seconds
                        
                        # Start a timer
                        start = QElapsedTimer()
                        start.start()
                        
                        # Fast initial API call without showing any dialog or loading indicators
                        images_data_from_api = None
                        try:
                            images_data_from_api = self.api_client.get_product_images(first_barcode)
                        except Exception as api_err:
                            print(f"Initial image check failed: {str(api_err)}")
                            # Don't show any error UI in load_product_data - just log the error
                        
                        # Don't show any loading dialog in load_product_data, since showEvent will handle proper loading
                        print("Initial images check complete - will do full refresh in showEvent")
                        
                        # Check if operation took too long
                        if start.elapsed() > timeout *  1000:  # Convert to milliseconds
                            print(f"Warning: Image loading took longer than {timeout} seconds")
                            
                        # Enhanced debug log with explicit type checking
                        print(f"DEBUG: For barcode {first_barcode}, API returned image data: {images_data_from_api} (type: {type(images_data_from_api)})")
                        
                        # Process images based on the response format
                        has_images = False
                        if isinstance(images_data_from_api, dict) and 'images' in images_data_from_api:
                            # New format with dictionary response
                            image_list = images_data_from_api.get('images', [])
                            has_images = len(image_list) > 0
                            print(f"Got {len(image_list)} images from server (new format) for barcode {first_barcode}")
                            
                            # Log main image if available
                            main_image = images_data_from_api.get('main_image')
                            print(f"Main image: {main_image}")
                        elif isinstance(images_data_from_api, dict):
                            # Try to find other image data in dictionary format
                            print(f"Response is a dictionary with keys: {list(images_data_from_api.keys())}")
                            for key, value in images_data_from_api.items():
                                if isinstance(value, list) and len(value) > 0:
                                    has_images = True
                                    print(f"Found potential image list in key '{key}' with {len(value)} items")
                                    break
                        elif isinstance(images_data_from_api, (list, tuple)) and len(images_data_from_api) > 0:
                            # Legacy format with direct list response
                            has_images = True
                            print(f"Got {len(images_data_from_api)} images from server (legacy format) for barcode {first_barcode}")
                            
                            # Safe access to first element for type/keys logging
                            if images_data_from_api:
                                first_image_for_debug = images_data_from_api[0]
                                print(f"First image type: {type(first_image_for_debug)}")
                                if isinstance(first_image_for_debug, dict):
                                    print(f"First image dict keys: {first_image_for_debug.keys()}")
                        else:
                            print(f"No valid image data found for barcode {first_barcode} in initial check")
            
                        # Only process if we have images in any format
                        if has_images:

                            api_base_url = getattr(self.api_client, 'base_url', 'http://127.0.0.1:8000').rstrip('/')
                            processed_image_structs = []
                            main_image = None
                            
                            # Process images based on the response format
                            if isinstance(images_data_from_api, dict) and 'images' in images_data_from_api:
                                # New format with dictionary response
                                image_list = images_data_from_api.get('images', [])
                                main_image = images_data_from_api.get('main_image')
                                
                                # Process all images in the list
                                for img_url in image_list:
                                    if img_url is not None:  # Skip None values
                                        try:
                                            # Convert URL string to proper format
                                            fname = os.path.basename(img_url)
                                            image_data = {"url": img_url, "filename": fname}
                                            # Mark the main image if it matches
                                            if main_image and img_url == main_image:
                                                image_data["is_main"] = True
                                            processed_image_structs.append(image_data)
                                        except Exception as e:
                                            print(f"Error processing image URL: {str(e)}")
                                
                                # Also process main_image if it wasn't already included in the images list
                                if main_image and main_image not in image_list:
                                    try:
                                        fname = os.path.basename(main_image)
                                        image_data = {"url": main_image, "filename": fname, "is_main": True}
                                        processed_image_structs.append(image_data)
                                        print(f"Added main_image that wasn't in images list: {main_image}")
                                    except Exception as e:
                                        print(f"Error processing main_image: {str(e)}")
                            elif isinstance(images_data_from_api, dict):
                                # Try to process other dictionary formats
                                print(f"Processing dictionary response with keys: {list(images_data_from_api.keys())}")
                                
                                # Look for any list fields that might contain images
                                for key, value in images_data_from_api.items():
                                    if isinstance(value, list) and key != 'images':
                                        print(f"Found potential image list in key '{key}' with {len(value)} items")
                                        for img in value:
                                            try:
                                                if isinstance(img, str):
                                                    # If a string URL, convert to proper format
                                                    img_url = str(img)
                                                    fname = os.path.basename(img_url)
                                                    processed_image_structs.append({"url": img_url, "filename": fname})
                                                elif isinstance(img, dict) and "url" in img:
                                                    # If a dictionary with URL, use directly
                                                    if "filename" not in img:
                                                        img["filename"] = os.path.basename(img["url"])
                                                    processed_image_structs.append(img)
                                            except Exception as e:
                                                print(f"Error processing alternative image format: {str(e)}")
                                
                                # Check for main_image field
                                if "main_image" in images_data_from_api and images_data_from_api["main_image"]:
                                    main_img = images_data_from_api["main_image"]
                                    try:
                                        if isinstance(main_img, str):
                                            fname = os.path.basename(main_img)
                                            image_data = {"url": main_img, "filename": fname, "is_main": True}
                                            processed_image_structs.append(image_data)
                                            print(f"Added main_image as a separate image: {main_img}")
                                    except Exception as e:
                                        print(f"Error processing main_image: {str(e)}")
                            else:
                                # Legacy format - process as direct list or other format
                                image_items = images_data_from_api if isinstance(images_data_from_api, (list, tuple)) else []
                                for img_data in image_items:
                                    img_url = None
                                    filename = None
                                    if isinstance(img_data, dict):
                                        if "url" in img_data:  # Case 1: Dict with full URL
                                            img_url = img_data["url"]
                                            filename = img_data.get("filename", os.path.basename(img_url))
                                        elif "filename" in img_data:  # Case 2: Dict with filename (relative path)
                                            relative_path = img_data["filename"]
                                            img_url = f"{api_base_url}/static/images/products/{relative_path.lstrip('/')}"
                                            filename = os.path.basename(relative_path)
                                        else:
                                            print(f"Skipping unrecognized dict image format: {img_data}")
                                            continue
                                    elif isinstance(img_data, str):  # Case 3: String (assume filename or relative path)
                                        relative_path = img_data
                                        img_url = f"{api_base_url}/static/images/products/{relative_path.lstrip('/')}"
                                        filename = os.path.basename(relative_path)
                                    else:
                                        print(f"Skipping unrecognized image format: {type(img_data)}")
                                        continue

                                    if img_url and filename:
                                        processed_image_structs.append({"url": img_url, "filename": filename})
                                    else:
                                        print(f"Could not determine URL or filename for image data: {img_data}")

                            self.server_images = processed_image_structs
                            print(f"Processed {len(self.server_images)} server images")
                        else:
                            # No images found in any format
                            self.server_images = []
                            if images_data_from_api is None:
                                print(f"API returned None for images (barcode {first_barcode}). No images to display.")
                            else:
                                print(f"API returned no valid images for barcode {first_barcode}. No images to display.")
                        
                    except Exception as e:
                        print(f"Error processing images in load_product_data: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    finally:
                        # Always update the UI - whether we got images or not
                        self.update_image_preview(include_local=True)
                else: # No barcode found for the first variant
                    print("No barcode found for the first variant. Cannot load images.")
                    self.server_images = [] # Ensure server_images is empty
                    self.update_image_preview(include_local=True)
            else: # No variants_data
                self.variants = []
                
                # Show a message indicating edit mode
                QMessageBox.information(self, "Edit Mode", 
                    f"Loaded product '{product.get('name')}' with {len(self.variants)} variants.\n\n"
                    f"You can add more variants or modify the existing ones.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load product data: {str(e)}")

    def show_product_info_dialog(self):
        """Show a dialog with information about the current product and its variants."""
        # Create a dialog to display the product information
        dialog = QDialog(self)
        dialog.setWindowTitle("Product Information")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Product information section
        info_group = QGroupBox("Product Information")
        info_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 15px; }")
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        
        # Display product name
        name_label = QLabel(self.name_input.text())
        name_label.setStyleSheet("font-size: 14px; padding: 5px 10px; font-weight: bold;")
        info_layout.addRow("<b>Product Name:</b>", name_label)
        
        # Display description
        desc_label = QLabel(self.description_input.text())
        desc_label.setStyleSheet("font-size: 14px; padding: 5px 10px;")
        info_layout.addRow("<b>Description:</b>", desc_label)
        
        # Display barcode prefix
        prefix_label = QLabel(self.barcode_prefix.text())
        prefix_label.setStyleSheet("font-size: 14px; padding: 5px 10px;")
        info_layout.addRow("<b>Barcode Prefix:</b>", prefix_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Variants table
        variants_group = QGroupBox(f"Variants ({len(self.variants)})")
        variants_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 15px; }")
        variants_layout = QVBoxLayout()
        
        # Create a table to show all variants
        variants_table = QTableWidget()
        variants_table.setColumnCount(5)
        variants_table.setHorizontalHeaderLabels(["Size", "Color", "Barcode", "Price", "Stock"])
        variants_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        variants_table.setSelectionBehavior(QTableWidget.SelectRows)
        variants_table.horizontalHeader().setStretchLastSection(True)
        variants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Add all variants to the table
        for variant in self.variants:
            row = variants_table.rowCount()
            variants_table.insertRow(row)
            
            variants_table.setItem(row, 0, QTableWidgetItem(variant.get('size', '')))
            variants_table.setItem(row, 1, QTableWidgetItem(variant.get('color', '')))
            variants_table.setItem(row, 2, QTableWidgetItem(variant.get('barcode', '')))
            variants_table.setItem(row, 3, QTableWidgetItem(f"{variant.get('price', 0):.2f} DZD"))
            
            # Stock quantity with color coding
            stock_value = variant.get('stock', 0)
            stock_item = QTableWidgetItem(f"{stock_value:.1f}")
            
            if stock_value > 10:
                stock_item.setBackground(QColor("#d5f5e3"))  # Green for high stock
            elif stock_value > 5:
                stock_item.setBackground(QColor("#f1f8ff"))  # Blue for medium stock
            else:
                stock_item.setBackground(QColor("#fadbd8"))  # Light red for low stock
                
            variants_table.setItem(row, 4, stock_item)
        
        variants_layout.addWidget(variants_table)
        variants_group.setLayout(variants_layout)
        layout.addWidget(variants_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        # Show dialog
        dialog.exec_()
    
    def showEvent(self, event):
        """Handle the dialog show event - ensure proper layout."""
        
        # Force image refresh when dialog is shown
        QTimer.singleShot(300, self.force_refresh_images)
        super().showEvent(event)
        
        # Fix any layout issues by forcing an update
        QTimer.singleShot(100, self.adjustVariantLayout)
        
        # Ensure images are refreshed when dialog appears, but only if we have valid data
        if hasattr(self, 'product_id') and self.product_id and hasattr(self, 'variants') and self.variants:
            try:
                # Check if first variant has a valid barcode
                first_variant = self.variants[0] if self.variants else None
                
                if first_variant and isinstance(first_variant, dict) and "barcode" in first_variant:
                    barcode = first_variant.get("barcode")
                    
                    # Validate that barcode is not empty or None
                    if barcode and isinstance(barcode, str) and len(barcode.strip()) > 0:
                        print(f"Will refresh images for barcode {barcode} after dialog appears")
                        
                        # Use a slightly longer delay to ensure API has time if called immediately after save
                        # Capture barcode in lambda's closure to avoid reference issues
                        # Using an explicit lambda parameter prevents issues with variable capture
                        QTimer.singleShot(500, lambda barcode_param=barcode: self.refresh_server_images(barcode_param))
                    else:
                        print(f"Invalid barcode format: '{barcode}', skipping image refresh")
                else:
                    print("First variant does not have a valid barcode, skipping image refresh")
            except Exception as e:
                print(f"Error in showEvent while preparing image refresh: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("No product ID or variants available, skipping image refresh")
    
    def refresh_server_images(self, barcode):
        """Refresh server images for a specific barcode and update the preview."""
        loading_label = None
        loading_msg = None
        # Initialize variables to prevent NameErrors
        preserved_local_images = []
        current_server_images = []
        error_occurred = False
        
        print(f"Starting refresh_server_images for barcode {barcode}")
        
        # IMPROVED: Create a reliable backup of local images first
        # Always make a backup of any existing local images by using the ensure method
        if hasattr(self, 'ensure_local_images_preserved') and callable(self.ensure_local_images_preserved):
            self.ensure_local_images_preserved()
            
        # Set up preserved_local_images for later use - always check both sources
        if hasattr(self, '_last_local_images') and self._last_local_images:
            preserved_local_images = self._last_local_images.copy()
            print(f"Using {len(preserved_local_images)} images from backup in refresh_server_images")
        
        # Also include current local images if available
        if hasattr(self, 'local_images') and self.local_images:
            # Add any local images not already in the preserved list
            current_local_filenames = {img.get('filename') for img in preserved_local_images if isinstance(img, dict)}
            for img in self.local_images:
                if isinstance(img, dict) and img.get('filename') not in current_local_filenames:
                    preserved_local_images.append(img.copy())
                    
            print(f"Combined preserved local images: {len(preserved_local_images)}")
            
        # Always update the backup with the most complete list
        if not hasattr(self, '_last_local_images'):
            self._last_local_images = []
        self._last_local_images = preserved_local_images.copy()
            
        # Backup current server images as fallback
        if hasattr(self, 'server_images') and self.server_images:
            current_server_images = self.server_images.copy()
        
        try:
            print(f"Attempting to refresh server images for barcode: {barcode}")
            
            # Import the image_format_detector (if available)
            try:
                from .image_format_detector import describe_image_response
                have_format_detector = True
            except ImportError:
                have_format_detector = False
                print("Image format detector not available")
            
            # Initialize/reset server_images first to avoid stale data if errors occur
            self.server_images = []
            
            # Check network connectivity first to provide better feedback
            if not self.check_network_status():
                # Update preview with empty list since no network, but still show local images
                self.update_image_preview(include_local=True)
                
                # Create an error message label
                error_label = QLabel("Network error: Cannot connect to server")
                error_label.setAlignment(Qt.AlignCenter)
                error_label.setStyleSheet("""
                    background-color: #ffecec;
                    color: #c0392b;
                    padding: 10px;
                    font-weight: bold;
                    border: 1px solid #e74c3c;
                    border-radius: 4px;
                """)
                
                # Add to image grid
                if hasattr(self, 'images_grid'):
                    self.images_grid.addWidget(error_label, 0, 0, 1, 4)  # span 4 columns
                    QApplication.processEvents()
                    
                # Set a timer to clear the error message after 3 seconds
                QTimer.singleShot(3000, lambda: self.safe_delete_later(error_label))
                return
            
            # Make the API call with minimal UI disruption - no loading dialog for fast operations
            images_data = None
            try:
                # Set a reasonable timeout (5 seconds)
                timeout_ms = 5000  # 5 seconds
                
                # Add network timeout to API client
                self.add_network_timeout_to_api_client()
                
                # Show loading indicators only if we expect the operation to take time
                start_time = QElapsedTimer()
                start_time.start()
                
                # Debug: Add enhanced logging before API call
                print(f"[IMAGE DEBUG] About to call get_product_images for barcode: {barcode}")
                
                # Make the API call with detailed debug logging
                images_data = self.api_client.get_product_images(barcode)
                
                # Debug: Log the response format in detail
                print(f"[IMAGE DEBUG] API Response type: {type(images_data)}")
                
                # Check if response is a dict with 'images' key (new format)
                if isinstance(images_data, dict) and 'images' in images_data:
                    image_list = images_data.get('images', [])
                    print(f"[IMAGE DEBUG] Number of images in dict format: {len(image_list)}")
                    if image_list and len(image_list) > 0:
                        first_item = image_list[0]
                        print(f"[IMAGE DEBUG] First image item type: {type(first_item)}")
                else:
                    # Legacy format - direct array
                    print(f"[IMAGE DEBUG] Number of images in legacy format: {len(images_data) if images_data else 0}")
                    if images_data and len(images_data) > 0:
                        first_item = images_data[0]
                        print(f"[IMAGE DEBUG] First item type: {type(first_item)}")
                        if isinstance(first_item, dict):
                            print(f"[IMAGE DEBUG] First item keys: {first_item.keys()}")
                        elif isinstance(first_item, str):
                            print(f"[IMAGE DEBUG] Image is a string: {first_item}")
            
                # Use non-blocking approach instead of QMessageBox
                has_images = False
                if isinstance(images_data, dict) and 'images' in images_data:
                    has_images = bool(images_data.get('images', []))
                elif images_data and isinstance(images_data, list):
                    has_images = len(images_data) > 0
                    
                if start_time.elapsed() > 300 and has_images:
                    # Create a temporary in-grid loading indicator instead of modal dialog
                    loading_label = QLabel("Loading images from server...")
                    loading_label.setAlignment(Qt.AlignCenter)
                    loading_label.setStyleSheet("""
                        background-color: #e8f5e9;
                        color: #2e7d32;
                        padding: 8px;
                        border: 1px solid #c8e6c9;
                        border-radius: 4px;
                    """)
                    if hasattr(self, 'images_grid'):
                        self.images_grid.addWidget(loading_label, 0, 0, 1, 4)
                        QApplication.processEvents()
                        
                    # Auto-cleanup this indicator after a reasonable timeout
                    QTimer.singleShot(5000, lambda: self.safe_delete_later(loading_label))
                else:
                    print(f"Fast response or no images for barcode {barcode}, skipping loading dialog")
            except Exception as api_err:
                print(f"API error during get_product_images: {str(api_err)}")
                import traceback
                traceback.print_exc()                # Enhanced debug information about API response
                print(f"API Response Type: {type(images_data)}")
                
                # Use the format detector if available
                if have_format_detector:
                    formatted_description = describe_image_response(images_data)
                    print(f"\n===== IMAGE RESPONSE FORMAT =====\n{formatted_description}\n===============================")
                else:
                    # Add extended debug info depending on response format
                    if isinstance(images_data, dict):
                        print(f"Response is a dictionary with keys: {list(images_data.keys())}")
                        image_list = images_data.get('images', [])
                        print(f"Number of images in dict format: {len(image_list)}")
                        if image_list and len(image_list) > 0:
                            first_img = image_list[0]
                            print(f"First image type: {type(first_img)}")
                            if isinstance(first_img, str):
                                print(f"Image URL: {first_img}")
                    elif isinstance(images_data, list) and images_data:
                        print(f"Response is a legacy list with {len(images_data)} items")
                        print(f"First image type: {type(images_data[0])}")
                        if isinstance(images_data[0], dict):
                            print("Image is a dictionary with keys:", list(images_data[0].keys()))
                            for key, value in images_data[0].items():
                                print(f"  {key}: {type(value)} = {value}")
                        elif isinstance(images_data[0], str):
                            print(f"Image is a string: {images_data[0]}")
                        else:
                            print(f"Image has unexpected type: {type(images_data[0])}")
                    
            # Continue with normal processing
            self.server_images = []  # Reset server images
            
            # Handle case where images_data is None or empty
            has_images = False
            if isinstance(images_data, dict) and 'images' in images_data:
                has_images = bool(images_data.get('images', []))
            elif images_data and isinstance(images_data, list):
                has_images = len(images_data) > 0
            
            if not has_images:
                self.ensure_loading_dialogs_closed()
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
                        QTimer.singleShot(5000, lambda: self.safe_delete_later(no_images_label))
                    except Exception as e:
                        print(f"Error adding no images label: {str(e)}")
            
            # Process valid images based on the response format
            if isinstance(images_data, dict) and 'images' in images_data:
                # New dictionary format with 'images' key
                image_list = images_data.get('images', [])
                main_image = images_data.get('main_image')
                print(f"Processing new format response with {len(image_list)} images")
                print(f"Main image: {main_image}")
                
                for img_url in image_list:
                    if img_url is not None:  # Skip None values
                        try:
                            fname = os.path.basename(img_url)
                            image_data = {"url": img_url, "filename": fname}
                            if main_image and img_url == main_image:
                                image_data["is_main"] = True
                            self.server_images.append(image_data)
                        except Exception as e:
                            print(f"Error processing image URL: {str(e)}")
                            error_occurred = True
            elif isinstance(images_data, list):
                # Legacy list format
                print(f"Processing legacy format response with {len(images_data)} images")
                for img in images_data:
                    if isinstance(img, dict) and "url" in img:
                        if "filename" not in img:
                            img["filename"] = os.path.basename(img["url"])
                        self.server_images.append(img)
                    elif img is not None:
                        try:
                            img_url = str(img)
                            fname = os.path.basename(img_url)
                            self.server_images.append({"url": img_url, "filename": fname})
                        except Exception as e:
                            print(f"Error processing image data: {str(e)}")
                            error_occurred = True
            
            # If no server images were found, use the previous ones as fallback
            if not self.server_images and current_server_images:
                print("No server images found in response, using previous server images as fallback")
                self.server_images = current_server_images
                
            # Check if we actually got any server images
            if not self.server_images:
                print("Warning: No server images found or processed")
                
            # Restore the preserved local images
            if preserved_local_images:
                # Keep track of which local images we'll need to restore
                # We'll identify uploaded images by filename and remove them from local_images
                if not hasattr(self, 'local_images') or self.local_images is None:
                    self.local_images = []
                else:
                    self.local_images.clear()
                
                print(f"Restoring {len(preserved_local_images)} preserved local images")
                
                # Check each preserved local image to see if it was uploaded to server
                for local_img in preserved_local_images:
                    local_filename = local_img.get('filename')
                    local_path = local_img.get('local_path')
                    
                    # Check if this local image is now on the server (by filename)
                    found_on_server = False
                    for server_img in self.server_images:
                        server_filename = server_img.get('filename')
                        if server_filename and local_filename and server_filename == local_filename:
                            found_on_server = True
                            print(f"Local image {local_filename} was uploaded to server, not restoring locally")
                            break
                    
                    # Only restore local images that aren't on the server yet
                    if not found_on_server and os.path.exists(local_path):
                        print(f"Restoring local image: {local_filename}")
                        self.local_images.append(local_img)
                    
            # Update the UI with both server and local images
            self.update_image_preview(include_local=True)
            print(f"Image refresh complete with {len(self.server_images)} server images and {len(self.local_images if hasattr(self, 'local_images') else [])} local images")
            
            # Show error message if needed
            if error_occurred:
                if hasattr(self, 'images_grid'):
                    error_label = QLabel("Some images failed to load. Please try refreshing.")
                    error_label.setStyleSheet("color: red; font-weight: bold;")
                    self.images_grid.addWidget(error_label, 0, 0, 1, 4)
                    QApplication.processEvents()
                    # Auto-remove after 3 seconds
                    QTimer.singleShot(3000, lambda: self.safe_delete_later(error_label))
            
        except Exception as e:
            print(f"Error in refresh_server_images: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc() 
            
            # Restore preserved local images on error
            if preserved_local_images and hasattr(self, 'local_images'):
                self.local_images = preserved_local_images
                
            # Use previous server images as fallback
            if current_server_images:
                self.server_images = current_server_images
            else:
                self.server_images = []  # Fallback to empty list if no previous images
                
            # Update UI to reflect error state but still include preserved local images
            self.update_image_preview(include_local=True)
            
        finally:
            # Clean up any UI elements
            if 'loading_label' in locals() and loading_label:
                try:
                    loading_label.setParent(None)
                    loading_label.deleteLater()
                except Exception:
                    pass
                    
            # Always ensure loading dialogs are closed to prevent UI blocking
            print("Ensuring all dialogs are closed in refresh_server_images")
            try:
                self.ensure_loading_dialogs_closed()
            except Exception as e:
                print(f"Error during final cleanup: {str(e)}")
    
    def delayed_image_refresh_with_local_preservation(self, barcode, timeout=10):
        """
        Refresh server images after upload while preserving local images.
        Unlike the standard refresh, this method doesn't clear local images.
        
        Args:
            barcode: The product barcode to fetch images for
            timeout: Timeout in seconds for API call
        """
        print(f"Refreshing images with local preservation for barcode: {barcode}")
        
        # Skip if barcode is None or empty
        if not barcode:
            print("No barcode provided to delayed_image_refresh_with_local_preservation, skipping")
            self.update_image_preview(include_local=True)  # Make sure to show local images
            self.ensure_loading_dialogs_closed()
            return
        
        # Use our improved method to ensure local images are preserved
        if hasattr(self, 'ensure_local_images_preserved'):
            self.ensure_local_images_preserved()
            
        # Keep a backup of local images to restore later
        preserved_local_images = []
        
        # Get preserved images from our backup first
        if hasattr(self, '_last_local_images') and self._last_local_images:
            preserved_local_images = [dict(img) for img in self._last_local_images if isinstance(img, dict)]
            print(f"Using {len(preserved_local_images)} images from backup")
            
        # Also check current local_images if available
        if hasattr(self, 'local_images') and self.local_images:
            # Get list of filenames already in preserved_local_images to avoid duplicates
            existing_filenames = {img.get('filename') for img in preserved_local_images if isinstance(img, dict)}
            
            # Add any local images that aren't already in the backup
            for img in self.local_images:
                if isinstance(img, dict) and img.get('filename') not in existing_filenames:
                    preserved_local_images.append(dict(img))
                    existing_filenames.add(img.get('filename'))
                    
            print(f"Total combined local images: {len(preserved_local_images)}")
            
            # Update our backup with the most complete set
            if not hasattr(self, '_last_local_images'):
                self._last_local_images = []
            self._last_local_images = [dict(img) for img in preserved_local_images if isinstance(img, dict)]
            
        # Also preserve any other current images as a fallback
        current_server_images = []
        if hasattr(self, 'server_images') and self.server_images:
            current_server_images = self.server_images.copy()
        
        # Show a loading indicator directly in the image grid
        loading_label = None
        if hasattr(self, 'images_grid'):
            try:
                loading_label = QLabel("Refreshing images...")
                loading_label.setAlignment(Qt.AlignCenter)
                loading_label.setStyleSheet("""
                    background-color: #e3f2fd; 
                    color: #1976d2; 
                    padding: 10px; 
                    border-radius: 4px;
                    font-weight: bold;
                    margin: 10px;
                """)
                self.images_grid.addWidget(loading_label, 0, 0, 1, 4)
                QApplication.processEvents()
            except Exception as e:
                print(f"Error adding loading indicator: {str(e)}")
                
        # Set safety timers to clean up UI
        for delay in [2000, 5000, 8000]:
            QTimer.singleShot(delay, self.ensure_loading_dialogs_closed)
            
        # Track if any errors occur during the process
        error_occurred = False
            
        try:
            # Add network timeout to prevent hanging
            self.add_network_timeout_to_api_client()
            
            # Fetch images from server
            print(f"Fetching images for {barcode} from server")
            images_data = self.api_client.get_product_images(barcode)
            
            # Process the server images
            self.server_images = []  # Only reset server images, not local ones
            
            # Log the image response format
            print(f"Server returned image data of type: {type(images_data)}")
            if isinstance(images_data, dict):
                print(f"Dictionary keys: {list(images_data.keys())}")
                
            # Process server images based on format
            if isinstance(images_data, dict) and 'images' in images_data:
                # New dictionary format
                image_list = images_data.get('images', [])
                main_image = images_data.get('main_image')
                print(f"Found {len(image_list)} server images")
                
                # Process all images in the list
                for img_url in image_list:
                    if img_url is not None:  # Skip None values
                        try:
                            fname = os.path.basename(img_url)
                            image_data = {"url": img_url, "filename": fname}
                            if main_image and img_url == main_image:
                                image_data["is_main"] = True
                            self.server_images.append(image_data)
                        except Exception as e:
                            print(f"Error processing image URL: {str(e)}")
                            error_occurred = True
            elif isinstance(images_data, list):
                # Legacy list format
                print(f"Found {len(images_data)} server images (legacy format)")
                for img in images_data:
                    if isinstance(img, dict) and "url" in img:
                        if "filename" not in img:
                            img["filename"] = os.path.basename(img["url"])
                        self.server_images.append(img)
                    elif img is not None:
                        try:
                            img_url = str(img)
                            fname = os.path.basename(img_url)
                            self.server_images.append({"url": img_url, "filename": fname})
                        except Exception as e:
                            print(f"Error processing image data: {str(e)}")
                            error_occurred = True
            
            # If no server images were found, use the previous ones as fallback
            if not self.server_images and current_server_images:
                print("No server images found in response, using previous server images as fallback")
                self.server_images = current_server_images
                
            # Check if we actually got any server images
            if not self.server_images:
                print("Warning: No server images found or processed")
                
            # Restore the preserved local images
            if preserved_local_images:
                # Keep track of which local images we'll need to restore
                # We'll identify uploaded images by filename and remove them from local_images
                if not hasattr(self, 'local_images') or self.local_images is None:
                    self.local_images = []
                else:
                    self.local_images.clear()
                
                print(f"Restoring {len(preserved_local_images)} preserved local images")
                
                # Check each preserved local image to see if it was uploaded to server
                for local_img in preserved_local_images:
                    local_filename = local_img.get('filename')
                    local_path = local_img.get('local_path')
                    
                    # Check if this local image is now on the server (by filename)
                    found_on_server = False
                    for server_img in self.server_images:
                        server_filename = server_img.get('filename')
                        if server_filename and local_filename and server_filename == local_filename:
                            found_on_server = True
                            print(f"Local image {local_filename} was uploaded to server, not restoring locally")
                            break
                    
                    # Only restore local images that aren't on the server yet
                    if not found_on_server and os.path.exists(local_path):
                        print(f"Restoring local image: {local_filename}")
                        self.local_images.append(local_img)
                    
            # Update the UI with both server and local images
            self.update_image_preview(include_local=True)
            print(f"Image refresh complete with {len(self.server_images)} server images and {len(self.local_images if hasattr(self, 'local_images') else [])} local images")
            
            # Show error message if needed
            if error_occurred:
                if hasattr(self, 'images_grid'):
                    error_label = QLabel("Some images failed to load. Please try refreshing.")
                    error_label.setStyleSheet("color: red; font-weight: bold;")
                    self.images_grid.addWidget(error_label, 0, 0, 1, 4)
                    QApplication.processEvents()
                    # Auto-remove after 3 seconds
                    QTimer.singleShot(3000, lambda: self.safe_delete_later(error_label))
            
        except Exception as e:
            print(f"Error in delayed_image_refresh_with_local_preservation: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Restore preserved local images on error
            if preserved_local_images and hasattr(self, 'local_images'):
                self.local_images = preserved_local_images
                
            # On error, make sure to update the UI anyway
            self.update_image_preview(include_local=True)
            
        finally:
            # Clean up the loading indicator
            if loading_label:
                try:
                    loading_label.setParent(None)
                    loading_label.deleteLater()
                    QApplication.processEvents()
                except Exception:
                    pass
                    
            # Always ensure dialogs are closed
            self.ensure_loading_dialogs_closed()
    
    def adjustVariantLayout(self):
        """Adjust the layout of variant inputs."""
        try:
            # Process pending events to ensure UI is responsive
            QApplication.processEvents()
            
            # Make sure any remaining dialogs are closed
            self.ensure_loading_dialogs_closed()
            
            # Update the variant_count_label if it exists
            if hasattr(self, 'variant_count_label') and self.variant_count_label:
                count = len(self.variants)
                if count > 0:
                    self.variant_count_label.setText(f"{count} variant{'s' if count > 1 else ''} added - You can edit price and stock levels directly in the table")
                else:
                    self.variant_count_label.setText("No variants added yet. Use 'Generate Variants' to create multiple variants.")
                
            # Note: Specific stock_input references were causing bugs, so we avoid direct manipulation
            
            print("Layout adjustment completed safely")
        except Exception as e:
            print(f"Error in adjustVariantLayout: {str(e)}")
            # Don't let exceptions block the UI
            pass
    
    def setupInputFocusHighlights(self):
        """Set up focus highlighting on all input fields for better UX."""
        for input_field in [self.name_input, self.description_input, self.barcode_prefix, 
                           self.size_input, self.color_input, self.quantity_input, 
                           self.price_input]:
            # Apply the focus style when focus is gained
            input_field.focusInEvent = lambda event, field=input_field: self.highlightField(field, event, True)
            # Remove the highlight when focus is lost
            input_field.focusOutEvent = lambda event, field=input_field: self.highlightField(field, event, False)
    
    def highlightField(self, field, event, highlight=True):
        """Apply or remove highlight from an input field."""
        original_event_handler = field.__class__.focusInEvent if highlight else field.__class__.focusOutEvent
        original_event_handler(field, event)
        
        if highlight:
            field.setStyleSheet(field.styleSheet() + "; border: 2px solid #3498db;")
        else:
            field.setStyleSheet(field.styleSheet().replace("; border: 2px solid #3498db;", ""))
    


    def delete_variant(self, variant_index):
        """Delete a variant from the variants list and update the table.
        
        Args:
            variant_index: Index of the variant in the variants list
        """
        if 0 <= variant_index < len(self.variants):
            variant = self.variants[variant_index]
            variant_id = variant.get("variant_id")
            
            # Ask for confirmation
            confirm = QMessageBox.question(
                self, 
                "Delete Variant", 
                f"Are you sure you want to delete this variant?\n\nSize: {variant['size']}\nColor: {variant['color']}\nBarcode: {variant['barcode']}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # If editing an existing product and variant has ID, flag for deletion on server
                if variant_id and self.product_id:
                    try:
                        self.api_client.delete_variant(variant_id)
                        print(f"Variant {variant_id} was deleted from the server")
                    except Exception as e:
                        print(f"Error deleting variant from server: {str(e)}")
                
                # Remove from local list
                self.variants.pop(variant_index)
                # Refresh the table
                self.update_variants_table()
                
                # Update variant count label
                count = len(self.variants)
                if count > 0:
                    self.variant_count_label.setText(f"{count} variant{'s' if count > 1 else ''} added - You can edit price and stock levels directly in the table")
                else:
                    self.variant_count_label.setText("No variants added yet. Use 'Generate Variants' to create multiple variants.")
                    self.variant_count_label.setStyleSheet("""
                        font-weight: bold; 
                        color: #e74c3c; 
                        font-size: 16px;
                        padding: 12px;
                        background-color: #fdf2f0;
                        border-radius: 4px;
                        border: 1px solid #fadbd8;
                        margin-bottom: 5px;
                    """)
        else:
            print(f"Invalid variant index: {variant_index}")
    
    def remove_local_image(self, img_data):
        """Remove a locally added image."""
        try:
            if not hasattr(self, 'local_images'):
                return
                
            local_path = img_data.get('local_path')
            if not local_path:
                return
            
            # Initialize deleted_images list if it doesn't exist
            if not hasattr(self, 'deleted_images'):
                self.deleted_images = []
            
            # Find and remove the image from local_images
            removed_image = None
            for i, image in enumerate(self.local_images):
                if image.get('local_path') == local_path:
                    removed_image = self.local_images.pop(i)
                    print(f"Removed local image: {local_path}")
                    break
            
            # If the image was previously uploaded and now removed, track it for backend sync
            if removed_image and not removed_image.get('new', True):
                # This was a local copy of a server image that's now being deleted
                # Keep a record so we can tell the backend to delete it
                self.deleted_images.append({
                    "filename": removed_image.get("filename"),
                    "local_path": local_path,
                    "deletion_time": time.time(),
                    "status": "pending_deletion",
                    "sync_status": "not_synced"
                })
                print(f"Added image to deletion tracking: {removed_image.get('filename')}")
            
            # Also remove from image_paths if it exists there
            if hasattr(self, 'image_paths') and local_path in self.image_paths:
                self.image_paths.remove(local_path)
            
            # Update the preview
            self.update_image_preview(include_local=True)
        except Exception as e:
            print(f"Error removing local image: {str(e)}")
    
    def remove_server_image(self, img_data):
        """Remove an image from the server."""
        try:
            # Print debug information about the image data format
            print("\n===== SERVER IMAGE DATA DEBUG =====")
            print(f"Image data type: {type(img_data)}")
            print(f"Image data content: {img_data}")
            
            # Extract filename and url based on the data type
            if isinstance(img_data, dict):
                url = img_data.get("url", "")
                filename = img_data.get("filename", os.path.basename(url) if url else "unknown.jpg")
                print(f"Dictionary format - URL: {url}, Filename: {filename}")
            elif isinstance(img_data, str):
                url = img_data
                filename = os.path.basename(url)
                print(f"String format - URL: {url}, Filename: {filename}")
            else:
                print(f"Unknown format - type: {type(img_data)}")
                return
            
            # Get barcode from the first variant if available
            barcode = None
            if self.variants and len(self.variants) > 0:
                barcode = self.variants[0].get("barcode", "")
            
            if not barcode:
                print("No barcode available to delete image")
                return
                
            print(f"Deleting image {filename} for barcode {barcode}")
            
            # Initialize deleted_images list if it doesn't exist
            if not hasattr(self, 'deleted_images'):
                self.deleted_images = []
                
            # Non-blocking indicator
            deleting_label = QLabel(f"Deleting {filename}...")
            deleting_label.setAlignment(Qt.AlignCenter)
            deleting_label.setStyleSheet("""
                background-color: #ffebee;
                color: #c62828;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            """)
            self.images_grid.addWidget(deleting_label, 0, 0, 1, 4)
            QApplication.processEvents()
            
            # Auto-remove after a reasonable timeout
            QTimer.singleShot(5000, lambda: self.safe_delete_later(deleting_label))
            
            # Delete the image
            success = self.delete_product_image_with_timeout(barcode, filename)
            
            if success:
                # Track deleted server images for reporting to backend
                self.deleted_images.append({
                    "filename": filename,
                    "url": url,
                    "barcode": barcode,
                    "deletion_time": time.time(),
                    "status": "deleted",
                    "sync_status": "synced",
                    "server_image": True
                })
                
                # Remove from server_images list
                self.server_images = [img for img in self.server_images 
                    if (isinstance(img, dict) and img.get("filename") != filename) or 
                   (isinstance(img, str) and os.path.basename(img) != filename)]
                
                # Refresh the image preview (include local images to ensure they're not lost)
                self.update_image_preview(include_local=True)
            else:
                # Show error message in the grid
                error_label = QLabel(f"Failed to delete {filename}")
                error_label.setStyleSheet("color: red; font-weight: bold;")
                self.images_grid.addWidget(error_label, 0, 0, 1, 4)
                QApplication.processEvents()
                # Auto-remove after 3 seconds
                QTimer.singleShot(3000, lambda: self.safe_delete_later(error_label))
        
            # Clean up the deleting label
            if 'deleting_label' in locals() and deleting_label:
                try:
                    deleting_label.hide()
                    deleting_label.setParent(None)
                    self.safe_delete_later(deleting_label)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error in remove_server_image: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
    
    def delete_product_image_with_timeout(self, barcode, image_filename, timeout=10):
        """Delete a product image with a timeout to avoid hanging."""
        try:
            # This assumes your api_client has a delete_product_image method
            # If it doesn't, you'll need to implement that too
            if not hasattr(self.api_client, 'delete_product_image'):
                print("API client does not support delete_product_image method.")
                return False
                
            # Create a variable to track timeout state and result
            result = {"success": False, "timed_out": False}
            
            # Define a function to handle timeout
            def on_timeout():
                result["timed_out"] = True
                print(f"Delete image operation timed out after {timeout} seconds")
            
            # Create a timer to handle timeout
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(on_timeout)
            timer.start(timeout * 1000)  # Convert to milliseconds
            
            # Try to delete the image
            result["success"] = self.api_client.delete_product_image(barcode, image_filename)
            
            # Cancel the timer if we're done
            timer.stop()
            
            # If we timed out, return False
            if result["timed_out"]:
                return False
                
            return result["success"]
        except Exception as e:
            print(f"Error deleting image with timeout: {str(e)}")
            return False
    
    def ensure_loading_dialogs_closed(self):
        """
        Safety method to ensure all loading dialogs are closed.
        This is a fail-safe to prevent hanging dialogs, especially when there are no images
        or when operations fail with exceptions.
        This method is EXTREMELY aggressive in finding and closing dialogs to prevent UI hangs.
        It will find and close ALL dialogs related to loading, refreshing, or product images.
        """
        try:
            # Increment attempt counter
            if not hasattr(self, 'dialog_closure_attempts'):
                self.dialog_closure_attempts = 0
            self.dialog_closure_attempts += 1
            print(f"Cleaning up: Closing all loading dialogs (attempt #{self.dialog_closure_attempts})")
            
            # Safety check for widget state - if we've been destroyed, do nothing
            if not self.isVisible():
                print("Dialog is no longer visible, skipping cleanup attempt")
                return
                
            # Find and track dialogs that need to be closed
            dialogs_to_close = []
            
            # Find all top-level widgets and identify any QMessageBox or QDialog related to loading 
            for widget in QApplication.topLevelWidgets():
                try:
                    if isinstance(widget, QMessageBox) or isinstance(widget, QDialog):
                        # Only target message boxes if they appear to be loading-related
                        if isinstance(widget, QMessageBox):
                            title = widget.windowTitle() if hasattr(widget, 'windowTitle') else ""
                            text = widget.text() if hasattr(widget, 'text') else ""
                            if ('loading' in title.lower() or 'loading' in text.lower() or
                                'refresh' in title.lower() or 'image' in title.lower() or 
                                'uploading' in title.lower()):
                                dialogs_to_close.append(widget)
                        # For problematic products, be more aggressive
                        elif hasattr(self, 'problematic_products'):
                            for prod in self.problematic_products:
                                if prod in widget.windowTitle():
                                    dialogs_to_close.append(widget)
                                    break
                except Exception:
                    pass
                    
            # Close all identified dialogs
            for dialog in dialogs_to_close:
                try:
                    dialog.reject()  # Try reject first
                except Exception:
                    try:
                        dialog.close()  # Then try close
                    except Exception:
                        pass
                    
            # Process events to allow dialog closures to complete
            QApplication.processEvents()

            # First, ensure no events are pending that might interfere
            try:
                QApplication.processEvents()
                QApplication.sendPostedEvents(None, 0)
                QApplication.processEvents()
            except Exception as event_err:
                print(f"Error processing events: {str(event_err)}")

            # Aggressively clean the images grid - find ANYTHING with loading text
            if hasattr(self, 'images_grid') and self.images_grid:
                try:
                    # Check if the layout is still valid by trying to access count()
                    grid_count = self.images_grid.count()
                except RuntimeError as e:
                    print(f"Warning: images_grid has been deleted or is invalid: {str(e)}")
                    grid_count = 0
                
                # Only clean loading indicators, don't close the dialog itself
                if grid_count > 0:
                    # First pass: remove any labels with loading text
                    try:
                        for i in range(grid_count):
                            try:
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widget = item.widget()
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
                    widgets_to_remove = []
                    try:
                        try:
                            current_count = self.images_grid.count()
                        except RuntimeError:
                            print("Grid layout was deleted during cleanup, skipping second pass")
                            current_count = 0
                        
                        if current_count > 0:
                            # Get all loading-related widgets to be removed
                            for i in range(current_count):
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widget = item.widget()
                                    # Only remove loading-related widgets, not "No images" labels
                                    if isinstance(widget, QLabel):
                                        try:
                                            label_text = widget.text().lower()
                                            if ('loading' in label_text or 'refreshing' in label_text):
                                                widgets_to_remove.append(widget)
                                        except:
                                            pass
                    except Exception as prep_err:
                        print(f"Error preparing widget list for removal: {str(prep_err)}")
                    
                    # Now actually remove the loading widgets
                    try:
                        for widget in widgets_to_remove:
                            try:
                                self.images_grid.removeWidget(widget)
                                widget.setParent(None)
                                widget.deleteLater()
                                QApplication.processEvents()
                            except Exception:
                                try:
                                    widget.hide()
                                except Exception:
                                    pass
                    except Exception as remove_err:
                        print(f"Error removing widgets: {str(remove_err)}")

            # Update image preview to refresh the UI state
            try:
                if hasattr(self, 'images_grid') and self.images_grid:
                    # For empty images, make sure we show a message
                    if not hasattr(self, 'server_images') or not self.server_images:
                        try:
                            # Check if we already have a "No images" label
                            has_no_images_label = False
                            for i in range(self.images_grid.count()):
                                item = self.images_grid.itemAt(i)
                                if item and item.widget() and isinstance(item.widget(), QLabel):
                                    if "no images available" in item.widget().text().lower():
                                        has_no_images_label = True
                                        break
                            
                            # If no "No images" label exists, add one
                            if not has_no_images_label:
                                no_images_label = QLabel("No images available for this product")
                                no_images_label.setAlignment(Qt.AlignCenter)
                                no_images_label.setStyleSheet("""
                                    background-color: #f5f5f5; 
                                    color: #757575; 
                                    padding: 15px; 
                                    border-radius: 5px;
                                    font-style: italic;
                                """)
                                self.images_grid.addWidget(no_images_label, 0, 0, 1, 4)
                        except Exception as e:
                            print(f"Error adding no images label: {str(e)}")
            except Exception as update_err:
                print(f"Error updating image preview after cleanup: {str(update_err)}")

            QApplication.processEvents()
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()

        except Exception as e:
            print(f"Error in ensure_loading_dialogs_closed: {str(e)}")
    
    def add_network_timeout_to_api_client(self):
        """
        Add network timeout settings to the API client if it doesn't already have them.
        This helps prevent UI freezes during network operations.
        """
        try:
            # Different approaches to add timeouts based on the API client implementation
            if hasattr(self.api_client, 'session'):
                # Most common case: requests library-based client
                if not hasattr(self.api_client.session, 'timeout') or not self.api_client.session.timeout:
                    # Set reasonable timeout values (connect_timeout, read_timeout)
                    self.api_client.session.timeout = (5, 10)
                    print("Added network timeout to API client session")
            
            # Additional approach: directly setting timeout on the client object
            if hasattr(self.api_client, 'timeout'):
                if not self.api_client.timeout:
                    self.api_client.timeout = 15  # seconds
                    print("Added timeout directly to API client")
                    
            # Add any other client-specific timeout settings here as needed
            
            # Set the local API client attribute as a fallback
            if not hasattr(self.api_client, '_has_timeout_configured'):
                self.api_client._has_timeout_configured = True
                print("Marked API client as having timeouts configured")
                
        except Exception as e:
            print(f"Error adding network timeout to API client: {str(e)}")
            # Even if it fails, try to continue - this is better than hanging the UI

    # Add a helper method at the class level for safe widget deletion
    def safe_delete_later(self, widget):
        """Safely delete a widget, checking first if it still exists.
        
        Args:
            widget: The widget to delete
        """
        if widget is None:
            return
            
        try:
            # Check if widget still exists
            if not sip.isdeleted(widget):
                widget.deleteLater()
        except (RuntimeError, AttributeError, Exception) as e:
            print(f"Error safely deleting widget: {str(e)}")
            pass  # Widget already deleted or invalid
    
    def ensure_local_images_preserved(self):
        """
        Makes sure that local images are preserved by backing them up.
        Called during image upload and refresh to prevent image loss.
        This is a critical method for maintaining image persistence.
        """
        # Initialize _last_local_images if it doesn't exist
        if not hasattr(self, '_last_local_images'):
            self._last_local_images = []
            
        # First make a backup if we have local images
        if hasattr(self, 'local_images') and self.local_images:
            # Only keep valid images in the backup 
            valid_images = []
            for img in self.local_images:
                if isinstance(img, dict) and 'local_path' in img:
                    if os.path.exists(img.get('local_path')):
                        # Create a deep copy to prevent reference issues
                        valid_images.append(dict(img))
            
            if valid_images:
                print(f"Backing up {len(valid_images)} valid local images")
                # Always update the backup with valid images
                self._last_local_images = valid_images
                return True
            else:
                print("No valid local images to back up")
        
        # Check if we already have a backup and if current local_images is empty
        elif hasattr(self, '_last_local_images') and self._last_local_images:
            # Verify backup images still exist
            valid_backup = []
            for img in self._last_local_images:
                if isinstance(img, dict) and 'local_path' in img:
                    if os.path.exists(img.get('local_path')):
                        valid_backup.append(dict(img))
            
            if valid_backup:
                print(f"Using {len(valid_backup)} existing backup images")
                # Make sure local_images exists
                if not hasattr(self, 'local_images'):
                    self.local_images = []
                # If local_images is empty, restore from backup
                if not self.local_images:
                    self.local_images = valid_backup
                return True
        
        # Initialize local_images if it doesn't exist
        if not hasattr(self, 'local_images'):
            self.local_images = []
            
        # Ensure we always return our current backup state
        return hasattr(self, '_last_local_images') and len(self._last_local_images) > 0
