#!/usr/bin/env python3
"""
Invoice Scanner - Desktop Application
Windows GUI version with embedded web interface
"""

import webview
import threading
import sys
import os

# Load environment variables BEFORE importing app
from dotenv import load_dotenv
load_dotenv()

# Verify API key is loaded
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file!")
    sys.exit(1)
else:
    print(f"✓ Google API key loaded: {api_key[:20]}...")

from app import app

# Set Flask to not reload
app.config['DEBUG'] = False

def start_flask():
    """Start Flask server in a separate thread"""
    app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)

def main():
    """Main entry point for desktop app"""
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    import time
    time.sleep(2)
    
    # Create native window with the Flask app
    window = webview.create_window(
        '🔥 LIU the crazy - Invoice Scanner',
        'http://127.0.0.1:5555',
        width=1200,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    
    webview.start()

if __name__ == '__main__':
    main()

