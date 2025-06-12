#!/usr/bin/env python3
"""
Script to test creating a receipt PDF.
"""

import os
import sys
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def create_test_sale_receipt():
    """Create a test sale receipt PDF."""
    print("Creating test sale receipt...")
    
    # Get base paths
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.join(backend_dir, "desktop_app")
    
    # Receipt directories
    backend_receipt_dir = os.path.join(backend_dir, "receipt")
    desktop_receipt_dir = os.path.join(desktop_app_dir, "receipt")
    
    # Ensure directories exist
    os.makedirs(backend_receipt_dir, exist_ok=True)
    os.makedirs(desktop_receipt_dir, exist_ok=True)
    
    print(f"Backend receipt directory: {backend_receipt_dir}")
    print(f"Desktop app receipt directory: {desktop_receipt_dir}")
    
    # Create test sale data
    sale_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define receipt paths
    backend_pdf = os.path.join(backend_receipt_dir, f"Sale-{sale_id}-{timestamp}.pdf")
    desktop_pdf = os.path.join(desktop_receipt_dir, f"Sale-{sale_id}-{timestamp}.pdf")
    
    # Create the PDF
    try:
        # Create backend PDF
        c = canvas.Canvas(backend_pdf, pagesize=(80 * mm, 200 * mm))
        c.setTitle(f"Sale-{sale_id}")
        
        # Set initial position
        y_position = 190 * mm
        line_height = 5 * mm
        
        # Draw header
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(40 * mm, y_position, "Shiakati شياكتي")
        y_position -= line_height * 1.5
        
        # Draw date and sale info
        c.setFont("Helvetica", 8)
        c.drawCentredString(40 * mm, y_position, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y_position -= line_height
        c.drawCentredString(40 * mm, y_position, f"Sale: {sale_id}")
        y_position -= line_height * 2
        
        # Draw a line
        c.line(5 * mm, y_position, 75 * mm, y_position)
        y_position -= line_height
        
        # Draw content
        c.setFont("Helvetica", 8)
        c.drawString(5 * mm, y_position, "TEST RECEIPT")
        y_position -= line_height
        c.drawString(5 * mm, y_position, "This is a test receipt")
        y_position -= line_height
        c.drawString(5 * mm, y_position, "to verify PDF creation is working")
        
        # Save the PDF
        c.save()
        
        if os.path.exists(backend_pdf):
            size = os.path.getsize(backend_pdf)
            print(f"✅ Backend PDF created: {backend_pdf} ({size} bytes)")
            
            # Copy to desktop app receipt dir
            import shutil
            shutil.copy2(backend_pdf, desktop_pdf)
            
            if os.path.exists(desktop_pdf):
                size = os.path.getsize(desktop_pdf)
                print(f"✅ Desktop PDF created: {desktop_pdf} ({size} bytes)")
            else:
                print(f"❌ Failed to copy to desktop app directory")
                
            print("\nPDFs have been created successfully!")
            print(f"\nYou can now look for these files:")
            print(f"1. {backend_pdf}")
            print(f"2. {desktop_pdf}")
            
            return True
        else:
            print(f"❌ Failed to create backend PDF")
            return False
            
    except Exception as e:
        import traceback
        print(f"Error creating test receipt: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    create_test_sale_receipt()
