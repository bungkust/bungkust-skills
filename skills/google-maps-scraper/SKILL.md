---
name: google-maps-scraper
description: "Scrape lokasi dari Google Maps — coffee shop, restoran, tempat wisata. Trigger: 'scrape google maps', 'cari coffee shop', 'cari tempat makan'"
---

# 🗺️ Google Maps Scraper

Scrape data lokasi dari Google Maps tanpa API key. Bisa cari coffee shop, restoran, tempat wisata, dll.

## Cara Pakai

### Basic Search
```
"Cari coffee shop di Jogja dari Google Maps"
"Scrape restoran di Jakarta Selatan rating >4.5"
"Tempat wisata di Bali yang buka 24 jam"
```

### Dengan Filter
```
"Cari coffee shop di Sleman yang buka sekarang"
"Scrape warung makan deket UGM rating di atas 4"
"Hotel di Jogja harga di bawah 500rb"
```

## Output Format

| Field | Contoh |
|-------|--------|
| Nama | Kopi Kultur |
| Rating | 4.8 ⭐ |
| Alamat | Jl. Kaliurang KM 5 |
| Jam Buka | 08:00 - 22:00 |
| Harga Range | Rp 25.000 - 50.000 |
| Phone | 0812-xxxx-xxxx |

## Teknis

Pakai Playwright + StealthyFetcher untuk bypass bot detection. Search Google Maps, parse hasilnya, export ke CSV/JSON/Notion.

## Contoh Output

```csv
Nama,Rating,Alamat,Jam Buka,Harga
Kopi Kultur,4.8,Jl. Kaliurang KM 5,08:00-22:00,25000-50000
Filosofi Kopi,4.6,Jl. Prawirotaman,09:00-23:00,30000-60000
```

## Limitasi

- Tanpa login: max ~20 results per search
- Rate limit: jangan scrape terlalu cepat
- Data bisa berubah sewaktu-waktu

---
*Made with ❤️ by @bungkust*
