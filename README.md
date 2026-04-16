# 🛠️ bungkust-skills

AI Agent Skills by [@bungkust](https://github.com/bungkust) — tools for daily life, career, and productivity.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Spec%20v1-green.svg)](https://agentskills.io/specification)

> 💡 Skills ini bisa dipake di **Hermes Agent**, **Claude Code**, **Codex CLI**, **Cursor**, dan AI agent lain yang support Agent Skills spec.

---

## 📦 Skills

| # | Skill | Description | Trigger |
|---|-------|-------------|---------|
| 🗺️ | [google-maps-scraper](skills/google-maps-scraper/) | Scrape lokasi dari Google Maps — coffee shop, restoran, tempat wisata | "scrape google maps", "cari coffee shop" |
| 🎯 | [job-fit-analyzer](skills/job-fit-analyzer/) | Analisis kecocokan CV dengan job description | "job fit", "skill gap", "evaluasi lowongan" |
| 🏸 | [badminton-slot-checker](skills/badminton-slot-checker/) | Cek jadwal dan slot kosong lapangan badminton | "jadwal badminton", "slot kosong" |
| 💰 | [cashflow-tracker](skills/cashflow-tracker/) | Catat dan track cash flow harian | "catat pengeluaran", "cashflow" |

---

## 🚀 Install

### Via npx (recommended)
```bash
npx skills add bungkust/bungkust-skills
```

### Via Claude Code
```
/plugin marketplace add bungkust/bungkust-skills
```

### Manual
```bash
git clone git@github.com:bungkust/bungkust-skills.git
cp -r bungkust-skills/skills/* ~/.hermes/skills/
```

---

## 🎯 Cara Pakai

Setiap skill punya **trigger phrases**. Cukup bilang ke AI agent:

```
"Cari coffee shop di Jogja dari Google Maps"
```

Agent akan otomatis detect skill yang tepat dan jalankan.

---

## 📁 Struktur

```
bungkust-skills/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── google-maps-scraper/
│   │   └── SKILL.md
│   ├── job-fit-analyzer/
│   │   └── SKILL.md
│   ├── badminton-slot-checker/
│   │   └── SKILL.md
│   └── cashflow-tracker/
│       └── SKILL.md
├── README.md
└── LICENSE
```

---

## 📝 Format Skill

Setiap folder berisi `SKILL.md` dengan:

```yaml
---
name: skill-name
description: "Kapan skill ini dipakai — trigger keywords"
---

# Judul Skill

Content dalam markdown...
```

---

## 🤝 Kontribusi

PR welcome! Kalau mau nambahin skill:
1. Fork repo ini
2. Buat folder di `skills/`
3. Bikin `SKILL.md` dengan frontmatter yang bener
4. Submit PR

---

## 📄 License

MIT — Made with ❤️ by [@bungkust](https://github.com/bungkust)
