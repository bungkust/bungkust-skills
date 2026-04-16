---
name: google-maps-scraper
description: "Scrape lokasi dari Google Maps — coffee shop, restoran, tempat wisata. Trigger: 'scrape google maps', 'cari coffee shop', 'cari tempat makan'"
---

# 🗺️ Google Maps Scraper

Scrape data lokasi dari Google Maps tanpa API key. Pakai Playwright untuk bypass bot detection.

## Dependencies

```bash
pip install playwright
python -m playwright install chromium
```

Kalau headless server/VPS, butuh extra deps:
```bash
sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2
```

## Cara Pakai

### CLI (direct)
```bash
python gmaps_scraper.py "coffee shop" "Yogyakarta" --max 20
python gmaps_scraper.py "restoran" "Jakarta Selatan" --max 10 -o hasil.csv
python gmaps_scraper.py "tempat wisata" "Bali" --max 15
```

### Via AI Agent
```
"Cari coffee shop di Jogja dari Google Maps"
"Scrape restoran di Jakarta Selatan rating >4.5"
"Tempat wisata di Bali yang buka 24 jam"
```

## Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `query` | required | Search query (e.g. "coffee shop") |
| `location` | required | Location (e.g. "Yogyakarta") |
| `--max` | 20 | Max results |
| `--output, -o` | auto | Output CSV path |
| `--headless` | True | Run without browser UI |
| `--no-headless` | - | Show browser (debug) |
| `--delay` | 1.5 | Scroll delay (seconds) |

## Output Format

CSV/JSON dengan fields:

| Field | Contoh |
|-------|--------|
| Name | Kopi Kultur |
| Rating | 4.8 |
| Reviews | 1234 |
| Price_range | Rp 25–50 rb |
| Category | Kedai Kopi |
| Address | Jl. Kaliurang KM 5 |
| Phone | 0812-xxxx-xxxx |
| Website | kopikultur.com |
| Hours | Buka · Tutup pukul 22.00 |

## Teknis

1. Buka Google Maps search URL
2. Scroll results panel untuk load lebih banyak listing
3. Klik setiap card → extract data dari detail panel
4. Parse: Name, Rating, Reviews, Price, Category, Address, Phone, Website, Hours
5. Save ke CSV + JSON

## Limitasi

- Tanpa login Google: max ~20 results per search
- Rate limit: jangan scrape terlalu cepat (default delay 1.5s)
- Data bisa berubah sewaktu-waktu (Google update struktur)
- CSS selectors mungkin perlu update kalau Google Maps redesign

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `playwright not found` | `pip install playwright && python -m playwright install chromium` |
| `chromium failed to launch` | `sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2` |
| `timeout` | Google Maps loading lambat, coba tambah timeout atau cek network |
| `no results` | Coba query yang lebih spesifik |

---
*Made with ❤️ by @bungkust*
