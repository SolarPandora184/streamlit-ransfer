import streamlit as st
from local_storage import push_data, read_data
from datetime import datetime
import uuid

def turned_away_tracker_page():
    """Track customers who were turned away"""
    st.header("👋 Turned Away Tracker")
    
    st.info("Use this section to track potential customers who didn't make a purchase.")
    
    # Display recent turned away entries
    display_recent_turned_away()
    
    st.divider()
    
    # Add new turned away entry
    st.subheader("➕ Add Turned Away Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quick buttons for common reasons
        st.subheader("Quick Entry")
        
        if st.button("💰 Too Expensive", width="stretch"):
            add_turned_away_entry("Too expensive")
        
        if st.button("🔍 Just Looking", width="stretch"):
            add_turned_away_entry("Just looking/browsing")
        
        if st.button("📦 Out of Stock", width="stretch"):
            add_turned_away_entry("Desired item out of stock")
        
        if st.button("⏰ No Time", width="stretch"):
            add_turned_away_entry("No time to purchase")
        
        if st.button("❓ Generic", width="stretch"):
            add_turned_away_entry("Generic - no specific reason")
    
    with col2:
        # Custom reason entry
        st.subheader("Custom Reason")
        
        with st.form("custom_turned_away"):
            custom_reason = st.text_area(
                "Custom Reason",
                placeholder="Enter specific reason why customer didn't purchase...",
                height=100
            )
            
            additional_notes = st.text_input(
                "Additional Notes (Optional)",
                placeholder="Any additional context or details..."
            )
            
            submitted = st.form_submit_button("Add Custom Entry", type="primary")
            
            if submitted:
                if custom_reason.strip():
                    full_reason = custom_reason
                    if additional_notes.strip():
                        full_reason += f" | Notes: {additional_notes}"
                    add_turned_away_entry(full_reason)
                else:
                    st.error("Please enter a reason for the turned away entry.")

def add_turned_away_entry(reason):
    """Add a turned away entry to Firebase"""
    entry_id = str(uuid.uuid4())
    entry_data = {
        'id': entry_id,
        'reason': reason,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'type': 'turned_away'
    }
    
    if push_data('turned_away', entry_data):
        st.success(f"✅ Turned away entry added: {reason}")
        st.rerun()
    else:
        st.error("❌ Failed to add turned away entry.")

def display_recent_turned_away():
    """Display recent turned away entries"""
    st.subheader("📊 Recent Turned Away Entries")
    
    turned_away_data = read_data('turned_away')
    
    if not turned_away_data:
        st.info("No turned away entries yet today.")
        return
    
    # Convert to list and sort by timestamp (most recent first)
    entries = list(turned_away_data.values())
    entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Filter for today's entries
    today = datetime.now().strftime('%Y-%m-%d')
    today_entries = [entry for entry in entries if entry.get('date') == today]
    
    if today_entries:
        st.write(f"**Today's turned away count: {len(today_entries)}**")
        
        # Display in expandable sections
        for i, entry in enumerate(today_entries[:10]):  # Show last 10 entries
            with st.expander(f"Entry {i+1}: {entry.get('time', 'N/A')} - {entry.get('reason', 'No reason')[:50]}..."):
                st.write(f"**Time:** {entry.get('time', 'N/A')}")
                st.write(f"**Reason:** {entry.get('reason', 'No reason provided')}")
                st.write(f"**Full Timestamp:** {entry.get('timestamp', 'N/A')}")
    else:
        st.info("No turned away entries for today yet.")
    
    # Summary statistics
    if turned_away_data:
        st.divider()
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Today's Turned Away", len(today_entries))
        
        with col2:
            st.metric("Total All Time", len(entries))
        
        with col3:
            # Most common reason analysis
            if today_entries:
                reasons = [entry.get('reason', 'Unknown') for entry in today_entries]
                most_common = max(set(reasons), key=reasons.count) if reasons else "None"
                st.metric("Most Common Today", most_common[:20] + "..." if len(most_common) > 20 else most_common)
