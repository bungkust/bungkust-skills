---
name: instagram-scraper
description: "General-purpose Instagram scraper using browser cookies + insta-fetcher Android API. Fetch posts, extract images/carousel, OCR text. Works for any public or private account you have session access to. Trigger: 'scrape ig', 'instagram scraper', 'fetch ig posts', 'scrape instagram'."
tags:
  - instagram
  - scrape
  - social-media
  - ocr
category: social-media
---

# Instagram Scraper

> General-purpose Instagram scraper for any account. Uses browser cookie + Android API — no camoufox needed, works reliably.

## Quick Start

```bash
# Required: Instagram session cookie from your browser
# Instagram → DevTools (F12) → Application → Cookies → Copy sessionid value

# Install deps (if not already)
cd /tmp/heartopia-scrape
npm install insta-fetcher 2>/dev/null

# Run scraper
node /root/.hermes/skills/social-media/instagram-scraper/scripts/ig_scrape.mjs \
  --user myheartopia.id \
  --cookie "sessionid=YOUR_SESSIONID..." \
  --amount 5
```

## Cookie Format

Full cookie string from browser (not just sessionid):
```
csrftoken=xxx; sessionid=xxx%3Axxx%3Axxx; mid=xxx; ig_did=xxx; datr=xxx; ds_user_id=xxx; ps_l=1; ps_n=1;
```

Get it from: Instagram web → DevTools → Application → Cookies → Select instagram.com → Copy all visible cookie name/value pairs.

## Usage

```bash
# Basic — fetch latest 5 posts
node ig_scrape.mjs --user USERNAME --cookie "COOKIE_STRING"

# With amount
node ig_scrape.mjs --user USERNAME --cookie "..." --amount 10

# Save images locally
node ig_scrape.mjs --user USERNAME --cookie "..." --save-images

# OCR on images
node ig_scrape.mjs --user USERNAME --cookie "..." --ocr

# Combined
node ig_scrape.mjs --user USERNAME --cookie "..." --amount 3 --save-images --ocr
```

## Output Format

```json
{
  "username": "myheartopia.id",
  "fetched_at": "2026-05-02T...",
  "posts": [
    {
      "shortcode": "ABC123xyz",
      "taken_at": "2026-05-02T14:30:00.000Z",
      "caption": "Update Harian...",
      "likes": 1234,
      "comments": 56,
      "images": ["url1", "url2"],
      "is_carousel": true,
      "ocr_text": "optional extracted text from images"
    }
  ]
}
```

## Post Data Structure (from Android API)

```
posts[].node.code              → shortcode
posts[].node.taken_at → Unix timestamp (Android API uses taken_at, NOT taken_at_timestamp)
posts[].node.caption.text      → caption text
posts[].node.likes_count        → likes
posts[].node.comments_count     → comments
posts[].node.carousel_media     → array (if carousel)
  [].image_versions2.candidates[0].url → image URL
posts[].node.image_versions2.candidates[0].url → single image URL
```

## OCR Images

```bash
# Install tesseract if needed
apt-get install -y tesseract-ocr

# OCR command
ffmpeg -i img.jpg -q:v 3 img.png -y
tesseract img.png stdout 2>/dev/null
```

## Cookie Refresh

If you get "Page Not Found" or auth errors:
1. Login to Instagram in your browser
2. Go to DevTools → Application → Cookies
3. Copy the full cookie string again
4. Update your script or environment

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| "useragent mismatch" | sessionid tied to different UA | Use Android UA: `Instagram 270.0.0.0.0 Android (24/7.0; ...)` |
| "Access denied" | Server IP blocked | Can't scrape from server — use browser cookie only |
| "No posts found" | Private account / wrong username | Check username is correct |
| Empty carousel | Post is single image | Single images under `image_versions2.candidates` |
| OCR empty | Text too small/color matching bg | Preprocess: convert to PNG, increase contrast |

## Key Quirks

- **Android API, not web API** — uses `i.instagram.com/api/v1/` endpoints
- **Session cookie works** — as long as you're logged in on browser, cookie from that session works
- **sessionid must match user-agent** — Android sessionid with Android UA
- **Data in images** — many accounts put info in image text, not captions. OCR required.
- **Carousel detection** — check `carousel_media` array exists

## Save Images

Images saved to `/tmp/ig_scrape/{username}/{shortcode}/`
