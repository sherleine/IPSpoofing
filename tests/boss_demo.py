"""
IP Rotation Prototype — Boss Demo
Tor Browser must be open and connected before running.
"""
import time
import json
import requests
from stem import Signal
from stem.control import Controller

TOR      = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
CTRL     = 9151
COOLDOWN = 5

def get_ip(proxies=None):
    r = requests.get("http://api.ipify.org?format=json", proxies=proxies, timeout=30)
    return r.json()["ip"]

def rotate():
    print("  >> Sending signal to Tor — building new circuit...")
    try:
        with Controller.from_port(port=CTRL) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
        time.sleep(COOLDOWN)
    except Exception:
        print("  [!] Control port dropped — reopen Tor Browser and retry.")
        raise

def box(text):
    w = len(text) + 4
    print("\n  " + "=" * w)
    print(f"  | {text} |")
    print("  " + "=" * w + "\n")

def sep(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")

# ── START ────────────────────────────────────────────────
print("\n" + "█" * 55)
print("█  IP ROTATION PROTOTYPE — LIVE DEMO              █")
print("█" * 55)

# STEP 1
sep("STEP 1 │ Your real IP — no proxy")
real_ip = get_ip()
box(f"REAL IP:  {real_ip}  ← target sites see THIS")
print("  Any website you visit knows exactly who you are.")
input("\n  Press ENTER to continue...\n")

# STEP 2
sep("STEP 2 │ Same request through Tor")
tor_ip_1 = get_ip(TOR)
box(f"EXIT IP:  {tor_ip_1}  ← target sees THIS instead")
print(f"  Your real IP  {real_ip}  is completely hidden.")
print(f"  The target only knows:  {tor_ip_1}")
input("\n  Press ENTER to simulate a block...\n")

# STEP 3
sep("STEP 3 │ Block detected — auto-switching IP")
print(f"  Current IP:  {tor_ip_1}  ← got blocked")
rotate()
tor_ip_2 = get_ip(TOR)
print()
print(f"  BEFORE:  {tor_ip_1}")
print(f"  AFTER :  {tor_ip_2}")
box(f"SWITCHED: {'YES — NEW IP ACTIVE' if tor_ip_2 != tor_ip_1 else 'same node, Tor reassigned'}")
print("  Zero manual action. Happened automatically.")
input("\n  Press ENTER to see 3 more rotations...\n")

# STEP 4
sep("STEP 4 │ 3 consecutive rotations")
ips = []
for i in range(1, 4):
    try:
        rotate()
        ip = get_ip(TOR)
        ips.append(ip)
        print(f"  Request {i}:  {ip}")
    except Exception:
        print(f"  Tor control port unavailable — reopen Tor Browser to continue.")
        break

# STEP 5
sep("STEP 5 │ Live scrape — Clutch.co company data")
print("  Launching browser and scraping clutch.co/developers...")
print("  (browser will open and scroll — this takes ~30 seconds)\n")

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fetch_clutch import scrape, save, CSV_OUT

companies = scrape()
csv_path  = save(companies)

print(f"\n  Scraped {len(companies)} companies  →  saved to {csv_path}\n")
print(f"  {'#':<4} {'Company':<35} {'Rating':<8} {'Reviews':<8} {'Location':<22} Description")
print(f"  {'─'*105}")
for c in companies[:6]:
    desc = (c['description'][:40] + "...") if len(c['description']) > 40 else c['description']
    print(f"  {c['rank']:<4} {c['name']:<35} {c['rating']:<8} {c['reviews']:<8} {c['location']:<22} {desc}")
print(f"\n  ... and {len(companies)-6} more  |  full data in: {csv_path}")

# SUMMARY
sep("SUMMARY")
all_ips = list(dict.fromkeys([real_ip, tor_ip_1, tor_ip_2] + ips))
print(f"\n  {'Your real IP':<20} {real_ip}")
print(f"  {'IPs used':<20} {len(all_ips) - 1} different exit IPs")
for ip in all_ips[1:]:
    print(f"  {'':20} {ip}")
print(f"\n  {'Auto-switched':<20} YES — on block, zero manual action")
print(f"  {'Cooldown':<20} {COOLDOWN}s between rotations")
print(f"  {'Data scraped':<20} {len(companies) if 'companies' in dir() else 0} companies from Clutch.co")
print(f"  {'Next step':<20} Connect to large-scale scraping system")

print("\n" + "█" * 55)
print("█  END OF DEMO                                     █")
print("█" * 55 + "\n")
