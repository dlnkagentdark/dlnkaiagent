import os
import shutil
import glob

# CONFIGURATION
TARGET_EXT_DIR = r"c:\Antigravity\resources\app\extensions\google-cloud-bridge"
TARGET_CONFIG = r"c:\Antigravity\resources\app\product.json"
WORKSPACE = r"c:\Antigravity"
DLNK_PRODUCT_DIR = r"c:\dLNk" # DO NOT TOUCH THIS

def restore_config():
    print("[*] Restoring product.json...")
    try:
        with open(TARGET_CONFIG, 'r') as f:
            content = f.read()
        
        # Revert the hijack
        if "127.0.0.1" in content:
            content = content.replace("http://127.0.0.1", "https://example.com")
            with open(TARGET_CONFIG, 'w') as f:
                f.write(content)
            print("    [+] Update URL restored to original.")
        else:
            print("    [!] Config seems clean already.")
    except Exception as e:
        print(f"    [!] Error: {e}")

def wipe_implant():
    print("[*] Removing malicious extension...")
    if os.path.exists(TARGET_EXT_DIR):
        try:
            shutil.rmtree(TARGET_EXT_DIR)
            print(f"    [+] Deleted {TARGET_EXT_DIR}")
        except Exception as e:
            print(f"    [!] Error deleting extension: {e}")
    else:
        print("    [!] Extension not found (Already clean?).")

def wipe_workspace_evidence():
    print(f"[*] Cleaning workspace {WORKSPACE}...")
    # List of attack scripts to remove
    attack_files = [
        "fake_update_server.py", "poison_hosts.py", "poison_hosts.ps1", "run_poison.bat",
        "exfil_client.py", "worm_project.py", "poison_telemetry.py", "c2_dashboard.py",
        "verify_ai_status.py", "exploit_node_pty.py", "persistence_registry.py", "trojan_builder.py",
        "fake_landing_page.html", "update_server.log", "target_intel.json"
    ]
    
    for filename in attack_files:
        path = os.path.join(WORKSPACE, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"    [+] Shredded: {filename}")
            except: pass
            
    # Remove loot dir
    loot_dir = os.path.join(WORKSPACE, "loot")
    if os.path.exists(loot_dir):
        try:
            shutil.rmtree(loot_dir)
            print("    [+] Shredded: loot/ directory")
        except: pass

def verify_safety():
    print(f"[*] Verifying Product Safety ({DLNK_PRODUCT_DIR})...")
    if os.path.exists(DLNK_PRODUCT_DIR):
        print(f"    [OK] dLNk Product Directory Intact.")
    else:
        print(f"    [!] WARNING: dLNk Directory Missing! (Check recycle bin?)")

if __name__ == "__main__":
    print("--- [ Protocol Zero: Operational Cleanup ] ---")
    print("WARNING: This will remove all attack traces from c:\\Antigravity")
    
    restore_config()
    wipe_implant()
    wipe_workspace_evidence()
    verify_safety()
    
    print("\n[+] CLEANUP COMPLETE. The operation is officially closed.")
