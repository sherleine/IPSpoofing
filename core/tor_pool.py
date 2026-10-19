"""
Tor-backed node pool with automatic IP rotation.

On a failed request, sends NEWNYM to Tor (new circuit = new exit IP),
waits briefly, then marks the node ready again.

Tor Browser must be open and connected before running this.
"""
import time
import requests
from stem import Signal
from stem.control import Controller

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.nodepool import Node, NodePool

TOR_SOCKS_PORT = 9150
TOR_CONTROL_PORT = 9151
NEWNYM_WAIT = 5  # seconds Tor needs to build a new circuit

# Single Tor node — one real exit IP at a time
NODES = [Node("tor-exit", TOR_SOCKS_PORT)]
pool = NodePool(NODES, cooldown_seconds=NEWNYM_WAIT)


def new_tor_ip() -> None:
    """Signal Tor to build a new circuit (new exit IP)."""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        print(f"  [tor] NEWNYM sent — waiting {NEWNYM_WAIT}s for new circuit...")
        time.sleep(NEWNYM_WAIT)
    except Exception as e:
        print(f"  [tor] Control port error: {e}")
        print("  Make sure Tor Browser is open and connected.")


def fetch_ip(node: Node) -> str:
    proxies = {"http": node.proxy_url, "https": node.proxy_url}
    r = requests.get(
        "http://api.ipify.org?format=json",
        proxies=proxies,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["ip"]


def main() -> None:
    print("Starting Tor rotation test — 5 requests, switching IP on each failure.\n")

    for i in range(5):
        node = pool.acquire()
        if node is None:
            print("Node is cooling down, waiting...")
            time.sleep(NEWNYM_WAIT)
            continue

        try:
            ip = fetch_ip(node)
            print(f"Request {i+1}: exit IP {ip}")
            pool.report(node, ok=True)
        except Exception as exc:
            print(f"Request {i+1}: FAILED ({exc}) — switching Tor IP...")
            pool.report(node, ok=False)
            new_tor_ip()

    print("\nFinal status:", pool.status())


if __name__ == "__main__":
    main()
