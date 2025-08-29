#!/bin/bash
# Deployment script for Airshow POS System

echo "Setting up Airshow POS System..."

# Create data directory if it doesn't exist
mkdir -p data

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || pip install streamlit pandas plotly openpyxl

# Start the application
echo "Starting Airshow POS System..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0