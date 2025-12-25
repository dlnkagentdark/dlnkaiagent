
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"

print(f"[*] Extracting Traces from {file_path}...")

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Regex to find JetskiTrace.task("...")
    matches = re.findall(r'JetskiTrace\.task\("([^"]+)"\)', content)
    unique_traces = sorted(list(set(matches)))
    
    print(f"Found {len(unique_traces)} traces:")
    for t in unique_traces:
        print(f"- {t}")

    print("\n[*] Searching for 'api.antigravity' string:")
    if "api.antigravity" in content:
        print("Found 'api.antigravity'")
    else:
        print("Not found 'api.antigravity'")

except Exception as e:
    print(f"[!] Error: {e}")
