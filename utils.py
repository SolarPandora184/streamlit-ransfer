import streamlit as st
from datetime import datetime
import re

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"

def format_datetime(dt_string):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_string

def validate_price(price):
    """Validate price input"""
    try:
        price_float = float(price)
        return price_float >= 0
    except:
        return False

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    return filename.strip('_')

def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_time():
    """Get current time in HH:MM:SS format"""
    return datetime.now().strftime('%H:%M:%S')

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def show_success_message(message):
    """Show a success message with emoji"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Show an error message with emoji"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Show a warning message with emoji"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Show an info message with emoji"""
    st.info(f"ℹ️ {message}")

def calculate_total(cart_items):
    """Calculate total price for cart items"""
    return sum(item['price'] * item['quantity'] for item in cart_items)

def validate_inventory_item(name, price, category):
    """Validate inventory item data"""
    errors = []
    
    if not name or not name.strip():
        errors.append("Item name is required")
    
    if not validate_price(price):
        errors.append("Price must be a positive number")
    
    if not category or category == "":
        errors.append("Category is required")
    
    return errors

def format_item_display(item_data):
    """Format item data for display"""
    name = item_data.get('name', 'Unknown Item')
    price = item_data.get('price', 0)
    stock = item_data.get('stock', 0)
    
    stock_status = f" (Stock: {stock})" if stock > 0 else " (Out of stock)"
    return f"{name} - ${price:.2f}{stock_status}"

def is_item_in_stock(item_data, requested_quantity=1):
    """Check if item has sufficient stock"""
    current_stock = item_data.get('stock', 0)
    return current_stock >= requested_quantity

def get_low_stock_items(inventory_data, threshold=5):
    """Get items with low stock"""
    low_stock_items = []
    
    for item_id, item_data in inventory_data.items():
        if item_data.get('active', True) and item_data.get('stock', 0) <= threshold:
            low_stock_items.append({
                'id': item_id,
                'name': item_data.get('name', 'Unknown'),
                'stock': item_data.get('stock', 0)
            })
    
    return low_stock_items

def generate_transaction_summary(transaction_data):
    """Generate a formatted transaction summary"""
    items = transaction_data.get('items', [])
    total = transaction_data.get('total', 0)
    payment_method = transaction_data.get('payment_method', 'Unknown')
    
    summary = f"Transaction Total: ${total:.2f}\n"
    summary += f"Payment Method: {payment_method}\n"
    summary += f"Items ({len(items)}):\n"
    
    for item in items:
        item_total = item['price'] * item['quantity']
        summary += f"  • {item['name']} x{item['quantity']} = ${item_total:.2f}\n"
    
    return summary
