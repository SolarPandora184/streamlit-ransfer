import streamlit as st
import os
from firebase_config import initialize_firebase
from inventory_manager import inventory_management_page
from sales_interface import sales_interface_page
from turned_away_tracker import turned_away_tracker_page
from export_manager import export_data_page

# Initialize Firebase
try:
    initialize_firebase()
    st.success("Connected to Firebase successfully!")
except Exception as e:
    st.error(f"Failed to connect to Firebase: {str(e)}")
    st.stop()

def main():
    st.set_page_config(
        page_title="Airshow POS System",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("✈️ Airshow Point of Sale System")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Sales Interface", "Inventory Management", "Turned Away Tracker", "Export Data"]
    )
    
    # Display current date and time
    import datetime
    st.sidebar.info(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Route to appropriate page
    if page == "Sales Interface":
        sales_interface_page()
    elif page == "Inventory Management":
        inventory_management_page()
    elif page == "Turned Away Tracker":
        turned_away_tracker_page()
    elif page == "Export Data":
        export_data_page()

if __name__ == "__main__":
    main()
