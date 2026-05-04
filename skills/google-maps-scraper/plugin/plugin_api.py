"""Google Maps Scraper dashboard plugin — backend API routes.
Mounted at /api/plugins/google-maps-scraper/ by the dashboard plugin system.
"""

import subprocess
import json
import os
import csv
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

SCRAPER_DIR = "/root/google-maps-scraper"
OUTPUT_DIR = f"{SCRAPER_DIR}/output"


def slugify(text):
    """Convert text to filename-safe slug."""
    return text.lower().replace(" ", "_").replace(",", "")


@router.get("/scrape")
async def scrape(query: str, daerah: str, max_results: int = 50):
    """Run Google Maps scraper and return results as JSON."""
    output_prefix = f"{slugify(query)}_{slugify(daerah)}"
    json_path = f"{OUTPUT_DIR}/{output_prefix}.json"
    csv_path = f"{OUTPUT_DIR}/{output_prefix}.csv"

    # Check cache first
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                data = json.load(f)
            return {"success": True, "results": data, "count": len(data), "cached": True}
        except Exception:
            pass

    # Run scraper
    cmd = [
        "python3", f"{SCRAPER_DIR}/gmaps_scraper.py", query, daerah,
        "--max", str(max_results), "-o", csv_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Scraper timed out after 600s"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Load results — prefer JSON, fallback to CSV
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                data = json.load(f)
            return {"success": True, "results": data, "count": len(data), "cached": False}
        except Exception:
            pass

    if os.path.exists(csv_path):
        results = []
        try:
            with open(csv_path) as f:
                for row in csv.DictReader(f):
                    results.append(row)
            return {"success": True, "results": results, "count": len(results), "cached": False}
        except Exception as e:
            return {"success": False, "error": f"CSV parse error: {e}"}

    return {
        "success": False,
        "error": "No output file generated",
        "stdout": result.stdout[-500:] if result.stdout else "",
        "stderr": result.stderr[-500:] if result.stderr else ""
    }


@router.get("/results/{query}/{daerah}")
async def get_results(query: str, daerah: str):
    """Get cached results for a query."""
    output_prefix = f"{slugify(query)}_{slugify(daerah)}"
    json_path = f"{OUTPUT_DIR}/{output_prefix}.json"

    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                return {"success": True, "results": json.load(f)}
        except Exception:
            pass
    return {"success": False, "error": "No cached results found"}


@router.get("/history")
async def get_history():
    """List all cached scrape results."""
    if not os.path.exists(OUTPUT_DIR):
        return {"success": True, "results": []}
    files = []
    for f in sorted(Path(OUTPUT_DIR).glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        try:
            with open(f) as fp:
                data = json.load(fp)
            files.append({"name": f.stem, "count": len(data), "path": str(f)})
        except Exception:
            files.append({"name": f.stem, "count": 0, "path": str(f)})
    return {"success": True, "results": files}
