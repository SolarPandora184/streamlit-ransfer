import streamlit as st
from local_storage import read_data
import pandas as pd
from datetime import datetime, timedelta
import io

def export_data_page():
    """Export data to Excel"""
    st.header("📊 Export Data")
    
    st.info("Export sales transactions, turned away entries, and inventory data to Excel format.")
    
    # Date range selection
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date())
    
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Export options
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_transactions = st.checkbox("Sales Transactions", value=True)
    
    with col2:
        include_turned_away = st.checkbox("Turned Away Entries", value=True)
    
    with col3:
        include_inventory = st.checkbox("Current Inventory", value=True)
    
    if st.button("📥 Generate Export", type="primary"):
        generate_export(start_date, end_date, include_transactions, include_turned_away, include_inventory)
    
    st.divider()
    
    # Quick export buttons
    st.subheader("🚀 Quick Exports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Today's Data", width="stretch"):
            today = datetime.now().date()
            generate_export(today, today, True, True, False)
    
    with col2:
        if st.button("This Week", width="stretch"):
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            generate_export(week_start, today, True, True, False)
    
    with col3:
        if st.button("Full Inventory Report", width="stretch"):
            today = datetime.now().date()
            generate_export(today, today, False, False, True)

def generate_export(start_date, end_date, include_transactions, include_turned_away, include_inventory):
    """Generate Excel export based on selected options"""
    
    try:
        # Create Excel writer object
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Export transactions
            if include_transactions:
                transactions_df = get_transactions_dataframe(start_date, end_date)
                if not transactions_df.empty:
                    transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
                    st.success(f"✅ Exported {len(transactions_df)} transactions")
                else:
                    # Create empty sheet with headers
                    empty_df = pd.DataFrame(columns=['Transaction ID', 'Date', 'Time', 'Total', 'Payment Method', 'Items'])
                    empty_df.to_excel(writer, sheet_name='Transactions', index=False)
                    st.info("ℹ️ No transactions found for the selected date range")
            
            # Export turned away entries
            if include_turned_away:
                turned_away_df = get_turned_away_dataframe(start_date, end_date)
                if not turned_away_df.empty:
                    turned_away_df.to_excel(writer, sheet_name='Turned Away', index=False)
                    st.success(f"✅ Exported {len(turned_away_df)} turned away entries")
                else:
                    # Create empty sheet with headers
                    empty_df = pd.DataFrame(columns=['Date', 'Time', 'Reason'])
                    empty_df.to_excel(writer, sheet_name='Turned Away', index=False)
                    st.info("ℹ️ No turned away entries found for the selected date range")
            
            # Export inventory
            if include_inventory:
                inventory_df = get_inventory_dataframe()
                if not inventory_df.empty:
                    inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
                    st.success(f"✅ Exported {len(inventory_df)} inventory items")
                else:
                    # Create empty sheet with headers
                    empty_df = pd.DataFrame(columns=['Name', 'Category', 'Price', 'Stock', 'SKU', 'Status'])
                    empty_df.to_excel(writer, sheet_name='Inventory', index=False)
                    st.info("ℹ️ No inventory items found")
            
            # Generate summary sheet
            generate_summary_sheet(writer, start_date, end_date)
            
            # Generate turned away statistics sheet
            generate_turned_away_stats_sheet(writer, start_date, end_date)
        
        # Prepare download
        output.seek(0)
        
        filename = f"airshow_data_{start_date}_{end_date}.xlsx"
        
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"❌ Failed to generate export: {str(e)}")

def get_transactions_dataframe(start_date, end_date):
    """Get transactions data as DataFrame"""
    transactions_data = read_data('transactions')
    
    if not transactions_data:
        return pd.DataFrame()
    
    # Convert to list and filter by date range
    transactions_list = []
    
    for transaction_id, transaction in transactions_data.items():
        transaction_date = datetime.strptime(transaction.get('date', ''), '%Y-%m-%d').date()
        
        if start_date <= transaction_date <= end_date:
            # Flatten items for easier Excel viewing
            items_str = "; ".join([f"{item['name']} x{item['quantity']} @ ${item['price']:.2f}" 
                                 for item in transaction.get('items', [])])
            
            # Include confirmation number for Zelle payments
            payment_info = transaction.get('payment_method', '')
            if transaction.get('payment_method') == 'Zelle' and transaction.get('confirmation_number'):
                payment_info += f" (Conf: {transaction.get('confirmation_number')})"
            
            transactions_list.append({
                'Transaction ID': transaction.get('id', transaction_id),
                'Date': transaction.get('date', ''),
                'Time': transaction.get('time', ''),
                'Total': f"${transaction.get('total', 0):.2f}",
                'Payment Method': payment_info,
                'Confirmation Number': transaction.get('confirmation_number', ''),
                'Customer Notes': transaction.get('customer_notes', ''),
                'Items': items_str,
                'Item Count': len(transaction.get('items', [])),
                'Timestamp': transaction.get('timestamp', '')
            })
    
    return pd.DataFrame(transactions_list)

def get_turned_away_dataframe(start_date, end_date):
    """Get turned away data as DataFrame"""
    turned_away_data = read_data('turned_away')
    
    if not turned_away_data:
        return pd.DataFrame()
    
    # Convert to list and filter by date range
    turned_away_list = []
    
    for entry_id, entry in turned_away_data.items():
        entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d').date()
        
        if start_date <= entry_date <= end_date:
            turned_away_list.append({
                'Date': entry.get('date', ''),
                'Time': entry.get('time', ''),
                'Reason': entry.get('reason', ''),
                'Timestamp': entry.get('timestamp', '')
            })
    
    return pd.DataFrame(turned_away_list)

def get_inventory_dataframe():
    """Get inventory data as DataFrame"""
    inventory_data = read_data('inventory')
    
    if not inventory_data:
        return pd.DataFrame()
    
    # Convert to list
    inventory_list = []
    
    for item_id, item in inventory_data.items():
        inventory_list.append({
            'Item ID': item.get('id', item_id),
            'Name': item.get('name', ''),
            'Category': item.get('category', ''),
            'Price': f"${item.get('price', 0):.2f}",
            'Stock': item.get('stock', 0),
            'SKU': item.get('sku', ''),
            'Description': item.get('description', ''),
            'Status': 'Active' if item.get('active', True) else 'Inactive',
            'Created': item.get('created_at', '')[:10] if item.get('created_at') else '',
            'Updated': item.get('updated_at', '')[:10] if item.get('updated_at') else ''
        })
    
    return pd.DataFrame(inventory_list)

def generate_summary_sheet(writer, start_date, end_date):
    """Generate a summary sheet with key metrics"""
    
    # Get data
    transactions_data = read_data('transactions')
    turned_away_data = read_data('turned_away')
    inventory_data = read_data('inventory')
    
    summary_data = []
    
    # Date range info
    summary_data.append(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    summary_data.append(['Date Range', f"{start_date} to {end_date}"])
    summary_data.append(['', ''])
    
    # Transaction summary
    if transactions_data:
        date_filtered_transactions = []
        total_revenue = 0
        
        for transaction in transactions_data.values():
            transaction_date = datetime.strptime(transaction.get('date', ''), '%Y-%m-%d').date()
            if start_date <= transaction_date <= end_date:
                date_filtered_transactions.append(transaction)
                total_revenue += transaction.get('total', 0)
        
        summary_data.append(['SALES SUMMARY', ''])
        summary_data.append(['Total Transactions', len(date_filtered_transactions)])
        summary_data.append(['Total Revenue', f"${total_revenue:.2f}"])
        summary_data.append(['Average Transaction', f"${total_revenue/len(date_filtered_transactions):.2f}" if date_filtered_transactions else "$0.00"])
    
    summary_data.append(['', ''])
    
    # Turned away summary
    if turned_away_data:
        date_filtered_turned_away = []
        
        for entry in turned_away_data.values():
            entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d').date()
            if start_date <= entry_date <= end_date:
                date_filtered_turned_away.append(entry)
        
        summary_data.append(['TURNED AWAY SUMMARY', ''])
        summary_data.append(['Total Turned Away', len(date_filtered_turned_away)])
    
    summary_data.append(['', ''])
    
    # Inventory summary
    if inventory_data:
        active_items = sum(1 for item in inventory_data.values() if item.get('active', True))
        total_stock_value = sum(item.get('price', 0) * item.get('stock', 0) 
                              for item in inventory_data.values() if item.get('active', True))
        
        summary_data.append(['INVENTORY SUMMARY', ''])
        summary_data.append(['Active Items', active_items])
        summary_data.append(['Total Inventory Value', f"${total_stock_value:.2f}"])
    
    # Create DataFrame and export
    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

def generate_turned_away_stats_sheet(writer, start_date, end_date):
    """Generate detailed turned away statistics sheet"""
    
    # Get turned away data
    turned_away_data = read_data('turned_away')
    
    if not turned_away_data:
        # Create empty sheet with message
        empty_stats = pd.DataFrame([['No turned away data available', '']], 
                                 columns=['Statistic', 'Value'])
        empty_stats.to_excel(writer, sheet_name='Turned Away Stats', index=False)
        return
    
    # Filter by date range
    date_filtered_turned_away = []
    for entry in turned_away_data.values():
        try:
            entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d').date()
            if start_date <= entry_date <= end_date:
                date_filtered_turned_away.append(entry)
        except:
            continue
    
    if not date_filtered_turned_away:
        # Create empty sheet with message
        empty_stats = pd.DataFrame([['No turned away data for selected date range', '']], 
                                 columns=['Statistic', 'Value'])
        empty_stats.to_excel(writer, sheet_name='Turned Away Stats', index=False)
        return
    
    # Calculate statistics
    stats_data = []
    
    # Basic counts
    stats_data.append(['Report Period', f"{start_date} to {end_date}"])
    stats_data.append(['Total Turned Away', len(date_filtered_turned_away)])
    stats_data.append(['', ''])
    
    # Reason breakdown
    reasons = [entry.get('reason', 'Unknown') for entry in date_filtered_turned_away]
    reason_counts = {}
    for reason in reasons:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    stats_data.append(['REASON BREAKDOWN', ''])
    
    # Specific important reasons
    wrong_payment = sum(1 for reason in reasons if 'wrong payment' in reason.lower())
    too_expensive = sum(1 for reason in reasons if 'too expensive' in reason.lower())
    just_looking = sum(1 for reason in reasons if 'just looking' in reason.lower() or 'browsing' in reason.lower())
    out_of_stock = sum(1 for reason in reasons if 'out of stock' in reason.lower())
    generic = sum(1 for reason in reasons if 'generic' in reason.lower())
    
    stats_data.append(['Wrong Payment Type', wrong_payment])
    stats_data.append(['Too Expensive', too_expensive])
    stats_data.append(['Just Looking/Browsing', just_looking])
    stats_data.append(['Out of Stock', out_of_stock])
    stats_data.append(['Generic Reason', generic])
    stats_data.append(['', ''])
    
    # All reasons with counts
    stats_data.append(['ALL REASONS (Detailed)', ''])
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(date_filtered_turned_away)) * 100
        stats_data.append([reason, f"{count} ({percentage:.1f}%)"])
    
    stats_data.append(['', ''])
    
    # Daily breakdown
    daily_counts = {}
    for entry in date_filtered_turned_away:
        date = entry.get('date', '')
        if date:
            daily_counts[date] = daily_counts.get(date, 0) + 1
    
    if daily_counts:
        stats_data.append(['DAILY BREAKDOWN', ''])
        for date in sorted(daily_counts.keys()):
            stats_data.append([date, daily_counts[date]])
        
        stats_data.append(['', ''])
        stats_data.append(['Average per Day', f"{len(date_filtered_turned_away) / len(daily_counts):.1f}"])
        stats_data.append(['Highest Day', f"{max(daily_counts.values())} turned away"])
        stats_data.append(['Lowest Day', f"{min(daily_counts.values())} turned away"])
    
    # Time analysis (if we have time data)
    times_with_data = [entry for entry in date_filtered_turned_away if entry.get('time')]
    if times_with_data:
        stats_data.append(['', ''])
        stats_data.append(['TIME ANALYSIS', ''])
        
        # Group by hour
        hour_counts = {}
        for entry in times_with_data:
            try:
                time_str = entry.get('time', '')
                hour = int(time_str.split(':')[0])
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                continue
        
        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            stats_data.append(['Peak Hour', f"{peak_hour[0]}:00 ({peak_hour[1]} turned away)"])
            
            # Show hourly breakdown
            stats_data.append(['', ''])
            stats_data.append(['HOURLY BREAKDOWN', ''])
            for hour in sorted(hour_counts.keys()):
                stats_data.append([f"{hour:02d}:00", hour_counts[hour]])
    
    # Create DataFrame and export
    stats_df = pd.DataFrame(stats_data, columns=['Statistic', 'Value'])
    stats_df.to_excel(writer, sheet_name='Turned Away Stats', index=False)
