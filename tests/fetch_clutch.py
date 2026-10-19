"""Fetches Clutch company data and saves to output/clutch_results.json."""
import json, time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=False)
    p = b.new_page(viewport={"width": 1280, "height": 900})
    p.goto("https://clutch.co/developers", wait_until="networkidle", timeout=40000)
    p.keyboard.press("Escape")
    time.sleep(2)

    results = []
    seen = set()
    for _ in range(6):
        for card in p.query_selector_all("div.provider-row"):
            n = card.query_selector("h3.provider__title a")
            if not n:
                continue
            name = n.inner_text().strip()
            if name in seen:
                continue
            seen.add(name)
            r  = card.query_selector("meta[itemprop='ratingValue']")
            rv = card.query_selector("a.sg-rating__reviews")
            l  = card.query_selector(".locality, .provider__location-link, [class*='location']")
            results.append({
                "name":     name,
                "rating":   r.get_attribute("content") if r else "n/a",
                "reviews":  rv.inner_text().split()[0] if rv else "n/a",
                "location": l.inner_text().strip() if l else "n/a",
            })
        p.evaluate("window.scrollBy(0, window.innerHeight * 3)")
        time.sleep(2)

    b.close()

with open("output/clutch_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Saved {len(results)} companies to output/clutch_results.json")
