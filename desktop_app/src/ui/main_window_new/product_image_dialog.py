"""
Product Image Management Dialog for Shiakati Store POS application.
Popup dialog for managing product images and website visibility.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QCheckBox, QMessageBox, QScrollArea, QWidget, QGridLayout,
    QFileDialog, QGroupBox, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import requests
from io import BytesIO


class ProductImageDialog(QDialog):
    """Dialog for managing product images and website visibility."""
    
    def __init__(self, parent, api_client, product_id, product_name):
        super().__init__(parent)
        self.api_client = api_client
        self.product_id = product_id
        self.product_name = product_name
        
        self.setWindowTitle(f"Manage Images - {product_name}")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_product_data()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Product title
        title = QLabel(f"Product: {self.product_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Images section
        images_group = QGroupBox("Product Images")
        images_layout = QVBoxLayout(images_group)
        
        # Upload controls
        upload_layout = QHBoxLayout()
        
        upload_btn = QPushButton("📷 Upload New Image")
        upload_btn.clicked.connect(self.upload_image)
        upload_layout.addWidget(upload_btn)
        
        self.set_as_main_checkbox = QCheckBox("Set as main image")
        upload_layout.addWidget(self.set_as_main_checkbox)
        
        upload_layout.addStretch()
        images_layout.addLayout(upload_layout)
        
        # Images scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        self.images_widget = QWidget()
        self.images_grid = QGridLayout(self.images_widget)
        self.images_grid.setSpacing(10)
        scroll_area.setWidget(self.images_widget)
        
        images_layout.addWidget(scroll_area)
        splitter.addWidget(images_group)
        
        # Website visibility section
        visibility_group = QGroupBox("Website Visibility")
        visibility_layout = QVBoxLayout(visibility_group)
        
        self.show_on_website_checkbox = QCheckBox("Show this product on the website")
        visibility_layout.addWidget(self.show_on_website_checkbox)
        
        visibility_note = QLabel("Note: Products need at least one image to be displayed properly on the website.")
        visibility_note.setStyleSheet("color: #666; font-style: italic; font-size: 12px;")
        visibility_layout.addWidget(visibility_note)
        
        # Visibility save button
        save_visibility_btn = QPushButton("💾 Save Visibility Setting")
        save_visibility_btn.clicked.connect(self.save_visibility)
        visibility_layout.addWidget(save_visibility_btn)
        
        splitter.addWidget(visibility_group)
        
        # Set splitter sizes (70% images, 30% visibility)
        splitter.setSizes([420, 180])
        layout.addWidget(splitter)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
    def load_product_data(self):
        """Load product images and visibility data."""
        try:
            # Load product details for visibility
            product = self.api_client.get_product_by_id(self.product_id)
            if product:
                self.show_on_website_checkbox.setChecked(product.get('show_on_website', 0) == 1)
            
            # Load images
            self.load_images()
            
        except Exception as e:
            print(f"Error loading product data: {str(e)}")
            self.show_error("Failed to load product data")
            
    def load_images(self):
        """Load and display product images."""
        try:
            # Clear existing images
            self.clear_images_grid()
            
            # Get images from API
            images = self.api_client.get_product_images_by_id(self.product_id)
            
            if not images:
                self.show_no_images_message()
                return
                
            # Display images in grid
            row, col = 0, 0
            max_cols = 3
            
            for img in images:
                self.add_image_to_grid(img, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        except Exception as e:
            print(f"Error loading images: {str(e)}")
            self.show_error("Failed to load images")
            
    def clear_images_grid(self):
        """Clear all widgets from the images grid."""
        while self.images_grid.count():
            item = self.images_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def show_no_images_message(self):
        """Show message when no images are available."""
        no_images_label = QLabel("No images available for this product")
        no_images_label.setAlignment(Qt.AlignCenter)
        no_images_label.setStyleSheet("""
            color: #666; 
            font-size: 16px; 
            padding: 40px;
            border: 2px dashed #ccc;
            border-radius: 8px;
            background-color: #f9f9f9;
        """)
        self.images_grid.addWidget(no_images_label, 0, 0, 1, 3)
        
    def add_image_to_grid(self, image_data, row, col):
        """Add an image widget to the grid."""
        try:
            # Create container
            container = QWidget()
            container.setFixedSize(200, 280)  # Increased height for better button layout
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            
            # Image label
            image_label = QLabel()
            image_label.setFixedSize(180, 180)
            image_label.setScaledContents(True)
            image_label.setAlignment(Qt.AlignCenter)
            
            # Load image
            image_url = image_data.get('image_url', '')
            is_main = image_data.get('is_main', False)
            
            pixmap = self.load_image_from_url(image_url)
            if pixmap:
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image\nNot Available")
                image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
            
            # Main image indicator
            if is_main:
                image_label.setStyleSheet("""
                    border: 3px solid #4CAF50;
                    border-radius: 5px;
                """)
                main_indicator = QLabel("★ Main Image")
                main_indicator.setAlignment(Qt.AlignCenter)
                main_indicator.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
                container_layout.addWidget(main_indicator)
            else:
                image_label.setStyleSheet("""
                    border: 2px solid #ddd;
                    border-radius: 5px;
                """)
            
            container_layout.addWidget(image_label)
            
            # Action buttons - Full width and better positioning
            buttons_layout = QVBoxLayout()
            buttons_layout.setSpacing(5)
            buttons_layout.setContentsMargins(0, 5, 0, 0)
            
            if not is_main:
                set_main_btn = QPushButton("⭐ Set as Main Image")
                set_main_btn.setFixedHeight(30)
                set_main_btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #4CAF50; 
                        color: white; 
                        font-weight: bold;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                set_main_btn.clicked.connect(lambda: self.set_main_image(image_url))
                buttons_layout.addWidget(set_main_btn)
            
            delete_btn = QPushButton("🗑️ Delete Image")
            delete_btn.setFixedHeight(30)
            delete_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #ff6b6b; 
                    color: white; 
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e55555;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_image(image_url))
            buttons_layout.addWidget(delete_btn)
            
            container_layout.addLayout(buttons_layout)
            
            # Add to grid
            self.images_grid.addWidget(container, row, col)
            
        except Exception as e:
            print(f"Error adding image to grid: {str(e)}")
            
    def load_image_from_url(self, url):
        """Load image from URL and return QPixmap."""
        try:
            if url.startswith('/'):
                url = f"{self.api_client.base_url}{url}"
                
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image = QImage()
                image.loadFromData(response.content)
                return QPixmap.fromImage(image).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return None
        except Exception as e:
            print(f"Error loading image from {url}: {str(e)}")
            return None
            
    def upload_image(self):
        """Upload a new image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.webp *.gif)"
        )
        
        if not file_path:
            return
            
        progress_msg = None
        try:
            # Show progress
            progress_msg = QMessageBox(self)
            progress_msg.setWindowTitle("Uploading")
            progress_msg.setText("Uploading image...")
            progress_msg.setStandardButtons(QMessageBox.NoButton)
            progress_msg.setFixedSize(200, 120)  # Compact size
            progress_msg.show()
            
            # Process events to ensure dialog shows
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Upload
            set_as_main = self.set_as_main_checkbox.isChecked()
            result = self.api_client.upload_product_image(self.product_id, file_path, set_as_main)
            
            if result:
                self.show_success("Image uploaded successfully!")
                self.load_images()  # Refresh images
            else:
                self.show_error("Failed to upload image")
                
        except Exception as e:
            self.show_error(f"Upload failed: {str(e)}")
        finally:
            # ALWAYS close the progress dialog in the finally block to ensure it's closed
            if progress_msg:
                try:
                    progress_msg.close()
                    progress_msg.deleteLater()
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()  # Ensure dialog is properly closed
                except Exception as cleanup_error:
                    print(f"Error cleaning up progress dialog: {cleanup_error}")
                progress_msg = None
            
    def set_main_image(self, image_url):
        """Set an image as the main image."""
        try:
            result = self.api_client.set_main_product_image(self.product_id, image_url)
            if result:
                self.show_success("Main image updated!")
                self.load_images()  # Refresh to show updated main image
            else:
                self.show_error("Failed to set main image")
        except Exception as e:
            self.show_error(f"Failed to set main image: {str(e)}")
            
    def delete_image(self, image_url):
        """Delete an image."""
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this image?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        try:
            result = self.api_client.delete_product_image(self.product_id, image_url)
            if result:
                self.show_success("Image deleted!")
                self.load_images()  # Refresh images
            else:
                self.show_error("Failed to delete image")
        except Exception as e:
            self.show_error(f"Failed to delete image: {str(e)}")
            
    def save_visibility(self):
        """Save website visibility setting."""
        try:
            visibility = 1 if self.show_on_website_checkbox.isChecked() else 0
            result = self.api_client.update_product_visibility(self.product_id, visibility)
            
            if result:
                self.show_success("Visibility updated!")
            else:
                self.show_error("Failed to update visibility")
        except Exception as e:
            self.show_error(f"Failed to update visibility: {str(e)}")
            
    def show_success(self, message):
        """Show compact success message."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setFixedSize(250, 120)
        msg.exec_()
        
    def show_error(self, message):
        """Show compact error message."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setFixedSize(250, 120)
        msg.exec_()
