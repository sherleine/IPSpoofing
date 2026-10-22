"""
Local web server that shows the current Tor exit IP in big text.
Open http://localhost:5000 in any browser.
The page auto-refreshes every 6 seconds.
Rotate in another terminal with: python tests/rotate_ip.py
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

TOR = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}

def get_exit_ip():
    try:
        r = requests.get("http://api.ipify.org?format=json", proxies=TOR, timeout=10)
        return r.json()["ip"]
    except Exception as e:
        return f"Error: {e}"

def get_real_ip():
    try:
        r = requests.get("http://api.ipify.org?format=json", timeout=10)
        return r.json()["ip"]
    except:
        return "unknown"

REAL_IP = get_real_ip()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        exit_ip = get_exit_ip()
        hidden = exit_ip != REAL_IP

        html = f"""<!DOCTYPE html>
<html>
<head>
  <title>IP Rotation — Live</title>
  <meta http-equiv="refresh" content="6">
  <style>
    body {{
      background: #0d1117;
      color: #fff;
      font-family: monospace;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }}
    .label  {{ font-size: 18px; color: #888; margin-bottom: 10px; }}
    .ip     {{ font-size: 72px; font-weight: bold; letter-spacing: 4px; color: #58d68d; }}
    .real   {{ font-size: 18px; color: #e74c3c; margin-top: 20px; }}
    .status {{ font-size: 22px; margin-top: 30px; padding: 12px 28px;
               border-radius: 8px; background: {'#1a4731' if hidden else '#4a1515'};
               color: {'#58d68d' if hidden else '#e74c3c'}; }}
    .note   {{ font-size: 14px; color: #555; margin-top: 40px; }}
  </style>
</head>
<body>
  <div class="label">CURRENT EXIT IP</div>
  <div class="ip">{exit_ip}</div>
  <div class="real">Your real IP: {REAL_IP}</div>
  <div class="status">{'✓  REAL IP HIDDEN — routing through Tor' if hidden else '✗  NOT HIDDEN — real IP exposed'}</div>
  <div class="note">Auto-refreshes every 6s &nbsp;|&nbsp; Rotate IP in terminal, then watch this page</div>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass  # silence request logs

if __name__ == "__main__":
    print("Starting IP display server...")
    print(f"Real IP: {REAL_IP}")
    print()
    print("  Open this in Chrome/Brave:")
    print("  http://localhost:5000")
    print()
    print("  To rotate IP, run in a second terminal:")
    print("  python tests\\rotate_ip.py")
    print()
    print("Press Ctrl+C to stop.\n")
    HTTPServer(("localhost", 5000), Handler).serve_forever()
