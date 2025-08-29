#!/usr/bin/env python3
"""
Airshow POS System Launcher
Run this script to start the Point of Sale system
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down Airshow POS System...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()