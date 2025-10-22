import os, time, glob, sys, base64, json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI
import pandas as pd
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("⚠️  Please set OPENAI_API_KEY in .env file")
    print("   Create a .env file with: OPENAI_API_KEY=your-api-key-here")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

INBOX  = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "inbox")
OUTBOX = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "outbox")

os.makedirs(INBOX, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)

# Store all invoice data globally
all_invoices_data = []

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
            model="gpt-4o",  # GPT-4 with vision
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
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        return json.loads(content)
    
    except Exception as e:
        print(f"   OpenAI API error: {e}")
        return None

def save_combined_excel(output_path):
    """Save all invoices to a single Excel file"""
    if not all_invoices_data:
        print("⚠️  No invoice data to save")
        return False
    
    try:
        # Combine all invoice rows with separators
        combined_rows = []
        
        for i, invoice in enumerate(all_invoices_data):
            # Add header row with file name
            combined_rows.append([f"=== 发票 {i+1}: {invoice['filename']} ==="])
            combined_rows.append([])  # Empty row
            
            # Add invoice data rows
            if 'rows' in invoice['data']:
                for row in invoice['data']['rows']:
                    combined_rows.append(row)
            
            # Add separator
            combined_rows.append([])  # Empty row
            combined_rows.append(['=' * 50])
            combined_rows.append([])  # Empty row
        
        # Create DataFrame
        df = pd.DataFrame(combined_rows)
        
        # Save to Excel with vertical orientation
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='所有发票', index=False, header=False)
            
            # Get the worksheet to adjust formatting
            workbook = writer.book
            worksheet = writer.sheets['所有发票']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return True
    except Exception as e:
        print(f"   Excel creation error: {e}")
        return False

def process_image(path):
    """Process image file and add to global data"""
    filename = os.path.basename(path)
    
    print(f"📄 Processing: {filename}")
    data = extract_invoice_data(path)
    
    if data:
        # Add to global collection
        all_invoices_data.append({
            'filename': filename,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        print(f"✔ Extracted data from {filename}")
        return True
    else:
        print(f"⚠️  Failed to extract data from {filename}")
        return False

def process_pdf(path):
    """Process PDF file - convert to images first"""
    name = os.path.splitext(os.path.basename(path))[0]
    
    try:
        # Convert PDF to images
        images = convert_from_path(path)
        
        for i, image in enumerate(images):
            # Save temporary image
            temp_image = f"/tmp/{name}_page_{i+1}.jpg"
            image.save(temp_image, 'JPEG')
            
            # Process the image
            filename = f"{name}_page_{i+1}"
            print(f"📄 Processing PDF page {i+1}/{len(images)}")
            
            data = extract_invoice_data(temp_image)
            if data:
                all_invoices_data.append({
                    'filename': filename,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✔ Extracted data from page {i+1}")
            
            # Clean up temp file
            os.remove(temp_image)
        
        return True
    except Exception as e:
        print(f"⚠️  PDF conversion error: {e}")
        return False

def convert(path):
    """Main conversion function"""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            process_image(path)
        elif ext == ".pdf":
            process_pdf(path)
        else:
            print(f"… Skipped unsupported file: {path}")
    except Exception as e:
        print(f"⚠️ Failed {path}: {e}")

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        path = event.src_path
        # Wait for file to finish writing
        time.sleep(1.0)
        convert(path)

if __name__ == "__main__":
    print("🚀 Invoice Scanner Started")
    print(f"📂 Inbox: {INBOX}")
    print(f"📊 Output: {OUTBOX}")
    print("=" * 60)
    
    # Convert any existing files first
    files_to_process = sorted(glob.glob(os.path.join(INBOX, "*")))
    image_files = [f for f in files_to_process if os.path.splitext(f)[1].lower() in ['.jpg', '.jpeg', '.png', '.pdf']]
    
    if not image_files:
        print("\n⚠️  No images found in inbox folder!")
        print("   Please add some invoice images (JPG, PNG, or PDF)")
        sys.exit(0)
    
    print(f"\n📸 Found {len(image_files)} invoice(s) to process\n")
    
    # Process all files
    for f in image_files:
        convert(f)
    
    # Save combined Excel file
    if all_invoices_data:
        output_file = os.path.join(OUTBOX, f"所有发票_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        print(f"\n💾 Saving combined Excel file...")
        if save_combined_excel(output_file):
            print(f"✅ SUCCESS! All {len(all_invoices_data)} invoices saved to:")
            print(f"   {output_file}")
            print(f"\n📊 Opening Excel file...")
            os.system(f"open '{output_file}'")
        else:
            print("❌ Failed to save Excel file")
    else:
        print("\n⚠️  No invoices were successfully processed")
    
    print("\n" + "=" * 60)
    print("✨ Processing complete!")

