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


4. RUN THE APP
--------------
a) Double-click InvoiceScanner.exe
b) If Windows SmartScreen appears:
   - Click "More info"
   - Click "Run anyway"
c) Window opens in 5-10 seconds


5. USE THE APP
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
→ Wait 5-10 seconds for app to fully load

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

