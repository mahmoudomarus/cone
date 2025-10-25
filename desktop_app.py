#!/usr/bin/env python3
"""
Invoice Scanner - Desktop Application
Windows GUI version with embedded web interface
"""

import webview
import threading
import sys
import os

# Set API key directly (embedded in .exe)
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBcF1OremOEFcR9e7bZ8wXBKUv8Ps8xl9w'

# Try to load .env if it exists (optional override)
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Import app after setting environment
from app import app

# Set Flask to not reload
app.config['DEBUG'] = False

def start_flask():
    """Start Flask server in a separate thread"""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    app.run(host='127.0.0.1', port=5555, debug=True, use_reloader=False)

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

