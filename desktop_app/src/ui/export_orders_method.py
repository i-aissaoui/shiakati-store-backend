def export_orders_to_excel(self):
    """Export orders data to Excel spreadsheet."""
    try:
        # Get orders data from API client
        orders = self.api_client.get_orders()
        if not orders:
            QMessageBox.warning(self, "No Data", "No orders available to export.")
            return
        
        # Create Excel workbook
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Orders"
        
        # Define header style
        header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4834d4', end_color='4834d4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        header_border = Border(
            left=Side(border_style='thin', color='000000'),
            right=Side(border_style='thin', color='000000'),
            top=Side(border_style='thin', color='000000'),
            bottom=Side(border_style='thin', color='000000')
        )
        
        # Define data style
        data_font = Font(name='Arial', size=11)
        data_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        data_border = Border(
            left=Side(border_style='thin', color='000000'),
            right=Side(border_style='thin', color='000000'),
            top=Side(border_style='thin', color='000000'),
            bottom=Side(border_style='thin', color='000000')
        )
        
        # Alternate row colors
        even_row_fill = PatternFill(start_color='f5f6fa', end_color='f5f6fa', fill_type='solid')
        odd_row_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
        
        # Define headers
        headers = [
            "Order ID", "Date", "Customer", "Phone", "Product", 
            "Size", "Color", "Quantity", "Price", "Total", 
            "Delivery Method", "Wilaya", "Commune", "Status", "Notes"
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = header_border
        
        # Add data rows
        row_num = 2
        for order in orders:
            order_id = order.get("id", "N/A")
            order_date = order.get("order_time", "")
            customer_name = order.get("customer_name", "N/A")
            phone_number = order.get("phone_number", "N/A")
            status = order.get("status", "N/A").capitalize()
            delivery_method = order.get("delivery_method", "N/A").capitalize()
            wilaya = order.get("wilaya", "N/A")
            commune = order.get("commune", "N/A")
            notes = order.get("notes", "")
            total = float(order.get("total", 0))
            
            # Get items for this order
            items = order.get("items", [])
            
            if not items:
                # If no items, add a single row with order info
                row_fill = even_row_fill if row_num % 2 == 0 else odd_row_fill
                
                for col_num, value in enumerate([
                    order_id, order_date, customer_name, phone_number, "No Items", 
                    "N/A", "N/A", 0, 0, total,
                    delivery_method, wilaya, commune, status, notes
                ], 1):
                    cell = worksheet.cell(row=row_num, column=col_num)
                    cell.value = value
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = data_border
                    cell.fill = row_fill
                    
                row_num += 1
            else:
                # Add a row for each item in the order
                for item in items:
                    product_name = item.get("product_name", "Unknown Product")
                    size = item.get("size", "N/A")
                    color = item.get("color", "N/A")
                    quantity = float(item.get("quantity", 0))
                    price = float(item.get("price", 0))
                    
                    row_fill = even_row_fill if row_num % 2 == 0 else odd_row_fill
                    
                    for col_num, value in enumerate([
                        order_id, order_date, customer_name, phone_number, product_name,
                        size, color, quantity, price, total,
                        delivery_method, wilaya, commune, status, notes
                    ], 1):
                        cell = worksheet.cell(row=row_num, column=col_num)
                        cell.value = value
                        cell.font = data_font
                        cell.alignment = data_alignment
                        cell.border = data_border
                        cell.fill = row_fill
                        
                    row_num += 1
        
        # Auto-adjust column widths
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            
            for cell in col:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column].width = adjusted_width
        
        # Ask for save location with default filename
        default_filename = f"Shiakati_Orders_{QDateTime.currentDateTime().toString('yyyy-MM-dd_hh-mm')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Orders to Excel",
            default_filename,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            # Add .xlsx extension if not provided by user
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # Save the file
            workbook.save(file_path)
            
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Orders data successfully exported to:\n{file_path}"
            )
            
            # Ask if user wants to open the file
            reply = QMessageBox.question(
                self,
                "Open File",
                "Do you want to open the exported file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Open the file with default system application
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # macOS/Linux
                    import subprocess
                    subprocess.call(('xdg-open', file_path))
    
    except Exception as e:
        QMessageBox.critical(
            self, 
            "Export Error", 
            f"Failed to export orders data: {str(e)}"
        )
        import traceback
        traceback.print_exc()
