
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"

print(f"[*] Tracing Jetski in {file_path}...")

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Trace Jetski Tasks
    print("\n[+] Jetski Traces:")
    # Regex to find JetskiTrace.task("...") or similar
    # Assuming code is minified like: ...JetskiTrace.task("Task Name")...
    trace_matches = re.finditer(r'JetskiTrace\.task\("([^"]+)"\)', content)
    traces = [m.group(1) for m in trace_matches]
    
    if not traces:
        print("    No JetskiTrace.task matches found. Trying looser search...")
        matches = re.finditer(r'JetskiTrace\.task\(([^)]+)\)', content)
        traces = [m.group(1) for m in matches]

    unique_traces = sorted(list(set(traces)))
    for t in unique_traces:
        print(f"    - {t}")

    # 2. Extract URLs
    print("\n[+] Extracting URLs:")
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w./?%&d=]*)?', content)
    unique_urls = sorted(list(set(urls)))
    for url in unique_urls:
        if "antigravity" in url or "api" in url or "exa" in url: # filtering relevant ones
            print(f"    - {url}")

    # 3. Search for "systemPrompt" assignments
    print("\n[+] systemPrompt Contexts:")
    # Look for "systemPrompt:" or "systemPrompt="
    sys_matches = re.finditer(r'(systemPrompt|defaultPrompt)\s*[:=]\s*', content)
    for m in sys_matches:
        start = m.start()
        end = min(len(content), start + 300)
        print(f"    ...{content[start:end]}...")
    
    # 4. Search for "role": "system" contexts (common in OpenAI calls)
    print("\n[+] 'role': 'system' Contexts:")
    role_matches = re.finditer(r'role\s*:\s*"system"\s*,\s*content\s*:', content)
    for m in role_matches:
        start = m.start()
        end = min(len(content), start + 500)
        print(f"    ...{content[start:end]}...")

except Exception as e:
    print(f"[!] Error: {e}")
