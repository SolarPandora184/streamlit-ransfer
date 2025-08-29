import firebase_admin
from firebase_admin import credentials, db
import os
import json
import streamlit as st

def initialize_firebase():
    """Initialize Firebase connection"""
    if not firebase_admin._apps:
        try:
            # Try to get Firebase credentials from environment variable
            firebase_key = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            
            if firebase_key:
                # Parse the JSON string
                cred_dict = json.loads(firebase_key)
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback to default credentials or service account file
                cred = credentials.ApplicationDefault()
            
            # Get database URL from environment variable
            database_url = os.getenv("FIREBASE_DATABASE_URL", "https://your-project-default-rtdb.firebaseio.com/")
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
        except Exception as e:
            st.error(f"Firebase initialization failed: {str(e)}")
            st.info("Please ensure FIREBASE_SERVICE_ACCOUNT_KEY and FIREBASE_DATABASE_URL environment variables are set correctly.")
            raise e

def get_database_ref(path):
    """Get a reference to a specific path in the database"""
    return db.reference(path)

def write_data(path, data):
    """Write data to Firebase"""
    try:
        ref = db.reference(path)
        ref.set(data)
        return True
    except Exception as e:
        st.error(f"Failed to write data: {str(e)}")
        return False

def read_data(path):
    """Read data from Firebase"""
    try:
        ref = db.reference(path)
        return ref.get()
    except Exception as e:
        st.error(f"Failed to read data: {str(e)}")
        return None

def push_data(path, data):
    """Push data to Firebase (generates unique key)"""
    try:
        ref = db.reference(path)
        new_ref = ref.push(data)
        return new_ref.key
    except Exception as e:
        st.error(f"Failed to push data: {str(e)}")
        return None

def update_data(path, data):
    """Update data in Firebase"""
    try:
        ref = db.reference(path)
        ref.update(data)
        return True
    except Exception as e:
        st.error(f"Failed to update data: {str(e)}")
        return False

def delete_data(path):
    """Delete data from Firebase"""
    try:
        ref = db.reference(path)
        ref.delete()
        return True
    except Exception as e:
        st.error(f"Failed to delete data: {str(e)}")
        return False
