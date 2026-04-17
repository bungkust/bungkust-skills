---
name: bungkus-eat-token
description: >
  Pantau dan analisis token consumption AI — track berapa token yang dipakai,
  detect waste, estimate theoretical cost, optimize penggunaan. Konsep dari
  CodeBurn. Bisa untuk semua provider (free & paid).
triggers:
  - "cek token"
  - "berapa token yang dipakai"
  - "eat token"
  - "cost report"
  - "token usage"
  - "optimize token"
  - "token consumption"
---

# 🔥 Bungkus Eat Token

Pantau dan analisis token consumption AI. Inspired by [CodeBurn](https://github.com/AgentSeal/codeburn).

## Kenapa track token meskipun gratis?

- Quota harian free tier ada limit
- Context window efficiency — token besar = slow response
- Cost awareness — kalau switch ke model berbayar, tau berapa biayanya
- Waste detection — token terbuang = resource terbuang

## Token Metrics

### Metrics yang WAJIB di-track:

| Metric | Cara Hitung | Target |
|---|---|---|
| **Total tokens** | input + output + cache_read + cache_write + reasoning | - |
| **Input tokens** | Token yang dikirim ke model | Minimalisir dengan prompt caching |
| **Output tokens** | Token yang di-generate model | <500 per response ideal |
| **Cache read** | Token dari cache (hemat!) | >80% dari total input |
| **Cache write** | Token untuk buat cache baru | Minimal setelah warm-up |
| **Reasoning tokens** | Token internal thinking (o3, Claude extended) | Monitor, bisa besar |
| **Token per session** | total_tokens / jumlah_session | Track tren naik/turun |
| **Token per message** | total_tokens / jumlah_message | <2K ideal |
| **Cache hit rate** | cache_read / (input + cache_read + cache_write) | >80% |

### Breakdown format:

```
🔤 Tokens:
   Input:        1.5M    ← yang dikirim ke API
   Output:       146K    ← yang di-generate
   Cache Read:   39.4M   ← dari cache (hemat!)
   Cache Write:  0       ← sudah warm, tidak perlu tulis ulang
   Reasoning:    0       ← model tidak pakai thinking
   ─────────────────────
   Total:        41M     ← total token yang lewat
   Cache hit:    96.4%   ← sangat bagus (>80%)
```

## Waste Detection (CodeBurn style)

| Pattern | Indikasi | Fix |
|---|---|---|
| Output > Input | Model terlalu verbose | Tambah "be concise" di prompt |
| Cache hit < 80% | Prompt/context tidak stabil | Cek system prompt, jangan ubah tiap turn |
| Reasoning tinggi | Model overthinking | Turunkan reasoning effort |
| Token/session naik | Context bengkak | Compress context, hapus history lama |
| Cache write terus | Cache tidak persist | Cek provider caching config |

## Cost Estimation

### Reference pricing (per 1M tokens USD):

| Model | Input | Output | Notes |
|---|---|---|---|
| MiMo / GLM / Qwen | $0 | $0 | Free tier |
| DeepSeek | $0.14 | $0.28 | Murah |
| Claude Haiku | $0.25 | $1.25 | Budget Claude |
| GPT-4o | $2.50 | $10.00 | Mid-range |
| GPT-5/5.4 | $5.00 | $15.00 | Premium |
| Claude Sonnet | $3.00 | $15.00 | Balanced |
| Claude Opus | $15.00 | $75.00 | Top-tier |

### Theoretical Cost

Bahkan model gratis tetap dihitung "berapa jika bayar":
```
🤖 Models:
   xiaomi/mimo-v2-pro: $0.0000 (240x, 0%)
   gpt-5.4: $0.0000 actual · ~$11.69 if paid (6x)
   💡 Theoretical cost if paid: ~$11.69
```

## Activity Classifier

13 kategori dari tool usage pattern:

| Kategori | Trigger |
|---|---|
| Coding | edit, write_file, patch |
| Debugging | fix, debug, error, bug |
| Feature Dev | create, implement, add, build |
| Refactoring | refactor, rename, simplify |
| Testing | test, pytest, vitest |
| Exploration | read_file, search_files, browser |
| Planning | plan, writing-plans, todo |
| Delegation | delegate_task |
| Git Ops | git, commit, push, merge |
| Build/Deploy | deploy, docker, build |
| Communication | send_message, clarify |
| Data/Analysis | execute_code, jupyter |
| General | lainnya |

## Hermes Commands

```bash
# Summary
python3 ~/.hermes/scripts/cost-logger.py           # All-time
python3 ~/.hermes/scripts/cost-logger.py today     # Hari ini
python3 ~/.hermes/scripts/cost-logger.py week      # 7 hari
python3 ~/.hermes/scripts/cost-logger.py month     # 30 hari

# Status (one-liner)
python3 ~/.hermes/scripts/cost-logger.py status

# Optimize scan
python3 ~/.hermes/scripts/cost-logger.py optimize

# Budget
python3 ~/.hermes/scripts/cost-logger.py budget 50     # Set $50/hari
python3 ~/.hermes/scripts/cost-logger.py budget        # Cek budget

# Export
python3 ~/.hermes/scripts/cost-logger.py export csv    # CSV
python3 ~/.hermes/scripts/cost-logger.py report --json # JSON
```

## Script: cost-logger.py

Script companion untuk Hermes. Taruh di `~/.hermes/scripts/cost-logger.py`.

Fitur:
- Activity classifier (13 kategori ala CodeBurn)
- Cache hit rate tracking
- Theoretical cost estimate (jika model tidak gratis)
- Token breakdown per model/source/session
- Budget alerts
- JSON/CSV export

## Code Burn Analysis (repo check)

Untuk cek code burn sebelum implementasi:

```bash
# Structure scan
find . -name "*.py" | xargs wc -l | tail -1
find . -name "*.js" | xargs wc -l | tail -1
tree -L 3 --dirsfirst -I 'node_modules|.git|__pycache__|venv'

# Dependencies
cat requirements.txt
cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('dependencies',{}), indent=2))"

# Security scan
grep -rn "password\|secret\|api_key" --include="*.py" --include="*.js"
grep -rn "eval\|exec\|os.system" --include="*.py" --include="*.js"
```

## Output Format

```
## Token Analysis: [project]

### Overview
- Sessions: [X]
- Messages: [X]
- Tools: [X]

### Token Consumption
- Input: [X]M
- Output: [X]K
- Cache hit: [X]%
- Theoretical cost: ~$[X]

### Activities
- Coding: [X]%
- Exploration: [X]%
- ...

### Risks
- 🔴 [blocker]
- 🟡 [medium]
- 🟢 [low]
```

## Pitfalls

- Token consumption ≠ cost (free models = $0 tapi token tetap terpakai)
- Cache hit rate target >80% (CodeBurn standard)
- Jangan cuma cek cost, cek token breakdown
- Reasoning tokens bisa besar tanpa disadari
- Session panjang = context bengkak = token boros
