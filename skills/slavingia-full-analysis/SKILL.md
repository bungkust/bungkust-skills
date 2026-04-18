---
name: slavingia-full-analysis
description: >
  Run ALL 10 Slavingia business skills in sequence for comprehensive business analysis.
  Covers: idea validation, community, MVP, customers, pricing, marketing, process,
  review, growth, values. Use when user wants full business analysis, "analisis semua",
  "cek semua", or "full review" of a product/business idea.
---

# 🚀 Slavingia Full Business Analysis

Run all 10 Slavingia skills in one go. Output consolidated report.

## Trigger

"analisis bisnis [product/idea]"
"full review [product]"
"cek semua slavingia"
"analisis semua"

## Skills Sequence

Load and run each skill in order:

### Phase 1: Foundation
1. **validate-idea** — Is this idea worth pursuing?
2. **find-community** — Where are the potential customers?
3. **company-values** — What do we stand for?

### Phase 4: Build
4. **mvp** — How to build the minimum viable product?
5. **processize** — Turn idea into manual-first process

### Phase 3: Go-to-Market
6. **first-customers** — Strategy for first 100 customers
7. **pricing** — How much to charge?
8. **marketing-plan** — How to reach customers?

### Phase 4: Review & Scale
9. **minimalist-review** — Gut-check the whole plan
10. **grow-sustainably** — Is this sustainable?

## Output Format

Consolidated report in this structure:

```markdown
# 📊 Full Business Analysis: [Product Name]

## 🟢 GO / 🟡 PIVOT / 🔴 NO-GO

### 1. Idea Validation
[Summary from validate-idea]

### 2. Target Community
[Summary from find-community]

### 3. Company Values
[Summary from company-values]

### 4. MVP Plan
[Summary from mvp]

### 5. Process
[Summary from processize]

### 6. First 100 Customers
[Summary from first-customers]

### 7. Pricing
[Summary from pricing]

### 8. Marketing Plan
[Summary from marketing-plan]

### 9. Review
[Summary from minimalist-review]

### 10. Growth Assessment
[Summary from grow-sustainably]

## 📋 Action Items
- [ ] Priority 1
- [ ] Priority 2
- [ ] Priority 3
```

## Execution

For each phase:
1. Load the skill with `skill_view(name)`
2. Apply to the product/idea context
3. Extract key findings (3-5 bullet points max per skill)
4. Move to next skill

Total output target: 1-2 pages max (summarized, not verbose).

## Pitfalls

- Don't repeat analysis across skills — each builds on previous
- Keep summaries SHORT (3-5 bullets each)
- Final GO/NO-GO must be clear and justified
- Focus on ACTION items, not theory
