#!/usr/bin/env python3
"""
FB Marketplace scraper using camoufox Python API.
Injects cookies + scrapes search results + detail pages.

Usage:
    python3 fb_scraper.py --cookies fb_cookies.json --query "rb" --city yogyakartacity --max 10
"""
import argparse, asyncio, json, re, sys, time
from pathlib import Path

try:
    from camoufox.async_api import AsyncCamoufox
except ImportError:
    print("Error: camoufox not installed.")
    print("  pip install camoufox")
    sys.exit(1)


def parse_args():
    p = argparse.ArgumentParser(description="FB Marketplace Scraper")
    p.add_argument("--cookies", required=True, help="FB cookies JSON file (Playwright format)")
    p.add_argument("--query", default="rb", help="Search query")
    p.add_argument("--city", default="yogyakartacity", help="FB Marketplace city")
    p.add_argument("--max", type=int, default=20, help="Max listings to scrape")
    p.add_argument("--output", default="/tmp/fb_marketplace_results.json", help="Output JSON file")
    p.add_argument("--headless", action="store_true", default=True, help="Run headless")
    p.add_argument("--wait", type=int, default=8, help="Wait seconds after page load")
    return p.parse_args()


async def extract_listing_details(page, listing_id):
    """Extract details from a listing detail page."""
    try:
        content = await page.content()
        
        # Extract from HTML
        title_m = re.search(r'<title>([^<]+)</title>', content)
        price_m = re.search(r'"price"\s*:\s*"*(\d[\d,]*)"', content)
        loc_m = re.search(r'"address"\s*:\s*"([^"]+)"', content)
        desc_m = re.search(r'"description"\s*:\s*"([^"]+)"', content)
        seller_m = re.search(r'"seller"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', content)
        
        # Fallback: parse from accessibility snapshot
        snap = await page.inner_text("body")
        
        # Title from h1
        h1 = re.search(r'^(.*?)(?:\n|$)', snap[:500])
        
        # Price from body text
        price_in_text = re.search(r'IDR?([\d,.]+(?:jt|juta|rb|ribu))', snap, re.I)
        
        result = {
            "id": listing_id,
            "url": f"https://www.facebook.com/marketplace/item/{listing_id}/",
            "title": title_m.group(1) if title_m else "N/A",
            "price": price_m.group(1) if price_m else (price_in_text.group(0) if price_in_text else "N/A"),
            "location": loc_m.group(1) if loc_m else "N/A",
            "description": desc_m.group(1) if desc_m else "N/A",
            "seller": seller_m.group(1) if seller_m else "N/A",
        }
        
        return result
        
    except Exception as e:
        return {"id": listing_id, "error": str(e)}


async def scrape_marketplace(args):
    cookies = json.load(open(args.cookies))
    
    results = {"search": f"{args.city}?query={args.query}", "listings": []}
    
    print(f"[*] Starting camoufox...")
    async with AsyncCamoufox(headless=args.headless) as browser:
        ctx = await browser.new_context()
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        
        # Step 1: Search page
        url = f"https://www.facebook.com/marketplace/{args.city}/search?query={args.query}"
        print(f"[*] Loading: {url}")
        await page.goto(url, timeout=30)
        await page.wait_for_timeout(args.wait)
        
        # Get listing IDs from content
        content = await page.content()
        listing_ids = re.findall(r'marketplace/item/(\d+)/', content)
        listing_ids = list(dict.fromkeys(listing_ids))
        print(f"[*] Found {len(listing_ids)} listing IDs")
        
        results["total_found"] = len(listing_ids)
        results["listing_ids"] = listing_ids[:args.max]
        
        # Step 2: Visit each listing
        for i, lid in enumerate(listing_ids[:args.max]):
            print(f"[*] [{i+1}/{min(args.max, len(listing_ids))}] Listing {lid}")
            
            detail = await extract_listing_details(page, lid)
            results["listings"].append(detail)
            
            if "error" not in detail:
                print(f"    -> {detail.get('title', 'N/A')[:50]}")
                print(f"    -> {detail.get('price', 'N/A')}")
            
            await asyncio.sleep(3)  # Rate limit
        
        await browser.close()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] Saved {len(results['listings'])} results to {args.output}")
    return results


def main():
    args = parse_args()
    
    if not Path(args.cookies).exists():
        print(f"Error: Cookie file not found: {args.cookies}")
        sys.exit(1)
    
    results = asyncio.run(scrape_marketplace(args))
    
    # Print summary
    print("\n=== SUMMARY ===")
    for l in results["listings"][:5]:
        print(f"  {l.get('id')}: {l.get('title', 'N/A')[:40]} | {l.get('price', 'N/A')}")
    if len(results["listings"]) > 5:
        print(f"  ... and {len(results['listings']) - 5} more")


if __name__ == "__main__":
    main()
