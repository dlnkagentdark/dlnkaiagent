
import requests
import json
import os

# Configuration to use our local proxy
proxies = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080",
}

target_url = "http://api.antigravity.ai/v1/embeddings" # Use HTTP to allow our simple proxy to see the content clearly
# In reality, the extension uses HTTPS, but for this POC we verify the interception logic with HTTP 
# or we would need to generate certs.

payload = {
    "model": "jetski-v1-turbo",
    "prompt": "Who are you?",
    "stream": False
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Antigravity-Client/1.0",
    "Authorization": "Bearer MOCK_TOKEN_123"
}

print(f"[*] Sending request to {target_url} via Proxy...")
try:
    # Verify is False because our proxy (if it were HTTPS) wouldn't have a valid cert
    response = requests.post(target_url, json=payload, headers=headers, proxies=proxies, verify=False, timeout=5)
    
    print(f"[*] Response Status: {response.status_code}")
    print(f"[*] Response Body: {response.text}")
except Exception as e:
    print(f"[!] Request Failed: {e}")
