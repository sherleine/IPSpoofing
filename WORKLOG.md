# Work Log — IP Rotation Prototype

---

## October 16, 2026

### Setup & Architecture
- Defined project goal: prove IP rotation end to end using a pool of exit nodes
- Established the core rule: one exit IP per distinct cellular connection (SIM)
- Wrote initial architecture — controller (VPS) + chisel reverse tunnels + exit nodes (phones/dongles)
- Created `nodepool.py` — round-robin rotation with 10-second cooldown on failure
- Created `run_prototype.py` — smoke test that calls an IP-echo API through each node

### Pivot: Local PC as Controller
- Dropped the VPS requirement — used local Windows PC as the controller instead
- Attempted Mullvad free SOCKS5 proxies as exit nodes (later found to be incorrect — those hostnames don't exist as free public endpoints)
- Switched to local mock SOCKS5 servers instead: `mock_nodes.py` — 3 fake nodes each returning a distinct IP

### First Live Test (Mock Nodes)
- Created Python venv, installed `requests[socks]`
- Ran `mock_nodes.py` + `run_prototype.py`
- **Result:** 3 distinct fake IPs confirmed, round-robin rotation working, cooldown logic verified

### Tor Integration
- Installed Tor Browser
- Wrote `tor_check.py` — confirmed Tor reachable via SOCKS5 on port 9150
  - **Exit IP confirmed:** `204.8.96.69`
- Wrote `tor_pool.py` — Tor-backed pool with NEWNYM auto-switch on failure
  - Ran 5 requests: all succeeded on same IP (expected — no failures occurred)
- Wrote `tor_rotate_test.py` — force-rotates circuit before every request
  - **Result:** 4 requests, distinct IPs confirmed:
    `185.220.101.32` → `192.42.116.100` → `192.42.116.100` → `185.220.100.244`

---

## October 17, 2026

### Scraper Demo (Clutch.co)
*Note: scraper was built as a live demo of the prototype in action — not part of the core deliverable.*

- Built `scraper.py` — Playwright (Chromium) through Tor, targeting `clutch.co/developers`
  - First run: blocked (HTTP 403) on all 3 Tor exit attempts — Tor exit nodes blacklisted by Clutch
- Built `scraper_direct.py` — same scraper, direct connection (no proxy)
  - HTTP 200 received but company cards timed out — Clutch is JS-rendered
- Built `scraper_inspect.py` — opened visible browser, captured screenshot and HTML
  - Screenshot confirmed page loads fully with company data visible
  - Inspected HTML to find real CSS selectors:
    - Card: `div.provider-row`
    - Name: `h3.provider__title a`
    - Rating: `meta[itemprop='ratingValue']` (content attribute)
    - Reviews: `a.sg-rating__reviews`
    - Location: `.locality`
- Rewrote `scraper_direct.py` with correct selectors + scroll logic
  - **Result:** 75 companies scraped — names, ratings, reviews, locations
- Rewrote `scraper.py` to route through Tor with correct selectors
  - **Result:** 75 companies scraped successfully through Tor on first attempt

### Project Restructure
- Reorganised all files into a clean folder structure:
  ```
  core/       → nodepool.py, tor_pool.py
  scrapers/   → clutch.py, clutch_direct.py
  tests/      → mock_nodes.py, run_prototype.py, tor_check.py, tor_rotate_test.py
  output/     → clutch_results.json
  ```
- Added `requirements.txt`

### Scope Correction
- Confirmed with user: scraper was only a demo — core deliverable is the IP rotation prototype
- Removed `scrapers/` and `output/` folders
- Finalised structure: `core/`, `tests/`, `venv/`, `requirements.txt`, `PROJECT.md`
- Updated `PROJECT.md` to reflect correct scope and proven results

---

## Summary

| Date | Key milestone |
|---|---|
| Oct 16 | Core rotation logic built and tested with mock nodes; Tor integration proven with real IP changes |
| Oct 17 | Live scraper demo through Tor; project restructured and scoped down to prototype deliverable |
