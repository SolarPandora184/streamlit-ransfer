import json
import os
import streamlit as st
from datetime import datetime
import uuid

# Data directory
DATA_DIR = "data"

def ensure_data_directory():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_file_path(collection):
    """Get file path for a collection"""
    ensure_data_directory()
    return os.path.join(DATA_DIR, f"{collection}.json")

def read_data(collection):
    """Read data from local JSON file"""
    try:
        file_path = get_file_path(collection)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Failed to read data from {collection}: {str(e)}")
        return {}

def write_data(collection, data):
    """Write data to local JSON file"""
    try:
        file_path = get_file_path(collection)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to write data to {collection}: {str(e)}")
        return False

def push_data(collection, data):
    """Add new data with unique key to collection"""
    try:
        # Generate unique key
        unique_key = str(uuid.uuid4())
        
        # Read existing data
        existing_data = read_data(collection)
        
        # Add new data with unique key
        existing_data[unique_key] = data
        
        # Write back to file
        if write_data(collection, existing_data):
            return unique_key
        return None
    except Exception as e:
        st.error(f"Failed to push data to {collection}: {str(e)}")
        return None

def update_data(collection, key, data):
    """Update specific item in collection"""
    try:
        # Read existing data
        existing_data = read_data(collection)
        
        if key in existing_data:
            # Update the existing item
            existing_data[key].update(data)
        else:
            # Create new item if it doesn't exist
            existing_data[key] = data
        
        # Write back to file
        return write_data(collection, existing_data)
    except Exception as e:
        st.error(f"Failed to update data in {collection}: {str(e)}")
        return False

def delete_data(collection, key=None):
    """Delete data from collection"""
    try:
        if key is None:
            # Delete entire collection
            file_path = get_file_path(collection)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        else:
            # Delete specific item
            existing_data = read_data(collection)
            if key in existing_data:
                del existing_data[key]
                return write_data(collection, existing_data)
            return True
    except Exception as e:
        st.error(f"Failed to delete data from {collection}: {str(e)}")
        return False

def get_database_ref(path):
    """Compatibility function - not needed for local storage"""
    return None

def initialize_local_storage():
    """Initialize local storage system"""
    ensure_data_directory()
    return True