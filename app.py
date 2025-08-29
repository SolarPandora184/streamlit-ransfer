import streamlit as st
import os
from local_storage import initialize_local_storage, read_data, push_data, update_data, write_data
from inventory_manager import inventory_management_page
from sales_interface import sales_interface_page
from turned_away_tracker import turned_away_tracker_page, add_turned_away_entry
from export_manager import export_data_page, generate_export
from datetime import datetime, timedelta
import uuid

# Initialize Local Storage
try:
    initialize_local_storage()
    st.success("Local storage initialized successfully!")
except Exception as e:
    st.error(f"Failed to initialize local storage: {str(e)}")
    st.stop()

def main():
    st.set_page_config(
        page_title="Airshow POS System",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("✈️ Airshow Point of Sale System")
    
    # Sidebar navigation - simplified
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Main Sales Panel", "Inventory Management"]
    )
    
    # Display current date and time
    import datetime
    st.sidebar.info(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Route to appropriate page
    if page == "Main Sales Panel":
        main_sales_panel()
    elif page == "Inventory Management":
        inventory_management_page()

def main_sales_panel():
    """Main sales panel with everything in one view"""
    # Load inventory (read-only)
    inventory = read_data('inventory')
    
    if not inventory:
        st.warning("⚠️ No inventory items available. Please add items in the Inventory Management section first.")
        return
    
    # Filter active items only
    active_items = {k: v for k, v in inventory.items() if v.get('active', True)}
    
    if not active_items:
        st.warning("⚠️ No active items available for sale.")
        return
    
    # Current cart in session state
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    # Main layout with columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Item buttons section
        st.subheader("🛍️ Select Items")
        
        # Create item buttons in a grid
        items_list = list(active_items.items())
        cols_per_row = 3
        
        for i in range(0, len(items_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(items_list):
                    item_id, item_data = items_list[i + j]
                    with col:
                        # Item button
                        button_text = f"{item_data['name']}\n${item_data['price']:.2f}"
                        stock_info = f"Stock: {item_data.get('stock', 0)}"
                        
                        if st.button(button_text, key=f"item_{item_id}", help=stock_info, width="stretch"):
                            add_item_to_cart(item_id, item_data, 1)
                        
                        # Show stock status
                        stock = item_data.get('stock', 0)
                        if stock <= 5:
                            if stock == 0:
                                st.error("Out of stock")
                            else:
                                st.warning(f"Low stock: {stock}")
                        else:
                            st.success(f"Stock: {stock}")
    
    with col2:
        # Cart and other controls
        display_cart_and_controls()

def add_item_to_cart(item_id, item_data, quantity):
    """Add item to cart"""
    # Check if item already in cart
    for cart_item in st.session_state.cart:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += quantity
            st.success(f"Updated {item_data['name']} in cart!")
            st.rerun()
            return
    
    # Add new item to cart
    cart_item = {
        'id': item_id,
        'name': item_data['name'],
        'price': item_data['price'],
        'quantity': quantity
    }
    
    st.session_state.cart.append(cart_item)
    st.success(f"Added {item_data['name']} to cart!")
    st.rerun()

def display_cart_and_controls():
    """Display cart and all other controls in right column"""
    st.subheader("🛒 Current Cart")
    
    if not st.session_state.cart:
        st.info("Cart is empty")
    else:
        total = 0
        
        # Display cart items
        for i, item in enumerate(st.session_state.cart):
            item_total = item['price'] * item['quantity']
            total += item_total
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"{item['name']}")
                st.caption(f"${item['price']:.2f} x {item['quantity']}")
            with col2:
                st.write(f"${item_total:.2f}")
            with col3:
                if st.button("❌", key=f"remove_{i}", help="Remove from cart"):
                    st.session_state.cart.pop(i)
                    st.rerun()
        
        st.divider()
        st.metric("Total", f"${total:.2f}")
        
        # Payment section
        if st.session_state.cart:
            st.subheader("💰 Payment")
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Zelle"]
            )
            
            customer_notes = st.text_input("Customer Notes (Optional)")
            
            if st.button("🔔 Complete Sale", type="primary", width="stretch"):
                complete_transaction(payment_method, customer_notes, total)
            
            if st.button("🗑️ Clear Cart", width="stretch"):
                st.session_state.cart = []
                st.rerun()
    
    st.divider()
    
    # Turned away section
    st.subheader("👋 Turned Away")
    st.caption("Track customers who didn't purchase")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💰 Too Expensive", width="stretch"):
            add_turned_away_entry("Too expensive")
        if st.button("🔍 Just Looking", width="stretch"):
            add_turned_away_entry("Just looking/browsing")
    
    with col2:
        if st.button("📦 Out of Stock", width="stretch"):
            add_turned_away_entry("Desired item out of stock")
        if st.button("❓ Generic", width="stretch"):
            add_turned_away_entry("Generic - no specific reason")
    
    # Custom reason
    custom_reason = st.text_input("Custom reason:", placeholder="Enter custom reason...")
    if st.button("Add Custom Reason") and custom_reason.strip():
        add_turned_away_entry(custom_reason)
    
    st.divider()
    
    # Quick export section
    st.subheader("📊 Quick Export")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Today's Data", width="stretch"):
            today = datetime.now().date()
            generate_export(today, today, True, True, False)
    
    with col2:
        if st.button("📋 Full Report", width="stretch"):
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            generate_export(week_start, today, True, True, True)

def complete_transaction(payment_method, customer_notes, total):
    """Complete the transaction and save to Firebase"""
    transaction_id = str(uuid.uuid4())
    transaction_data = {
        'id': transaction_id,
        'items': st.session_state.cart,
        'total': total,
        'payment_method': payment_method,
        'customer_notes': customer_notes,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'type': 'sale'
    }
    
    # Save transaction
    if push_data('transactions', transaction_data):
        # Update inventory stock
        update_inventory_stock()
        
        st.success(f"✅ Transaction completed successfully!")
        st.success(f"Transaction ID: {transaction_id}")
        st.success(f"Total: ${total:.2f}")
        
        # Clear cart
        st.session_state.cart = []
        
        # Show transaction summary
        st.balloons()
        
        st.rerun()
    else:
        st.error("❌ Failed to complete transaction. Please try again.")

def update_inventory_stock():
    """Update inventory stock after sale"""
    inventory = read_data('inventory')
    
    if not inventory:
        return
    
    for cart_item in st.session_state.cart:
        item_id = cart_item['id']
        quantity_sold = cart_item['quantity']
        
        if item_id in inventory:
            current_stock = inventory[item_id].get('stock', 0)
            new_stock = max(0, current_stock - quantity_sold)
            
            inventory[item_id].update({
                'stock': new_stock,
                'updated_at': datetime.now().isoformat()
            })
    
    # Write updated inventory back to storage
    write_data('inventory', inventory)

if __name__ == "__main__":
    main()
