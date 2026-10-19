"""Quick check: is Tor Browser running and reachable?"""
import requests

proxies = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}

try:
    r = requests.get("http://api.ipify.org?format=json", proxies=proxies, timeout=30)
    print("Tor is working. Exit IP:", r.json()["ip"])
except Exception as e:
    print("Tor not reachable:", e)
    print("Make sure Tor Browser is open and shows 'Connected to Tor'.")
