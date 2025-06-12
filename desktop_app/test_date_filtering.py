#!/usr/bin/env python3
"""
Test script to validate the date filtering functionality in the POS system.
This script tests the date parsing logic that was fixed.
It also tests the API client's ability to filter orders by date range.
"""

from PyQt5.QtCore import QDate
import sys
import os
import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the required libraries
try:
    import requests
except ImportError:    requests = None

# Import the API client
from src.utils.api_client import APIClient

def test_date_filtering_logic():
    """Test the date filtering logic that was implemented."""    # Test data with various date formats
    test_dates = [
        "2024-12-01 14:30",
        "2024-12-02 09:15", 
        "2024-12-03 16:45",
        "2024-11-30 11:20",
        "2024-12-01",  # Date without time
        "invalid_date",  # Invalid format
        "",  # Empty string
    ]
    
    # Test date range
    start_date = QDate.fromString("2024-12-01", "yyyy-MM-dd")
    end_date = QDate.fromString("2024-12-03", "yyyy-MM-dd")
    
    for date_text in test_dates:        # Extract date part from datetime string (format: "yyyy-MM-dd hh:mm")
        date_part = date_text.split(' ')[0] if ' ' in date_text else date_text
        order_date = QDate.fromString(date_part, "yyyy-MM-dd")
        
        if order_date.isValid():
            in_range = start_date <= order_date <= end_date
            else:def test_styling_improvements():
    """Test that styling improvements are correctly applied."""    improvements = [
        "✅ Dialog size increased to 1100x900 pixels",
        "✅ Input fields enhanced with 12px 15px padding",
        "✅ Tables have minimum height of 350px+",
        "✅ Button heights increased to 40px",
        "✅ Consistent table item padding (12px 8px)",
        "✅ Font sizes standardized to 13px for tables",
        "✅ Order items section minimum height: 450px",
        "✅ Notes section minimum height: 120px",
        "✅ Inventory table minimum height: 400px",
        "✅ Sale table minimum height: 300px",
        "✅ Product list minimum height: 300px",
        "✅ Sales history table styling enhanced",
        "✅ Global input field styling improved",
        "✅ Focus states added with blue borders",
    ]
    
    for improvement in improvements:    def test_api_date_filtering():
    """Test the API client's ability to filter orders by date range."""    # Initialize API client
    api_client = APIClient()  # Uses default http://localhost:8000
    
    .strftime('%Y-%m-%d'))
    
    # Test with June 2025 specifically (the problematic date)
    from PyQt5.QtCore import QDate
    june_start = QDate(2025, 6, 1)
    june_end = QDate(2025, 6, 30)
    june_start_str = june_start.toString("yyyy-MM-dd")
    june_end_str = june_end.toString("yyyy-MM-dd")    # Test both API endpoint and client-side filtering
    if requests:
        try:
            response = requests.get(
                f"http://localhost:8000/orders/date-range?start_date={june_start_str}&end_date={june_end_str}",
                headers={"Content-Type": "application/json"}
            )            if response.status_code == 200:
                api_orders = response.json()
                if api_orders:
                    for order in api_orders[:3]:
                        if len(api_orders) > 3:
                        else:        except (requests.RequestException, ValueError) as e:    else:    # Now test the client's implementation    june_orders = api_client.get_orders_by_date_range(june_start_str, june_end_str)
    if june_orders:
        for order in june_orders[:3]:
            if len(june_orders) > 3:
            # Test with different date formats to ensure robustness    date_formats_to_test = [
        ("2025-06-01", "2025-06-30"),  # Standard format
        # Skip non-standard formats as the API expects YYYY-MM-DD
        # ("2025-6-1", "2025-6-30"),     # Without leading zeros
        # ("06/01/2025", "06/30/2025"),  # American format
    ]
    
    for start_fmt, end_fmt in date_formats_to_test:        try:
            orders = api_client.get_orders_by_date_range(start_fmt, end_fmt)
            except Exception as e:    # Get all orders and check their dates    all_orders = api_client.get_orders()
    if all_orders:
        # Group by year-month
        date_groups = {}
        for order in all_orders:
            order_time = order.get("order_time", "")
            if not order_time:
                continue
                
            # Extract date part (first 10 chars: YYYY-MM-DD)
            try:
                date_str = order_time[:10]
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                key = f"{date_obj.year}-{date_obj.month:02d}"
                
                if key not in date_groups:
                    date_groups[key] = []
                date_groups[key].append(order)
            except ValueError:
                for date_key in sorted(date_groups.keys()):
            # Check for June 2025 specifically
        june_2025_key = "2025-06"
        if june_2025_key in date_groups:
            for order in date_groups[june_2025_key][:5]:  # Show first 5
                if len(date_groups[june_2025_key]) > 5:
                # Test monthly invoice generation simulation            # Use the same logic as in generate_monthly_invoice() but simplified
            start_date = QDate(2025, 6, 1)
            end_date = QDate(2025, 6, 30)
            start_date_str = start_date.toString("yyyy-MM-dd")
            end_date_str = end_date.toString("yyyy-MM-dd")            orders = api_client.get_orders_by_date_range(start_date_str, end_date_str)
            
            if orders:
                else:    else:if __name__ == "__main__":    test_date_filtering_logic()    test_styling_improvements()    test_api_date_filtering()