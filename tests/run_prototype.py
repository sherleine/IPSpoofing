"""Smoke test for the mobile-proxy prototype.

Rotates an IP-echo request across every live node and prints the exit IP each
one produces. If each node is on its own cellular connection, you'll see a
different IP per node -- that's the proof the pool works.

Setup:
    pip install "requests[socks]"
Run this ON the controller (the public-IP VPS) AFTER the chisel tunnels are up.
Add one Node line per live reverse-SOCKS port (one per SIM/connection).
"""
import requests

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.nodepool import Node, NodePool

# One entry per live chisel reverse-SOCKS port = one per cellular connection.
NODES = [
    Node("mullvad-us-ny",  1080),
    Node("mullvad-uk-lon", 1081),
    Node("mullvad-de-fra", 1082),
]

pool = NodePool(NODES, cooldown_seconds=10)


def fetch_exit_ip(node: Node) -> str:
    resp = requests.get(
        "http://api.ipify.org?format=json",
        proxies={"http": node.proxy_url, "https": node.proxy_url},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("ip", "?")


def main() -> None:
    # two passes so you can see rotation reuse each node
    for _ in range(len(NODES) * 2):
        node = pool.acquire()
        if node is None:
            print("all nodes are cooling down -- wait a few seconds and retry")
            break
        try:
            ip = fetch_exit_ip(node)
            print(f"{node.name:14s} -> exit IP {ip}")
            pool.report(node, ok=True)
        except Exception as exc:  # timeout, tunnel down, block, etc.
            print(f"{node.name:14s} -> FAILED ({exc}); resting {pool.cooldown:.0f}s")
            pool.report(node, ok=False)

    print("\nstatus:", pool.status())


if __name__ == "__main__":
    main()
