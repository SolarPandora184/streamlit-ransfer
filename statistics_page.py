import streamlit as st
from local_storage import read_data
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

def statistics_page():
    """Comprehensive statistics and analytics page"""
    st.header("📊 Statistics & Analytics")
    
    # Load all data
    transactions_data = read_data('transactions') or {}
    turned_away_data = read_data('turned_away') or {}
    inventory_data = read_data('inventory') or {}
    
    if not transactions_data and not turned_away_data:
        st.info("No data available yet. Make some sales or track turned away customers to see statistics.")
        return
    
    # Date filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Filter data by date range
    filtered_transactions = filter_data_by_date(transactions_data, start_date, end_date)
    filtered_turned_away = filter_data_by_date(turned_away_data, start_date, end_date)
    
    # Main metrics
    display_key_metrics(filtered_transactions, filtered_turned_away, inventory_data)
    
    st.divider()
    
    # Create tabs for different analytics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Sales Analytics", 
        "Payment Analytics", 
        "Category Analytics", 
        "Turned Away Analytics", 
        "Transaction Details"
    ])
    
    with tab1:
        display_sales_analytics(filtered_transactions, inventory_data)
    
    with tab2:
        display_payment_analytics(filtered_transactions)
    
    with tab3:
        display_category_analytics(filtered_transactions, inventory_data)
    
    with tab4:
        display_turned_away_analytics(filtered_turned_away)
    
    with tab5:
        display_transaction_details(filtered_transactions)

def filter_data_by_date(data, start_date, end_date):
    """Filter data by date range"""
    if not data:
        return {}
    
    filtered = {}
    for key, item in data.items():
        try:
            item_date = datetime.strptime(item.get('date', ''), '%Y-%m-%d').date()
            if start_date <= item_date <= end_date:
                filtered[key] = item
        except:
            continue
    
    return filtered

def display_key_metrics(transactions, turned_away, inventory):
    """Display key performance metrics"""
    st.subheader("📈 Key Metrics")
    
    # Calculate metrics
    total_transactions = len(transactions)
    total_revenue = sum(t.get('total', 0) for t in transactions.values())
    avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
    total_turned_away = len(turned_away)
    
    # Get payment type breakdown
    payment_wrong_type = sum(1 for t in turned_away.values() 
                           if 'wrong payment' in t.get('reason', '').lower())
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Sales", total_transactions)
    
    with col2:
        st.metric("Total Revenue", f"${total_revenue:.2f}")
    
    with col3:
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    with col4:
        st.metric("Turned Away", total_turned_away)
    
    with col5:
        st.metric("Wrong Payment", payment_wrong_type)

def display_sales_analytics(transactions, inventory):
    """Display sales analytics"""
    st.subheader("💰 Sales Analytics")
    
    if not transactions:
        st.info("No sales data for selected period.")
        return
    
    # Daily sales chart
    daily_sales = {}
    daily_revenue = {}
    
    for trans in transactions.values():
        date = trans.get('date', '')
        if date:
            daily_sales[date] = daily_sales.get(date, 0) + 1
            daily_revenue[date] = daily_revenue.get(date, 0) + trans.get('total', 0)
    
    if daily_sales:
        # Create daily sales chart
        dates = list(daily_sales.keys())
        sales_counts = list(daily_sales.values())
        revenues = list(daily_revenue.values())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Transaction Count")
            fig = px.bar(x=dates, y=sales_counts, labels={'x': 'Date', 'y': 'Transactions'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Daily Revenue")
            fig = px.bar(x=dates, y=revenues, labels={'x': 'Date', 'y': 'Revenue ($)'})
            st.plotly_chart(fig, use_container_width=True)

def display_payment_analytics(transactions):
    """Display payment method analytics"""
    st.subheader("💳 Payment Method Analytics")
    
    if not transactions:
        st.info("No transaction data for selected period.")
        return
    
    # Count payment methods
    payment_methods = [t.get('payment_method', 'Unknown') for t in transactions.values()]
    payment_counts = Counter(payment_methods)
    
    if payment_counts:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Payment Method Usage")
            fig = px.pie(
                values=list(payment_counts.values()),
                names=list(payment_counts.keys()),
                title="Payment Methods Used"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Payment Method Stats")
            df = pd.DataFrame([
                {'Payment Method': method, 'Count': count, 'Percentage': f"{count/sum(payment_counts.values())*100:.1f}%"}
                for method, count in payment_counts.most_common()
            ])
            st.dataframe(df, use_container_width=True)

def display_category_analytics(transactions, inventory):
    """Display category sales analytics"""
    st.subheader("🏷️ Category Sales Analytics")
    
    if not transactions:
        st.info("No transaction data for selected period.")
        return
    
    # Count items by category
    category_counts = {'Drink': 0, 'Snack': 0, 'Other': 0}
    category_revenue = {'Drink': 0, 'Snack': 0, 'Other': 0}
    
    for trans in transactions.values():
        for item in trans.get('items', []):
            item_id = item.get('id')
            quantity = item.get('quantity', 0)
            price = item.get('price', 0)
            
            # Find category from inventory
            if inventory and item_id in inventory:
                category = inventory[item_id].get('category', 'Other')
            else:
                category = 'Other'
            
            if category in category_counts:
                category_counts[category] += quantity
                category_revenue[category] += price * quantity
    
    # Display category analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Items Sold by Category")
        st.metric("Drinks Sold", category_counts['Drink'])
        st.metric("Snacks Sold", category_counts['Snack'])
        st.metric("Other Items Sold", category_counts['Other'])
    
    with col2:
        st.subheader("Revenue by Category")
        if any(category_counts.values()):
            fig = px.bar(
                x=list(category_counts.keys()),
                y=list(category_revenue.values()),
                labels={'x': 'Category', 'y': 'Revenue ($)'},
                title="Revenue by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

def display_turned_away_analytics(turned_away):
    """Display turned away analytics"""
    st.subheader("👋 Turned Away Analytics")
    
    if not turned_away:
        st.info("No turned away data for selected period.")
        return
    
    # Count reasons
    reasons = [t.get('reason', 'Unknown') for t in turned_away.values()]
    reason_counts = Counter(reasons)
    
    # Specifically track wrong payment type
    wrong_payment_count = sum(1 for reason in reasons 
                            if 'wrong payment' in reason.lower())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Turned Away Reasons")
        st.metric("Wrong Payment Type", wrong_payment_count)
        st.metric("Total Turned Away", len(turned_away))
        
        # Show top reasons
        if reason_counts:
            st.subheader("Top Reasons")
            for reason, count in reason_counts.most_common(5):
                st.write(f"• {reason}: {count}")
    
    with col2:
        if reason_counts:
            st.subheader("Reason Distribution")
            fig = px.pie(
                values=list(reason_counts.values()),
                names=list(reason_counts.keys()),
                title="Turned Away Reasons"
            )
            st.plotly_chart(fig, use_container_width=True)

def display_transaction_details(transactions):
    """Display detailed transaction information"""
    st.subheader("🧾 Transaction Details")
    
    if not transactions:
        st.info("No transaction data for selected period.")
        return
    
    # Create detailed transaction table
    transaction_list = []
    
    for trans_id, trans in transactions.items():
        items_str = ", ".join([f"{item['name']} x{item['quantity']}" 
                              for item in trans.get('items', [])])
        item_count = len(trans.get('items', []))
        total_quantity = sum(item.get('quantity', 0) for item in trans.get('items', []))
        
        confirmation_info = ""
        if trans.get('payment_method') == 'Zelle' and trans.get('confirmation_number'):
            confirmation_info = f" (Conf: {trans.get('confirmation_number')})"
        
        transaction_list.append({
            'Transaction ID': trans.get('id', trans_id)[:8] + "...",
            'Date': trans.get('date', ''),
            'Time': trans.get('time', ''),
            'Items': items_str,
            'Item Count': item_count,
            'Total Quantity': total_quantity,
            'Total Amount': f"${trans.get('total', 0):.2f}",
            'Payment Method': trans.get('payment_method', '') + confirmation_info,
            'Customer Notes': trans.get('customer_notes', '')
        })
    
    # Sort by date and time
    transaction_list.sort(key=lambda x: f"{x['Date']} {x['Time']}", reverse=True)
    
    if transaction_list:
        df = pd.DataFrame(transaction_list)
        st.dataframe(df, use_container_width=True)
        
        # Summary stats
        st.subheader("Transaction Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_items_per_transaction = sum(t['Item Count'] for t in transaction_list) / len(transaction_list)
            st.metric("Avg Items per Transaction", f"{avg_items_per_transaction:.1f}")
        
        with col2:
            avg_quantity_per_transaction = sum(t['Total Quantity'] for t in transaction_list) / len(transaction_list)
            st.metric("Avg Quantity per Transaction", f"{avg_quantity_per_transaction:.1f}")
        
        with col3:
            total_items_sold = sum(t['Total Quantity'] for t in transaction_list)
            st.metric("Total Items Sold", total_items_sold)