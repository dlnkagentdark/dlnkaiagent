
import http.server
import http.client
import socketserver
import urllib.parse
import ssl
import sys

PORT = 8080
TARGET_HOST = "api.antigravity.ai"
TARGET_PORT = 443

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # Handle HTTPS tunneling (CONNECT method)
        # In a real MITM, we would need to wrap this in SSL with a CA cert.
        # For this POC, we will just establish the tunnel to show we can intercept the *request* to connect,
        # but decoding the encrypted traffic inside requires a valid cert trusted by the client.
        print(f"\n[MITM] CONNECT request to {self.path}")
        self.send_response(200, 'Connection Established')
        self.end_headers()

        # Simple tunnel (blind forwarding) - we can't see traffic inside unless we terminate SSL
        # This is a limitation of a simple script without a generated CA.
        # But we can log *that* a connection happened.
        pass

    def do_GET(self):
        self.handle_http_request()

    def do_POST(self):
        self.handle_http_request()

    def handle_http_request(self):
        url = self.path
        print(f"\n[MITM] Intercepted {self.command} to {url}")
        
        # Read headers
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        if body:
            print(f"[MITM] Request Body ({content_length} bytes):")
            try:
                print(f"       {body.decode('utf-8')}")
            except:
                print(f"       (Binary Data) {body[:50]}...")

        # Forwarding (Mocking the response for safety in this env)
        # In a real attack, we would use http.client to send to TARGET_HOST
        print("[MITM] Forwarding to target (Simulated)...")
        
        # Mock Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "intercepted", "message": "MITM Successful"}')

print(f"[*] Starting MITM Proxy on port {PORT}...")
print(f"[*] Target: {TARGET_HOST}")

try:
    with socketserver.ThreadingTCPServer(("", PORT), ProxyHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n[*] Stopping MITM Proxy.")
