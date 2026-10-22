"""
Local web server that shows the current Tor exit IP in big text.
Open http://localhost:5000 in any browser.
The page auto-refreshes every 6 seconds.
Click "Rotate IP Now" to get a new exit IP instantly.
"""
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from stem import Signal
from stem.control import Controller

TOR  = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
CTRL = 9151

rotate_status = {"msg": "", "ts": 0}
status_lock   = threading.Lock()

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

def do_rotate():
    try:
        with Controller.from_port(port=CTRL) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
        with status_lock:
            rotate_status["msg"] = "Rotation requested — new IP loading..."
            rotate_status["ts"]  = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] NEWNYM sent — new circuit requested")
    except Exception as e:
        with status_lock:
            rotate_status["msg"] = f"Rotation failed: {e}"
            rotate_status["ts"]  = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Rotate error: {e}")

REAL_IP = get_real_ip()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/rotate":
            threading.Thread(target=do_rotate, daemon=True).start()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        exit_ip = get_exit_ip()
        hidden  = exit_ip != REAL_IP

        with status_lock:
            banner = rotate_status["msg"] if time.time() - rotate_status["ts"] < 12 else ""

        banner_html = (
            f'<div class="banner">{banner}</div>' if banner else ""
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
  <title>IP Rotation — Live</title>
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
      gap: 0;
    }}
    .label   {{ font-size: 18px; color: #888; margin-bottom: 10px; }}
    .ip      {{ font-size: 72px; font-weight: bold; letter-spacing: 4px; color: #58d68d; }}
    .real    {{ font-size: 18px; color: #e74c3c; margin-top: 20px; }}
    .status  {{ font-size: 22px; margin-top: 30px; padding: 12px 28px;
                border-radius: 8px; background: {'#1a4731' if hidden else '#4a1515'};
                color: {'#58d68d' if hidden else '#e74c3c'}; }}
    .btn     {{ margin-top: 36px; padding: 16px 48px; font-size: 20px; font-family: monospace;
                font-weight: bold; background: #2563eb; color: #fff; border: none;
                border-radius: 10px; cursor: pointer; letter-spacing: 1px;
                transition: background 0.2s; }}
    .btn:hover   {{ background: #1d4ed8; }}
    .btn:active  {{ background: #1e3a8a; }}
    .btn:disabled{{ background: #374151; color: #6b7280; cursor: default; }}
    .banner  {{ margin-top: 18px; font-size: 15px; color: #f59e0b;
                background: #2d2000; padding: 8px 24px; border-radius: 6px; }}
    .note    {{ font-size: 13px; color: #444; margin-top: 28px; }}
    #counter {{ color: #555; }}
  </style>
</head>
<body>
  <div class="label">CURRENT EXIT IP</div>
  <div class="ip" id="ipval">{exit_ip}</div>
  <div class="real">Your real IP: {REAL_IP}</div>
  <div class="status">{'&#10003;&nbsp; REAL IP HIDDEN &mdash; routing through Tor' if hidden else '&#10007;&nbsp; NOT HIDDEN &mdash; real IP exposed'}</div>
  <button class="btn" id="rotbtn" onclick="rotateNow()">&#8635; Rotate IP Now</button>
  {banner_html}
  <div class="note">Auto-refreshes every 6s &nbsp;|&nbsp; <span id="counter">refreshing in 6s</span></div>

  <script>
    var countdown = 6;
    var timer = setInterval(function() {{
      countdown--;
      document.getElementById('counter').textContent = 'refreshing in ' + countdown + 's';
      if (countdown <= 0) location.reload();
    }}, 1000);

    function rotateNow() {{
      var btn = document.getElementById('rotbtn');
      btn.disabled = true;
      btn.textContent = 'Rotating...';
      clearInterval(timer);
      document.getElementById('counter').textContent = 'reloading after rotation...';
      fetch('/rotate', {{method: 'POST'}}).then(function() {{
        setTimeout(function() {{ location.reload(); }}, 6000);
      }}).catch(function() {{
        btn.disabled = false;
        btn.textContent = '↻ Rotate IP Now';
      }});
    }}
  </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("Starting IP display server...")
    print(f"Real IP: {REAL_IP}")
    print()
    print("  Open this in Chrome/Brave:")
    print("  http://localhost:5000")
    print()
    print("  Click  [Rotate IP Now]  in the browser to switch exit IP on demand.")
    print()
    print("Press Ctrl+C to stop.\n")
    HTTPServer(("localhost", 5000), Handler).serve_forever()
