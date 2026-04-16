---
name: badminton-slot-checker
description: "Cek jadwal dan slot kosong lapangan badminton. Trigger: 'jadwal badminton', 'slot kosong', 'booking badminton'"
---

# 🏸 Badminton Slot Checker

Cek jadwal dan slot kosong lapangan badminton dari website GOR.

## Cara Pakai

```
"Cek jadwal badminton GOR DS hari Jumat"
"Slot kosong lapangan badminton jam 7 malam"
"Mau booking badminton besok, cek yang kosong"
```

## Output Format

| Line | Jam 19-20 | Jam 20-21 | Jam 21-22 |
|------|-----------|-----------|-----------|
| Line 1 | KOSONG | KOSONG | KOSONG |
| Line 2 | KOSONG | KOSONG | KOSONG |
| Line 3 | KOSONG | KOSONG | KOSONG |

## Supported GOR

- GOR DS (Sleman, Jogja)
- Bisa ditambah GOR lain kalau ada website-nya

## Teknis

Scrape website jadwal GOR, parse data, tampilkan slot yang kosong.

---
*Made with ❤️ by @bungkust*
