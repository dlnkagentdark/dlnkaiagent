
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"

print(f"[*] Extracting Prompts from {file_path}...")

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Search for systemPrompt assignments or properties
    targets = ["systemPrompt", "defaultPrompt", "userPrompt", "Jetski"]
    
    for target in targets:
        print(f"\n[+] Contexts for '{target}':")
        indices = [m.start() for m in re.finditer(re.escape(target), content, re.IGNORECASE)]
        for i, idx in enumerate(indices[:10]):
            start = max(0, idx - 100)
            end = min(len(content), idx + 200)
            print(f"    Match {i+1}: ...{content[start:end]}...")

    # Heuristic: Find long string literals that might be prompts
    # Looking for strings > 100 chars containing "You are" or "Assistant"
    print("\n[+] Searching for potential prompt strings...")
    # Regex for double quoted strings
    dq_strings = re.finditer(r'"([^"\\]*(\\.[^"\\]*)*)"', content)
    # Regex for backtick strings (template literals) - often used for multiline prompts
    bt_strings = re.finditer(r'`([^`\\]*(\\.[^`\\]*)*)`', content)
    
    potential_prompts = []
    
    for m in dq_strings:
        s = m.group(1)
        if len(s) > 50 and ("You are" in s or "Act as" in s or "system" in s or "AI" in s):
            potential_prompts.append(s[:200])

    for m in bt_strings:
        s = m.group(1)
        if len(s) > 50 and ("You are" in s or "Act as" in s or "system" in s or "AI" in s):
            potential_prompts.append(s[:200])

    print(f"    Found {len(potential_prompts)} potential prompt strings.")
    for i, p in enumerate(potential_prompts[:10]):
        print(f"    Prompt Candidate {i+1}: {p}")

except Exception as e:
    print(f"[!] Error: {e}")
