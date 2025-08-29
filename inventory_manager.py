import streamlit as st
from local_storage import read_data, write_data, update_data, delete_data
import uuid
from datetime import datetime

def inventory_management_page():
    """Inventory management interface"""
    st.header("📦 Inventory Management")
    
    # Tabs for different inventory operations
    tab1, tab2, tab3 = st.tabs(["Add New Item", "Edit Items", "View Inventory"])
    
    with tab1:
        add_new_item()
    
    with tab2:
        edit_items()
    
    with tab3:
        view_inventory()

def add_new_item():
    """Add new inventory item"""
    st.subheader("➕ Add New Item")
    
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Item Name*", placeholder="e.g., T-Shirt, Poster, Model Plane")
            item_category = st.selectbox("Category", 
                ["Apparel", "Merchandise", "Models", "Accessories", "Books", "Other"])
            item_price = st.number_input("Price ($)*", min_value=0.0, step=0.01, format="%.2f")
        
        with col2:
            item_description = st.text_area("Description", placeholder="Optional item description")
            initial_stock = st.number_input("Initial Stock", min_value=0, value=0)
            item_sku = st.text_input("SKU (Optional)", placeholder="Stock Keeping Unit")
        
        submitted = st.form_submit_button("Add Item", type="primary")
        
        if submitted:
            if item_name and item_price > 0:
                item_id = str(uuid.uuid4())
                item_data = {
                    'id': item_id,
                    'name': item_name,
                    'category': item_category,
                    'price': float(item_price),
                    'description': item_description,
                    'stock': initial_stock,
                    'sku': item_sku,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'active': True
                }
                
                # Read existing inventory
                inventory = read_data('inventory')
                inventory[item_id] = item_data
                
                if write_data('inventory', inventory):
                    st.success(f"✅ Item '{item_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add item")
            else:
                st.error("Please fill in all required fields (marked with *)")

def edit_items():
    """Edit existing inventory items"""
    st.subheader("✏️ Edit Items")
    
    # Load inventory
    inventory = read_data('inventory')
    
    if not inventory:
        st.info("No items in inventory yet.")
        return
    
    # Create list of items for selection
    items_list = []
    for item_id, item_data in inventory.items():
        if item_data.get('active', True):
            items_list.append((f"{item_data['name']} - ${item_data['price']:.2f}", item_id))
    
    if not items_list:
        st.info("No active items to edit.")
        return
    
    selected_item = st.selectbox("Select item to edit:", 
                                options=[item[1] for item in items_list],
                                format_func=lambda x: next(item[0] for item in items_list if item[1] == x))
    
    if selected_item:
        item_data = inventory[selected_item]
        
        with st.form("edit_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Item Name", value=item_data['name'])
                new_category = st.selectbox("Category", 
                    ["Apparel", "Merchandise", "Models", "Accessories", "Books", "Other"],
                    index=["Apparel", "Merchandise", "Models", "Accessories", "Books", "Other"].index(item_data.get('category', 'Other')))
                new_price = st.number_input("Price ($)", value=float(item_data['price']), min_value=0.0, step=0.01, format="%.2f")
            
            with col2:
                new_description = st.text_area("Description", value=item_data.get('description', ''))
                new_stock = st.number_input("Stock", value=item_data.get('stock', 0), min_value=0)
                new_sku = st.text_input("SKU", value=item_data.get('sku', ''))
            
            col3, col4 = st.columns(2)
            with col3:
                update_submitted = st.form_submit_button("Update Item", type="primary")
            with col4:
                deactivate_submitted = st.form_submit_button("Deactivate Item", type="secondary")
            
            if update_submitted:
                updated_data = {
                    'name': new_name,
                    'category': new_category,
                    'price': float(new_price),
                    'description': new_description,
                    'stock': new_stock,
                    'sku': new_sku,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Update inventory item
                inventory = read_data('inventory')
                if selected_item in inventory:
                    inventory[selected_item].update(updated_data)
                    if write_data('inventory', inventory):
                        st.success("✅ Item updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update item")
            
            if deactivate_submitted:
                inventory = read_data('inventory')
                if selected_item in inventory:
                    inventory[selected_item].update({'active': False, 'updated_at': datetime.now().isoformat()})
                    if write_data('inventory', inventory):
                        st.success("✅ Item deactivated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to deactivate item")

def view_inventory():
    """View all inventory items"""
    st.subheader("👀 View Inventory")
    
    inventory = read_data('inventory')
    
    if not inventory:
        st.info("No items in inventory yet.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_inactive = st.checkbox("Show inactive items")
    with col2:
        category_filter = st.selectbox("Filter by category", 
                                     ["All"] + ["Apparel", "Merchandise", "Models", "Accessories", "Books", "Other"])
    
    # Display items in a table format
    items_data = []
    for item_id, item_data in inventory.items():
        if not show_inactive and not item_data.get('active', True):
            continue
        if category_filter != "All" and item_data.get('category') != category_filter:
            continue
            
        items_data.append({
            'Name': item_data['name'],
            'Category': item_data.get('category', 'N/A'),
            'Price': f"${item_data['price']:.2f}",
            'Stock': item_data.get('stock', 0),
            'SKU': item_data.get('sku', 'N/A'),
            'Status': 'Active' if item_data.get('active', True) else 'Inactive',
            'Created': item_data.get('created_at', 'N/A')[:10] if item_data.get('created_at') else 'N/A'
        })
    
    if items_data:
        st.dataframe(items_data, use_container_width=True)
        st.info(f"Total items: {len(items_data)}")
    else:
        st.info("No items match the current filters.")
