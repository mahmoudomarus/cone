#!/usr/bin/env python3
"""
Invoice Scanner Web App
Upload multiple invoices and get a combined Excel file
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import base64
import json
from datetime import datetime
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import tempfile
import shutil

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Get OpenAI API key
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise Exception("Please set OPENAI_API_KEY in .env file")

client = OpenAI(api_key=API_KEY)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_invoice_data(image_path):
    """Use OpenAI Vision API to extract invoice data - preserving original text"""
    base64_image = encode_image(image_path)
    
    prompt = """Extract ALL text from this invoice exactly as it appears. Keep all original Chinese characters.

Return as a JSON with this structure:
{
  "rows": [
    ["col1", "col2", "col3", ...],
    ["col1", "col2", "col3", ...],
    ...
  ]
}

- Preserve the table structure exactly
- Keep all Chinese text as-is
- Each row should be an array of cell values
- Return ONLY the JSON, no markdown"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        return json.loads(content)
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def create_combined_excel(invoices_data, output_path):
    """Create combined Excel file from all invoices"""
    combined_rows = []
    
    for i, invoice in enumerate(invoices_data):
        # Add header row with file name
        combined_rows.append([f"=== 发票 {i+1}: {invoice['filename']} ==="])
        combined_rows.append([])  # Empty row
        
        # Add invoice data rows
        if 'rows' in invoice['data']:
            for row in invoice['data']['rows']:
                combined_rows.append(row)
        
        # Add separator
        combined_rows.append([])
        combined_rows.append(['=' * 50])
        combined_rows.append([])
    
    # Create DataFrame
    df = pd.DataFrame(combined_rows)
    
    # Save to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='所有发票', index=False, header=False)
        
        # Auto-adjust column widths
        workbook = writer.book
        worksheet = writer.sheets['所有发票']
        
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('没有选择文件 / No files selected', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        flash('没有选择文件 / No files selected', 'error')
        return redirect(url_for('index'))
    
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp()
    all_invoices = []
    
    try:
        # Save and process each file
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                
                # Extract data from invoice
                print(f"Processing: {filename}")
                data = extract_invoice_data(filepath)
                
                if data:
                    all_invoices.append({
                        'filename': filename,
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    })
        
        if not all_invoices:
            flash('无法处理任何发票 / Could not process any invoices', 'error')
            return redirect(url_for('index'))
        
        # Create Excel file
        output_filename = f"所有发票_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(temp_dir, output_filename)
        create_combined_excel(all_invoices, output_path)
        
        # Send file to user
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        flash(f'处理出错 / Error: {str(e)}', 'error')
        return redirect(url_for('index'))
    
    finally:
        # Clean up temporary directory (after a delay to allow file download)
        # Note: In production, use a background task for cleanup
        pass

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Invoice Scanner API is running'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

