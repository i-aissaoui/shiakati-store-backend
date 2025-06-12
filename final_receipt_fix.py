#!/usr/bin/env python3
"""
Final fix script for the receipt generation issue.
"""

import os
import sys
import shutil
import re
import datetime
import traceback

def find_and_fix_print_sale_ticket():
    """Find and fix the print_sale_ticket function in the POS page."""
    print("Starting receipt generation fix...")
    
    # Find the pos_page.py file
    pos_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "pos_page.py"
    )
    print(f"Looking for POS page at: {pos_file_path}")
    
    if not os.path.exists(pos_file_path):
        print(f"❌ Error: Could not find pos_page.py at {pos_file_path}")
        return False
        
    # Create backup with timestamp
    backup_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{pos_file_path}.bak_{backup_timestamp}"
    
    try:
        shutil.copy2(pos_file_path, backup_path)
        print(f"✅ Created backup at: {backup_path}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False
        
    # Read the file content
    try:
        with open(pos_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ Successfully read file: {pos_file_path} ({len(content)} bytes)")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
        
    # Find the print_sale_ticket function
    pattern = r'def print_sale_ticket\(self, sale_data\):.*?(?=\n    def|\n\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Error: Could not find print_sale_ticket function")
        return False
        
    print(f"✅ Found print_sale_ticket function (length: {len(match.group(0))} chars)")
    
    # Prepare the replacement function with triple quotes correctly escaped
    replacement = '''def print_sale_ticket(self, sale_data):
        """Print a sale ticket and open it with the default PDF viewer."""
        try:
            import os
            import sys
            import shutil
            import subprocess
            import time
            import logging
            import traceback
            from threading import Thread
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from reportlab.lib.pagesizes import A4
            from PyQt5.QtWidgets import QMessageBox
            
            # Set up logging for diagnostics
            log_file = os.path.join(os.path.expanduser("~"), "receipt_debug_fixed.log")
            logging.basicConfig(
                filename=log_file,
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
            logging.info("===== RECEIPT CREATION STARTED (FIXED VERSION) =====")
            
            # Get the relevant directory paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            desktop_app_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            backend_dir = os.path.dirname(desktop_app_dir)
            
            logging.info(f"Current directory: {current_dir}")
            logging.info(f"Desktop app directory: {desktop_app_dir}")
            logging.info(f"Backend directory: {backend_dir}")
            
            # Define receipt directories
            backend_receipt_dir = os.path.join(backend_dir, "receipt")
            desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
            
            logging.info(f"Backend receipt directory: {backend_receipt_dir}")
            logging.info(f"Desktop receipt directory: {desktop_receipt_dir}")
            
            # Create directories if they don't exist
            os.makedirs(backend_receipt_dir, exist_ok=True)
            os.makedirs(desktop_receipt_dir, exist_ok=True)
            
            # Create receipt filename with timestamp to avoid overwriting
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            receipt_filename = f"Sale-{sale_data['id']}-{timestamp}.pdf"
            backend_path = os.path.join(backend_receipt_dir, receipt_filename)
            desktop_path = os.path.join(desktop_receipt_dir, receipt_filename)
            
            logging.info(f"Backend receipt path: {backend_path}")
            logging.info(f"Desktop receipt path: {desktop_path}")
            
            try:
                # Create PDF with reportlab
                logging.info("Creating PDF with reportlab...")
                
                # Create the canvas for drawing
                c = canvas.Canvas(backend_path, pagesize=(80 * mm, 200 * mm))
                c.setTitle(f"Sale-{sale_data['id']}")
                
                # Set initial position
                y_position = 190 * mm  # Start from top
                line_height = 5 * mm
                
                # Draw header
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(40 * mm, y_position, "Shiakati شياكتي")
                y_position -= line_height * 1.5
                
                # Draw date and sale number
                c.setFont("Helvetica", 8)
                date_str = sale_data.get('sale_time', 'Unknown Date')
                if isinstance(date_str, str) and 'T' in date_str:
                    # Format ISO date string
                    from datetime import datetime
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                c.drawCentredString(40 * mm, y_position, f"Date: {date_str}")
                y_position -= line_height
                
                c.drawCentredString(40 * mm, y_position, f"Sale: {sale_data['id']}")
                y_position -= line_height * 2
                
                # Draw separator line
                c.line(5 * mm, y_position, 75 * mm, y_position)
                y_position -= line_height
                
                # Draw column headers
                c.setFont("Helvetica-Bold", 7)
                c.drawString(5 * mm, y_position, "Item")
                c.drawRightString(55 * mm, y_position, "Qty")
                c.drawRightString(65 * mm, y_position, "Price")
                c.drawRightString(75 * mm, y_position, "Total")
                y_position -= line_height
                
                # Draw separator line
                c.line(5 * mm, y_position, 75 * mm, y_position)
                y_position -= line_height
                
                # Draw items
                c.setFont("Helvetica", 7)
                total_amount = 0
                
                # Helper function to handle long product names
                def draw_wrapped_text(text, x, y, width, line_height):
                    from reportlab.lib.utils import simpleSplit
                    chunks = simpleSplit(text, "Helvetica", 7, width)
                    for i, chunk in enumerate(chunks):
                        c.drawString(x, y - i * line_height * 0.8, chunk)
                    return len(chunks)
                
                for item in sale_data.get("items", []):
                    product_name = item.get("product_name", "Unknown Product")
                    quantity = float(item.get("quantity", 1))
                    price = float(item.get("price", 0))
                    total = price * quantity
                    total_amount += total
                    
                    # Draw product name (possibly wrapping to multiple lines)
                    lines = draw_wrapped_text(product_name, 5 * mm, y_position, 40 * mm, line_height)
                    
                    # Draw quantity, price, and total
                    c.drawRightString(55 * mm, y_position, f"{int(quantity)}")
                    c.drawRightString(65 * mm, y_position, f"{price:.2f}")
                    c.drawRightString(75 * mm, y_position, f"{total:.2f}")
                    
                    # Move position down based on number of text lines
                    y_position -= line_height * max(lines, 1) + line_height * 0.2
                
                # Draw separator line
                c.line(5 * mm, y_position, 75 * mm, y_position)
                y_position -= line_height * 1.5
                
                # Draw total
                c.setFont("Helvetica-Bold", 10)
                c.drawRightString(40 * mm, y_position, "Total:")
                c.drawRightString(75 * mm, y_position, f"{total_amount:.2f} DZD")
                y_position -= line_height * 3
                
                # Draw footer
                c.setFont("Helvetica", 8)
                c.drawCentredString(40 * mm, y_position, "Thank you")
                
                # Save the PDF
                c.save()
                
                # Verify the PDF was created
                if os.path.exists(backend_path) and os.path.getsize(backend_path) > 0:
                    size = os.path.getsize(backend_path)
                    logging.info(f"PDF created successfully: {backend_path} ({size} bytes)")
                else:
                    logging.error(f"PDF file not found after creation: {backend_path}")
                    raise FileNotFoundError(f"PDF file not found after creation: {backend_path}")
                
                # Copy to desktop app receipt directory
                try:
                    shutil.copy2(backend_path, desktop_path)
                    if os.path.exists(desktop_path):
                        size = os.path.getsize(desktop_path)
                        logging.info(f"PDF copied to desktop app directory: {desktop_path} ({size} bytes)")
                    else:
                        logging.error(f"Copy exists but file not found: {desktop_path}")
                except Exception as e:
                    logging.error(f"Error copying to desktop directory: {e}")
                    # Continue anyway, we have the primary copy
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Receipt has been saved successfully to {backend_receipt_dir}"
                )
                
                # Open the PDF in a separate thread
                def open_pdf_thread():
                    try:
                        # Small delay to ensure PDF is fully written
                        time.sleep(1.0)
                        
                        # Try to open the PDF
                        receipt_path = backend_path
                        logging.info(f"Opening receipt: {receipt_path}")
                        
                        # Platform-specific opening
                        if sys.platform == 'win32':
                            os.startfile(receipt_path)
                        elif sys.platform == 'darwin':  # macOS
                            subprocess.call(['open', receipt_path])
                        else:  # Linux
                            try:
                                subprocess.call(['xdg-open', receipt_path])
                            except:
                                # Show message with location
                                QMessageBox.information(
                                    self,
                                    "Receipt Location",
                                    f"The receipt has been saved to: {receipt_path}"
                                )
                                
                    except Exception as e:
                        logging.error(f"Error opening PDF: {e}")
                
                # Start the thread to open the PDF
                Thread(target=open_pdf_thread).start()
                
                logging.info("===== RECEIPT CREATION COMPLETED (FIXED VERSION) =====")
                return True
            except Exception as e:
                logging.error(f"Error creating PDF: {e}")
                logging.error(traceback.format_exc())
                
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to create receipt PDF: {str(e)}"
                )
                return False
        except Exception as e:
            logging.error(f"Unhandled error in print_sale_ticket: {e}")
            logging.error(traceback.format_exc())
            
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to print receipt: {str(e)}"
            )
            return False'''
    
    # Replace the function
    new_content = content.replace(match.group(0), replacement)
    
    # Write the updated content back to file
    try:
        with open(pos_file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Successfully updated print_sale_ticket function")
        return True
    except Exception as e:
        print(f"❌ Error writing updated file: {e}")
        return False

def check_directories():
    """Check if receipt directories exist and are writable."""
    print("\nChecking receipt directories...")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.join(backend_dir, "desktop_app")
    
    backend_receipt_dir = os.path.join(backend_dir, "receipt")
    desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
    
    dirs_to_check = [
        ("Backend receipt directory", backend_receipt_dir),
        ("Desktop app receipt directory", desktop_receipt_dir)
    ]
    
    all_valid = True
    
    for name, directory in dirs_to_check:
        print(f"\nChecking {name}: {directory}")
        
        # Check if directory exists
        if not os.path.exists(directory):
            print(f"  Directory does not exist, creating it...")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"  ✅ Created directory")
            except Exception as e:
                print(f"  ❌ Failed to create directory: {e}")
                all_valid = False
                continue
        else:
            print(f"  ✅ Directory exists")
            
        # Check if directory is writable
        test_file = os.path.join(directory, "test_write_permission.txt")
        try:
            with open(test_file, "w") as f:
                f.write("Test write permission")
            os.remove(test_file)
            print(f"  ✅ Directory is writable")
        except Exception as e:
            print(f"  ❌ Directory is not writable: {e}")
            all_valid = False
    
    return all_valid

def create_test_pdf():
    """Create a test PDF in both receipt directories."""
    print("\nCreating test PDF files...")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.join(backend_dir, "desktop_app")
    
    backend_receipt_dir = os.path.join(backend_dir, "receipt")
    desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
    
    backend_path = os.path.join(backend_receipt_dir, "test_receipt.pdf")
    desktop_path = os.path.join(desktop_receipt_dir, "test_receipt.pdf")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.lib.pagesizes import A4
        
        # Create backend test PDF
        c = canvas.Canvas(backend_path)
        c.setFont("Helvetica", 12)
        c.drawString(30, 800, "Receipt Test PDF")
        c.drawString(30, 780, f"Created at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.save()
        
        size = os.path.getsize(backend_path) if os.path.exists(backend_path) else 0
        print(f"✅ Backend test PDF created: {backend_path} ({size} bytes)")
        
        # Create desktop test PDF
        c = canvas.Canvas(desktop_path)
        c.setFont("Helvetica", 12)
        c.drawString(30, 800, "Receipt Test PDF")
        c.drawString(30, 780, f"Created at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.save()
        
        size = os.path.getsize(desktop_path) if os.path.exists(desktop_path) else 0
        print(f"✅ Desktop test PDF created: {desktop_path} ({size} bytes)")
        
        return True
    except Exception as e:
        print(f"❌ Error creating test PDFs: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("===== RECEIPT GENERATION FIX =====")
    
    # Check for reportlab
    try:
        import reportlab
        print(f"✅ reportlab is installed (version {reportlab.__version__})")
    except ImportError:
        print("❌ reportlab is not installed")
        print("Installing reportlab...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
            print("✅ Successfully installed reportlab")
        except Exception as e:
            print(f"❌ Failed to install reportlab: {e}")
            print("Please manually install reportlab with: pip install reportlab")
            return False
    
    # Check directories
    if not check_directories():
        print("\n⚠️ Warning: Some directory issues detected. Fix may not work completely.")
    
    # Create test PDFs to verify reportlab is working
    if not create_test_pdf():
        print("\n❌ Error: Failed to create test PDFs. Fix may not work.")
        return False
    
    # Fix the print_sale_ticket function
    if not find_and_fix_print_sale_ticket():
        print("\n❌ Error: Failed to fix the print_sale_ticket function.")
        return False
    
    print("\n===== FIX COMPLETED SUCCESSFULLY =====")
    print("The receipt generation should now work properly.")
    print("\nNext steps:")
    print("1. Restart the POS application")
    print("2. Create a test sale")
    print("3. Check if receipt files are now being saved to:")
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"   - {os.path.join(backend_dir, 'receipt/')}")
    print(f"   - {os.path.join(backend_dir, 'desktop_app/receipt/')}")
    print("4. If issues persist, check the log at ~/receipt_debug_fixed.log")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
        traceback.print_exc()
        sys.exit(1)
