# IP Rotation Prototype

A proof-of-concept that routes requests through a pool of exit IPs, rotates
across them automatically, and switches to a new IP when one gets blocked.

## Status: Complete

---

## What it does

- Routes outbound requests through Tor (a real, changing exit IP)
- Rotates to a new IP on demand or automatically on failure/block
- Rests a failed node for a cooldown period before retrying
- Proven: distinct IPs confirmed across multiple requests

---

## Project structure

```
spoofing prototype/
├── core/
│   ├── nodepool.py          Rotation engine — round-robin + 10s cooldown
│   └── tor_pool.py          Tor-backed pool — auto-switches IP on failure
├── tests/
│   ├── mock_nodes.py        3 fake local SOCKS5 servers (offline testing)
│   ├── run_prototype.py     Rotation smoke test across mock nodes
│   ├── tor_check.py         Confirms Tor Browser is connected
│   └── tor_rotate_test.py   Force-rotates exit IP and prints each one
├── venv/                    Python virtual environment
├── requirements.txt         Dependencies
└── PROJECT.md               This file
```

---

## How it works

```
Your request
    │
    ▼
nodepool.py  ──  picks next available node (round-robin)
    │
    ▼
Tor SOCKS5 (127.0.0.1:9150)
    │
    ▼
Real exit IP on the internet
    │
  on block or failure
    │
    ▼
NEWNYM signal → Tor builds new circuit → new exit IP → retry
```

---

## How to run

**Prerequisite:** Tor Browser must be open and showing "Connected to Tor."

```powershell
cd "D:\spoofing prototype"
.\venv\Scripts\Activate.ps1
```

| What | Command |
|---|---|
| Check Tor is working | `python tests\tor_check.py` |
| See IP changing in real time | `python tests\tor_rotate_test.py` |
| Test rotation + cooldown (no internet needed) | `python tests\mock_nodes.py` then `python tests\run_prototype.py` |
| Tor pool with auto-switch on failure | `python core\tor_pool.py` |

---

## Proven results

| Test | Result |
|---|---|
| Tor connected | Exit IP: `204.8.96.69` |
| IP rotation (4 requests) | `185.220.101.32` → `192.42.116.100` → `192.42.116.100` → `185.220.100.244` |
| Mock node rotation | 3 distinct fake IPs, round-robin confirmed |
| Cooldown on failure | Failed node rested 10s, skipped, then rejoined |

---

## Dependencies

```
pip install -r requirements.txt
```

- `requests[socks]` — HTTP requests through SOCKS5
- `stem` — Python interface to Tor control port (sends NEWNYM)
- `playwright` — headless browser (used in scraper demo, not core prototype)

---

## Upgrade path

| Need | Solution |
|---|---|
| Multiple simultaneous IPs | Phones/PCs on mobile data via chisel tunnels |
| Faster exits | ProtonVPN Plus or Mullvad (paid, CLI-controllable) |
| No Tor dependency | Real mobile SIMs — one SIM = one carrier IP |
