"""
Fetches Clutch company listings and saves to output/ as both JSON and CSV.
Collects: rank, name, rating, reviews, location, tagline, description.
"""
import json
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

STAMP  = datetime.now().strftime("%Y-%m-%d_%H-%M")
JSON_OUT = "output/clutch_results.json"
CSV_OUT  = f"output/clutch_{STAMP}.csv"

FIELDS = ["rank", "name", "rating", "reviews", "location", "description"]


def scrape():
    results = []
    seen = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto("https://clutch.co/developers", wait_until="networkidle", timeout=40000)
        page.keyboard.press("Escape")
        time.sleep(2)

        for _ in range(6):
            for card in page.query_selector_all("div.provider-row"):
                name_el = card.query_selector("h3.provider__title a")
                if not name_el:
                    continue
                name = name_el.inner_text().strip()
                if not name or name in seen:
                    continue
                seen.add(name)

                def t(sel):
                    el = card.query_selector(sel)
                    return el.inner_text().strip() if el else "n/a"

                rating_el = card.query_selector("meta[itemprop='ratingValue']")
                rating = rating_el.get_attribute("content") if rating_el else "n/a"

                reviews_el = card.query_selector("a.sg-rating__reviews")
                reviews = reviews_el.inner_text().split()[0] if reviews_el else "n/a"

                loc_el = card.query_selector(".locality, .provider__location-link, [class*='location']")
                location = loc_el.inner_text().strip() if loc_el else "n/a"

                desc_el = card.query_selector(".provider__description-text-more, .project-highlight-text, [class*='description']")
                description = desc_el.inner_text().strip()[:300] if desc_el else "n/a"

                results.append({
                    "rank":        len(results) + 1,
                    "name":        name,
                    "rating":      rating,
                    "reviews":     reviews,
                    "location":    location,
                    "description": description,
                })

            page.evaluate("window.scrollBy(0, window.innerHeight * 3)")
            time.sleep(2)

        browser.close()
    return results


def save(results):
    # JSON
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # CSV
    with open(CSV_OUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    return CSV_OUT


if __name__ == "__main__":
    print("Fetching Clutch.co/developers...")
    results = scrape()
    csv_path = save(results)
    print(f"\nSaved {len(results)} companies")
    print(f"  JSON : {JSON_OUT}")
    print(f"  CSV  : {csv_path}")
    print(f"\nSample:")
    print(f"  {'#':<4} {'Company':<35} {'Rating':<8} {'Location':<25} Description")
    print(f"  {'-'*105}")
    for c in results[:5]:
        desc = c['description'][:45] + "..." if len(c['description']) > 45 else c['description']
        print(f"  {c['rank']:<4} {c['name']:<35} {c['rating']:<8} {c['location']:<25} {desc}")
