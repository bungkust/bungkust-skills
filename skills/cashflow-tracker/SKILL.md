---
name: cashflow-tracker
description: "Catat dan track cash flow harian. Trigger: 'catat pengeluaran', 'cashflow', 'berapa habis hari ini'"
---

# 💰 Cash Flow Tracker

Catat pengeluaran/pemasukan harian. Auto hitung total, kategorisasi, dan simpan ke Notion.

## Cara Pakai

```
"Catat: gorengan tahu 8 biji Rp 10.000, bayar cash"
"Pengeluaran hari ini: es kopi Rp 15.000, parkir Rp 2.000"
"Berapa total pengeluaran minggu ini?"
```

## Output Format

| Deskripsi | Qty | Harga | Kategori | Bayar |
|-----------|-----|-------|----------|-------|
| Gorengan Tahu | 8 biji | Rp 10.000 | Jajan | Cash |
| Es Kopi | 1 | Rp 15.000 | Minum | QRIS |

## Features

- Auto kategorisasi (Makan, Minum, Transport, Jajan, dll)
- Simpan ke Notion database
- Export ke CSV
- Weekly/monthly summary

## Setup

Butuh Notion API key dan Cash Flow database ID.

---
*Made with ❤️ by @bungkust*
