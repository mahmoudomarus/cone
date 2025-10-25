#!/usr/bin/env python3
"""
Invoice Scanner - Desktop Application
Windows GUI version with embedded web interface
"""

import webview
import threading
import sys
import os
import requests
from datetime import datetime

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

# Global window reference
window = None

class API:
    """JavaScript API for desktop features"""
    
    def save_file_dialog(self, url):
        """
        Show native save file dialog and download the file
        Args:
            url: URL to download the file from (e.g., '/download/filename.xlsx')
        """
        try:
            # Get default filename
            default_name = f"所有发票_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Show save dialog
            result = window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory=os.path.expanduser('~/Downloads'),
                save_filename=default_name,
                file_types=('Excel Files (*.xlsx)', 'All Files (*.*)')
            )
            
            if result:
                save_path = result[0] if isinstance(result, tuple) else result
                
                # Download file from Flask
                response = requests.get(f'http://127.0.0.1:5555{url}')
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return {'success': True, 'path': save_path}
                else:
                    return {'success': False, 'error': 'Download failed'}
            else:
                return {'success': False, 'error': 'Cancelled'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

def start_flask():
    """Start Flask server in a separate thread"""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    app.run(host='127.0.0.1', port=5555, debug=True, use_reloader=False)

def main():
    """Main entry point for desktop app"""
    global window
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    import time
    time.sleep(2)
    
    # Create API instance
    api = API()
    
    # Create native window with the Flask app
    window = webview.create_window(
        '🔥 LIU the crazy - Invoice Scanner',
        'http://127.0.0.1:5555',
        width=1200,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        js_api=api  # Expose API to JavaScript
    )
    
    webview.start()

if __name__ == '__main__':
    main()

