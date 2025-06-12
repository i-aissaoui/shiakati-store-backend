#!/usr/bin/env python3
"""
Direct fix for pos_page.py - run this to clean up the pos_page
"""

import os
import re
import shutil
import sys

def fix_pos_page():
    """Fix the POS page by directly replacing it with a clean version."""
    print("Starting direct pos_page.py fix...")
    
    # Find the POS page file
    pos_page_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_app", "src", "ui", "main_window_new", "pos_page.py"
    )
    
    if not os.path.exists(pos_page_path):
        print(f"Error: Could not find pos_page.py at {pos_page_path}")
        return False
    
    # Create a backup
    backup_path = f"{pos_page_path}.debug_bak"
    try:
        shutil.copy2(pos_page_path, backup_path)
        print(f"Created backup at: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    # Read the file
    try:
        with open(pos_page_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Read pos_page.py: {len(content)} bytes")
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Replace print_sale_ticket function - completely rewritten version without any logging/debugging
    pattern = r'def print_sale_ticket\(self, sale_data\):.*?(?=\n    def|\n\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find print_sale_ticket function in pos_page.py")
        return False
    
    clean_function = """    def print_sale_ticket(self, sale_data):
        \"\"\"Print a sale ticket and open it with the default PDF viewer.\"\"\"
        try:
            import os
            import sys
            import shutil
            import subprocess
            import time
            from threading import Thread
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from reportlab.lib.pagesizes import A4
            from PyQt5.QtWidgets import QMessageBox
            
            # Get the relevant directory paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            desktop_app_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            backend_dir = os.path.dirname(desktop_app_dir)
            
            # Define receipt directories
            backend_receipt_dir = os.path.join(backend_dir, "receipt")
            desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
            
            # Create directories if they don't exist
            os.makedirs(backend_receipt_dir, exist_ok=True)
            os.makedirs(desktop_receipt_dir, exist_ok=True)
            
            # Create receipt filename with timestamp to avoid overwriting
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            receipt_filename = f"Sale-{sale_data['id']}-{timestamp}.pdf"
            backend_path = os.path.join(backend_receipt_dir, receipt_filename)
            desktop_path = os.path.join(desktop_receipt_dir, receipt_filename)
            
            try:
                # Create PDF with reportlab
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
                    # PDF was created successfully
                    pass
                else:
                    raise FileNotFoundError(f"PDF file not found after creation: {backend_path}")
                
                # Copy to desktop app receipt directory
                try:
                    shutil.copy2(backend_path, desktop_path)
                except Exception:
                    # Continue anyway, we have the primary copy
                    pass
                
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
                    except Exception:
                        pass
                
                # Start the thread to open the PDF
                Thread(target=open_pdf_thread).start()
                return True
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to create receipt PDF: {str(e)}"
                )
                return False
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to print receipt: {str(e)}"
            )
            return False"""
    
    # Replace the function
    new_content = content.replace(match.group(0), clean_function)
    
    # Also remove print error statements
    new_content = new_content.replace('print(f"Error adding product: {str(e)}")  # Add debug logging', 'pass  # Error adding product')
    
    # Write the updated content back to the file
    try:
        with open(pos_page_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully updated pos_page.py!")
        return True
    except Exception as e:
        print(f"Error writing updated file: {e}")
        return False

if __name__ == "__main__":
    if fix_pos_page():
        print("POS page fixed successfully!")
    else:
        print("Failed to fix POS page")
        sys.exit(1)
