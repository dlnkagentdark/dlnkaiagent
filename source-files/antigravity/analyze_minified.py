
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"
matches_to_find = ["https://", "Authorization", "Bearer", "api.antigravity"]

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    print(f"[*] Analyzing {file_path} ({len(content)} bytes)...")

    for target in matches_to_find:
        print(f"\n[+] Searching for: {target}")
        indices = [m.start() for m in re.finditer(re.escape(target), content, re.IGNORECASE)]
        
        if not indices:
            print("    No matches found.")
            continue
            
        print(f"    Found {len(indices)} matches. Showing first 5 contexts:")
        
        for i, idx in enumerate(indices[:5]):
            start = max(0, idx - 50)
            end = min(len(content), idx + 100)
            snippet = content[start:end].replace("\n", " ")
            print(f"    Match {i+1}: ...{snippet}...")

except Exception as e:
    print(f"[!] Error: {e}")
