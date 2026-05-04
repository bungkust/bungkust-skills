---
name: airtable-to-browserstack
description: Push test cases from Airtable table to BrowserStack Test Management folder via API. Handles field mapping, enum conversion, step parsing, and Section patching.
category: data-science
tags: [airtable, browserstack, qa, test-case, automation]
related_skills:
  - browserstack-testcase-update
  - browserstack-to-airtable
  - testcase-creation-guidelines
---

# Airtable → BrowserStack Test Case Push

> ⚠️ **Before using: Load `testcase-creation-guidelines` first** — title format, step structure, and expected result rules must be followed consistently before pushing.

Bulk create test cases in BrowserStack from Airtable. Workflow: fetch → parse → create → patch Section.

## Credentials

**BrowserStack:**
- Username: `kusbot_80QMqF`
- Access Key: in `~/.hermes/secrets/browserstack.env` as `BS_KEY`
- Base URL: `https://test-management.browserstack.com/api/v2`
- Auth: Basic (`base64(username:access_key)`)

**Airtable:**
- Token: `/root/.hermes/secrets/airtable.env` (`AIRTABLE_TOKEN=pat...`)
- Base ID: `appZBHS426cptfXRN` (Admin Dashboard)

## Project & Folder IDs

**PR-7** (Admin Dashboard):

| Feature | Folder | Sub-folder IDs |
|---------|--------|----------------|
| 01-Contents | 45332794 | List: 45332851, Form: 45332852 |
| 02-Clubs | 45332796 | List: 45332853, Form: 45332854, Club Form: 46160954 |
| 03-Users | 45332798 | List: 45332855, Detail: 45332864 |
| 04-Admin Users | 45332799 | List: 45332880, Form: 45332881 |
| 05-Competitions | 45332802 | List: 45332882, Form: 45332883, Create: 46160003, Edit: 46160007 |
| 06-Matches | 45332804 | List: 45332884, Form: 45332885 |
| 07-Ads | 45332805 | List: 45332886, Form: 45332887 |
| 08-Merchant Voucher | 45332807 | List: 45332888, Form: 45332889 |
| 09-Surveys | 45332808 | Survey List: 46158674, Create Survey: 46158673, Edit Survey: 46158675 |

## Workflow

1. **Inspect Airtable** — fetch records, count by Section
2. **Check existing BS folders** — verify folder IDs exist
3. **Map sections → folder IDs** — group records by Section
4. **Push test cases** — POST to correct folder
5. **Patch Section** — PATCH custom_fields after create

### Step 1 — Inspect Airtable

```python
import urllib.request, urllib.parse, json

with open("/root/.hermes/secrets/airtable.env") as f:
    for line in f:
        if "AIRTABLE_TOKEN=" in line:
            at_token = line.split("=", 1)[1].strip()

table_id = "tblXXXXXXXX"  # from Airtable URL

url = f"https://api.airtable.com/v0/appZBHS426cptfXRN/{table_id}?pageSize=3"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {at_token}"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

for r in data.get("records", []):
    ff = r["fields"]
    print(f"[{ff.get('TC ID')}] {ff.get('Title')}")
    print(f"  Section: {ff.get('Section')} | Type: {ff.get('Type')} | Priority: {ff.get('Priority')}")
```

### Step 2 — Enum Mappings

```python
type_map = {
    "Positive": "Positive flows",
    "Negative": "Negative flows",
    "Edge Case": "Edge cases",
    "Edge Cases": "Edge cases",
    "Boundary": "Functional",
    "Smoke": "Smoke",
    "Regression": "Regression",
    "Accessibility": "Accessibility",
}
priority_map = {"Critical": "High", "High": "High", "Medium": "Medium", "Low": "Low"}
```

### Step 3 — Step Parsing

```python
import re

def parse_steps(steps_text, expected_text):
    def extract_items(text):
        if not text: return []
        items = []
        for line in (text.strip().split("\n") if text else []):
            line = line.strip()
            if not line: continue
            m = re.match(r'^\d+[.\)]\s*(.+)', line)
            items.append(m.group(1).strip() if m else line)
        return items
    steps_list = extract_items(steps_text)
    expected_list = extract_items(expected_text)
    n = max(len(steps_list), 1)
    return [{"step": steps_list[i] if i < len(steps_list) else f"Step {i+1}",
             "result": expected_list[i] if i < len(expected_list) else ""}
            for i in range(n)]
```

### Step 4 — Full Push Script

```python
import urllib.request, urllib.parse, json, base64, time, re

# Setup
with open("/root/.hermes/secrets/airtable.env") as f:
    for line in f:
        if "AIRTABLE_TOKEN=" in line:
            at_token = line.split("=", 1)[1].strip()

bs_user = "kusbot_80QMqF"
with open("/root/.hermes/secrets/browserstack.env") as f:
    for line in f:
        if "BS_KEY=" in line:
            bs_key = line.split("=", 1)[1].strip()

bs_url = "https://test-management.browserstack.com/api/v2"
bs_auth = base64.b64encode(f"{bs_user}:{bs_key}".encode()).decode()
bs_headers = {"Authorization": f"Basic {bs_auth}", "Content-Type": "application/json", "Accept": "application/json"}

table_id = "{{AT_TABLE_ID}}"       # from Airtable URL
project = "PR-7"
list_folder_id = {{LIST_FOLDER_ID}}
form_folder_id = {{FORM_FOLDER_ID}}

at_headers = {"Authorization": f"Bearer {at_token}"}

type_map = {"Positive": "Positive flows", "Negative": "Negative flows",
    "Edge Case": "Edge cases", "Edge Cases": "Edge cases",
    "Boundary": "Functional", "Smoke": "Smoke", "Regression": "Regression", "Accessibility": "Accessibility"}
priority_map = {"Critical": "High", "High": "High", "Medium": "Medium", "Low": "Low"}

def parse_steps(steps_text, expected_text):
    def extract_items(text):
        if not text: return []
        items = []
        for line in (text.strip().split("\n") if text else []):
            line = line.strip()
            if not line: continue
            m = re.match(r'^\d+[.\)]\s*(.+)', line)
            items.append(m.group(1).strip() if m else line)
        return items
    steps_list = extract_items(steps_text)
    expected_list = extract_items(expected_text)
    n = max(len(steps_list), 1)
    return [{"step": steps_list[i] if i < len(steps_list) else f"Step {i+1}",
             "result": expected_list[i] if i < len(expected_list) else ""}
            for i in range(n)]

def push_tcs(records, folder_id, folder_name):
    created = failed = 0
    print(f"=== {folder_name} ({folder_id}) ===")
    for r in records:
        ff = r["fields"]
        parsed = parse_steps(ff.get("Steps", ""), ff.get("Expected Result", ""))
        payload = {"test_case": {
            "name": ff.get("Title", "Untitled"),
            "case_type": type_map.get(ff.get("Type", ""), "Functional"),
            "priority": priority_map.get(ff.get("Priority", ""), "Medium"),
            "preconditions": ff.get("Precondition", ""),
            "test_case_steps": parsed}}
        url = f"{bs_url}/projects/{project}/folders/{folder_id}/test-cases"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=bs_headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            if result.get("data", {}).get("success"):
                tc = result["data"]["test_case"]
                created += 1
                print(f"  ✅ {ff.get('TC ID')} → {tc['identifier']}")
            else:
                failed += 1
                print(f"  ❌ {ff.get('TC ID')}")
        except urllib.error.HTTPError as e:
            failed += 1
            print(f"  ❌ {ff.get('TC ID')}: HTTP {e.code}")
        time.sleep(0.35)
    print(f"  → {created} created, {failed} failed")
    return created, failed

# Fetch all records
all_records = []
offset = None
while True:
    params = {"pageSize": "100"}
    if offset: params["offset"] = offset
    url = f"https://api.airtable.com/v0/appZBHS426cptfXRN/{urllib.parse.quote(table_id)}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=at_headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    all_records.extend(data.get("records", []))
    offset = data.get("offset")
    if not offset: break

sections = {}
for r in all_records:
    ff = r.get("fields", {})
    sec = ff.get("Section", "Uncategorized")
    if sec not in sections:
        sections[sec] = []
    sections[sec].append(r)

print(f"Total: {len(all_records)}")
for sec, recs in sorted(sections.items()):
    print(f"  {sec}: {len(recs)} TCs")

# Categorize and push
list_recs = [r for r in all_records if "list" in r["fields"].get("Section","").lower()]
form_recs = [r for r in all_records if "form" in r["fields"].get("Section","").lower()]

push_tcs(list_recs, list_folder_id, "List")
push_tcs(form_recs, form_folder_id, "Form")
```

## ⚠️ Critical Pitfalls

1. **Field name: `name` not `title`** — BS create uses `name`, response returns `title`.
2. **`custom_fields` NOT allowed on create** — create without, then PATCH separately.
3. **PATCH uses `identifier` (e.g. `TC-3272`) not numeric ID.**
4. **Steps DO persist via POST** — use `test_case_steps` key in POST payload.
5. **Rate limit** — 0.35s sleep between POSTs.
6. **Pagination** — Airtable max 100/page. Loop with `offset`.
7. **Airtable PAT returns 401 mid-session** — If 401 on valid token, re-authenticate.
8. **Nested folder TC list endpoint** — use `GET /projects/{project}/test-cases?folder_id={fid}` not folder-level endpoint.
