# 🗺️ Google Maps Scraper — HOWTO

Cara install dan pakai skill scrape Google Maps.

---

## 📋 Prerequisites

- Python 3.10+
- pip

## 🚀 Install

### Step 1: Install Hermes Agent

```bash
curl -sSL https://hermes.ai/install | bash
```

Atau kalau udah ada Hermes, skip ke Step 2.

### Step 2: Install Skill

```bash
# Install semua skills (recommended)
npx skills add bungkust/bungkust-skills

# Atau install skill ini aja
npx skills add bungkust/bungkust-skills --skill google-maps-scraper
```

### Step 3: Install Dependencies

```bash
pip install playwright
python -m playwright install chromium
```

### Step 4: Test

```bash
hermes run "Cari coffee shop di Jogja dari Google Maps"
```

---

## 🎯 Cara Pakai

### Basic Search
```
"Cari coffee shop di Jogja dari Google Maps"
"Scrape restoran di Jakarta Selatan"
"Tempat wisata di Bali"
```

### Dengan Filter
```
"Cari coffee shop di Sleman yang buka sekarang"
"Scrape warung makan deket UGM rating di atas 4"
"Hotel di Jogja harga di bawah 500rb"
"Restoran vegetarian di Jakarta yang open 24 jam"
```

### Export ke Format Lain
```
"Scrape coffee shop di Jogja, export ke CSV"
"Cari restoran di Bandung, simpan ke Notion"
"Scrape tempat wisata di Bali, export ke JSON"
```

---

## 📊 Output

Hasil scrape berupa data:

| Field | Contoh |
|-------|--------|
| Nama | Kopi Kultur |
| Rating | 4.8 ⭐ |
| Alamat | Jl. Kaliurang KM 5, Sleman |
| Jam Buka | 08:00 - 22:00 |
| Harga Range | Rp 25.000 - 50.000 |
| Phone | 0812-xxxx-xxxx |
| Website | kopikultur.com |

---

## ☁️ Bisa Dipake di Cloud?

**YA!** Skill ini works di:

| Environment | Status | Notes |
|-------------|--------|-------|
| Local (laptop/PC) | ✅ Works | Best performance |
| VPS (Ubuntu) | ✅ Works | Butuh `playwright install chromium` |
| Cloud Sandbox | ✅ Works | Hermes sandbox |
| Docker | ✅ Works | Butuh chromium di container |

### Install di VPS/Cloud:

```bash
# SSH ke VPS
ssh user@your-vps

# Install Hermes
curl -sSL https://hermes.ai/install | bash

# Install skill
npx skills add bungkust/bungkust-skills --skill google-maps-scraper

# Install dependencies
pip install playwright
python -m playwright install chromium
# Kalau headless butuh extra deps:
sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2

# Test
hermes run "Cari coffee shop di Jogja"
```

---

## ⚠️ Limitasi

- Tanpa login Google: max ~20 results per search
- Rate limit: jangan scrape terlalu cepat (delay 2-3 detik antar request)
- Data bisa berubah sewaktu-waktu (Google update struktur)
- Beberapa lokasi mungkin gak lengkap data-nya

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `playwright not found` | `pip install playwright && python -m playwright install chromium` |
| `chromium failed to launch` | `sudo apt install libnss3 libatk-bridge2.0-0 libdrm2` |
| `timeout` | Google Maps loading lambat, coba tambah timeout |
| `no results` | Coba query yang lebih spesifik |

---

## 💬 Cara Share

Kasih link ini ke orang yang mau pake:

```
https://github.com/bungkust/bungkust-skills/blob/main/skills/google-maps-scraper/HOWTO.md
```

Atau reply comment "mau":
```
Nih cara install + pakai: [link HOWTO]
Gratis kok! ⭐
```

---

*Made with ❤️ by @bungkust*
