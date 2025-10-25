========================================
INVOICE SCANNER - WINDOWS INSTALLATION
========================================

⚠️ IMPORTANT: Windows Defender will block this app!
This is NORMAL for unsigned executables.

========================================
INSTALLATION STEPS
========================================

1. DOWNLOAD
-----------
Download InvoiceScanner-Windows.zip from GitHub Actions


2. EXTRACT
----------
Extract to: C:\InvoiceScanner\
(Or any folder you prefer)


3. ADD TO WINDOWS DEFENDER EXCLUSIONS
--------------------------------------
This is REQUIRED or Windows will delete the .exe!

a) Press Windows key
b) Type: "Windows Security"
c) Click "Virus & threat protection"
d) Click "Manage settings"
e) Scroll to "Exclusions"
f) Click "Add or remove exclusions"
g) Click "Add an exclusion" → "Folder"
h) Select: C:\InvoiceScanner\
i) Done!


4. CREATE .ENV FILE
-------------------
In the same folder as InvoiceScanner.exe:

a) Right-click → New → Text Document
b) Open it
c) Type: GOOGLE_API_KEY=AIzaSyBcF1OremOEFcR9e7bZ8wXBKUv8Ps8xl9w
d) Save As → .env
e) Change "Save as type" to "All Files"
f) Save


5. RUN THE APP
--------------
a) Double-click InvoiceScanner.exe
b) If Windows SmartScreen appears:
   - Click "More info"
   - Click "Run anyway"
c) Window opens in 5-10 seconds


6. USE THE APP
--------------
a) Upload invoice images (JPG, PNG)
b) Click "开始处理 / Start Processing"
c) Wait 10-15 seconds
d) Excel file downloads to your Downloads folder!


========================================
TROUBLESHOOTING
========================================

❌ "Windows protected your PC"
→ Click "More info" → "Run anyway"

❌ .exe disappears after extraction
→ Add folder to Defender exclusions (Step 3)

❌ App doesn't start / blank screen
→ Check .env file exists with API key

❌ "VCRUNTIME140.dll is missing"
→ Install: https://aka.ms/vs/17/release/vc_redist.x64.exe

❌ Excel file not downloading
→ Check Downloads folder: C:\Users\YourName\Downloads\


========================================
WHY DOES WINDOWS BLOCK IT?
========================================

PyInstaller .exe files trigger false positives because:
- They bundle Python (looks suspicious)
- Many malware use PyInstaller
- Your .exe is unsigned (no $200/year certificate)

YOUR APP IS SAFE! You built it yourself from source.


========================================
COMPLETE GUIDE
========================================

See FIX_WINDOWS_DEFENDER.txt for detailed solutions.


========================================

