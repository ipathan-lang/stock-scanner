#!/usr/bin/env python3
"""
Fetch Nasdaq earnings calendar for today + next 7 business days
and cache as static JSON files in docs/data/earnings/YYYY-MM-DD.json.

Run from repo root. Requires no third-party libraries.
"""
import json
import os
import datetime
import urllib.request
import urllib.error

OUT_DIR = os.path.join("docs", "data", "earnings")
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/",
    "Origin": "https://www.nasdaq.com",
}

today = datetime.date.today()

# Fetch yesterday through +7 calendar days (covers any weekend boundaries)
for delta in range(-1, 8):
    d = today + datetime.timedelta(days=delta)
    date_str = d.strftime("%Y-%m-%d")
    url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"
    out_path = os.path.join(OUT_DIR, f"{date_str}.json")

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            data = json.loads(raw)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"))
            rows = len(data.get("data", {}).get("rows") or [])
            print(f"  ✓ {date_str}  ({rows} rows)")
    except urllib.error.HTTPError as e:
        print(f"  ✗ {date_str}  HTTP {e.code}")
    except Exception as e:
        print(f"  ✗ {date_str}  {e}")
