"""
Images and Posts page for Shiakati Store POS application.
Allows management of product images and website visibility.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView,
    QFileDialog, QMessageBox, QSplitter, QSpacerItem, QSizePolicy,
    QAbstractItemView, QCompleter
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QBrush
import os
import requests
from io import BytesIO
from .product_image_dialog import ProductImageDialogosts page for Shiakati Store POS application.
Allows management of product images and website visibility.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView,
    QFileDialog, QMessageBox, QSplitter, QSpacerItem, QSizePolicy,
    QAbstractItemView, QCompleter
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QBrush
import os
import requests
from io import BytesIO

class ImagesPageMixin:
    """Mixin for the Images and Posts page."""
    
    def setup_images_page(self):
        """Set up the Images and Posts page."""
        layout = QVBoxLayout(self.images_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add page title
        title = QLabel("Images and Posts Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Add instruction label
        instruction_label = QLabel("📋 Double-click any product row to manage its images and website visibility")
        instruction_label.setStyleSheet("""
            color: #666; 
            font-size: 14px; 
            padding: 10px; 
            background-color: #f8f9fa; 
            border: 1px solid #dee2e6; 
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(instruction_label)
        
        # Top toolbar with search and refresh
        toolbar_layout = QHBoxLayout()
        
        # Search label
        search_label = QLabel("Search Products:")
        search_label.setFixedWidth(120)
        toolbar_layout.addWidget(search_label)
        
        # Search input
        self.image_search_input = QComboBox()
        self.image_search_input.setEditable(True)
        self.image_search_input.setMinimumWidth(300)
        self.image_search_input.setInsertPolicy(QComboBox.NoInsert)
        self.image_search_input.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.image_search_input.editTextChanged.connect(self.filter_products_table)
        toolbar_layout.addWidget(self.image_search_input)
        
        toolbar_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Products")
        refresh_btn.clicked.connect(self.load_products_for_images)
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Main splitter to divide products table and image management
        main_splitter = QSplitter(Qt.Vertical)
        
        # Products table (make it bigger)
        self.setup_products_table()
        main_splitter.addWidget(self.products_table)
        
        # Splitter to divide images section and website visibility section
        splitter = QSplitter(Qt.Vertical)
        
        # Images section
        images_widget = QWidget()
        images_layout = QVBoxLayout(images_widget)
        images_layout.setContentsMargins(0, 0, 0, 0)
        
        # Upload image button
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton("📷 Upload New Image")
        upload_btn.clicked.connect(self.upload_product_image)
        upload_layout.addWidget(upload_btn)
        
        # Set as main image checkbox
        self.set_as_main_checkbox = QCheckBox("Set as Main Product Image")
        upload_layout.addWidget(self.set_as_main_checkbox)
        upload_layout.addStretch()
        
        images_layout.addLayout(upload_layout)
        
        # Image preview area
        self.image_preview_layout = QHBoxLayout()
        self.image_preview_layout.setAlignment(Qt.AlignLeft)
        images_layout.addLayout(self.image_preview_layout)
        
        # Add a placeholder text for when there are no images (separate from preview layout)
        self.no_images_label = QLabel("No images available for this product")
        self.no_images_label.setStyleSheet("color: gray; font-size: 16px;")
        self.no_images_label.setAlignment(Qt.AlignCenter)
        # Add to main images layout instead of preview layout to prevent deletion
        images_layout.addWidget(self.no_images_label)
        self.images_layout = images_layout  # Keep reference to recreate label if needed
        
        splitter.addWidget(images_widget)
        
        # Website visibility section
        visibility_widget = QWidget()
        visibility_layout = QVBoxLayout(visibility_widget)
        visibility_layout.setContentsMargins(0, 0, 0, 0)
        
        # Website visibility title
        visibility_title = QLabel("Website Visibility")
        visibility_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        visibility_layout.addWidget(visibility_title)
        
        # Show on website checkbox
        visibility_controls = QHBoxLayout()
        self.show_on_website_checkbox = QCheckBox("Show this product on the website")
        self.show_on_website_checkbox.stateChanged.connect(self.toggle_product_visibility)
        visibility_controls.addWidget(self.show_on_website_checkbox)
        visibility_controls.addStretch()
        
        # Save button
        save_visibility_btn = QPushButton("💾 Save Visibility Setting")
        save_visibility_btn.clicked.connect(self.save_product_visibility)
        visibility_controls.addWidget(save_visibility_btn)
        
        visibility_layout.addLayout(visibility_controls)
        
        # Add note about main image
        note_label = QLabel("Note: Products need a main image to be displayed properly on the website.")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        visibility_layout.addWidget(note_label)
        
        splitter.addWidget(visibility_widget)
        
        # Set default sizes for the splitter sections (70% images, 30% visibility)
        splitter.setSizes([700, 300])
        
        # Add image management splitter to main splitter
        main_splitter.addWidget(splitter)
        
        # Set sizes: 75% for products table, 25% for image management (bigger table)
        main_splitter.setSizes([750, 250])
        
        layout.addWidget(main_splitter)
        
        # Load products on init
        self.load_products_for_images()
        
    def setup_products_table(self):
        """Set up the products table for image management."""
        self.products_table = QTableWidget()
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.products_table.doubleClicked.connect(self.on_product_selected)
        self.products_table.setAlternatingRowColors(True)
        
        # Set minimum height to make table more prominent (increased from 400 to 500)
        self.products_table.setMinimumHeight(500)
        
        # Improve table styling
        self.products_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8f9fa;
                background-color: white;
                selection-background-color: #007acc;
                selection-color: white;
                gridline-color: #ddd;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                padding: 10px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # Set up columns
        columns = ["ID", "Product Name", "Category", "Variants", "Has Images", "Website Visible"]
        self.products_table.setColumnCount(len(columns))
        self.products_table.setHorizontalHeaderLabels(columns)
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.products_table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.products_table.setColumnWidth(0, 60)  # ID
        self.products_table.setColumnWidth(2, 150)  # Category
        self.products_table.setColumnWidth(3, 80)  # Variants
        self.products_table.setColumnWidth(4, 100)  # Has Images
        self.products_table.setColumnWidth(5, 120)  # Website Visible
        
    def load_products_for_images(self):
        """Load all products into the products table."""
        try:
            # Clear existing table and search
            self.products_table.setRowCount(0)
            self.image_search_input.clear()
            
            # Set cursor to wait
            self.setCursor(Qt.WaitCursor)
            
            print("Loading products for images page...")
            
            # Get unique products (not variants) using the proper API endpoint
            products = []
            try:
                # Try to get products directly from /products endpoint
                import requests
                
                # Ensure we have a valid API client
                if not hasattr(self, 'api_client') or not self.api_client:
                    raise Exception("API client not available")
                
                print(f"Making request to: {self.api_client.base_url}/products")
                response = requests.get(
                    f"{self.api_client.base_url}/products?limit=1000",
                    headers=self.api_client.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    products = response.json()
                    print(f"Successfully loaded {len(products)} products from /products endpoint")
                elif response.status_code == 401:
                    print("Authentication failed, trying to re-authenticate...")
                    if hasattr(self.api_client, '_handle_auth_error'):
                        self.api_client._handle_auth_error(response)
                        # Retry after authentication
                        response = requests.get(
                            f"{self.api_client.base_url}/products?limit=1000",
                            headers=self.api_client.get_headers(),
                            timeout=10
                        )
                        if response.status_code == 200:
                            products = response.json()
                            print(f"Successfully loaded {len(products)} products after re-auth")
                else:
                    print(f"Products endpoint failed with status {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"Error with direct API call: {str(e)}")
                
            # Fallback to API client methods if direct call failed
            if not products:
                try:
                    print("Trying fallback methods...")
                    # Try using API client methods
                    if hasattr(self.api_client, 'get_products') and callable(self.api_client.get_products):
                        products = self.api_client.get_products()
                        print(f"Loaded {len(products) if products else 0} products using api_client.get_products()")
                    elif hasattr(self.api_client, 'get_combined_inventory') and callable(self.api_client.get_combined_inventory):
                        all_data = self.api_client.get_combined_inventory()
                        if all_data:
                            # Extract unique products by ID
                            products_dict = {}
                            for item in all_data:
                                product_id = item.get('product_id') or item.get('id')
                                if product_id and product_id not in products_dict:
                                    # Create a product object from the variant data
                                    product = {
                                        'id': product_id,
                                        'name': item.get('product_name', 'Unknown Product'),
                                        'category_name': item.get('category', 'Uncategorized'),
                                        'variants_count': 1,  # Will be updated below
                                        'image_url': item.get('image_url'),
                                        'show_on_website': item.get('show_on_website', 0)
                                    }
                                    products_dict[product_id] = product
                                elif product_id in products_dict:
                                    # Update variant count
                                    products_dict[product_id]['variants_count'] += 1
                            
                            products = list(products_dict.values())
                            print(f"Extracted {len(products)} unique products from combined inventory")
                        else:
                            products = []
                except Exception as fallback_error:
                    print(f"Fallback methods also failed: {str(fallback_error)}")
                    products = []
            
            if not products:
                self.setCursor(Qt.ArrowCursor)
                # Show compact error message
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText("Failed to load products")
                msg.setIcon(QMessageBox.Warning)
                msg.setFixedSize(220, 120)
                msg.exec_()
                return
                
            # Add product search suggestions
            product_names = set()
            categories = set()
            
            # Store data for table
            rows = []
            
            # Process products for table display
            for product in products:
                product_id = product.get('id')
                if not product_id:  # Skip if no ID
                    continue
                    
                product_name = product.get('name', 'Unknown Product')
                category_name = product.get('category_name', 'Uncategorized')
                variants_count = str(product.get('variants_count', 0))
                show_on_website = product.get('show_on_website', 0)
                
                # Add to search suggestions
                if product_name:
                    product_names.add(product_name)
                if category_name:
                    categories.add(category_name)
                
                # Check if product has images
                has_images = False
                main_image_url = product.get('image_url')
                if main_image_url and main_image_url != "None" and main_image_url.strip():
                    has_images = True
                    
                rows.append({
                    'id': product_id,
                    'name': product_name,
                    'category': category_name,
                    'variants': variants_count,
                    'has_images': has_images,
                    'show_on_website': show_on_website == 1
                })
            
            # Add search suggestions
            self.image_search_input.addItems(sorted(list(product_names)))
            self.image_search_input.addItems(sorted(list(categories)))
            
            # Fill table with data
            self.products_table.setRowCount(len(rows))
            for row_idx, product in enumerate(rows):
                # ID Column
                id_item = QTableWidgetItem(str(product['id']))
                self.products_table.setItem(row_idx, 0, id_item)
                
                # Product Name
                name_item = QTableWidgetItem(product['name'])
                self.products_table.setItem(row_idx, 1, name_item)
                
                # Category
                category_item = QTableWidgetItem(product['category'])
                self.products_table.setItem(row_idx, 2, category_item)
                
                # Variants count
                variants_item = QTableWidgetItem(product['variants'])
                variants_item.setTextAlignment(Qt.AlignCenter)
                self.products_table.setItem(row_idx, 3, variants_item)
                
                # Has Images
                has_images_item = QTableWidgetItem()
                has_images_item.setTextAlignment(Qt.AlignCenter)
                if product['has_images']:
                    has_images_item.setText("✔️")
                    has_images_item.setForeground(QBrush(QColor("#2e7d32")))
                else:
                    has_images_item.setText("❌")
                    has_images_item.setForeground(QBrush(QColor("#c62828")))
                self.products_table.setItem(row_idx, 4, has_images_item)
                
                # Website Visible
                visible_item = QTableWidgetItem()
                visible_item.setTextAlignment(Qt.AlignCenter)
                if product['show_on_website']:
                    visible_item.setText("✔️ Visible")
                    visible_item.setForeground(QBrush(QColor("#2e7d32")))
                else:
                    visible_item.setText("❌ Hidden")
                    visible_item.setForeground(QBrush(QColor("#c62828")))
                self.products_table.setItem(row_idx, 5, visible_item)
            
            # Clear any previously loaded images
            self.clear_image_previews()
            if hasattr(self, 'no_images_label') and self.no_images_label:
                try:
                    self.no_images_label.setVisible(True)
                except RuntimeError:
                    pass  # Widget deleted
            if hasattr(self, 'show_on_website_checkbox') and self.show_on_website_checkbox:
                try:
                    self.show_on_website_checkbox.setChecked(False)
                except RuntimeError:
                    pass  # Widget deleted
            
            # Reset cursor
            self.setCursor(Qt.ArrowCursor)
            
        except Exception as e:
            self.setCursor(Qt.ArrowCursor)
            # Show compact error message
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Load failed: {str(e)}")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(250, 120)
            msg.exec_()
    
    def filter_products_table(self, text):
        """Filter the products table based on search text."""
        text = text.lower()
        for row in range(self.products_table.rowCount()):
            match = False
            
            # Check product name (column 1)
            product_name = self.products_table.item(row, 1).text().lower()
            if text in product_name:
                match = True
                
            # Check category (column 2)
            category = self.products_table.item(row, 2).text().lower()
            if text in category:
                match = True
                
            # Show/hide row based on match
            self.products_table.setRowHidden(row, not match)
    
    def on_product_selected(self, index):
        """Handle product selection from the table."""
        try:
            row = index.row()
            if row < 0 or row >= self.products_table.rowCount():
                return
                
            product_id_item = self.products_table.item(row, 0)
            if not product_id_item:
                return
                
            product_id = int(product_id_item.text())
            self.selected_product_id = product_id
            self.load_product_images(product_id)
        except Exception as e:
            print(f"Error in on_product_selected: {str(e)}")
        
    def load_product_images(self, product_id):
        """Load images for the selected product."""
        if not product_id:
            try:
                self.clear_image_previews()
                self.show_no_images_label()
                if hasattr(self, 'show_on_website_checkbox') and self.show_on_website_checkbox:
                    try:
                        self.show_on_website_checkbox.setChecked(False)
                    except RuntimeError:
                        pass
            except Exception as e:
                print(f"Error in load_product_images (empty): {str(e)}")
            return
            
        try:
            # Get product details to check visibility status
            try:
                product = self.api_client.get_product_by_id(product_id)
                if product and hasattr(self, 'show_on_website_checkbox') and self.show_on_website_checkbox:
                    try:
                        self.show_on_website_checkbox.setChecked(product.get('show_on_website', 0) == 1)
                    except RuntimeError:
                        pass  # Widget deleted
            except Exception as e:
                print(f"Warning: Could not load product details: {str(e)}")
                if hasattr(self, 'show_on_website_checkbox') and self.show_on_website_checkbox:
                    try:
                        self.show_on_website_checkbox.setChecked(False)
                    except RuntimeError:
                        pass  # Widget deleted
            
            # Get images for this product
            images = self.api_client.get_product_images_by_id(product_id)
            
            # Clear existing previews
            self.clear_image_previews()
            
            if not images or len(images) == 0:
                self.show_no_images_label()
                return
                
            if hasattr(self, 'no_images_label') and self.no_images_label:
                try:
                    self.no_images_label.setVisible(False)
                except RuntimeError:
                    pass  # Widget deleted
            
            # Add image previews
            for img in images:
                try:
                    self.add_image_preview(img['image_url'], img['is_main'])
                except Exception as img_error:
                    print(f"Error adding image preview: {str(img_error)}")
                    continue
                
        except Exception as e:
            print(f"Error in load_product_images: {str(e)}")
            self.show_no_images_label()

    def show_no_images_label(self):
        """Safely show or recreate the no_images_label if it was deleted."""
        try:
            if not hasattr(self, 'no_images_label') or self.no_images_label is None:
                self.no_images_label = QLabel("No images available for this product")
                self.no_images_label.setStyleSheet("color: gray; font-size: 16px;")
                self.no_images_label.setAlignment(Qt.AlignCenter)
                # Add to main images layout if not already present
                if hasattr(self, 'images_layout'):
                    self.images_layout.addWidget(self.no_images_label)
            self.no_images_label.setVisible(True)
        except RuntimeError:
            # If label was deleted, recreate and add again
            self.no_images_label = QLabel("No images available for this product")
            self.no_images_label.setStyleSheet("color: gray; font-size: 16px;")
            self.no_images_label.setAlignment(Qt.AlignCenter)
            if hasattr(self, 'images_layout'):
                self.images_layout.addWidget(self.no_images_label)
            self.no_images_label.setVisible(True)
    
    def clear_image_previews(self):
        """Clear all image previews."""
        try:
            # Show the no images label using the safe helper
            self.show_no_images_label()
            # Remove all widgets from the image preview layout safely
            widgets_to_delete = []
            while self.image_preview_layout.count():
                item = self.image_preview_layout.takeAt(0)
                if item and item.widget():
                    widget = item.widget()
                    # Don't delete the no_images_label even if it's somehow in this layout
                    if hasattr(self, 'no_images_label') and widget == self.no_images_label:
                        continue
                    widget.setParent(None)
                    widgets_to_delete.append(widget)
            for widget in widgets_to_delete:
                try:
                    widget.deleteLater()
                except RuntimeError:
                    pass
        except Exception as e:
            print(f"Error clearing image previews: {str(e)}")
    
    def add_image_preview(self, image_url, is_main=False):
        """Add an image preview to the layout."""
        try:
            # Create a container for the image and its controls
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            
            # Create image label
            image_label = QLabel()
            image_label.setFixedSize(150, 150)
            image_label.setStyleSheet("""
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            """)
            image_label.setScaledContents(True)
            image_label.setAlignment(Qt.AlignCenter)
            
            # Load image from URL
            image_data = self.load_image_from_url(image_url)
            if image_data:
                pixmap = QPixmap.fromImage(image_data)
                image_label.setPixmap(pixmap)
            else:
                # Show placeholder if image can't be loaded
                image_label.setText("Image\nNot\nAvailable")
                image_label.setAlignment(Qt.AlignCenter)
            
            # Add main image indicator if applicable
            if is_main:
                main_label = QLabel("Main Image")
                main_label.setStyleSheet("color: green; font-weight: bold;")
                main_label.setAlignment(Qt.AlignCenter)
                container_layout.addWidget(main_label)
                
                # Also add a border to highlight the main image
                image_label.setStyleSheet("""
                    border: 3px solid #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: white;
                """)
            
            container_layout.addWidget(image_label)
            
            # Add buttons for actions
            buttons_layout = QHBoxLayout()
            
            # Set as main button (only if not already main)
            if not is_main:
                set_main_btn = QPushButton("Set as Main")
                set_main_btn.setFixedHeight(30)
                set_main_btn.clicked.connect(lambda checked, url=image_url: self.set_main_image(url))
                buttons_layout.addWidget(set_main_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedHeight(30)
            delete_btn.setFixedWidth(30)
            delete_btn.clicked.connect(lambda checked, url=image_url: self.delete_image(url))
            buttons_layout.addWidget(delete_btn)
            
            container_layout.addLayout(buttons_layout)
            
            # Add to the image preview layout
            self.image_preview_layout.addWidget(container)
            
        except Exception as e:
            print(f"Error adding image preview: {str(e)}")
    
    def load_image_from_url(self, url):
        """Load an image from a URL."""
        try:
            # If it's a relative URL, make it absolute
            if url.startswith('/'):
                url = f"{self.api_client.base_url}{url}"
                
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                image = QImage()
                image.loadFromData(response.content)
                return image
            return None
        except Exception as e:
            print(f"Error loading image from URL {url}: {str(e)}")
            return None
    
    def upload_product_image(self):
        """Upload a new image for the selected product."""
        if not hasattr(self, 'selected_product_id'):
            # Show compact warning
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Please select a product first\nby double-clicking on a row")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(250, 120)
            msg.exec_()
            return
            
        product_id = self.selected_product_id
            
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.webp *.gif)"
        )
        
        if not file_path:
            return  # User canceled
            
        try:
            # Show compact uploading message
            msg = QMessageBox(self)
            msg.setWindowTitle("Upload")
            msg.setText("Uploading image...")
            msg.setStandardButtons(QMessageBox.NoButton)
            msg.setFixedSize(200, 100)
            msg.show()
            
            # Upload the image
            set_as_main = self.set_as_main_checkbox.isChecked()
            result = self.api_client.upload_product_image(product_id, file_path, set_as_main)
            
            if result:
                msg.close()
                # Show compact success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Image uploaded!")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setFixedSize(200, 120)
                success_msg.exec_()
                
                # Reload images
                self.load_product_images(product_id)
                
                # Update table to show that product now has images
                self.update_product_image_status(product_id, True)
            else:
                msg.close()
                # Show compact error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to upload image")
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.setFixedSize(200, 120)
                error_msg.exec_()
                
        except Exception as e:
            if 'msg' in locals():
                msg.close()
            # Show compact error message
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText(f"Upload failed: {str(e)}")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setFixedSize(250, 120)
            error_msg.exec_()
    
    def set_main_image(self, image_url):
        """Set an image as the main image for the product."""
        if not hasattr(self, 'selected_product_id'):
            # Show compact warning
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Please select a product first")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(220, 120)
            msg.exec_()
            return
            
        product_id = self.selected_product_id
        if not product_id or not image_url:
            return
            
        try:
            result = self.api_client.set_main_product_image(product_id, image_url)
            if result:
                # Reload images to show updated main image
                self.load_product_images(product_id)
                
                # Update product has images status in table (just to be sure)
                self.update_product_image_status(product_id, True)
            else:
                # Show compact error message
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText("Failed to set as main image")
                msg.setIcon(QMessageBox.Warning)
                msg.setFixedSize(220, 120)
                msg.exec_()
                
        except Exception as e:
            # Show compact error message
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Set main failed: {str(e)}")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(250, 120)
            msg.exec_()
    
    def delete_image(self, image_url):
        """Delete an image from the product."""
        if not hasattr(self, 'selected_product_id'):
            # Show compact warning
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Please select a product first")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(220, 120)
            msg.exec_()
            return
            
        product_id = self.selected_product_id
        if not product_id or not image_url:
            return
            
        # Confirm deletion with compact dialog
        confirm_msg = QMessageBox(self)
        confirm_msg.setWindowTitle("Confirm")
        confirm_msg.setText("Delete this image?")
        confirm_msg.setIcon(QMessageBox.Question)
        confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_msg.setDefaultButton(QMessageBox.No)
        confirm_msg.setFixedSize(200, 120)
        
        if confirm_msg.exec_() == QMessageBox.No:
            return
            
        try:
            result = self.api_client.delete_product_image(product_id, image_url)
            if result:
                # Reload images
                self.load_product_images(product_id)
                
                # Check if this was the last image
                images = self.api_client.get_product_images_by_id(product_id)
                if not images or len(images) == 0:
                    # Update status in the table to reflect no images
                    self.update_product_image_status(product_id, False)
            else:
                # Show compact error message
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText("Failed to delete image")
                msg.setIcon(QMessageBox.Warning)
                msg.setFixedSize(200, 120)
                msg.exec_()
                
        except Exception as e:
            # Show compact error message
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Delete failed: {str(e)}")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(250, 120)
            msg.exec_()
    
    def toggle_product_visibility(self):
        """Toggle the product visibility preview."""
        # This just toggles the UI checkbox, actual saving happens with the save button
        pass
    
    def save_product_visibility(self):
        """Save the product visibility setting."""
        if not hasattr(self, 'selected_product_id'):
            # Show compact warning
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Please select a product first")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(220, 120)
            msg.exec_()
            return
            
        product_id = self.selected_product_id
        if not product_id:
            # Show compact warning
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Please select a product first")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(220, 120)
            msg.exec_()
            return
            
        try:
            # Get the checkbox state (0 = hidden, 1 = visible)
            visibility = 1 if self.show_on_website_checkbox.isChecked() else 0
            
            result = self.api_client.update_product_visibility(product_id, visibility)
            if result:
                # Show compact success message
                msg = QMessageBox(self)
                msg.setWindowTitle("Success")
                msg.setText("Visibility updated!")
                msg.setIcon(QMessageBox.Information)
                msg.setFixedSize(200, 120)
                msg.exec_()
                
                # Update the visibility status in the table
                self.update_product_visibility_status(product_id, visibility == 1)
            else:
                # Show compact error message
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText("Failed to update visibility")
                msg.setIcon(QMessageBox.Warning)
                msg.setFixedSize(220, 120)
                msg.exec_()
                
        except Exception as e:
            # Show compact error message
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Update failed: {str(e)}")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(250, 120)
            msg.exec_()
    
    def update_product_image_status(self, product_id, has_images):
        """Update the image status for a product in the table."""
        try:
            for row in range(self.products_table.rowCount()):
                if int(self.products_table.item(row, 0).text()) == product_id:
                    # Update "Has Images" column (column 4)
                    has_images_item = QTableWidgetItem()
                    has_images_item.setTextAlignment(Qt.AlignCenter)
                    if has_images:
                        has_images_item.setText("✔️")
                        has_images_item.setForeground(QBrush(QColor("#2e7d32")))
                    else:
                        has_images_item.setText("❌")
                        has_images_item.setForeground(QBrush(QColor("#c62828")))
                    self.products_table.setItem(row, 4, has_images_item)
                    break
        except Exception as e:
            print(f"Error updating product image status: {str(e)}")
    
    def update_product_visibility_status(self, product_id, is_visible):
        """Update the visibility status for a product in the table."""
        try:
            for row in range(self.products_table.rowCount()):
                if int(self.products_table.item(row, 0).text()) == product_id:
                    # Update the "Website Visible" column (column 5)
                    visible_item = QTableWidgetItem()
                    visible_item.setTextAlignment(Qt.AlignCenter)
                    if is_visible:
                        visible_item.setText("✔️ Visible")
                        visible_item.setForeground(QBrush(QColor("#2e7d32")))
                    else:
                        visible_item.setText("❌ Hidden")
                        visible_item.setForeground(QBrush(QColor("#c62828")))
                    self.products_table.setItem(row, 5, visible_item)
                    break
        except Exception as e:
            print(f"Error updating product visibility status: {str(e)}")
