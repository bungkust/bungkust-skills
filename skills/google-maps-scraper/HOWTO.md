# 🗺️ Google Maps Scraper — HOWTO

Cara install dan pakai skill + dashboard plugin untuk scrape Google Maps.

---

## 🎯 Yang Didapat

1. **Dashboard Plugin** — tab GMaps Scraper di Hermes dashboard (UI table + export CSV)
2. **AI Skill** — chat ke AI agent untuk scrape via perintah natural

---

## 📋 Prerequisites

- Python 3.10+
- pip
- Hermes Agent sudah terinstall

---

## 🚀 Install

### Step 1: Clone Repo

```bash
git clone https://github.com/bungkust/bungkust-skills.git ~/bungkust-skills
```

### Step 2: Setup Dashboard Plugin

Dashboard plugin perlu kamu copy manual ke folder plugin Hermes:

```bash
# Copy plugin files
PLUGIN_SRC="~/bungkust-skills/skills/google-maps-scraper/plugin"
PLUGIN_DST="~/.hermes/hermes-agent/plugins/google-maps-scraper-dashboard"

mkdir -p "$PLUGIN_DST/dashboard"
cp "$PLUGIN_SRC/manifest.json" "$PLUGIN_DST/dashboard/"
cp "$PLUGIN_SRC/plugin_api.py" "$PLUGIN_DST/dashboard/"
mkdir -p "$PLUGIN_DST/dashboard/dist"
cp "$PLUGIN_SRC/dist/index.js" "$PLUGIN_DST/dashboard/dist/"
```

### Step 3: Setup Scraper Directory

Scraper core perlu ada di `/root/google-maps-scraper/`:

```bash
SCRAPER_SRC="~/bungkust-skills/skills/google-maps-scraper/gmaps_scraper.py"
SCRAPER_DST="/root/google-maps-scraper"

sudo mkdir -p "$SCRAPER_DST"
sudo cp "$SCRAPER_SRC" "$SCRAPER_DST/gmaps_scraper.py"
sudo mkdir -p "$SCRAPER_DST/output"
sudo chmod 755 "$SCRAPER_DST/gmaps_scraper.py"
```

### Step 4: Install Dependencies

```bash
pip install playwright
python -m playwright install chromium
```

VPS/headless server butuh extra deps:
```bash
sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2
```

### Step 5: Restart Hermes

```bash
# Restart hermes-gateway untuk load plugin baru
sudo systemctl restart hermes-gateway

# Atau kalau pakai hermes langsung:
hermes restart
```

### Step 6: Verify

Buka Hermes dashboard →你应该 lihat tab **GMaps Scraper** di sebelah kanan tab Skills.

---

## 🎯 Cara Pakai

### Via Dashboard Plugin

1. Buka Hermes dashboard → tab **GMaps Scraper**
2. Isi query (e.g. "coffee shop") dan daerah (e.g. "Yogyakarta")
3. Klik **🔍 Mulai Search**
4. Tunggu hasil → table view dengan rating, reviews, address
5. Klik **📥 Export CSV** untuk download

### Via AI Chat

```
"Cari coffee shop di Jogja dari Google Maps"
"Scrape restoran di Jakarta Selatan rating >4.5"
"Tempat wisata di Bali yang buka 24 jam"
```

---

## 📊 Output

Hasil scrape:

| Field | Contoh |
|-------|--------|
| Name | Kopi Kultur |
| Rating | 4.8 ⭐ |
| Reviews | 1234 |
| Category | Kedai Kopi |
| Price_range | Rp 25–50 rb |
| Address | Jl. Kaliurang KM 5, Sleman |
| Phone | 0812-xxxx-xxxx |
| Hours | Buka · Tutup pukul 22.00 |

---

## ⚠️ Limitasi

- Tanpa login Google: max ~20 results per search
- Rate limit: jangan scrape terlalu cepat (delay 1.5s)
- Google Maps struktur bisa berubah sewaktu-waktu
- CSS selectors mungkin perlu update periodik

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `playwright not found` | `pip install playwright && python -m playwright install chromium` |
| `chromium failed to launch` | `sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2` |
| Tab GMaps Scraper gak muncul | Restart hermes-gateway, cek `~/.hermes/hermes-agent/plugins/` |
| Timeout | Google Maps lambat — normal untuk first run |
| No results | Query terlalu umum — coba lebih spesifik |

---

## 📁 File Structure

```
~/.hermes/hermes-agent/plugins/google-maps-scraper-dashboard/
└── dashboard/
    ├── manifest.json      ← plugin definition
    ├── plugin_api.py      ← FastAPI backend (/api/plugins/google-maps-scraper/)
    └── dist/
        └── index.js       ← React UI (table + CSV export)

/root/google-maps-scraper/
├── gmaps_scraper.py       ← Playwright scraper core
└── output/                 ← cached results (JSON + CSV)
```

---

## 🔄 Update

```bash
cd ~/bungkust-skills && git pull

# Copy ulang plugin files
PLUGIN_SRC="~/bungkust-skills/skills/google-maps-scraper/plugin"
cp -r "$PLUGIN_SRC/"* "~/.hermes/hermes-agent/plugins/google-maps-scraper-dashboard/dashboard/"

# Restart
sudo systemctl restart hermes-gateway
```

---

*Made with ❤️ by @bungkust*
