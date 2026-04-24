---
name: fb-marketplace-scraper
description: "Scrape Facebook Marketplace listings — titles, prices, locations, seller info. Uses camoufox/camofox-browser with cookie injection. Trigger: 'scrape facebook marketplace', 'fb marketplace', 'cari barang di fb marketplace'"
---

# FB Marketplace Scraper 🛒

Scrape Facebook Marketplace listings using camoufox with authenticated cookie sessions.

## Two Tool Options

| Tool | Best For | Setup |
|------|----------|-------|
| **camofox-browser** (jo-inc) | REST API, tab management, quick scripts | `node server.js` in cloned repo |
| **camoufox** (Python) | Advanced, programmatic control | `pip install camoufox` |

Both use the same Firefox fork engine — camofox-browser wraps it as a REST API, camoufox gives Python-level control.

## Quick Start

### Option 1: REST API (camofox-browser)

```bash
# Start server
cd /tmp/camofox-browser && node server.js &
# Server: http://localhost:9377

# 1. Create session
curl -X POST http://localhost:9377/sessions/FB1 \
  -H 'Content-Type: application/json' -d '{}'

# 2. Inject cookies (Playwright format)
curl -X POST http://localhost:9377/sessions/FB1/cookies \
  -H 'Content-Type: application/json' \
  -d '{"cookies": [COOKIES_ARRAY]}'

# 3. Create tab + navigate
curl -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d '{"userId": "FB1", "sessionKey": "FB1", "url": "https://www.facebook.com/marketplace/yogyakartacity/search?query=rb"}'

# 4. Snapshot (after wait)
curl "http://localhost:9377/tabs/{TAB_ID}/snapshot?userId=FB1"

# 5. Screenshot
curl "http://localhost:9377/tabs/{TAB_ID}/snapshot?userId=FB1&includeScreenshot=true"
```

### Option 2: Python (camoufox)

```python
import asyncio, json
from camoufox.async_api import AsyncCamoufox

async def scrape():
    cookies = json.load(open('fb_cookies.json'))
    
    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context()
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        
        await page.goto("https://www.facebook.com/marketplace/yogyakartacity/search?query=rb",
                       timeout=30)
        await page.wait_for_timeout(8000)
        
        content = await page.content()
        with open('/tmp/fb_listings.html', 'w') as f:
            f.write(content)
        print(f"Saved {len(content)} bytes")

asyncio.run(scrape())
```

## Cookie Format (Playwright)

Convert EditThisCookie export to Playwright format:

```python
import json
from datetime import datetime

def convert_cookie(name, value, domain, path, expires_str, http_only, secure, same_site):
    expires = -1 if expires_str == "Session" else \
              datetime.fromisoformat(expires_str.replace('Z', '+00:00')).timestamp()
    return {
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "expires": expires,
        "httpOnly": http_only,
        "secure": secure,
        "sameSite": same_site or "None"
    }
```

**Critical fields:**
- `expires`: Unix timestamp as **float** (e.g., `1808532702.397`), NOT ISO string
- `sameSite`: "None" (capital N), "Lax", or "Strict"
- `httpOnly`: True/False
- `secure`: True (always for FB)

## FB Marketplace URL Patterns

```
# Location-based search
https://www.facebook.com/marketplace/{city}/search?query={query}

# Category
https://www.facebook.com/marketplace/{city}/{category}/

# Listing detail
https://www.facebook.com/marketplace/item/{LISTING_ID}/

# Specific cities (Indonesia)
yogyakartacity, jakartacity, surabaya, bandung, semarangcity, malangkota, medankota
```

## Extraction Patterns

### From snapshot (REST API)
```bash
# Get all listing IDs
curl "http://localhost:9377/tabs/{TAB_ID}/snapshot?userId=FB1" | \
  python3 -c "import sys, re; print(re.findall(r'marketplace/item/(\d+)', sys.stdin.read()))"

# Get full snapshot for detail extraction
curl "http://localhost:9377/tabs/{TAB_ID}/snapshot?userId=FB1"
```

### Parse listing detail from snapshot
```python
import re

def parse_listing_snapshot(snapshot_text):
    """Extract fields from FB Marketplace listing snapshot."""
    lines = snapshot_text.split('\n')
    
    title = None
    price = None
    location = None
    description = None
    seller = None
    listed_time = None
    
    for i, line in enumerate(lines):
        # Title (h1 heading)
        h1 = re.search(r'heading "(.+)" \[level=1\]', line)
        if h1:
            title = h1.group(1)
        
        # Price + listed time
        price_match = re.search(r'(IDR[\d,]+(?:\.\d+)?)\s+Listed\s+(\d+\s+\w+\s+ago)', line)
        if price_match:
            price = price_match.group(1)
            listed_time = price_match.group(2)
        
        # Location
        loc = re.search(r'link "(.+), Daerah Istimewa Yogyakarta"', line)
        if loc:
            location = loc.group(1)
        
        # Description (text after "Details" heading)
        if 'Details' in line:
            desc_match = re.search(r'^\s*- text: "(.+)"', lines[i+1] if i+1 < len(lines) else '')
            if desc_match:
                description = desc_match.group(1)
        
        # Seller name
        seller_match = re.search(r'link "(.+)" \[e\d+\]:\s*\n\s*- link "(.+)".*seller', lines[max(0,i-2):i+1])
        if not seller_match:
            seller_match = re.search(r'link "(.+)" \[e\d+\]:\s*\n\s*-\s*link "(.+)"', lines[max(0,i-2):i+3])
    
    return {
        "title": title,
        "price": price,
        "location": location,
        "description": description,
        "seller": seller,
        "listed_time": listed_time
    }
```

## Workflow: Scrape Listings + Details

```python
import asyncio, json, re, time
from camoufox.async_api import AsyncCamoufox

async def scrape_marketplace(query="rb", city="yogyakartacity", max_listings=20):
    cookies = json.load(open('/tmp/fb_cookies.json'))
    
    results = []
    
    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context()
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        
        # Step 1: Search page
        print(f"[*] Loading marketplace search: {query}")
        await page.goto(
            f"https://www.facebook.com/marketplace/{city}/search?query={query}",
            timeout=30
        )
        await page.wait_for_timeout(8000)
        
        # Step 2: Get listing IDs from page content
        content = await page.content()
        listing_ids = re.findall(r'marketplace/item/(\d+)/', content)
        listing_ids = list(dict.fromkeys(listing_ids))  # dedupe
        print(f"[*] Found {len(listing_ids)} listings")
        
        # Step 3: Visit each listing detail
        for lid in listing_ids[:max_listings]:
            try:
                print(f"[*] Fetching listing {lid}")
                await page.goto(
                    f"https://www.facebook.com/marketplace/item/{lid}/",
                    timeout=20
                )
                await page.wait_for_timeout(3000)
                
                snap = await page.inner_text('body')
                
                # Extract via regex patterns
                title_m = re.search(r'"name"\s*:\s*"([^"]+)"', snap)
                price_m = re.search(r'"price"\s*:\s*(\d+)', snap)
                loc_m = re.search(r'"address"\s*:\s*"([^"]+)"', snap)
                desc_m = re.search(r'"description"\s*:\s*"([^"]+)"', snap)
                
                results.append({
                    "id": lid,
                    "title": title_m.group(1) if title_m else "N/A",
                    "price": price_m.group(1) if price_m else "N/A",
                    "location": loc_m.group(1) if loc_m else "N/A",
                    "description": desc_m.group(1) if desc_m else "N/A",
                    "url": f"https://www.facebook.com/marketplace/item/{lid}/"
                })
                
                await asyncio.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"[!] Error listing {lid}: {e}")
        
        await browser.close()
    
    return results

# Run
results = asyncio.run(scrape_marketplace(query="rb", city="yogyakartacity"))
print(json.dumps(results, indent=2, ensure_ascii=False))
```

## REST API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:9377/sessions/{id}` | POST | Create session |
| `http://localhost:9377/sessions/{id}/cookies` | POST | Inject cookies |
| `http://localhost:9377/tabs` | POST | Create tab + navigate |
| `http://localhost:9377/tabs/{tabId}/snapshot` | GET | Get page snapshot |
| `http://localhost:9377/tabs/{tabId}/snapshot?includeScreenshot=true` | GET | Screenshot |
| `http://localhost:9377/tabs/{tabId}/click?ref={refId}&userId={uid}` | POST | Click element |
| `http://localhost:9377/tabs/{tabId}/scroll?userId={uid}` | POST | Scroll |
| `http://localhost:9377/tabs/{tabId}/wait?userId={uid}` | POST | Wait |
| `http://localhost:9377/tabs/{tabId}/navigate?userId={uid}` | POST | Navigate tab |
| `http://localhost:9377/sessions/{id}` | DELETE | Close session |
| `http://localhost:9377/health` | GET | Health check |

**Snapshot query params:**
- `userId` — session identifier
- `format` — "text" (default) or "json"
- `offset` — for pagination of large snapshots
- `includeScreenshot` — "true" for base64 PNG

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot POST /sessions/xxx" | Session auto-created on first tab. POST to `/tabs` directly. |
| "userId required" | Always pass `userId` as query param, not body |
| Login page shown | Cookies expired/invalid — re-export from browser |
| Tab returns 404 | Tab expired (sessions auto-cleanup). Create new tab. |
| Marketplace search blank | FB renders listings via JS. Wait 8-10s after goto. |
| Listing detail blocked | Some listings need additional checkpoint cookies |
| Screenshot empty/dark | Browser still loading. Increase wait time. |
| `set_cookie` AttributeError | Use `ctx.add_cookies(cookies)` NOT `page.set_cookie()` |

## Server Startup

```bash
# Start camofox-browser REST API server
cd /tmp/camofox-browser && node server.js &

# Verify
curl http://localhost:9377/health
# {"ok":true,"engine":"camoufox","browserConnected":false,"browserRunning":false,...}

# Stop
pkill -f "node server.js"
```

## Cookie Security Notes

- Cookies are credentials — treat like passwords
- Store exported cookies with `chmod 600`
- Session cookies expire when user logs out of Facebook
- Re-export cookies if marketplace shows "Log in" instead of listings
