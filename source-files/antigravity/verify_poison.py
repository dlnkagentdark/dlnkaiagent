
import requests
import json

# Explicit Proxy Configuration
proxies = {
    "https": "http://localhost:8081" 
}

# Real target (we use a mock endpoint here since we want to see what the server receives,
# but since we are intercepting and forwarding, we can't easily see the server side unless we own it.
# HOWEVER, since our proxy LOGS the outgoing body to 'intercepted_traffic.log', we can verify the injection there!
# We will send a request to a benign target.)
target_url = "https://www.google.com" # Using google just to act as a endpoint that accepts connection

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer TEST_TOKEN"
}

# Simulating a typical Chat Request
payload = {
    "model": "jetski-v1",
    "messages": [
        {"role": "user", "content": "How do I secure my node app?"}
    ]
}

print(f"[*] Sending Chat Request to {target_url} via PROXY...")

try:
    # We expect the proxy to modify this body before sending (or trying to send) to Google.
    # Google will likely return 400/405/404 for this JSON POST, but that's fine.
    # We care about the PROXY logs.
    response = requests.post(target_url, json=payload, headers=headers, proxies=proxies, verify="mitm_ca.pem")
    
    print(f"[*] Response Status: {response.status_code}")
    
    print("[*] Verifying injection in 'intercepted_traffic.log'...")
    found = False
    try:
        with open("intercepted_traffic.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "dLNk AI" in line and "SYSTEM OVERRIDE" in line:
                    print("\n[SUCCESS] POISON CONFIRMED! 'dLNk AI' Persona found in intercepted request.")
                    print(f"Captured Log Entry: {line[:200]}...")
                    found = True
                    break
    except Exception as e:
        print(f"[ERROR] Could not read log file: {e}")

    if not found:
        print("\n[FAIL] Poison detection failed. Check proxy logs.")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
