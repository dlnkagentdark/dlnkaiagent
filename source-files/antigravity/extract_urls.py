
import re

file_path = r"c:\Antigravity\resources\app\extensions\antigravity\dist\extension.js"

def extract_urls():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex for https URLs
        # Basic: https:// followed by non-whitespace/quote characters
        url_pattern = r'https://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=-]*)?'
        
        urls = re.findall(url_pattern, content)
        
        unique_urls = sorted(list(set(urls)))
        
        print(f"[*] Found {len(unique_urls)} unique URLs:")
        for url in unique_urls:
            # Filter out common junk or very short ones
            if len(url) > 12:
                print(f"  {url}")
                
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    extract_urls()
