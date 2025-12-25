
import requests
import warnings


# Explicit Proxy Configuration
proxies = {
    "https": "http://localhost:8081" 
}

# Real target (we can test with google.com/generate_204 to verify tunneling if antigravity is dead)
target_url = "https://www.google.com/generate_204"
# Or keep existing if we want to test that specific flow, 
# but if api.antigravity.ai is dead it will fail. 
# Let's try the suspected real domain if we found one, or sticking to the one in code.
# The user wants to "Exploit Antigravity", so we should try to mock the real domain behavior 
# or use a generic one to prove the proxy works.
target_url = "https://www.google.com" # Reliable target to prove PROXY works.

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer REAL_ENCRYPTED_SECRET"
}

payload = {
    "message": "Can you see this secret message?"
}

print(f"[*] Sending SECURE HTTPS request to {target_url} via PROXY...")
print("[*] Using CA: mitm_ca.pem for verification...")

try:
    # 1. We talk to the target "through" the proxy.
    # 2. 'verify' here checks the CERT presented by the proxy (since proxy intercepts).
    # 3. Because we added mitm_ca.pem to trust store in OS, 
    #    requests *might* use system trust store, but we specify it explicitly to be sure.
    response = requests.post(target_url, json=payload, headers=headers, proxies=proxies, verify="mitm_ca.pem")
    
    print(f"[*] Response Status: {response.status_code}")
    print(f"[*] Response Body: {response.text[:100]}...") # Truncate for readability
    
    if response.status_code < 500:
        print("\n[SUCCESS] Proxy tunnel established and traffic intercepted!")
    else:
        print("\n[FAIL] Unexpected response code.")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
