---
name: social-media-analyzer
description: >
  All-in-one social media analysis: audit accounts, extract insights, develop content strategy.
  Covers Threads, Instagram, TikTok. Trigger: "bedah akun", "analisis akun", "audit profile",
  "belajar dari akun", "develop content series", "plan konten".
category: social-media
---

# 📊 Social Media Analyzer

Unified skill: audit + learn + strategy. One skill, any platform.

## Trigger

- "bedah akun @username"
- "analisis akun [platform]"
- "belajar dari @username"
- "develop content series"
- "plan konten untuk @username"
- "audit profile [link]"

## Flow (Optimized — 3 Steps)

```
User: "bedah akun @username"
         │
         ▼
    Step 1: SCRAPE (1 call)
         │
         ▼
    Step 2: ANALYZE (inline, no extra calls)
         │
         ▼
    Step 3: OUTPUT (structured report)
```

## Step 1: Scrape (1 tool call)

### Threads (Primary)
```bash
cd ~/threads-scraper && source venv/bin/activate
python3 src/scraper.py -u USERNAME --limit 50
```
Output: `~/threads-scraper/output/threads_YYYYMMDD_HHMMSS.json`

### Instagram (Fallback)
```bash
curl -s -L \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -H "X-IG-App-ID: 936619743392459" \
  "https://www.instagram.com/api/v1/users/web_profile_info/?username=USERNAME"
```

### Browser (Last Resort)
```
browser_navigate(url="threads.com/@username")
browser_snapshot(full=true)
browser_vision(question="Analyze profile and visible posts")
```

## Step 2: Analyze (All Inline)

From scraped JSON, compute ALL metrics in ONE execute_code block:

```python
import json
from collections import Counter
from datetime import datetime

with open("path/to/scraped.json") as f:
    posts = json.load(f)

# === ENGAGEMENT STATS ===
likes = [p.get('like_count', 0) for p in posts]
replies = [p.get('reply_count', 0) for p in posts]
# Report: avg, max, min, total

# === POSTING FREQUENCY ===
dates = sorted([p['created_at'] for p in posts])
# Calculate: posts/day, avg gap, max gap, day distribution

# === CONTENT THEMES ===
# Categorize posts by keywords
# Compare engagement BY THEME (most actionable insight!)

# === STYLE PATTERNS ===
# Count: emoji %, hashtag %, question %, CTA %, link %

# === CONTENT LENGTH ===
lengths = [len(p.get('text', '')) for p in posts]
# avg, max, min

# === VIRAL OUTLIERS ===
threshold = sum(likes) / len(likes) * 3  # 3x average
viral = [p for p in posts if p.get('like_count', 0) > threshold]
```

## Step 3: Output (Choose Mode)

### Mode A: AUDIT (default — "bedah akun")
```markdown
## 🔍 AUDIT: @{username}

### 📊 SNAPSHOT
| Metric | Value |
|--------|-------|
| Followers | X |
| Posts analyzed | X |
| Avg engagement | X |
| Top content type | X |

### 📈 ENGAGEMENT (Full Breakdown)
| Metric | Avg | Max | Best Post |
|--------|-----|-----|-----------|
| Likes | X | X | [topic] |
| Replies | X | X | [topic] |

### 📅 POSTING PATTERNS
| Metric | Value |
|--------|-------|
| Frequency | X posts/week |
| Best day | [day] |
| Biggest gap | X days |

### 🎯 CONTENT THAT WORKS
| Theme | Posts | Avg Likes | Win Rate |
|-------|-------|-----------|----------|
| [theme1] | X | X | X% |

### ✅ STRENGTHS
### ⚠️ IMPROVEMENTS
### 🎯 TOP 3 PRIORITIES
```

### Mode B: LEARN ("belajar dari @username")
```markdown
## 📖 BELAJAR: @{username} tentang [TOPIK]

### 🔑 PRINSIP UTAMA
[1 kalimat prinsip besar]

### 📘 Pelajaran 1: "[Judul]"
> Quote asli
**Ilmunya:** [poin]
**Praktek:** [action item]

### 📘 Pelajaran 2: ...

### 🎯 RINGKASAN: N Langkah
[Tabel actionable steps]
```

### Mode C: CONTENT STRATEGY ("develop content series")
```markdown
## 🎯 CONTENT SERIES: [Nama Series]

### COMPARISON
| Element | Reference | Your Style | Adaptation |
|---------|-----------|------------|------------|
| Tone | X | Y | Z |

### SERIES FORMAT
- Structure: [thread/single]
- Cadence: [frequency]
- Hashtags: [list]

### READINESS CHECK
| Item | Status |
|------|--------|
| Materials ready | ✅/❌ |
| Visual content | ✅/❌ |
| Bio aligned | ✅/❌ |

### BATCH POSTS (3-5)
[Generated posts in approved format]
```

## Multi-Account Rule

If user has multiple accounts:
1. VERIFIKASI dulu akun mana
2. Simpan per akun di memory
3. JANGAN ketuker

## Pitfalls

- **Scraper first, browser last** — scraper = 50+ posts, browser = ~8
- **Engagement by THEME** = most actionable insight, always include
- **Cookie may expire** — if scraper fails, refresh from browser
- **Quote asli** when learning — don't paraphrase away context
- **Keep style unique** — don't force user to change their voice
- **3 cafes per post** for food list (500 char Threads limit)
