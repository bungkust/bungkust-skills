#!/usr/bin/env python3
"""
Google Maps Scraper — scrape business listings to CSV.
Usage: python gmaps_scraper.py "coffee shop" "Yogyakarta" --max 20
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout


def parse_args():
    p = argparse.ArgumentParser(description="Google Maps Scraper")
    p.add_argument("query", help='Search query, e.g. "coffee shop"')
    p.add_argument("location", help='Location, e.g. "Yogyakarta"')
    p.add_argument("--max", type=int, default=20, help="Max results (default: 20)")
    p.add_argument("--output", "-o", default=None, help="Output CSV path (auto if omitted)")
    p.add_argument("--headless", action="store_true", default=True, help="Run headless (default)")
    p.add_argument("--no-headless", action="store_false", dest="headless", help="Show browser")
    p.add_argument("--delay", type=float, default=1.5, help="Scroll delay seconds")
    return p.parse_args()


def extract_one_listing(page, card_index):
    """Click a single card and extract its data. Returns dict or None."""
    # Re-query cards each time (DOM changes on scroll)
    cards = page.query_selector_all('a[class*="hfpxzc"]')
    if card_index >= len(cards):
        return None

    card = cards[card_index]

    # Get name from card aria-label (backup)
    card_name = card.get_attribute("aria-label") or ""

    try:
        # Scroll card into view and click
        card.scroll_into_view_if_needed()
        card.click()
        time.sleep(3)

        # Wait for detail panel to appear (look for the reviews+price line)
        try:
            page.wait_for_function(
                """() => {
                    const body = document.body.innerText;
                    return body.includes('(') && (body.includes('Rp') || body.includes('rb'));
                }""",
                timeout=6000
            )
        except:
            pass

        data = {}

        # Name — from h1 or fallback to card aria-label
        name_el = page.query_selector('h1.DUwDvf')
        data["Name"] = name_el.inner_text().strip() if name_el else card_name
        if not data["Name"]:
            return None

        # Get body text for pattern matching
        body_text = page.inner_text('body')
        lines = [l.strip() for l in body_text.split('\n') if l.strip()]

        # Find the line with name in body text to extract nearby data
        name_idx = -1
        for idx, line in enumerate(lines):
            if data["Name"] in line:
                name_idx = idx
                break

        # === Extract from body text using Ringkasan anchor ===
        # Structure: ...\nName\n4,5\n(1.234)·Rp 25–50 rb\nKedai Kopi·\nRingkasan...
        # So: Ringkasan_idx - 4 = Name, -3 = Rating, -2 = Reviews+Price, -1 = Category
        data["Rating"] = ""
        data["Reviews"] = ""
        data["Price_range"] = ""
        data["Category"] = ""

        ringkasan_idx = -1
        for idx, line in enumerate(lines):
            if line == "Ringkasan":
                ringkasan_idx = idx

        if ringkasan_idx >= 4:
            # Rating: line at ringkasan - 3
            rating_line = lines[ringkasan_idx - 3].strip()
            if re.match(r'^\d+[.,]?\d*$', rating_line) and len(rating_line) <= 4:
                data["Rating"] = rating_line.replace(",", ".")

            # Reviews + Price: line at ringkasan - 2
            rp_line = lines[ringkasan_idx - 2].strip()
            rp_match = re.search(r'\(([\d.,]+)\)[·\s]*(Rp[\s\d.,kKrb\-–~\$]+)', rp_line)
            if rp_match:
                data["Reviews"] = rp_match.group(1).replace(".", "").replace(",", "")
                raw_price = rp_match.group(2).strip()
                raw_price = re.sub(r'\xa0', ' ', raw_price)  # non-breaking space
                data["Price_range"] = raw_price
            else:
                # Try separate
                rev_m = re.search(r'\(([\d.,]+)\)', rp_line)
                if rev_m:
                    data["Reviews"] = rev_m.group(1).replace(".", "").replace(",", "")
                price_m = re.search(r'(Rp[\s\d.,kKrb\-–~\$]+)', rp_line)
                if price_m:
                    data["Price_range"] = price_m.group(1).strip()

            # Category: line at ringkasan - 1
            cat_line = lines[ringkasan_idx - 1].strip()
            # Clean category: remove trailing special chars
            cat_clean = re.split(r'[·\ue934\ue413]', cat_line)[0].strip()
            if cat_clean and len(cat_clean) > 2:
                data["Category"] = cat_clean

        # Fallback: if Ringkasan approach failed, try other markers
        if not data["Rating"]:
            for marker in ("Menu", "Ulasan", "Tentang"):
                marker_idx = -1
                for idx, line in enumerate(lines):
                    if line == marker:
                        marker_idx = idx
                if marker_idx >= 4:
                    rating_line = lines[marker_idx - 3].strip()
                    if re.match(r'^\d+[.,]?\d*$', rating_line) and len(rating_line) <= 4:
                        data["Rating"] = rating_line.replace(",", ".")
                        rp_line = lines[marker_idx - 2].strip()
                        rp_match = re.search(r'\(([\d.,]+)\)[·\s]*(Rp[\s\d.,kKrb\-–~\$]+)', rp_line)
                        if rp_match:
                            data["Reviews"] = rp_match.group(1).replace(".", "").replace(",", "")
                            data["Price_range"] = re.sub(r'\xa0', ' ', rp_match.group(2).strip())
                        cat_line = lines[marker_idx - 1].strip()
                        cat_clean = re.split(r'[·\ue934\ue413]', cat_line)[0].strip()
                        if cat_clean and len(cat_clean) > 2:
                            data["Category"] = cat_clean
                        break

        # Address, Phone, Website, Hours — from Io6YTe info blocks
        addr_els = page.query_selector_all('div.Io6YTe')
        data["Address"] = ""
        data["Phone"] = ""
        data["Website"] = ""
        data["Hours"] = ""

        for el in addr_els:
            text = el.inner_text().strip()
            if not text:
                continue
            # Phone: starts with + or area code
            if re.match(r'^[\+\d][\d\s\-\(\)]{7,}$', text):
                data["Phone"] = text
            # Website
            elif any(kw in text.lower() for kw in ["http", "www.", ".com", ".id", ".co", ".net", "instagram", "tokopedia", "linktr"]):
                data["Website"] = text
            # Hours
            elif any(kw in text for kw in ["Buka", "Tutup", "Closed", "Open", "24 jam", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]):
                data["Hours"] = text
            # Address (longer text, has street indicators)
            elif len(text) > 10 and not data["Address"]:
                if any(kw in text for kw in ["Jl.", "Jalan", "No.", "Gg.", "RT.", "RW.", "Kec.", "Kota", "Kabupaten", "Gang"]):
                    data["Address"] = text
                elif len(text) > 20:
                    data["Address"] = text

        # Phone fallback
        if not data["Phone"]:
            phone_el = page.query_selector('button[aria-label*="phone"], a[aria-label*="Phone"]')
            if phone_el:
                raw = phone_el.inner_text().strip() or phone_el.get_attribute("aria-label") or ""
                data["Phone"] = raw.replace("Phone: ", "").replace("Telepon: ", "")

        # Website fallback
        if not data["Website"]:
            web_el = page.query_selector('a[aria-label*="Website"]')
            if web_el:
                href = web_el.get_attribute("href") or ""
                data["Website"] = href

        # Hours from body text fallback
        if not data["Hours"]:
            hours_match = re.search(r'(Buka[·\s]*(?:Tutup pukul [\d.]+|24 jam)|Tutup pukul [\d.]+|Buka 24 jam)', body_text)
            if hours_match:
                data["Hours"] = hours_match.group(1).strip()

        return data

    except Exception as e:
        print(f"  ⚠ Error at card {card_index}: {e}", file=sys.stderr)
        return None


def extract_listings(page, max_results):
    """Extract business info by clicking cards one by one."""
    results = []
    seen_names = set()
    i = 0
    fails = 0

    while len(results) < max_results and fails < 5:
        data = extract_one_listing(page, i)
        i += 1

        if data and data["Name"] and data["Name"] not in seen_names:
            seen_names.add(data["Name"])
            results.append(data)
            print(f"  ✅ [{len(results)}] {data['Name']}")
            fails = 0
        else:
            fails += 1
            if data is None:
                print(f"  ⏭ Card {i-1}: skipped")

    return results


def scroll_results_panel(page, max_results, delay):
    """Scroll the results panel to load more listings."""
    # Find the scrollable results container
    feed = page.query_selector('div[role="feed"]')
    if not feed:
        feed = page.query_selector('div.m6QErb.DxyBCb')

    if not feed:
        print("⚠ Could not find scrollable results panel", file=sys.stderr)
        return

    prev_count = 0
    scroll_attempts = 0

    while scroll_attempts < 30:
        current_cards = page.query_selector_all('a[class*="hfpxzc"]')
        current_count = len(current_cards)
        print(f"  📋 Loaded {current_count} listings...")

        if current_count >= max_results:
            break

        if current_count == prev_count:
            scroll_attempts += 1
            if scroll_attempts >= 3:
                print("  🛑 No more results loading")
                break
        else:
            scroll_attempts = 0

        prev_count = current_count

        # Scroll down
        feed.evaluate('el => el.scrollTop = el.scrollHeight')
        time.sleep(delay)

        # Check if "end of results" message appeared
        end_msg = page.query_selector('span.HlvSq')
        if end_msg:
            print("  🏁 Reached end of results")
            break


def save_csv(data, filepath):
    """Save results to CSV."""
    if not data:
        print("⚠ No data to save")
        return

    fieldnames = ["Name", "Rating", "Reviews", "Price_range", "Category",
                  "Address", "Phone", "Website", "Hours"]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Saved {len(data)} results to {filepath}")


def save_json(data, filepath):
    """Save results to JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(data)} results to {filepath}")


def main():
    args = parse_args()

    # Auto output path
    if args.output:
        out_path = Path(args.output)
    else:
        slug = re.sub(r'[^\w]+', '_', f"{args.query}_{args.location}").strip('_')
        out_path = Path(f"./output/{slug}.csv")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_path.with_suffix('.json')

    from urllib.parse import quote_plus
    search_query = f"{args.query} {args.location}"
    search_url = f"https://www.google.com/maps/search/{quote_plus(search_query)}"

    print(f"🔍 Searching: {args.query} in {args.location}")
    print(f"🌐 URL: {search_url}")
    print(f"📊 Max results: {args.max}")
    print()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=args.headless,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="id-ID",
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("🌐 Opening Google Maps...")
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)

            # Handle cookie consent if present
            try:
                consent_btn = page.query_selector('button[aria-label*="Accept"], button[jsname="higCR"]')
                if consent_btn:
                    consent_btn.click()
                    time.sleep(1)
            except:
                pass

            # Scroll to load results
            print("📜 Scrolling to load listings...")
            scroll_results_panel(page, args.max, args.delay)

            # Extract data
            print("\n⛏ Extracting data...")
            results = extract_listings(page, args.max)

            # Save
            save_csv(results, str(out_path))
            save_json(results, str(json_path))

            print(f"\n🎉 Done! {len(results)} businesses scraped.")

        except PwTimeout:
            print("❌ Timeout loading page. Try again or check network.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
