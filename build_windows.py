"""
Build script for creating Windows .exe
Run this on Windows: python build_windows.py
"""

import PyInstaller.__main__
import os
import sys

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Determine path separator for this OS
separator = ';' if sys.platform == 'win32' else ':'

PyInstaller.__main__.run([
    'desktop_app.py',
    '--name=InvoiceScanner',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    f'--add-data=templates{separator}templates',
    # No .env file needed - API key is embedded in desktop_app.py
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=openpyxl',
    '--hidden-import=google.generativeai',
    '--hidden-import=flask',
    '--hidden-import=webview',
    '--hidden-import=clr',
    '--collect-all=openpyxl',
    '--collect-all=flask',
    '--collect-all=google',
    '--collect-all=google.generativeai',
    '--noconsole',
    '--clean',
    '--exclude-module=_testcapi',  # Remove test modules that trigger AV
    '--exclude-module=unittest',
    '--exclude-module=test',
])

