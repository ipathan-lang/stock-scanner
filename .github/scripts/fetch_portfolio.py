"""
Fetches Yahoo Finance chart + summary + news for each portfolio stock.
Saves raw data to docs/data/stocks/TICKER.json (same-origin, no CORS).
Run by GitHub Actions every 2h on weekdays.
"""
import os, json, time, sys
import urllib.request, urllib.error

PORTFOLIO = [
    # Trillion-dollar & near-trillion
    'NVDA','AAPL','MSFT','AMZN','GOOGL','META','TSLA','AVGO','TSM','LLY','JPM','V','MA',
    # Nearing $1T - fast growing (>$500B)
    'WMT','NFLX','ASML','XOM','COST','ABBV','INTU','UBER','ACN',
    # Fast-growing tech
    'PLTR','CRWD','PANW','ARM','SHOP','NOW','CRM','ORCL','NBIS','ZETA',
    # Semiconductors
    'AMD','AMAT','QCOM','KLAC','MU','ON','GFS',
    # Financials
    'GS','BN',
    # Healthcare
    'UNH','ELV','CVS',
    # Energy / Utilities
    'CEG','NEE','PBR',
    # Other / Hardware
    'DELL','BOOT','KHC',
    # ETFs
    'SPY','VTI','XLF','XLV','GLD','VXUS','FIG',
    # Gold / Miners
    'GDX','GDXJ','GLDM','IAU','GOLD','KGC','PHYS','UGL',
    # Bonds / Cash
    'SGOV',
    # Energy
    'XOP','XLE',
    # Consumer / Watchlist
    'DIS','KO',
    # Semiconductors (expanded)
    'INTC','MRVL',
    # AI Infrastructure / Data Centers
    'SMCI','ANET','EQIX','DLR',
    # Energy (expanded)
    'CVX','GEV','DVN',
    # Defense / Aerospace
    'LMT','RTX','NOC','GD',
    # Cybersecurity (expanded)
    'ZS','FTNT','NET',
    # Industrials / Robotics
    'CAT','HON','DE','ROK','ABBNY',
    # Healthcare / Biotech (expanded)
    'NVO','AMGN','REGN',
    # Financials (expanded)
    'BAC','MS',
    # Nuclear Energy
    'OKLO','SMR',
    # Defense (expanded)
    'AVAV','KTOS',
    # Cybersecurity (expanded further)
    'S','OKTA',
    # Industrials (expanded)
    'F',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://finance.yahoo.com/',
    'Origin': 'https://finance.yahoo.com',
}

def fetch_json(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_ticker(ticker):
    chart_url = (
        f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
        f'?interval=1d&range=2y&includePrePost=false&events=earnings'
    )
    combo_url = (
        f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}'
        f'?modules=calendarEvents,defaultKeyStatistics,financialData,'
        f'insiderHolders,netSharePurchaseActivity&formatted=false'
    )
    news_url = f'https://query2.finance.yahoo.com/v1/finance/search?q={ticker}&newsCount=3'

    chart = fetch_json(chart_url)
    time.sleep(0.6)

    combo = None
    try:
        combo = fetch_json(combo_url)
        time.sleep(0.6)
    except Exception as e:
        print(f'  combo WARN: {e}')

    news = None
    try:
        news = fetch_json(news_url)
        time.sleep(0.3)
    except Exception as e:
        print(f'  news WARN: {e}')

    return {
        'chart': chart,
        'combo': combo,
        'news':  news,
        '_fetched': int(time.time() * 1000),
    }

def main():
    out_dir = os.path.join('docs', 'data', 'stocks')
    os.makedirs(out_dir, exist_ok=True)

    errors = []
    for ticker in PORTFOLIO:
        print(f'Fetching {ticker}...', end=' ', flush=True)
        try:
            data = fetch_ticker(ticker)
            path = os.path.join(out_dir, f'{ticker}.json')
            with open(path, 'w') as f:
                json.dump(data, f, separators=(',', ':'))
            print('OK')
        except Exception as e:
            print(f'ERROR: {e}')
            errors.append(ticker)
        time.sleep(1.2)  # be polite to Yahoo

    if errors:
        print(f'\nFailed: {errors}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
