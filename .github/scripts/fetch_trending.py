"""
Fetches Yahoo Finance trending stocks list + chart/news for each.
Saves:
  docs/data/trending.json           – list of trending symbols
  docs/data/stocks/TICKER.json      – stock data (shared with portfolio cache)
Run by GitHub Actions every 2h on weekdays.
"""
import os, json, time
import urllib.request, urllib.error

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
    news_url = f'https://query2.finance.yahoo.com/v1/finance/search?q={ticker}&newsCount=3'

    chart = fetch_json(chart_url)
    time.sleep(0.6)

    # Inject regularMarketPreviousClose into chart meta (v8/chart only has chartPreviousClose
    # which is split-adjusted and wrong for daily % change display).
    try:
        quote_url = (
            f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}'
            f'&fields=regularMarketPreviousClose,regularMarketChange,'
            f'regularMarketChangePercent&formatted=false'
        )
        qdata = fetch_json(quote_url)
        qresult = (qdata.get('quoteResponse') or {}).get('result') or []
        if qresult:
            q = qresult[0]
            meta = chart.get('chart', {}).get('result', [{}])[0].get('meta', {})
            if q.get('regularMarketPreviousClose'):
                meta['regularMarketPreviousClose'] = q['regularMarketPreviousClose']
            if q.get('regularMarketChange') is not None:
                meta['regularMarketChange'] = q['regularMarketChange']
            if q.get('regularMarketChangePercent') is not None:
                meta['regularMarketChangePercent'] = q['regularMarketChangePercent'] / 100
        time.sleep(0.4)
    except Exception as e:
        print(f'  quote WARN: {e}')

    news = None
    try:
        news = fetch_json(news_url)
        time.sleep(0.3)
    except Exception as e:
        print(f'  news WARN: {e}')

    return {
        'chart': chart,
        'combo': None,
        'news':  news,
        '_fetched': int(time.time() * 1000),
    }

def main():
    # 1 — Fetch trending list
    trending_url = 'https://query1.finance.yahoo.com/v1/finance/trending/US?count=25'
    print('Fetching trending list...', end=' ', flush=True)
    try:
        data = fetch_json(trending_url)
        quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        symbols = [q['symbol'] for q in quotes if q.get('symbol')]
        if not symbols:
            raise ValueError('empty trending list')
        print(f'OK ({len(symbols)} symbols)')
    except Exception as e:
        print(f'ERROR: {e}')
        return

    # 2 — Save trending list
    out_dir = os.path.join('docs', 'data')
    os.makedirs(out_dir, exist_ok=True)
    trending_path = os.path.join(out_dir, 'trending.json')
    with open(trending_path, 'w') as f:
        json.dump({'symbols': symbols, '_fetched': int(time.time() * 1000)}, f, separators=(',', ':'))

    # 3 — Fetch stock data for each trending symbol (skip ones already cached recently)
    stocks_dir = os.path.join('docs', 'data', 'stocks')
    os.makedirs(stocks_dir, exist_ok=True)

    now_ms = int(time.time() * 1000)
    TWO_HOURS = 2 * 3600 * 1000

    errors = []
    for ticker in symbols:
        path = os.path.join(stocks_dir, f'{ticker}.json')
        # Skip if already freshly cached (e.g. it's also a portfolio stock)
        try:
            with open(path) as f:
                cached = json.load(f)
            if now_ms - cached.get('_fetched', 0) < TWO_HOURS:
                print(f'  {ticker}: cached, skip')
                continue
        except Exception:
            pass

        print(f'Fetching {ticker}...', end=' ', flush=True)
        try:
            stock_data = fetch_ticker(ticker)
            with open(path, 'w') as f:
                json.dump(stock_data, f, separators=(',', ':'))
            print('OK')
        except Exception as e:
            print(f'ERROR: {e}')
            errors.append(ticker)
        time.sleep(0.6)

    if errors:
        print(f'\nFailed: {errors}')
    else:
        print('\nAll done.')

if __name__ == '__main__':
    main()
