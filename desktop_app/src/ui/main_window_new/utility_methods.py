"""
Utility methods for the Shiakati Store POS application that are added to the MainWindow class.
"""

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox


def format_price(self, amount):
    """Format a price with the DZD currency."""
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            return amount
    
    return f"{amount:.2f} DZD"


def parse_price(self, price_str):
    """Parse a price string into a float."""
    if isinstance(price_str, (int, float)):
        return float(price_str)
        
    # Remove currency symbol and any thousand separators
    clean_str = price_str.replace('DZD', '').replace(',', '').strip()
    try:
        return float(clean_str)
    except ValueError:
        return 0.0


def format_datetime(self, dt_str, output_format="yyyy-MM-dd hh:mm"):
    """Format a datetime string into a more readable format."""
    date_time = QDateTime.fromString(dt_str, Qt.ISODateWithMs)
    return date_time.toString(output_format)


def apply_spinbox_styling(self, spinbox):
    """Apply consistent styling to a spinbox."""
    if isinstance(spinbox, (QSpinBox, QDoubleSpinBox)):
        spinbox.setStyleSheet("""
            QSpinBox, QDoubleSpinBox {
                padding: 8px 12px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                width: 20px;
                border-left: 1px solid #dcdde1;
                border-bottom: 1px solid #dcdde1;
                border-top-right-radius: 4px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 20px;
                border-left: 1px solid #dcdde1;
                border-top: 1px solid #dcdde1;
                border-bottom-right-radius: 4px;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 10px;
                height: 10px;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)
