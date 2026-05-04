---
name: testcase-creation-guidelines
description: Guidelines for writing clear, consistent test case titles, steps, and structure across BrowserStack and Airtable.
category: data-science
---

# Test Case Creation Guidelines

Rules for creating test cases that are clear, consistent, and testable. Prevents vague/ambiguous titles and ensures proper structure.

## Title Format (MANDATORY — Read Before Creating Any TC)

Every title MUST follow this template:

```
[Action] [Input/Condition] on/in [Target] shows/returns/changes [Expected]
```

**Template breakdown:**
| Part | What to write | Example |
|------|--------------|---------|
| Action | What user does | Creating, Editing, Searching, Filtering, Clicking, Uploading |
| Input/Condition | Exact value or condition | empty Name, "XYZ123", exceeding 255 chars, .pdf file |
| Target | What is being acted upon | competition Name field, Season filter, Delete dialog |
| Expected | What happens | shows validation error, returns 3 competitions, changes status to Inactive |

**Examples of CORRECT titles:**
```
Verify creating competition with empty Name field shows validation error
Verify searching "XYZNone" in competition name shows empty state
Verify filtering by Season "2099/2100" returns no matching competitions
Verify clicking Cancel on Create form discards all entered data and closes form
Verify uploading .pdf file as logo shows file type not supported error
Verify clicking Next on page 1 loads page 2 competitions
```

### Precondition & Expected Result Format

**MANDATORY rule — apply EVERY time before saving:**

Count the NUMBER OF DISTINCT STATEMENTS (each ended by `.`, `?`, or `!`):

| Condition | Format |
|-----------|--------|
| **>1 statement** | Bullet list with `-` prefix |
| **1 statement** | Single sentence (no bullet needed) |

**✅ CORRECT — 2 statements, separate lines:**
```
Precondition:
- Admin is logged in.
- A valid PNG image file is available.
```

**✅ CORRECT — 2 statements in 1 paragraph (but still bullet because >1 statement):**
```
Precondition:
- Admin is logged in.
- A valid PNG image file is available.
```

**✅ CORRECT — 2 statements, single paragraph (no bullet needed):**
```
Precondition: Admin is logged in and a valid PNG image file is available.
```

**❌ WRONG — 2 statements but no bullet:**
```
Expected Result: Club name updated to Edited Club Name. All other fields remain unchanged.
```

**❌ WRONG — multiple items without bullets:**
```
Precondition:
User is logged in as Admin
At least 3 competitions exist in the system

Expected Result:
Competition "ABC" appears in the results
Total count shows "3 competitions"
```

> **Self-check before saving:** How many distinct statements? Count the `.` (periods) — 2+ periods = 2+ statements → use bullets.

**ALWAYS ask yourself before saving a title:**
1. Does it tell me WHAT action is being done?
2. Does it tell me WHAT input/condition is used?
3. Does it tell me WHAT the expected result is?
4. Would a tester who has never seen this feature know exactly what to do just from the title?

## Section Naming Rules (MANDATORY)

Section MUST match the TC ID prefix. Do NOT dump all TCs into one generic section.

### TC ID Prefix → Section Mapping

| Prefix | Section Name |
|--------|-------------|
| NC-, TC-, ES- | `Competition List` |
| CC- | `Create Competition` |
| EC- | `Edit Competition` |
| DC- | `Delete Competition` |
| SC- | `Search Competition` |
| FC- | `Filter Competition` |
| PC- | `Pagination Competition` |

### ❌ WRONG

```
TC ID: CC-004
Section: 01-Competition List   ❌ Wrong — all CC-* dumped into generic section
```

### ✅ CORRECT

```
TC ID: CC-004
Section: Create Competition     ✅ Section matches action being tested
```

### Why This Matters

- Testers can filter by Section to run only the TCs they need
- Coverage reporting by section is accurate
- Easy to spot gaps in a specific feature area

---

## Type & Technique Mapping (MANDATORY)

Every TC MUST have **both** `Type` and `Technique` filled. Use this mapping.

### ⚠️ CRITICAL — Valid Technique Values ONLY

**"UI Testing", "Functional", "Exploratory", " Smoke", "Regression" are NOT valid Technique values for this skill.**

The ONLY valid Technique values are the **8 Black Box Testing techniques** below. Anything else will be rejected during review.

### 8 Black Box Testing Techniques

| # | Technique | Description |
|---|-----------|-------------|
| 1 | `Equivalence Partitioning` | Membagi input jadi partisi valid dan invalid — test satu representative dari tiap partisi |
| 2 | `Boundary Value Analysis` | Menguji nilai batas bawah dan batas atas suatu variabel |
| 3 | `All-Pair Testing` | Menguji seluruh kemungkinan kombinasi dari 2 atau lebih input diskrit |
| 4 | `Decision Table Testing` | Merangkum kombinasi input dalam tabel untuk fungsi dengan hubungan logis |
| 5 | `State Transition Testing` | Menguji perubahan state/output sistem berdasarkan kondisi/peristiwa input |
| 6 | `Cause-Effect Technique` | Menggambarkan hubungan antara penyebab error dan efeknya menggunakan grafik |
| 7 | `Error Guessing` | Identifikasi error berdasarkan pengalaman dan pengetahuan penguji |
| 8 | `Use Case Testing` | Menguji setiap fungsi dari tahap awal hingga akhir (end-to-end) |

### Type → Technique Reference

| Type | Technique | When to Use |
|------|-----------|-------------|
| **Positive** | `Equivalence Partitioning` | Happy path, valid inputs, normal workflows |
| **Positive** | `Use Case Testing` | End-to-end user flow dari awal sampai akhir |
| **Positive** | `All-Pair Testing` | Kombinasi 2+ input diskrit (dropdown, checkbox, radio) |
| **Positive** | `State Transition Testing` | State berubah berdasarkan kondisi (New → Created, Active → Inactive) |
| **Negative** | `Error Guessing` | Invalid inputs, missing required fields, wrong formats, cancel/discard actions |
| **Negative** | `Decision Table Testing` | Kombinasi input logis (match vs mismatch, filled vs empty) |
| **Edge Case** | `Boundary Value Analysis` | Min/max limits, empty boundary, first/last item, overflow |
| **Edge Case** | `Error Guessing` | Edge case berdasarkan pengalaman: special chars, duplicate, very long string |
| **Regression** | `Decision Table Testing` | Complex business logic dengan multiple input combinations |
| **Regression** | `State Transition Testing` | Perubahan state yang harus konsisten di seluruh fitur |

### Quick Decision Tree

```
Is the TC testing at the EDGE of a boundary (min/max/overflow)?
  → YES: Type = Edge Case, Technique = Boundary Value Analysis
  → NO: Is the TC testing INVALID/WRONG input or user error?
        → YES: Type = Negative, Technique = Error Guessing
        → NO: Is the TC an end-to-end user flow?
              → YES: Type = Positive, Technique = Use Case Testing
        → NO: Is the TC testing combinations of 2+ discrete inputs?
              → YES: Type = Positive, Technique = All-Pair Testing
        → NO: Is the TC testing state changes (New/Active/Inactive)?
              → YES: Type = Positive, Technique = State Transition Testing
        → NO: Is the TC a happy-path/valid-input workflow?
              → YES: Type = Positive, Technique = Equivalence Partitioning
```

### Type-Technique Mismatch Examples

| TC Title | Type | Correct Tech | Wrong Tech |
|----------|------|-------------|-----------|
| Empty Name → validation error | Negative | Error Guessing ✅ | Boundary Value ❌ |
| Exceed 255 chars → error | Edge Case | Boundary Value Analysis ✅ | Error Guessing ❌ |
| Password min 8 chars (7 chars fails) | Edge Case | Boundary Value Analysis ✅ | Equivalence Partitioning ❌ |
| Province selected → City enabled | Positive | Cause-Effect ✅ | Decision Table ❌ |
| Valid input → saves | Positive | Equivalence Partitioning ✅ | — |
| Create admin: fill all → success | Positive | Use Case Testing ✅ | Equivalence Partitioning ❌ |
| Cancel create → no admin created | Negative | Error Guessing ✅ | State Transition ❌ |
| Gender × Role all combinations | Positive | All-Pair Testing ✅ | Decision Table ❌ |
| Password match → success, mismatch → error | Negative | Decision Table Testing ✅ | Error Guessing ❌ |
| Empty Season → saves blank | Positive | Equivalence Partitioning ✅ | Boundary Value ❌ |

## Title Rules

### Format
```
Verify [WHAT] [CONDITION/CONTEXT]
```

### ✅ DO
- Start with **"Verify"**
- Specify the **exact feature/element** being tested
- Include the **expected behavior** when it adds clarity
- Use English consistently (no Indo-Inggris mix)
- Keep under 60 characters when possible

### ❌ DON'T — Vague Titles

Every title MUST answer: **"Who does what to what, and what happens?"**

- **"Verify Search"** alone — search apa? kolom apa? input apa?
- **"Verify Filter"** alone — filter apa? hasil apa?
- **"Verify Empty State"** alone — halaman apa? aksi apa yang menyebabkan?
- **"Verify Cancel"** alone — cancel apa? form create? form edit?
- **"gracefully"** — not testable, specify exact outcome
- **"resets"** without object — what resets? specify what
- Compound with colon unless it's a feature name: `Verify X: Y with Z` → split or simplify
- No input value in title for search/filter/input tests
- No expected outcome in title (that's what Expected Result is for)

### ✅ Title = [Action] + [Input/Condition] + [Target/Context] + [Expected Behavior]

```
Verify searching "XYZ" in competition name shows empty state
Verify filtering Season "2099/2100" returns no matching competitions
Verify creating competition with empty Name shows validation error
Verify clicking Cancel on Create Competition form discards data and closes form
Verify editing competition Active status to unchecked changes status to Inactive
Verify uploading .exe file as logo shows file type error
```

### ❌ → ✅ Title Fixes

| ❌ Bad | ✅ Good | Why |
|-------|--------|-----|
| Verify Search — No Results | Verify searching with non-existent name shows empty state | Specify input + outcome |
| Verify Filter Season | Verify filtering by Season "2025/2026" returns matching competitions | Specify filter value |
| Verify Empty Name | Verify creating competition with empty Name shows error | Specify condition |
| Verify Cancel | Verify Cancel on Create form closes form without saving | Specify where + what |
| Verify Edit Logo | Verify uploading new logo on Edit form updates competition logo | Specify what changed |
| Verify Pagination | Verify clicking Next on page 1 loads page 2 competitions | Specify action + result |
| Verify Delete | Verify confirming Delete competition removes it from table | Specify what deleted |

### ✅ Examples

| ❌ Bad | ✅ Good |
|--------|---------|
| Verify app behavior when survey unpublished mid-session | Verify survey shows removed error when unpublished mid-session |
| Verify exit on last question also resets | Verify exit on last question (before submit) resets survey progress |
| Verify app handles survey with no questions gracefully | Verify empty state shown when survey has no questions |
| Verify completion modal shows 0 poin | Verify completion modal shows 0 points |
| Verify exiting and re-entering resets to blank | Verify exiting and re-entering survey clears all previous answers |

## Steps Rules

### ✅ Recommended Format (BrowserStack Native)

Use this format — it renders natively in BrowserStack UI as separate Step + Result fields:

```
Step 01
[Tulis aksi yang jelas dan single-purpose di sini]

Result
[Tulis observable outcome — apa yang tester SEE setelah step ini]
```

```
Step 01
Open Media > Latest tab

Result
Latest articles list is displayed

Step 02
Scroll to a mid-list article

Result
Article thumbnail and title become visible in viewport

Step 03
Tap on the article

Result
Article detail page opens with full content

Step 04
Press back button

Result
Returns to the Latest tab with previous scroll position preserved
```

### Format Rules

| Rule | Why |
|------|-----|
| **No "Step 01" prefix inside the step** — write action directly after label | BrowserStack UI renders label "Step 01" separately from the action text |
| **Result per step** — every step has its own Result | Makes verification traceable, not lumped at the end |
| **One action per step** | Each step must be independently reproducible |
| **Result = observable outcome** | What tester sees/verifies after this action — NOT a repeat of the action |
| **Verification is NOT a separate step** | "Check X" is a verification → put it as Result of the action step that triggers X |
| **Declarative language** | Use "is displayed", "changes to", "navigates to" — NOT "should show", "will be" |

### ❌ WRONG Patterns

**Redundant step + result (result just repeats the action):**
```
Step 01
Tap Bayar to proceed to payment gateway

Result
Session is finalized when user is redirected to payment gateway  ← repeats action
```

**"Check X" as a separate step (verification should be Result):**
```
Step 01
Tap Bayar to proceed to payment gateway

Result
User is redirected to payment gateway page

Step 02
Check session status  ← this is verification, not a new action

Result
Session status changes to "Finalized"
```

**Duplicate results (two steps with identical results):**
```
Step 01
Tap Bayar button

Result
User is redirected to payment gateway

Step 02
Check session status  ← no new action, same result → suspicious

Result
User is redirected to payment gateway  ← identical to Step 01
```

### ✅ Correct Pattern

An action step → its Result. Verification belongs in the Result of the step that triggers it:

```
Step 01
Tap Bayar button to proceed to payment gateway

Result
User is redirected to external payment gateway page

Step 02
Complete payment on payment gateway

Result
Payment confirmation is received and order status changes to "Paid"

Step 03
Return to app and navigate to Order History

Result
Order appears in history with status "Paid" and correct amount
```

### Old Format (Airtable / Numbered List)

If creating TCs in Airtable (where Result is a single field for all steps), use numbered list format:

```
1. Open Media > Latest tab
2. Scroll to a mid-list article
3. Tap on the article
4. Press back button

Expected Result: Returns to Latest tab with previous scroll position preserved
```

> Note: In Airtable, verification is lumped into Expected Result since there's no per-step Result field. BrowserStack is preferred because it supports per-step Results.

## Expected Result Rules

> For BrowserStack TCs: put expected results **per step** in each step's Result field (see Steps Rules above). This section applies to Airtable TCs where Expected Result is a single shared field, or to BS TCs where verification needs to be summarized.

- Describe **what tester should see**, not what they did
- Be specific: names, values, UI elements
- Include negative case: "no crash", "no error", "no duplicate"
- Use declarative language: "is displayed", "changes to", "navigates to" — NOT "should show", "will be"
- If >1 distinct statement, use bullet list (see Precondition/Result format rules above)

### ✅ CORRECT
```
Expected Result: Returns to exact previous scroll position in the list
Expected Result: Validation error message "Email is required" is displayed; no form data is submitted
```

### ❌ WRONG
```
❌ Should show the list (too vague)
❌ Will navigate back (not declarative)
```

## Field Mapping (Airtable — Survey App)

| Field | Type | Purpose |
|-------|------|---------|
| TC ID | text | Unique identifier with action prefix (e.g., CC-001, EC-001) — **prefix determines Section** |
| Title | text | Clear test case name — follow Title Format above |
| **Section** | text | **Must match TC ID prefix: `Competition List`, `Create Competition`, `Edit Competition`, `Delete Competition`, `Search Competition`, `Filter Competition`, `Pagination Competition`** |
| Priority | singleSelect | Critical / High / Medium / Low |
| **Type** | singleSelect | **Positive / Negative / Edge Case / Regression** (Smoke not used — map to Functional for BS) |
| **Technique** | text | **Black-box testing technique — MUST match Type (see Type & Technique Mapping above)** |
| Precondition | multilineText | Setup requirements — use bullet list if >1 item |
| Steps | multilineText | Numbered action list — one action per step |
| Expected Result | multilineText | What should happen — use bullet list if >1 item |
| Status | singleSelect | Untested / Pass / Failed |

## Field Mapping (BrowserStack — Test Management)

| Field | Purpose |
|-------|---------|
| `identifier` | TC-XX or TC-XXXX (e.g. `TC-3057`) |
| `name` | Test case name (NOT `title`) — required on CREATE |
| `case_type` | See valid values below |
| `priority` | High / Medium / Low (case-insensitive) |
| `test_case_steps` | Array of `{step, result}` objects on CREATE/PATCH |
| `steps` | Array of `{step, result}` — returned in GET responses |
| `preconditions` | Setup requirements |
| `custom_fields.Section` | Feature group (PATCH only, not on CREATE) |

### Valid case_type Values (Verified April 2026)

All of these work — no 400 errors:

| Value | Use for |
|-------|---------|
| `Positive flows` | Positive test flows ✅ |
| `Negative flows` | Negative test flows ✅ |
| `Functional` | General functional tests ✅ |
| `Regression` | Regression tests ✅ |
| `Edge cases` | Edge case tests ✅ |
| `Others` | Other test types ✅ |
| `Smoke` | Smoke tests ✅ |
| `Other` | Misc ✅ |
| `Accessibility` | Accessibility tests ✅ |

> ⚠️ `Positive - EP` is NOT a valid case_type — use `Positive flows` instead.

```python
# PR-7: "Smoke" is rejected by BrowserStack API — use "Functional" instead
type_map = {
    "Positive": "Positive flows",
    "Negative": "Negative flows",
    "Edge Case": "Edge cases",
    "Boundary": "Functional",
    "Smoke": "Functional",   # NOTE: "Smoke" causes 400 error on PR-7 — use "Functional"
    "Regression": "Regression",
    "Accessibility": "Accessibility",
}
```

### Valid Priority Values

```python
priority_map = {
    "Critical": "High",   # No "Critical" in BS — map to "High"
    "High": "High",
    "Medium": "Medium",
    "Low": "Low"
}
```
Note: Priority is case-insensitive — `High`, `high`, `HIGH` all work.

## Coverage Rules — Field-Level Testing

Every form/input field MUST be tested across these dimensions. When creating TCs for any feature with forms, use this checklist to ensure 100% coverage.

### Field Test Matrix

For each field in a form, test ALL of these:

| Dimension | What to Test |
|-----------|--------------|
| **Mandatory** | Empty → validation error shown |
| **Optional** | Empty → saves successfully |
| **Valid input** | Normal valid value → saves correctly |
| **Format/Pattern** | Valid format accepted, invalid rejected |
| **Character limit — valid** | Boundary value (e.g., 255 chars) accepted |
| **Character limit — exceed** | Exceed limit → error or truncated |
| **Special characters** | Symbols/emoji preserved or rejected correctly |
| **Duplicate** | Duplicate value → error or warning |
| **Whitespace** | Leading/trailing/multi spaces handled correctly |

### Optional vs Mandatory — Required TCs

**Mandatory fields:**
- Empty → Error (Negative TC)
- Valid input → Success (Positive TC)
- Max char limit → handled correctly (Boundary TC)

**Optional fields:**
- Empty → Success (Positive TC)
- Valid input → saved correctly (Positive TC)
- Invalid input → Error (Negative TC)

### Action-Level Coverage

Every user action (Create, Edit, Delete, Search, Filter, etc.) needs these TC types:

| Action | Required TCs |
|--------|-------------|
| **Create** | ✅ Mandatory empty, ✅ All fields filled, ✅ Optional empty, ✅ Invalid input, ✅ Duplicate name, ✅ Char limit boundary, ✅ Cancel discards |
| **Edit** | ✅ Pre-filled form correct, ✅ Edit each field individually, ✅ All fields changed, ✅ Mandatory empty → error, ✅ Cancel discards changes |
| **Delete** | ✅ Confirm → removed, ✅ Cancel → preserved, ✅ Last item → empty state |
| **Search** | ✅ Exact match, ✅ Partial match, ✅ No results, ✅ Clear restores list |
| **Filter** | ✅ Exact match, ✅ No match (empty state), ✅ Clear resets |
| **Pagination** | ✅ Next/Prev navigation, ✅ Boundary states (1st/last page disabled) |

### Duplicate TC Prevention

Before creating a new TC, check existing ones:
1. Same action + same field + same condition → SKIP (already covered)
2. Same action + different field → CREATE (new coverage)
3. Same action + same field + different condition → CREATE (different dimension)

### Example — Full Field Coverage for "Name" Field

Given a form with: `Name` (mandatory, max 255 chars), `Season` (optional), `Description` (optional), `Logo` (optional), `Active` (checkbox, default checked)

```
CREATE FORM — Name field coverage:
✅ Creating competition with empty Name shows validation error        [Negative / Error Guessing]
✅ Creating competition with 255-char Name saves successfully          [Positive / Equivalence Partitioning]
✅ Creating competition with Name exceeding 255 chars shows error       [Edge Case / Boundary Value Analysis]
✅ Creating competition with duplicate Name shows error                [Negative / Error Guessing]
✅ Creating competition with Name containing special chars shows error [Negative / Error Guessing]

CREATE FORM — Season field coverage:
✅ Creating competition with empty Season saves successfully           [Positive / Equivalence Partitioning]
✅ Creating competition with Season "2025/2026" saves correctly        [Positive / Equivalence Partitioning]

CREATE FORM — Logo field coverage:
✅ Uploading valid PNG as competition logo saves correctly             [Positive / Equivalence Partitioning]
✅ Uploading .pdf file as logo shows file type error                   [Negative / Error Guessing]
✅ Uploading image exceeding 10MB shows size error                      [Edge Case / Boundary Value Analysis]

CREATE FORM — Active checkbox:
✅ Unchecking Active checkbox on Create creates competition as Inactive [Positive / Equivalence Partitioning]
✅ Clicking Cancel on Create form discards data and returns to list     [Negative / Error Guessing]
```

## Related Skills

| Skill | Purpose |
|-------|---------|
| `airtable-to-browserstack` | Push TC from Airtable → BrowserStack |
| `browserstack-to-airtable` | Sync execution results back to Airtable |
| `browserstack-testcase-update` | Update/delete/move TCs in BrowserStack |

## Create TC in Airtable (API Script)

Use this to create new TC records directly via Airtable API. Follow guidelines above before creating.

### Pre-Save QA Checklist

Before saving ANY test case, verify ALL of these:

- [ ] **Title**: follows `[Action] [Input/Condition] on [Target] shows [Expected]` — no technique prefix like "EP -", "BVT -"
- [ ] **Section**: clean name only — `List`, `Create Form`, `Edit Form`, `Delete` — no technique suffix like "- EP"
- [ ] **Type + Technique**: Type AND Technique are both set, AND they match the mapping above
- [ ] **Technique**: MUST be one of the 8 Black Box Testing techniques — NOT "UI Testing", NOT "Functional", NOT "Smoke", NOT "Regression", NOT "Exploratory"
- [ ] **Precondition**: specific test data (e.g., "Admin 'Coba City' with email 'cobacity@psb.com' exists"), NOT vague (e.g., "admin exists")
- [ ] **Expected Result**: observable UI result (e.g., "validation error message 'Email is required' is displayed"), NOT action description (e.g., "shows validation error")
- [ ] **Steps**: numbered list, one action per step
- [ ] **Priority**: always set
- [ ] **Status**: always set (default: Ready)
- [ ] **No duplicate**: same Title doesn't already exist in the table
- [ ] **Section consistent**: TC about Create → Section=`Create Form`, not dumped into generic section

```python
import urllib.request, urllib.parse, json

with open("/root/.hermes/secrets/airtable.env") as f:
    for line in f:
        if "AIRTABLE_TOKEN=" in line:
            at_token = line.split("=", 1)[1].strip()

base_id = "{{AT_BASE_ID}}"
table_id = "tblXXXXXXXX"  # from Airtable URL
at_headers = {"Authorization": f"Bearer {at_token}", "Accept": "application/json", "Content-Type": "application/json"}

# === TC DATA — follow guidelines above ===
# Title: "Verify [WHAT] [CONDITION]"
# Steps: numbered list, one action per step
# Expected Result: declarative, specific, no "should show"
tc_data = {
    "records": [{
        "fields": {
            "TC ID": "TC-APP-001",
            "Title": "Verify [WHAT] [CONDITION]",        # follow title format
            "Section": "Section Name",
            "Priority": "High",                           # Critical/High/Medium/Low
            "Type": "Positive",                           # Positive/Negative/Edge Case/Regression
            "Technique": "Boundary Value Analysis",       # optional
            "Precondition": "User is logged in",
            "Steps": "1. Step one\n2. Step two\n3. Step three",
            "Expected Result": "Expected outcome one\nExpected outcome two\nExpected outcome three",
            "Status": "Draft"                            # Draft/In Review/Active/Deprecated
        }
    }]
}

url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
req = urllib.request.Request(url, data=json.dumps(tc_data).encode(), headers=at_headers, method="POST")
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    created = result.get("records", [])
    print(f"✅ Created: {created[0]['fields']['TC ID']} → ID: {created[0]['id']}")
```

### TC ID Format

Use consistent format based on project:
- `TC-APP-XXX` — Survey App / general app TCs
- `TC-E2E-XXX` — End-to-end TCs
- Format: `{PREFIX}-{NUMBER}` (e.g. `TC-001`, `TC-APP-016`, `TC-E2E-001`)
