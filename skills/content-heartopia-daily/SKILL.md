---
name: content-heartopia-daily
description: "Scrape Heartopia daily update dari Instagram @myheartopia.id — extract weather, events, resource locations via OCR, update ke Obsidian vault. Trigger: 'heartopia daily', 'scrape heartopia', 'update heartopia', 'heartopia info'."
tags:
  - content
  - heartopia
  - instagram
  - scrape
  - ocr
category: social-media
---

# Content Heartopia Daily

> Scrape Heartopia game info dari Instagram @myheartopia.id, OCR images, update ke Obsidian vault.

## Workflow

```
1. Fetch latest "Update Harian" post dari @myheartopia.id (insta-fetcher)
2. Extract image carousel URLs
3. Download images + OCR with tesseract
4. Parse OCR output → structured data
5. Append entry to Heartopia-Daily-Tracker.md in vault
```

## Setup (First Time)

```bash
# Install deps if needed
cd /tmp/heartopia-scrape
npm install insta-fetcher 2>/dev/null

# Install tesseract
apt-get install -y tesseract-ocr 2>/dev/null

# Get Instagram cookies from browser:
# Instagram → DevTools → Application → Cookies → Copy sessionid value
# Format: sessionid=YOUR_DS_USER_ID%3A90HYFuvCoL9HCs%3A19%3AAYjerQ...
```

## Cookie Format

```javascript
// Full cookie string from browser (not just sessionid)
const cookieStr = 'csrftoken=...; sessionid=...; mid=...; ig_did=...; datr=...; ds_user_id=...; ps_l=1; ps_n=1;';
```

## Key Quirks

- **Data ada di IMAGES, bukan caption** — Heartopia "Update Harian" info ada di carousel images, bukan caption text
- **OCR required** — tesseract untuk extract text dari image
- **Post structure:** `items[].carousel_media[].image_versions2.candidates[].url`
- **Dory's position during rain = same as Fluorite location** — confirmed by user (Lira): "Doris posisi saat hujan" is in the image showing Dory at Fluorite's house
- **Dory items (hujan):** Ingredient, Postcard, Umbrella — extracted from img_1 via OCR
- **Image preprocessing:** convert ke PNG dulu sebelum OCR (`ffmpeg -i img.jpg img.png`)

## OCR Parsing

Heartopia update images biasanya berisi:

```
img_0: Tanggal, Oak Tree location, Fluorite location, Cuaca
img_1: Dory's items (saat hujan), price info
```

### OCR Command

```bash
ffmpeg -i img.jpg -q:v 3 img.png -y
tesseract img.png stdout 2>/dev/null
```

## Vault Update Format

```markdown
## DD MMMM YYYY

**Cuaca:** [description]
**Oak Tree:** Rumah No. X
**Fluorite:** Rumah No. X
**Dory (saat hujan):** Rumah No. X / Jual: Item1, Item2, Item3
**Events:** [jika ada]
```

## Script Location

Scripts ada di `/tmp/heartopia-scrape/`:

- `scrape_heartopia.mjs` — main scraper script
- `cookies.json` — cookie storage (gitignored, jangan commit!)
- `package.json` — dependencies

## Daily Check

```bash
cd /tmp/heartopia-scrape
node scrape_heartopia.mjs
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Page Not Found" on IG API | sessionid expired — refresh cookie dari browser |
| OCR returns empty | Image terlalu kecil, convert ke PNG + resize sebelum OCR |
| No carousel images | Post mungkin single image, bukan carousel |
| tesseract not found | `apt-get install tesseract-ocr` |
| Wrong home location | Check @hey.bunnyxo untuk referensi |

## Pitfalls

- Jangan scrape dari server IP — Instagram block ASN-level. Selalu pakai browser cookie dari login yang sudah ada
- sessionid cookie harus match dengan user-agent yang dipake (Android UA works best)
- OCR text sering noisy — capture关键的 keywords aja (Rumah No., Cuaca, Oak, Fluorite)
