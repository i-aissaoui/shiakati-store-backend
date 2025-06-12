#!/usr/bin/env python3
"""
This script creates a fixed version of the print_sale_ticket function that
uses reportlab instead of Qt's PDF generator, which may be more reliable.
"""

import os
import sys
import shutil
import re

def create_fixed_ticket_function():
    """Create a fixed version of the print_sale_ticket function."""
    
    fixed_function = """    def print_sale_ticket(self, sale_data):
        """Print a sale ticket and open it with the default PDF viewer."""
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
                
                c.drawString(10 * mm, y_position, f"Date: {date_str}")
                y_position -= line_height
                c.drawString(10 * mm, y_position, f"Sale: {sale_data['id']}")
                y_position -= line_height * 1.5
                
                # Draw separator
                c.line(10 * mm, y_position, 70 * mm, y_position)
                y_position -= line_height
                
                # Draw column headers
                c.setFont("Helvetica-Bold", 7)
                c.drawString(10 * mm, y_position, "Item")
                c.drawString(50 * mm, y_position, "Qty")
                c.drawString(55 * mm, y_position, "Price")
                c.drawString(65 * mm, y_position, "Total")
                y_position -= line_height
                
                # Draw separator
                c.line(10 * mm, y_position, 70 * mm, y_position)
                y_position -= line_height
                
                # Draw items
                c.setFont("Helvetica", 7)
                total_amount = 0
                
                for item in sale_data.get("items", []):
                    product_name = item.get("product_name", "Unknown Product")
                    quantity = float(item.get("quantity", 1))
                    price = float(item.get("price", 0))
                    total = quantity * price
                    total_amount += total
                    
                    # Handle long product names
                    if len(product_name) > 25:
                        # First line with name
                        c.drawString(10 * mm, y_position, product_name[:25])
                        y_position -= line_height
                        # Second line with quantity, price, total
                        c.drawString(10 * mm, y_position, product_name[25:50])
                        c.drawString(50 * mm, y_position, f"{int(quantity)}")
                        c.drawString(55 * mm, y_position, f"{price:.2f}")
                        c.drawString(65 * mm, y_position, f"{total:.2f}")
                    else:
                        c.drawString(10 * mm, y_position, product_name)
                        c.drawString(50 * mm, y_position, f"{int(quantity)}")
                        c.drawString(55 * mm, y_position, f"{price:.2f}")
                        c.drawString(65 * mm, y_position, f"{total:.2f}")
                    
                    y_position -= line_height
                    
                    # Check if we need a new page
                    if y_position < 20 * mm:
                        c.showPage()
                        y_position = 190 * mm
                        c.setFont("Helvetica", 7)
                
                # Draw separator
                c.line(10 * mm, y_position, 70 * mm, y_position)
                y_position -= line_height * 1.5
                
                # Draw total
                c.setFont("Helvetica-Bold", 10)
                c.drawString(40 * mm, y_position, f"Total: {total_amount:.2f} DZD")
                y_position -= line_height * 2
                
                # Draw footer
                c.setFont("Helvetica", 8)
                c.drawCentredString(40 * mm, y_position, "Thank you")
                
                # Save the PDF
                c.showPage()
                c.save()
                
                # Check if file was created
                backend_exists = os.path.exists(backend_path)
                if backend_exists:
                    file_size = os.path.getsize(backend_path)
                    logging.info(f"PDF successfully generated: {backend_path} ({file_size} bytes)")
                else:
                    logging.error(f"PDF not found after generation: {backend_path}")
                
                # Copy to desktop_app receipt directory
                try:
                    if backend_exists:
                        shutil.copyfile(backend_path, desktop_path)
                        desktop_exists = os.path.exists(desktop_path)
                        if desktop_exists:
                            file_size = os.path.getsize(desktop_path)
                            logging.info(f"PDF copied to desktop app: {desktop_path} ({file_size} bytes)")
                        else:
                            logging.error(f"Failed to copy PDF to desktop app")
                except Exception as e:
                    logging.error(f"Error copying PDF: {e}")
                
                # Verify files exist
                backend_exists = os.path.exists(backend_path)
                desktop_exists = os.path.exists(desktop_path)
                logging.info(f"Backend receipt exists: {backend_exists}, path: {backend_path}")
                logging.info(f"Desktop receipt exists: {desktop_exists}, path: {desktop_path}")
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Receipt has been saved successfully."
                )
                
                # Define PDF opening function
                def open_pdf_thread():
                    try:
                        # Small delay to ensure PDF is fully written
                        time.sleep(0.5)
                        
                        # Choose which file to open (prefer backend)
                        receipt_path = backend_path if backend_exists else desktop_path
                        
                        if not os.path.exists(receipt_path):
                            logging.error(f"No receipt file found to open")
                            return False
                        
                        logging.info(f"Opening receipt: {receipt_path}")
                        
                        # Platform-specific opening
                        if sys.platform == 'win32':
                            os.startfile(receipt_path)
                            logging.info("Used os.startfile on Windows")
                        elif sys.platform == 'darwin':  # macOS
                            subprocess.call(['open', receipt_path])
                            logging.info("Used 'open' on macOS")
                        else:  # Linux
                            viewers = ['xdg-open', 'evince', 'okular', 'firefox', 'google-chrome']
                            success = False
                            
                            for viewer in viewers:
                                try:
                                    logging.info(f"Trying {viewer}...")
                                    result = subprocess.call([viewer, receipt_path])
                                    if result == 0:
                                        logging.info(f"Successfully opened with {viewer}")
                                        success = True
                                        break
                                except Exception as e:
                                    logging.error(f"Error with {viewer}: {e}")
                            
                            if not success:
                                logging.info("All PDF viewers failed, opening receipt directory...")
                                receipt_dir = os.path.dirname(receipt_path)
                                subprocess.call(['xdg-open', receipt_dir])
                                QMessageBox.information(
                                    self,
                                    "Receipt Location",
                                    f"Your receipt has been saved to:\n{receipt_path}\n\nOpening the folder containing the receipt."
                                )
                    except Exception as e:
                        logging.error(f"Error opening PDF: {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                
                # Start PDF opening in a separate thread
                Thread(target=open_pdf_thread).start()
                
                logging.info("===== RECEIPT CREATION COMPLETED SUCCESSFULLY =====")
                return True
                
            except Exception as e:
                logging.error(f"Error creating receipt PDF: {e}")
                import traceback
                logging.error(traceback.format_exc())
                
                QMessageBox.warning(
                    self,
                    "Receipt Creation Error",
                    f"Failed to create receipt: {str(e)}\n\nPlease check the log file for details."
                )
                return False
                
        except Exception as e:
            print(f"Error in print_sale_ticket: {str(e)}")
            import traceback
            traceback.print_exc()
            
            QMessageBox.warning(self, "Print Error", f"Failed to print receipt: {str(e)}")
            return False"""
    
    return fixed_function

def update_pos_page():
    """Update the pos_page.py file with the fixed print_sale_ticket function."""
    pos_page_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "pos_page.py"
    )
    
    # Back up the original file
    backup_path = pos_page_path + ".reportlab_backup"
    shutil.copy2(pos_page_path, backup_path)
    print(f"Created backup at: {backup_path}")
    
    # Read the file content
    with open(pos_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the pattern for the print_sale_ticket function
    function_pattern = re.compile(r"def print_sale_ticket\(self, sale_data\):.*?(?=\n    def|\n\nclass|\Z)", re.DOTALL)
    
    # Find the function in the file
    match = function_pattern.search(content)
    if not match:
        print("Error: Could not find the print_sale_ticket function in the file.")
        return False
    
    # Replace the old function with the new implementation
    new_content = function_pattern.sub(create_fixed_ticket_function(), content)
    
    # Write the updated content back to the file
    with open(pos_page_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated {pos_page_path}")
    print("The receipt generation now uses reportlab instead of Qt's PDF generator.")
    print("This should fix the issues with receipts not being saved.")
    
    return True

def update_requirements():
    """Add reportlab to requirements.txt if it's not already there."""
    requirements_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "requirements.txt"
    )
    
    if not os.path.exists(requirements_path):
        print(f"Requirements file not found at: {requirements_path}")
        return False
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = f.read()
    
    if "reportlab" not in requirements.lower():
        with open(requirements_path, 'a', encoding='utf-8') as f:
            f.write("\n# Added for improved receipt generation\nreportlab>=3.6.12\n")
        print("Added reportlab to requirements.txt")
        print("Please run: pip install reportlab")
    else:
        print("reportlab already in requirements.txt")
    
    return True

def main():
    print("===== FIXED RECEIPT GENERATION IMPLEMENTATION =====")
    
    # Update the print_sale_ticket function
    success = update_pos_page()
    
    # Update requirements.txt
    update_requirements()
    
    if success:
        print("\n===== NEXT STEPS =====")
        print("1. Install reportlab if it's not already installed:")
        print("   pip install reportlab")
        print("\n2. Restart the POS application")
        print("\n3. Try creating a sale with the new receipt generator")
        print("\n4. Check the debug log file at:")
        print("   ~/receipt_debug_fixed.log")
    
    return success

if __name__ == "__main__":
    main()
