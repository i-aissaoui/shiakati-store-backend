"""
Utility functions for the Shiakati Store POS application.
"""

import os
import base64
import io
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QTextDocument, QPageSize
from PyQt5.QtPrintSupport import QPrinter


def format_datetime(dt_str, output_format="yyyy-MM-dd hh:mm"):
    """Format a datetime string into a more readable format."""
    date_time = QDateTime.fromString(dt_str, Qt.ISODateWithMs)
    return date_time.toString(output_format)


def open_file_with_default_app(file_path):
    """Open a file with the default application."""
    import os
    import platform
    import subprocess
    
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux and other Unix-like systems
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        return False
    """Open a file with the default application for its type."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        else:  # macOS/Linux
            import subprocess
            subprocess.call(('xdg-open', file_path))
        return True
    except Exception as e:
        return False


def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    try:
        # Convert to absolute path if it's a relative path
        if not os.path.isabs(directory_path):
            directory_path = os.path.join(os.getcwd(), directory_path)
            
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except Exception as e:
        return False


def print_receipt(sale_data, logo_path=None):
    """
    Generate a PDF receipt for a sale.
    
    Args:
        sale_data (dict): Dictionary containing sale information
        logo_path (str, optional): Path to the logo file
        
    Returns:
        str: Path to the generated PDF file or None if failed
    """
    try:
        # Create receipts directory if it doesn't exist
        import os
        
        # Get the project root directory (one level up from the current file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
        
        # Create receipts directory in the project root
        receipt_dir = os.path.join(project_root, "receipt")
        if not os.path.exists(receipt_dir):
            os.makedirs(receipt_dir)
        
        file_path = os.path.join(receipt_dir, f"Sale-{sale_data['id']}.pdf")
        
        printer = QPrinter()
        custom_page_size = QPageSize(QSizeF(80, 200), QPageSize.Unit.Millimeter)
        printer.setPageSize(custom_page_size)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setPageMargins(2.0, 2.0, 2.0, 2.0, QPrinter.Unit.Millimeter)
        
        document = QTextDocument()
        document.setDocumentMargin(0)
        
        # Create HTML receipt with monospace font and better alignment
        html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page { 
                        size: 80mm 200mm;
                        margin: 0mm;
                    }
                    body { 
                        font-family: "Courier", monospace;
                        width: 72mm;
                        margin: 0;
                        padding: 2mm;
                        font-size: 6.5pt;
                        line-height: 1.1;
                        white-space: pre;
                    }
                    .content {
                        width: 100%;
                        text-align: center;
                    }
                    .store-logo {
                        width: 15mm !important;
                        max-width: 15mm !important;
                        height: 15mm !important;
                        max-height: 15mm !important;
                        margin-bottom: 3mm;
                        display: block;
                        margin-left: auto;
                        margin-right: auto;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 6mm;
                    }
                    .items-section {
                        text-align: left;
                        margin: 0;
                    }
                    .items-header {
                        margin: 1mm 0;
                        font-weight: normal;
                    }
                    .item-row {
                        margin: 0.5mm 0;
                    }
                    .item-name {
                        margin-left: 2mm;
                        color: #000;
                    }
                    .separator {
                        margin: 1mm 0;
                    }
                    .total {
                        text-align: center;
                        margin: 3mm 0;
                        font-size: 10pt;
                        font-weight: bold;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 6mm;
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
                <div class="content">"""
        
        # Add logo if available
        if logo_path and os.path.exists(logo_path):
            from PIL import Image
            
            # Load and resize the ICO file
            img = Image.open(logo_path)
            # Set to a larger size for better visibility
            img = img.resize((60, 60), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Add logo and store name
            html += f'<img src="data:image/png;base64,{img_str}" class="store-logo" />'
            
        # Add store name
        html += '<div style="text-align: center; font-weight: bold; margin-bottom: 2mm; font-size: 9pt;">Shiakati شياكتي</div></br>'

        # Add date and sale number - centered in header section
        date_str = QDateTime.fromString(sale_data['sale_time'], Qt.ISODate).toString('yyyy-MM-dd HH:mm')
        html += '<div class="header">'
        html += f"Date: {date_str}\n"
        html += f"Sale : {sale_data['id']}\n\n"  # Added extra newline
        html += '</div>'
        
        # Start items section
        html += '<div class="items-section">'
        
        # Add separator line at top
        html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n'
        
        # Add header with spacings matching the data format
        html += 'Item              Qty   Price  Total\n'
        html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n'
        
        # Add items with proper spacing
        total_items = 0
        total_amount = 0
        for item in sale_data["items"]:
            product_name = item.get("product_name", "Unknown Product")
            quantity = float(item.get("quantity", 1))
            price = float(item.get("price", 0))
            total = price * quantity
            total_items += quantity
            total_amount += total
            
            # Format numbers with consistent decimal places and spacing
            name_width = 16  # Width for product name
            qty_str = f"{int(quantity)}".rjust(3)     # Width for quantity
            price_str = f"{price:.2f}".rjust(7)      # Width for price
            total_str = f"{total:.2f}".rjust(6)      # Width for total - pulled in
            
            # Handle long product names by truncating
            if len(product_name) > name_width:
                product_name = product_name[:name_width-3] + "..."
                
            # Single line format with consistent spacing
            html += f"{product_name.ljust(name_width)}{qty_str}   {price_str}  {total_str}\n"
        
        # Add separator line
        html += '<span style="font-weight: bold;">───────────────────────────────────────</span>\n\n'
        html += '</div>'
        
        # Add centered total with proper spacing
        html += f'<div class="total">Total: {total_amount:>8.2f} DZD</div>'
        
        # Add centered footer
        html += '<div class="footer">'
        html += "Thank you"
        html += '</div>'
        
        # Close HTML tags
        html += """
                </div>
            </body>
            </html>
        """
        
        document.setHtml(html)
        document.setMetaInformation(QTextDocument.DocumentTitle, f"Sale-{sale_data['id']}")
        rect = printer.pageRect(QPrinter.Unit.Point)
        document.setPageSize(QSizeF(rect.width(), rect.height()))
        
        # Print the document
        document.print_(printer)
        
        return file_path
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
