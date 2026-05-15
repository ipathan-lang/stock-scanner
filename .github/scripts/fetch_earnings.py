#!/usr/bin/env python3
"""
Fetch Nasdaq earnings calendar for yesterday through +14 calendar days
and cache as docs/data/earnings/YYYY-MM-DD.json.

Also pre-fetches Yahoo Finance chart + news for the top earnings stocks
(by market cap, $1B+, up to 60 unique tickers) and saves them to
docs/data/stocks/TICKER.json — the same cache used by Portfolio/Trends.

Run from repo root. Requires no third-party libraries.
"""
import json, os, re, time, datetime
import urllib.request, urllib.error

EARNINGS_DIR = os.path.join("docs", "data", "earnings")
STOCKS_DIR   = os.path.join("docs", "data", "stocks")
os.makedirs(EARNINGS_DIR, exist_ok=True)
os.makedirs(STOCKS_DIR,   exist_ok=True)

NASDAQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/",
    "Origin": "https://www.nasdaq.com",
}
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com",
}

FOUR_HOURS_MS = 4 * 3600 * 1000
MAX_TICKERS   = 60  # top N earnings stocks to pre-cache

def fetch_url(url, headers, timeout=20):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def parse_mcap(s):
    """Parse '$51.2B', '$392,184,880,140', '$2.1T' → float (or 0)."""
    if not s or s == "--":
        return 0
    s = re.sub(r"[$,\s]", "", s)
    m = re.search(r"[\d.]+", s)
    if not m:
        return 0
    n = float(m.group())
    if "T" in s: return n * 1e12
    if "B" in s: return n * 1e9
    if "M" in s: return n * 1e6
    if "K" in s: return n * 1e3
    return n

def fetch_stock(ticker):
    chart_url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?interval=1d&range=2y&includePrePost=false&events=earnings"
    )
    news_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}&newsCount=3"

    chart = fetch_url(chart_url, YAHOO_HEADERS)
    time.sleep(0.5)

    news = None
    try:
        news = fetch_url(news_url, YAHOO_HEADERS)
        time.sleep(0.3)
    except Exception as e:
        print(f"    news WARN: {e}")

    return {"chart": chart, "combo": None, "news": news, "_fetched": int(time.time() * 1000)}

def main():
    today  = datetime.date.today()
    now_ms = int(time.time() * 1000)

    all_tickers = {}  # ticker → best (highest) market cap seen across all dates

    # ── Step 1: Fetch earnings calendars ─────────────────────────────────────
    print("=== Earnings calendars ===")
    for delta in range(-1, 15):   # yesterday through +14 days (~2 full weeks)
        d        = today + datetime.timedelta(days=delta)
        date_str = d.strftime("%Y-%m-%d")
        url      = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"
        out_path = os.path.join(EARNINGS_DIR, f"{date_str}.json")

        try:
            data = fetch_url(url, NASDAQ_HEADERS, timeout=15)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"))
            rows = data.get("data", {}).get("rows") or []
            print(f"  ✓ {date_str}  ({len(rows)} rows)")

            # Collect $1B+ tickers
            for row in rows:
                ticker = row.get("symbol", "").strip().upper()
                if not ticker or len(ticker) > 6 or not ticker.isalnum():
                    continue
                mc = parse_mcap(row.get("marketCap", ""))
                if mc >= 1e9 and mc > all_tickers.get(ticker, 0):
                    all_tickers[ticker] = mc

        except urllib.error.HTTPError as e:
            print(f"  ✗ {date_str}  HTTP {e.code}")
        except Exception as e:
            print(f"  ✗ {date_str}  {e}")

        time.sleep(0.4)

    # ── Step 2: Cache stock data for top earnings tickers ────────────────────
    sorted_tickers = sorted(all_tickers.items(), key=lambda x: x[1], reverse=True)
    top_tickers    = [t for t, _ in sorted_tickers[:MAX_TICKERS]]
    print(f"\n=== Stock cache: {len(top_tickers)} tickers ===")

    fetched = 0
    errors  = []
    for ticker in top_tickers:
        path = os.path.join(STOCKS_DIR, f"{ticker}.json")

        # Skip if recently cached (< 4h old)
        if os.path.exists(path):
            try:
                with open(path) as f:
                    existing = json.load(f)
                age_ms = now_ms - existing.get("_fetched", 0)
                if age_ms < FOUR_HOURS_MS:
                    print(f"  skip {ticker}  (cached {int(age_ms/60000)}m ago)")
                    continue
            except Exception:
                pass

        print(f"  fetch {ticker}...", end=" ", flush=True)
        try:
            data = fetch_stock(ticker)
            with open(path, "w") as f:
                json.dump(data, f, separators=(",", ":"))
            fetched += 1
            print("OK")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(ticker)

        time.sleep(0.6)

    print(f"\nDone. Calendars saved. {fetched} stocks fetched, {len(errors)} errors.")
    if errors:
        print("Stock errors:", errors)

if __name__ == "__main__":
    main()
