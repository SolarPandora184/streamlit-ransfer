import streamlit as st
from firebase_config import read_data, push_data, update_data
from datetime import datetime
import uuid

def sales_interface_page():
    """Sales interface for creating transactions"""
    st.header("💳 Sales Interface")
    
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
    
    # Display current cart
    display_current_cart()
    
    st.divider()
    
    # Item selection section
    st.subheader("🛍️ Add Items to Cart")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create a list of items for selection
        item_options = []
        for item_id, item_data in active_items.items():
            stock_info = f" (Stock: {item_data.get('stock', 0)})" if item_data.get('stock', 0) > 0 else " (Out of stock)"
            item_options.append({
                'display': f"{item_data['name']} - ${item_data['price']:.2f}{stock_info}",
                'id': item_id,
                'data': item_data
            })
        
        selected_item_index = st.selectbox(
            "Select item to add:",
            range(len(item_options)),
            format_func=lambda x: item_options[x]['display']
        )
    
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1)
    
    if st.button("➕ Add to Cart", type="primary"):
        selected_item = item_options[selected_item_index]
        add_item_to_cart(selected_item['id'], selected_item['data'], quantity)
    
    st.divider()
    
    # Checkout section
    if st.session_state.cart:
        checkout_section()

def display_current_cart():
    """Display the current cart"""
    st.subheader("🛒 Current Cart")
    
    if not st.session_state.cart:
        st.info("Cart is empty")
        return
    
    total = 0
    cart_data = []
    
    for i, item in enumerate(st.session_state.cart):
        item_total = item['price'] * item['quantity']
        total += item_total
        
        cart_data.append({
            'Item': item['name'],
            'Price': f"${item['price']:.2f}",
            'Quantity': item['quantity'],
            'Total': f"${item_total:.2f}"
        })
    
    # Display cart items
    st.dataframe(cart_data, use_container_width=True)
    
    # Cart actions
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("Total", f"${total:.2f}")
    
    with col2:
        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = []
            st.rerun()
    
    with col3:
        # Remove individual items
        if len(st.session_state.cart) > 0:
            item_to_remove = st.selectbox(
                "Remove item:",
                range(len(st.session_state.cart)),
                format_func=lambda x: f"{st.session_state.cart[x]['name']} (Qty: {st.session_state.cart[x]['quantity']})"
            )
            
            if st.button("Remove Selected"):
                st.session_state.cart.pop(item_to_remove)
                st.rerun()

def add_item_to_cart(item_id, item_data, quantity):
    """Add item to cart"""
    # Check if item already in cart
    for cart_item in st.session_state.cart:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += quantity
            st.success(f"Updated quantity of {item_data['name']} in cart!")
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

def checkout_section():
    """Checkout and payment processing"""
    st.subheader("💰 Checkout")
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)
    
    with st.form("checkout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            payment_method = st.selectbox(
                "Payment Method*",
                ["Cash", "Credit Card", "Debit Card", "Mobile Payment", "Check", "Other"]
            )
            
        with col2:
            customer_notes = st.text_input("Customer Notes (Optional)")
        
        # Display order summary
        st.subheader("Order Summary")
        for item in st.session_state.cart:
            st.write(f"• {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}")
        
        st.write(f"**Total: ${total:.2f}**")
        
        submitted = st.form_submit_button("🔔 Complete Sale", type="primary")
        
        if submitted:
            complete_transaction(payment_method, customer_notes, total)

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
            
            update_data(f'inventory/{item_id}', {
                'stock': new_stock,
                'updated_at': datetime.now().isoformat()
            })
