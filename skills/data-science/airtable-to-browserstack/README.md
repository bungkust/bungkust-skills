# airtable-to-browserstack

Push test cases from Airtable table to BrowserStack Test Management via REST API.

## What This Does

- Fetch TCs from Airtable (paginated, auth via PAT)
- Parse Steps + Expected Result (numbered lists → 1:1 paired steps)
- Map Type + Priority enums to BS values
- Bulk create in correct BS folder
- Patch Section custom_field after create

## Usage

1. Copy `scripts/push_template.py` to your working directory
2. Fill in `table_id`, `list_folder_id`, `form_folder_id`
3. Run: `python3 push_template.py`

## File Structure

```
airtable-to-browserstack/
├── SKILL.md           # Full skill documentation
├── README.md          # This file
└── scripts/
    └── push_template.py   # Ready-to-use push script
```

## Credentials

- **Airtable PAT:** `/root/.hermes/secrets/airtable.env`
- **BrowserStack:** `/root/.hermes/secrets/browserstack.env`
