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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
import requests
from .product_image_dialog import ProductImageDialog


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
        instruction_label = QLabel("📋 Double-click any product row to open the image management window")
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
        # Add tooltip
        refresh_btn.setToolTip("Refresh product list and update image/visibility status")
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Products table (full width now)
        self.setup_products_table()
        layout.addWidget(self.products_table)
        
        # Load products on init
        self.load_products_for_images()
        
    def setup_products_table(self):
        """Set up the products table for image management."""
        self.products_table = QTableWidget()
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.products_table.doubleClicked.connect(self.open_image_dialog)
        self.products_table.setAlternatingRowColors(True)
        
        # Set minimum height
        self.products_table.setMinimumHeight(600)
        
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
            
            # Clear API cache to ensure we get fresh data
            if hasattr(self.api_client, 'clear_cache'):
                self.api_client.clear_cache()
            
            # Set cursor to wait
            self.setCursor(Qt.WaitCursor)
            
            print("Loading products for images page...")
            
            # Get unique products using API client
            products = []
            try:
                if hasattr(self.api_client, 'get_products') and callable(self.api_client.get_products):
                    products = self.api_client.get_products()
                    print(f"Loaded {len(products) if products else 0} products")
                else:
                    # Fallback to combined inventory
                    all_data = self.api_client.get_combined_inventory()
                    if all_data:
                        # Extract unique products by ID
                        products_dict = {}
                        for item in all_data:
                            product_id = item.get('product_id') or item.get('id')
                            if product_id and product_id not in products_dict:
                                product = {
                                    'id': product_id,
                                    'name': item.get('product_name', 'Unknown Product'),
                                    'category_name': item.get('category', 'Uncategorized'),
                                    'variants_count': 1,
                                    'image_url': item.get('image_url'),
                                    'show_on_website': item.get('show_on_website', 0)
                                }
                                products_dict[product_id] = product
                            elif product_id in products_dict:
                                products_dict[product_id]['variants_count'] += 1
                        
                        products = list(products_dict.values())
                        print(f"Extracted {len(products)} unique products from inventory")
                        
            except Exception as e:
                print(f"Error loading products: {str(e)}")
                products = []
            
            if not products:
                self.setCursor(Qt.ArrowCursor)
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
            
            # Process products for table display - get fresh data for each product
            rows = []
            for product in products:
                product_id = product.get('id')
                if not product_id:
                    continue
                
                try:
                    # Get fresh product data to ensure we have latest visibility status
                    fresh_product = self.api_client.get_product_by_id(product_id)
                    if fresh_product:
                        product = fresh_product  # Use the fresh data
                except Exception as e:
                    print(f"Warning: Could not get fresh data for product {product_id}: {str(e)}")
                    # Continue with the original product data as fallback
                    
                product_name = product.get('name', 'Unknown Product')
                category_name = product.get('category_name', 'Uncategorized')
                variants_count = str(product.get('variants_count', 0))
                show_on_website = product.get('show_on_website', 0)
                
                # Debug logging for visibility
                print(f"Product {product_id} ({product_name}): show_on_website = {show_on_website} (type: {type(show_on_website)})")
                
                # Add to search suggestions
                if product_name:
                    product_names.add(product_name)
                if category_name:
                    categories.add(category_name)
                
                # Check if product has images using the proper API method
                has_images = False
                try:
                    # Use the dedicated API method to check for images
                    product_images = self.api_client.get_product_images_by_id(product_id)
                    has_images = bool(product_images and len(product_images) > 0)
                    print(f"Product {product_id}: Found {len(product_images) if product_images else 0} images via API")
                except Exception as e:
                    print(f"Error checking images for product {product_id}: {str(e)}")
                    # Fallback to checking the main image URL
                    main_image_url = product.get('image_url')
                    if main_image_url and main_image_url != "None" and main_image_url.strip():
                        has_images = True
                        print(f"Product {product_id}: Fallback found main image: {main_image_url}")
                    else:
                        print(f"Product {product_id}: No images found (fallback)")
                    
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
            
            # Reset cursor
            self.setCursor(Qt.ArrowCursor)
            
        except Exception as e:
            self.setCursor(Qt.ArrowCursor)
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
    
    def open_image_dialog(self, index):
        """Open the image management dialog for the selected product."""
        try:
            row = index.row()
            if row < 0 or row >= self.products_table.rowCount():
                return
                
            # Get product info
            product_id_item = self.products_table.item(row, 0)
            product_name_item = self.products_table.item(row, 1)
            
            if not product_id_item or not product_name_item:
                return
                
            product_id = int(product_id_item.text())
            product_name = product_name_item.text()
            
            # Open the image management dialog
            dialog = ProductImageDialog(self, self.api_client, product_id, product_name)
            
            # Show dialog and refresh table when closed
            if dialog.exec_() == dialog.Accepted:
                # Refresh the specific row first
                self.refresh_product_row(row, product_id)
                # Also clear the cache to ensure fresh data on next full refresh
                if hasattr(self.api_client, 'clear_cache'):
                    self.api_client.clear_cache()
                
        except Exception as e:
            print(f"Error opening image dialog: {str(e)}")
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Failed to open image manager")
            msg.setIcon(QMessageBox.Warning)
            msg.setFixedSize(220, 120)
            msg.exec_()
    
    def refresh_product_row(self, row, product_id):
        """Refresh a specific product row after changes."""
        try:
            # Get updated product info
            product = self.api_client.get_product_by_id(product_id)
            if not product:
                return
                
            # Check if product has images
            images = self.api_client.get_product_images_by_id(product_id)
            has_images = bool(images and len(images) > 0)
            
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
            
            # Update "Website Visible" column (column 5)
            visible_item = QTableWidgetItem()
            visible_item.setTextAlignment(Qt.AlignCenter)
            show_on_website = product.get('show_on_website', 0) == 1
            if show_on_website:
                visible_item.setText("✔️ Visible")
                visible_item.setForeground(QBrush(QColor("#2e7d32")))
            else:
                visible_item.setText("❌ Hidden")
                visible_item.setForeground(QBrush(QColor("#c62828")))
            self.products_table.setItem(row, 5, visible_item)
            
        except Exception as e:
            print(f"Error refreshing product row: {str(e)}")