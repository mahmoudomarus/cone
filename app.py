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
    """Use OpenAI Vision API to extract invoice data in structured format"""
    base64_image = encode_image(image_path)
    
    prompt = """Extract ALL items from this Chinese invoice/receipt.

Return JSON in this EXACT format:
{
  "date": "采购时间：2020.10.1",
  "items": [
    {"品名": "海带丝", "数量": "1", "单价": "5.00", "金额": "5.00"},
    {"品名": "大头菜(颗)", "数量": "2.1", "单价": "1.70", "金额": "3.57"}
  ]
}

IMPORTANT:
- Extract EVERY single line item
- Keep Chinese characters exactly as shown (品名 = product name)
- 数量 = quantity (can be decimal like 2.1, 0.5)
- 单价 = unit price
- 金额 = total amount
- Return valid JSON ONLY, no markdown, no explanation"""

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
    """Create combined Excel file from all invoices in clean table format"""
    all_items = []
    
    for i, invoice in enumerate(invoices_data):
        data = invoice['data']
        
        # Add invoice header
        date = data.get('date', invoice['filename'])
        all_items.append({
            '品名': f"=== 发票 {i+1} ===",
            '数量': '',
            '单价': '',
            '金额': date
        })
        all_items.append({'品名': '', '数量': '', '单价': '', '金额': ''})
        
        # Add all items from this invoice
        if 'items' in data and data['items']:
            for item in data['items']:
                # Ensure all required fields exist
                row = {
                    '品名': item.get('品名', ''),
                    '数量': item.get('数量', ''),
                    '单价': item.get('单价', ''),
                    '金额': item.get('金额', '')
                }
                all_items.append(row)
            
            # Add separator between invoices
            all_items.append({'品名': '', '数量': '', '单价': '', '金额': ''})
            all_items.append({'品名': '=' * 60, '数量': '', '单价': '', '金额': ''})
            all_items.append({'品名': '', '数量': '', '单价': '', '金额': ''})
    
    # Create DataFrame
    df = pd.DataFrame(all_items)
    
    # Save to Excel with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='所有发票', index=False)
        
        # Format the worksheet
        from openpyxl.styles import Font, Alignment
        workbook = writer.book
        worksheet = writer.sheets['所有发票']
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 25  # 品名
        worksheet.column_dimensions['B'].width = 10  # 数量
        worksheet.column_dimensions['C'].width = 10  # 单价
        worksheet.column_dimensions['D'].width = 10  # 金额
        
        # Center align all cells
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal='center', vertical='center')

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

