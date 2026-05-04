#!/usr/bin/env python3
"""
Airtable → BrowserStack Test Case Push Template
Configure: table_id, list_folder_id, form_folder_id
"""
import urllib.request, urllib.parse, json, base64, time, re, os

# === SETUP ===
with open("/root/.hermes/secrets/airtable.env") as f:
    for line in f:
        if "AIRTABLE_TOKEN=" in line:
            at_token = line.split("=", 1)[1].strip()

with open("/root/.hermes/secrets/browserstack.env") as f:
    for line in f:
        if "BS_KEY=" in line:
            bs_key = line.split("=", 1)[1].strip()

bs_user = "kusbot_80QMqF"
bs_url = "https://test-management.browserstack.com/api/v2"
bs_auth = base64.b64encode(f"{bs_user}:{bs_key}".encode()).decode()
bs_headers = {"Authorization": f"Basic {bs_auth}", "Content-Type": "application/json", "Accept": "application/json"}
project = "PR-7"

# === CONFIGURE THESE ===
table_id = "tblXXXXXXXX"           # Airtable table ID
list_folder_id = 0                 # BS List folder ID
form_folder_id = 0                 # BS Form folder ID
# ======================

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

list_recs = [r for r in all_records if "list" in r["fields"].get("Section","").lower()]
form_recs = [r for r in all_records if "form" in r["fields"].get("Section","").lower()]

push_tcs(list_recs, list_folder_id, "List")
push_tcs(form_recs, form_folder_id, "Form")
