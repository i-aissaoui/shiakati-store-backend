#!/usr/bin/env python3
"""
Manual fix script for replacing the receipt generation function.
"""

import os
import sys
import shutil
import re

def replace_function_in_file():
    """Replaces the print_sale_ticket function in the pos_page.py file."""
    pos_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "pos_page.py"
    )
    
    # Make a backup
    backup_path = pos_file_path + ".bak_" + str(os.getpid())
    shutil.copy2(pos_file_path, backup_path)
    print(f"Backup created at: {backup_path}")
    
    # Read the file
    with open(pos_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define the pattern to find the function
    pattern = re.compile(r"def print_sale_ticket\(self, sale_data\):.*?(?=\n    def|\n\nclass|\Z)", re.DOTALL)
    
    # Define the replacement function
    replacement = """def print_sale_ticket(self, sale_data):
        \"\"\"Print a sale ticket and open it with the default PDF viewer.\"\"\"
        try:
            import os
            import sys
            import shutil
            import subprocess
            import time
            import logging
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
            print("===== RECEIPT CREATION STARTED (FIXED VERSION) =====")
            
            # Get the relevant directory paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            desktop_app_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            backend_dir = os.path.dirname(desktop_app_dir)
            
            logging.info(f"Current directory: {current_dir}")
            logging.info(f"Desktop app directory: {desktop_app_dir}")
            logging.info(f"Backend root directory: {backend_dir}")
            
            # Define receipt directories
            desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
            backend_receipt_dir = os.path.join(backend_dir, "receipt")
            
            logging.info(f"Desktop receipt directory: {desktop_receipt_dir}")
            logging.info(f"Backend receipt directory: {backend_receipt_dir}")
            
            # Create receipt directories if they don't exist
            for receipt_dir in [desktop_receipt_dir, backend_receipt_dir]:
                if not os.path.exists(receipt_dir):
                    try:
                        os.makedirs(receipt_dir)
                        logging.info(f"Created directory: {receipt_dir}")
                    except Exception as e:
                        logging.error(f"Error creating directory {receipt_dir}: {e}")
            
            # Define receipt filename and paths
            receipt_filename = f"Sale-{sale_data['id']}.pdf"
            backend_path = os.path.join(backend_receipt_dir, receipt_filename)
            desktop_path = os.path.join(desktop_receipt_dir, receipt_filename)
            
            logging.info(f"Backend receipt path: {backend_path}")
            logging.info(f"Desktop receipt path: {desktop_path}")
            
            try:
                # Create PDF with reportlab (more reliable than Qt's PDF generation)
                logging.info("Creating PDF with reportlab...")
                
                # Make both directories again just to be sure
                os.makedirs(os.path.dirname(backend_path), exist_ok=True)
                os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
                
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
                
                # Verify the file exists and has content
                if os.path.exists(backend_path):
                    size = os.path.getsize(backend_path)
                    logging.info(f"PDF created successfully: {backend_path} ({size} bytes)")
                    print(f"PDF created successfully: {backend_path} ({size} bytes)")
                else:
                    logging.error(f"PDF file not found after creation: {backend_path}")
                    print(f"PDF file not found after creation: {backend_path}")
                    raise FileNotFoundError(f"PDF file not found after creation: {backend_path}")
                
                # Copy the file to the desktop receipt directory
                try:
                    shutil.copy2(backend_path, desktop_path)
                    if os.path.exists(desktop_path):
                        size = os.path.getsize(desktop_path)
                        logging.info(f"PDF copied to desktop app directory: {desktop_path} ({size} bytes)")
                        print(f"PDF copied to desktop app directory: {desktop_path} ({size} bytes)")
                    else:
                        logging.error(f"Copy exists but file not found: {desktop_path}")
                        print(f"Copy exists but file not found: {desktop_path}")
                except Exception as e:
                    logging.error(f"Error copying to desktop directory: {e}")
                    print(f"Error copying to desktop directory: {e}")
                    # Continue anyway, we have the primary copy
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Receipt has been saved successfully."
                )
                
                # Open the PDF in a separate thread
                def open_pdf_thread():
                    try:
                        # Small delay to ensure PDF is fully written
                        time.sleep(1.0)
                        
                        # Verify the file exists
                        receipt_path = None
                        for path in [backend_path, desktop_path]:
                            if os.path.exists(path) and os.path.getsize(path) > 0:
                                receipt_path = path
                                logging.info(f"Using receipt path: {receipt_path}")
                                break
                                
                        if not receipt_path:
                            logging.error("No valid receipt file found to open")
                            raise FileNotFoundError("No valid receipt file found to open")
                            
                        logging.info(f"Opening receipt: {receipt_path}")
                        
                        # Platform-specific opening
                        if sys.platform == 'win32':
                            os.startfile(receipt_path)
                            logging.info("Used os.startfile on Windows")
                        elif sys.platform == 'darwin':  # macOS
                            subprocess.call(['open', receipt_path])
                            logging.info("Used 'open' command on macOS")
                        else:  # Linux
                            # Try different viewers
                            viewers = ['xdg-open', 'evince', 'okular', 'firefox', 'google-chrome']
                            opened = False
                            
                            for viewer in viewers:
                                try:
                                    logging.info(f"Trying to open with {viewer}...")
                                    result = subprocess.call([viewer, receipt_path])
                                    if result == 0:
                                        logging.info(f"Successfully opened with {viewer}")
                                        opened = True
                                        break
                                except Exception as e:
                                    logging.info(f"Error with {viewer}: {e}")
                            
                            if not opened:
                                # Fall back to opening the directory
                                directory = os.path.dirname(receipt_path)
                                logging.info(f"Opening directory: {directory}")
                                subprocess.call(['xdg-open', directory])
                                
                                # Show message about the location
                                QMessageBox.information(
                                    self,
                                    "Receipt Location",
                                    f"The receipt has been saved to:\n{receipt_path}\n\nOpening the folder containing the receipt."
                                )
                                
                    except Exception as e:
                        logging.error(f"Error in open_pdf_thread: {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                
                # Start the thread to open the PDF
                Thread(target=open_pdf_thread).start()
                
                logging.info("===== RECEIPT CREATION COMPLETED (FIXED VERSION) =====")
                return True
            except Exception as e:
                logging.error(f"Error creating PDF: {e}")
                logging.error(traceback.format_exc())
                print(f"Error creating PDF: {e}")
                
                # Show error message
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to create receipt PDF: {str(e)}"
                )
                return False
        except Exception as e:
            logging.error(f"Unhandled error in print_sale_ticket: {e}")
            import traceback
            logging.error(traceback.format_exc())
            print(f"Unhandled error in print_sale_ticket: {e}")
            
            # Show error message
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to print receipt: {str(e)}"
            )
            return False"""
    
    # Replace the function in the content
    new_content = pattern.sub(replacement, content)
    
    # Write the updated content back to the file
    with open(pos_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Successfully updated print_sale_ticket function in {pos_file_path}")
    return True

if __name__ == "__main__":
    print("=== Fixing Receipt Generation ===")
    replace_function_in_file()
    print("\nNext steps:")
    print("1. Restart the POS application")
    print("2. Create a test sale")
    print("3. Check if the receipt is created in the receipt directory")
    print("4. If issues persist, check the log file at:")
    print("   ~/receipt_debug_fixed.log")
