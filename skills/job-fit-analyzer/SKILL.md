---
name: job-fit-analyzer
description: "Analisis kecocokan CV dengan job description. Trigger: 'job fit', 'cocok gak sama CV', 'skill gap', 'evaluasi lowongan'"
---

# 🎯 Job Fit Analyzer

Hitung persentase kecocokan antara CV/profile dengan job description. Bantu tau skill apa yang kurang.

## Cara Pakai

```
"Evaluasi lowongan ini sama CV gw: [paste JD]"
"Cek job fit CV gw sama posisi QA Lead di Tokopedia"
"Skill apa yang kurang dari CV gw buat apply di sini?"
```

## Scoring System

| Component | Weight | Yang Diukur |
|-----------|--------|-------------|
| Skills Match | 40% | Hard skills overlap |
| Tools/Tech Match | 25% | Tools yang dipakai |
| Level Match | 15% | Seniority alignment |
| Keyword Overlap | 10% | General keyword matching |
| Soft Skills | 10% | Communication, leadership |

## Match Tiers

- 🔥 80%+ → STRONG MATCH — langsung apply!
- ✅ 65-79% → GOOD MATCH — fokus cover gaps
- ⚠️ 50-64% → DECENT — worth kalau tertarik
- ❌ <50% → WEAK — upskill dulu

## Output

- Overall match percentage
- Breakdown per kategori
- Skills yang DIMILIKI
- Skills yang KURANG (prioritize ini!)
- Rekomendasi: APPLY / SKIP

## Setup

Butuh file `cv.md` dan `config/profile.yml` di working directory.

---
*Made with ❤️ by @bungkust*
