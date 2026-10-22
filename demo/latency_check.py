"""Measures request latency: direct vs through Tor."""
import time
import requests

URL = "http://api.ipify.org?format=json"
TOR = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
RUNS = 5


def measure(label, proxies=None):
    times = []
    for i in range(RUNS):
        try:
            t0 = time.perf_counter()
            requests.get(URL, proxies=proxies, timeout=30)
            ms = (time.perf_counter() - t0) * 1000
            times.append(ms)
            print(f"  [{label}] run {i+1}: {ms:.0f}ms")
        except Exception as e:
            print(f"  [{label}] run {i+1}: FAILED ({e})")

    if times:
        print(f"  → avg: {sum(times)/len(times):.0f}ms  "
              f"min: {min(times):.0f}ms  max: {max(times):.0f}ms\n")


print("=== Direct (no proxy) ===")
measure("direct")

print("=== Through Tor ===")
measure("tor", proxies=TOR)
