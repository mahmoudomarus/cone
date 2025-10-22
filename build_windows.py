"""
Build script for creating Windows .exe
Run this on Windows: python build_windows.py
"""

import PyInstaller.__main__
import os

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'desktop_app.py',
    '--name=InvoiceScanner',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=templates;templates',
    '--add-data=.env;.',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=openpyxl',
    '--hidden-import=openai',
    '--hidden-import=flask',
    '--hidden-import=webview',
    '--collect-all=openpyxl',
    '--collect-all=flask',
    '--noconsole',
])

