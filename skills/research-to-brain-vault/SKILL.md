---
name: research-to-brain-vault
description: >
  Auto-route research results to Brain (summary) + Obsidian Vault (deep dive).
  Trigger: "research", "riset", "cek repo", "deep dive", "analisis [thing]"
---

# 🔬 Research → Brain + Vault

Automatic dual-output: summary to Brain, deep dive to Obsidian.

## Trigger

- "research [topic/repo]"
- "riset [topic]"
- "cek repo [url]"
- "deep dive [thing]"
- "analisis [thing]"

## Flow

```
User: "research X"
         │
         ▼
    1. Research (web, GitHub, API)
         │
         ▼
    2. Extract key facts
         │
    ┌────┴────┐
    ▼         ▼
  🧠 Brain  📒 Obsidian
  summary   deep dive
```

## Steps

### 1. Research

Do the actual research:
- GitHub repo? → API: stars, forks, language, license, issues, commits, contributors
- Website/tool? → web_search, browser
- Topic? → web_search + arxiv

### 2. Extract Brain Summary

Write to `/tmp/brain-research.json`:

```json
[
  {
    "title": "Name",
    "category": "projects",
    "content": "## Overview\n[1 line]\n\n- Repo/URL\n- Stars/language/status\n- Tech stack (1 line)\n- Fit untuk kita: TIER 1/2/3 + reason\n- Notes: [key point]",
    "tags": ["research", "tool-name"]
  }
]
```

Rules:
- MAX 10 baris
- Include: apa ini, stars, tech, fit kita, status
- Exclude: detail pipeline, full README, code samples
- Category: `projects` kalau tool/repo, `config` kalau API/service, `notes` kalau konsep

### 3. Write Obsidian Deep Dive (optional)

Only if research is substantial. Write to `/tmp/obsidian-research.json`:

```json
[
  {
    "title": "🔬 Deep Dive: Name",
    "category": "research",
    "path": "30-Resources/Research/[Name].md",
    "content": "Full analysis with:\n- Overview\n- Tech stack detail\n- Architecture/pipeline\n- Strengths & weaknesses\n- Fit untuk Hermes/Kulino\n- Implementation notes\n- Sources",
    "tags": ["research", "deep-dive"]
  }
]
```

Skip this step if:
- Research is simple (just a link/info)
- User only wants summary
- Not substantial enough

### 4. Route

```bash
# Brain (always)
python3 /root/gbrain/scripts/wiki-route.py \
  --target brain \
  --source "Research" \
  --pages /tmp/brain-research.json

# Obsidian (if deep dive exists)
python3 /root/gbrain/scripts/wiki-route.py \
  --target obsidian \
  --source "Research" \
  --pages /tmp/obsidian-research.json
```

### 5. Report

```
✅ Research saved:
🧠 Brain: [title] — summary (X lines)
📒 Obsidian: [title] — deep dive (X lines)
```

## Quick Mode (skip deep dive)

User: "research X, singkat aja"
→ Brain only, no Obsidian

User: "research X, detail"
→ Brain + Obsidian

## Pitfalls

- Brain summary HARUS singkat (< 1KB)
- Jangan duplikat full content ke Brain
- Deep dive only kalau substantial
- Always route brain FIRST, obsidian SECOND
- Clean /tmp files after routing
