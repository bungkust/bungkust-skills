# 🛠️ bungkust-skills

AI Agent Skills by [@bungkust](https://github.com/bungkust) — tools for daily life, career, and productivity.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📦 Skills

| Skill | Description |
|-------|-------------|
| 🗺️ [google-maps-scraper](skills/google-maps-scraper/) | Scrape lokasi dari Google Maps — coffee shop, restoran, tempat wisata |
| 🎯 [job-fit-analyzer](skills/job-fit-analyzer/) | Analisis kecocokan CV dengan job description |
| 🏸 [badminton-slot-checker](skills/badminton-slot-checker/) | Cek jadwal dan slot kosong lapangan badminton |
| 💰 [cashflow-tracker](skills/cashflow-tracker/) | Catat dan track cash flow harian |

## 🚀 Install

### Via npx (recommended)
```bash
npx skills add bungkust/bungkust-skills
```

### Via Claude Code
```bash
/plugin marketplace add bungkust/bungkust-skills
```

### Manual
```bash
git clone https://github.com/bungkust/bungkust-skills.git
cp -r bungkust-skills/skills/* ~/.hermes/skills/
```

## 🎯 Cara Pakai

Setiap skill punya trigger phrases. Cukup bilang ke AI agent:

> "Cari coffee shop di Jogja dari Google Maps"

Agent akan otomatis detect skill yang tepat dan jalankan.

## 📝 Format Skill

```
skills/
├── google-maps-scraper/
│   └── SKILL.md
├── job-fit-analyzer/
│   └── SKILL.md
├── badminton-slot-checker/
│   └── SKILL.md
└── cashflow-tracker/
    └── SKILL.md
```

Setiap folder berisi `SKILL.md` dengan:
- **Frontmatter**: `name` + `description` (trigger phrases)
- **Content**: Cara pakai, output format, limitations

## 📄 License

MIT — Made with ❤️ by @bungkust
