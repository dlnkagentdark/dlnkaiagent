
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"
matches_to_find = [
    "Jetski", 
    "You are", 
    "system", 
    "role", 
    "model", 
    "temperature", 
    "max_tokens", 
    "completion", 
    "messages",
    "prompt",
    "http",
    "generate"
]

print(f"[*] Deep Analyzing {file_path}...")

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    for target in matches_to_find:
        print(f"\n[+] Searching for: {target}")
        # Case insensitive search
        indices = [m.start() for m in re.finditer(re.escape(target), content, re.IGNORECASE)]
        
        if not indices:
            print("    No matches found.")
            continue
            
        print(f"    Found {len(indices)} matches. Showing first 10 contexts:")
        
        for i, idx in enumerate(indices[:10]):
            start = max(0, idx - 100)
            end = min(len(content), idx + 200)
            snippet = content[start:end].replace("\n", " ")
            print(f"    Match {i+1}: ...{snippet}...")

except Exception as e:
    print(f"[!] Error: {e}")
