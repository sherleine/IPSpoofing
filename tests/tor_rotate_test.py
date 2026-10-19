"""
Force-rotate test: sends NEWNYM before every request so you can see
Tor actually changing exit IPs, not just handling failures.
"""
import time
import requests
from stem import Signal
from stem.control import Controller

TOR_SOCKS = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
TOR_CONTROL_PORT = 9151
NEWNYM_WAIT = 5


def new_tor_ip() -> None:
    with Controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
        ctrl.authenticate()
        ctrl.signal(Signal.NEWNYM)
    time.sleep(NEWNYM_WAIT)


def fetch_ip() -> str:
    r = requests.get("http://api.ipify.org?format=json", proxies=TOR_SOCKS, timeout=30)
    return r.json()["ip"]


if __name__ == "__main__":
    print("Forcing a new Tor circuit before each request...\n")
    for i in range(4):
        print(f"Request {i+1}: rotating...", end=" ", flush=True)
        new_tor_ip()
        ip = fetch_ip()
        print(f"exit IP {ip}")
