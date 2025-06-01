def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    arabic_ranges = [
        (0x0600, 0x06FF),  # Arabic
        (0x0750, 0x077F),  # Arabic Supplement
        (0x08A0, 0x08FF),  # Arabic Extended-A
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
    ]
    
    for char in text:
        code = ord(char)
        for start, end in arabic_ranges:
            if start <= code <= end:
                return True
    return False

def format_column_layout(product_name: str, qty: str, price: str, total: str, name_width: int = 16) -> str:
    """Format a row in the receipt with proper RTL/LTR handling."""
    if is_arabic(product_name):
        # RTL format: Total, Price, Qty, Item
        return f"{total.rjust(6)}  {price.rjust(7)}  {qty.rjust(3)}  {product_name.rjust(name_width)}"
    else:
        # LTR format: Item, Qty, Price, Total
        return f"{product_name.ljust(name_width)}{qty.rjust(3)}  {price.rjust(7)}  {total.rjust(6)}"
