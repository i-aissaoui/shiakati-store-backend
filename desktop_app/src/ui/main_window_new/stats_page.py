"""
Statistics Page functionality for the Shiakati Store POS application.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
    QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime


class StatsPageMixin:
    """Mixin class for the Statistics page functionality."""
    
    def setup_stats_page(self):
        """Set up the statistics page."""
        # Main layout for stats page with history sidebar
        main_layout = QHBoxLayout(self.stats_page)
        
        # Create left panel for main stats
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create cards layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)  # Minimal spacing between cards
        
        # Total Sales Card
        sales_card = QWidget()
        sales_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #4b6cb7, stop:1 #182848);
                border-radius: 4px;
                padding: 4px;
                color: white;
                min-height: 30px;
            }
            QLabel {
                background: transparent;
            }
        """)
        sales_layout = QVBoxLayout(sales_card)
        sales_layout.setContentsMargins(8, 4, 8, 4)
        sales_layout.setSpacing(0)  # Minimal spacing between elements
        
        sales_icon = QLabel("🛍️")
        sales_icon.setStyleSheet("font-size: 16px;")
        sales_layout.addWidget(sales_icon)
        
        sales_title = QLabel("Total Sales")
        sales_title.setStyleSheet("font-size: 14px; color: #e2e8f0;")
        sales_layout.addWidget(sales_title)
        
        self.total_sales_label = QLabel("0")
        self.total_sales_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0;
        """)
        self.total_sales_label.setObjectName("total_sales_label")
        sales_layout.addWidget(self.total_sales_label)
        
        sales_subtitle = QLabel("Total number of transactions")
        sales_subtitle.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        sales_layout.addWidget(sales_subtitle)
        
        cards_layout.addWidget(sales_card)
        
        # Revenue Card
        revenue_card = QWidget()
        revenue_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #11998e, stop:1 #38ef7d);
                border-radius: 4px;
                padding: 4px;
                color: white;
                min-height: 30px;
            }
            QLabel {
                background: transparent;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_card)
        revenue_layout.setContentsMargins(8, 4, 8, 4)
        revenue_layout.setSpacing(0)  # Minimal spacing between elements
        
        revenue_icon = QLabel("💰")
        revenue_icon.setStyleSheet("font-size: 16px;")
        revenue_layout.addWidget(revenue_icon)
        
        revenue_title = QLabel("Total Revenue")
        revenue_title.setStyleSheet("font-size: 14px; color: #e2e8f0;")
        revenue_layout.addWidget(revenue_title)
        
        self.revenue_label = QLabel("0 DZD")
        self.revenue_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0;
        """)
        self.revenue_label.setObjectName("revenue_label")
        revenue_layout.addWidget(self.revenue_label)
        
        revenue_subtitle = QLabel("Total earnings from all sales")
        revenue_subtitle.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        revenue_layout.addWidget(revenue_subtitle)
        
        cards_layout.addWidget(revenue_card)
        
        # Add cards layout to left panel
        left_layout.addLayout(cards_layout)
        
        # Top Products Section
        top_products_container = QWidget()
        top_products_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                color: #1e293b;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
            }
            QTableWidget {
                border: none;
                gridline-color: #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
                min-height: 300px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
                min-height: 20px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                color: #475569;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        top_products_layout = QVBoxLayout(top_products_container)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_label = QLabel("📊 Top Performing Products")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        top_products_layout.addLayout(header_layout)
        
        # Table
        self.top_products_table = QTableWidget()
        self.top_products_table.setObjectName("top_products_table")
        self.top_products_table.setColumnCount(4)
        
        # Force the header to be visible and set its style
        header = self.top_products_table.horizontalHeader()
        header.setVisible(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #475569;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        
        # Set column headers
        self.top_products_table.setHorizontalHeaderLabels([
            "Product", "Quantity Sold", "Revenue (DZD)", "Profit (DZD)"
        ])
        header.setStretchLastSection(True)
        self.top_products_table.setAlternatingRowColors(True)
        self.top_products_table.verticalHeader().setVisible(False)
        self.top_products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        header = self.top_products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.top_products_table.setColumnWidth(1, 150)  # Quantity
        self.top_products_table.setColumnWidth(2, 150)  # Revenue
        self.top_products_table.setColumnWidth(3, 150)  # Profit
        
        top_products_layout.addWidget(self.top_products_table)
        left_layout.addWidget(top_products_container)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel, stretch=2)
        
        # Create right panel for sales history
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sales History Title
        history_title = QLabel("Sales History")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        right_layout.addWidget(history_title)
        
        # Sales History Table
        self.sales_history_table = QTableWidget()
        self.sales_history_table.setObjectName("sales_history_table")
        self.sales_history_table.setColumnCount(3)
        self.sales_history_table.setHorizontalHeaderLabels([
            "Date", "Items", "Total"
        ])
        self.sales_history_table.setMinimumHeight(300)
        self.sales_history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 15px 10px;
                border-bottom: 1px solid #f1f2f6;
                min-height: 30px;
            }
            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 15px 10px;
                border: none;
                font-weight: bold;
            }
        """)
        self.sales_history_table.horizontalHeader().setStretchLastSection(True)
        self.sales_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing
        
        # Increase row height for better readability
        self.sales_history_table.verticalHeader().setDefaultSectionSize(50)
        self.sales_history_table.verticalHeader().setVisible(False)  # Hide row numbers
        
        right_layout.addWidget(self.sales_history_table)
        
        # Style the right panel
        right_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #dcdde1;
            }
        """)
        
        # Add right panel to main layout
        main_layout.addWidget(right_panel, stretch=1)
        
        # Connect double click event for sales history
        self.sales_history_table.cellDoubleClicked.connect(self.show_sale_details)
        
        # Initial load of sales history
        self.load_sales_history()
        
        # Set up periodic stats refresh
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial stats update
        self.update_stats()

    def load_sales_history(self):
        """Load and display sales history in the sidebar table."""
        try:
            if not hasattr(self, 'sales_history_table') or not self.sales_history_table:
                return
                
            sales_history = self.api_client.get_sales_history()
            self.sales_history_table.setRowCount(0)
            
            for sale in reversed(sales_history):  # Show newest first
                row = self.sales_history_table.rowCount()
                self.sales_history_table.insertRow(row)
                
                # Format date
                sale_date = QDateTime.fromString(sale["sale_time"], Qt.ISODateWithMs)
                formatted_date = sale_date.toString("yyyy-MM-dd hh:mm")
                
                # Calculate total quantity from all items, handling floating point display
                total_quantity = sum(float(item["quantity"]) for item in sale["items"])
                items_summary = f"{total_quantity:.1f} items"
                
                # Calculate total from items to ensure consistency
                items_total = sum(float(item["quantity"]) * float(item["price"]) for item in sale["items"])
                
                # Set table items
                self.sales_history_table.setItem(row, 0, QTableWidgetItem(formatted_date))
                self.sales_history_table.setItem(row, 1, QTableWidgetItem(items_summary))
                self.sales_history_table.setItem(row, 2, QTableWidgetItem(self.format_price(items_total)))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load sales history: {str(e)}")

    def update_stats(self):
        """Update statistics display."""
        try:
            # Get stats from API
            stats = self.api_client.get_stats()
            
            if not stats:
                return
            
            # Update total sales count
            total_sales = stats.get('total_sales', 0)
            self.total_sales_label.setText(str(total_sales))
            
            # Update total revenue
            total_revenue = float(stats.get('total_revenue', 0))
            self.revenue_label.setText(self.format_price(total_revenue))
            
            # Update top products table
            top_products = stats.get('top_products', [])
            self.top_products_table.setRowCount(0)
            
            try:
                for product in top_products:
                    row = self.top_products_table.rowCount()
                    self.top_products_table.insertRow(row)
                    
                    # Get the product name, using name as primary and falling back to the ID if needed
                    product_name = product.get('name', '')
                    if not product_name:
                        product_name = product.get('product_name', '')
                    if not product_name and 'id' in product:
                        product_name = f"Product {product['id']}"
                    if not product_name:
                        product_name = "Unknown"
                        
                    # Get sales quantity (may be stored as total_sales or total_quantity)
                    quantity = product.get('total_quantity', product.get('total_sales', 0))
                    if quantity is not None:
                        quantity = float(quantity)
                    else:
                        quantity = 0.0
                    
                    revenue = float(product.get('total_revenue', 0))
                    # Calculate profit as 30% of revenue if not provided
                    profit = float(product.get('profit', revenue * 0.3))
                    
                    self.top_products_table.setItem(row, 0, QTableWidgetItem(product_name))
                    self.top_products_table.setItem(row, 1, QTableWidgetItem(f"{quantity:.1f}"))
                    self.top_products_table.setItem(row, 2, QTableWidgetItem(self.format_price(revenue)))
                    self.top_products_table.setItem(row, 3, QTableWidgetItem(self.format_price(profit)))
                    
            except Exception as e:
                print(f"Error loading top products: {str(e)}")
                
            # Update sales history
            self.load_sales_history()
                
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging

    def show_sale_details(self, row: int):
        """Show details for a selected sale."""
        try:
            # Get sale from the stored data
            sales_history = self.api_client.get_sales_history()
            if not sales_history:
                QMessageBox.warning(self, "Error", "Could not load sale details")
                return

            # Get the current sale since we store them in reverse order (newest first)
            current_sale = sales_history[-(row + 1)]  # Simple negative indexing to get the correct sale
            current_sale_id = current_sale["id"]
            sale = self.api_client.get_sale_details(current_sale_id)
            
            if not sale or "items" not in sale:
                QMessageBox.warning(self, "Error", "Could not load sale details")
                return
            
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Sale Details")
            details_dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(details_dialog)
            layout.setSpacing(10)
            
            # Date and time info
            date_label = QLabel(f"Date: {QDateTime.fromString(sale['sale_time'], Qt.ISODateWithMs).toString('yyyy-MM-dd hh:mm')}")
            date_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(date_label)
            
            # Create items table
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Product", "Price", "Quantity", "Total"])
            
            # Set column widths
            items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
            items_table.setColumnWidth(1, 100)  # Price
            items_table.setColumnWidth(2, 80)   # Quantity
            items_table.setColumnWidth(3, 100)  # Total
            
            # Style the table
            items_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                    background-color: white;
                    font-size: 13px;
                    min-height: 200px;
                }
                QTableWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #f1f2f6;
                    min-height: 20px;
                }
                QHeaderView::section {
                    background-color: #f1f2f6;
                    padding: 12px 8px;
                    border: none;
                    font-weight: bold;
                }
            """)
            
            # Disable editing
            items_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Add sale items
            total_items = 0
            items_total = 0
            for item in sale["items"]:
                row = items_table.rowCount()
                items_table.insertRow(row)
                
                price = float(item["price"])
                quantity = float(item["quantity"])
                total = price * quantity
                items_total += total
                
                items_table.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                items_table.setItem(row, 1, QTableWidgetItem(self.format_price(price)))
                items_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.1f}"))  # Display 1 decimal place
                items_table.setItem(row, 3, QTableWidgetItem(self.format_price(total)))
                
                total_items += quantity
        
            layout.addWidget(items_table)
            
            # Summary section
            summary_widget = QWidget()
            summary_layout = QVBoxLayout(summary_widget)
            summary_layout.setSpacing(5)
            
            items_count = QLabel(f"Total Items: {total_items}")
            items_count.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(items_count)
            
            total_label = QLabel(f"Total Amount: {self.format_price(float(sale['total']))}")
            total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3436; margin-top: 5px;")
            summary_layout.addWidget(total_label)
            
            layout.addWidget(summary_widget)
            
            # Button container
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            
            # Print button
            print_button = QPushButton("🖨️ Print Ticket")
            print_button.clicked.connect(lambda: self.print_sale_ticket(sale))
            print_button.setStyleSheet("""
                QPushButton {
                    background-color: #00b894;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00a885;
                }
            """)
            button_layout.addWidget(print_button)
            
            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(details_dialog.close)
            close_button.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    font-weight: bold;
                }
            """)
            button_layout.addWidget(close_button)
            
            layout.addWidget(button_container)
            
            details_dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load sale details: {str(e)}")
            # Debug logging

    def cleanup_stats_widgets(self):
        """Safely clean up stats page widgets."""
        if hasattr(self, 'stats_timer') and self.stats_timer:
            self.stats_timer.stop()
        
        # Clear references to tables to help garbage collection
        if hasattr(self, 'top_products_table'):
            self.top_products_table = None
        if hasattr(self, 'sales_history_table'):
            self.sales_history_table = None
