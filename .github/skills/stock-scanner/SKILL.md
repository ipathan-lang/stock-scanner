---
name: stock-scanner
description: 'Web-based trading platform for portfolio tracking, automated test simulations, and stock analysis. Use when working with the IntelliMarket Analyst platform, running test simulations, validating predictions, analyzing portfolios, updating the trading algorithm, or debugging the simulator. Includes automated intraday trading simulator with P&L tracking, algorithmic entry/exit logic, and real-time performance metrics.'
argument-hint: 'Describe what you want to do: add features, fix bugs, analyze performance, update algorithm, or validate predictions'
applyTo:
  - docs/index.html
  - "*.py"
  - stock_scanner.py
  - analyze_trades.py
  - trade_journal_coach.py
---

# IntelliMarket Analyst — Trading Platform Skill

## Platform Overview

**Live URL**: https://ipathan-lang.github.io/stock-scanner/
**Architecture**: Single-page HTML/CSS/JavaScript application (`docs/index.html`, ~4700 lines)
**Data Persistence**: localStorage — keys: `ss_port`, `ss_sim`, `ss_watch`, `ss_config`, `ss_activeTab`

### API Sources
- Yahoo Finance v8 chart: `query1.finance.yahoo.com/v8/finance/chart/{ticker}` — price, OHLCV, 2yr history
- Yahoo Finance v10 quoteSummary: `query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}` — fundamentals, earnings, insider data
- Yahoo Finance v1 news: `query2.finance.yahoo.com/v1/finance/search` — headlines
- Nasdaq earnings-surprise API: `api.nasdaq.com/api/company/{ticker}/earnings-surprise`

### CORS Proxies (rotated per-ticker)
```javascript
const PROXIES = [
  v => `https://api.allorigins.win/raw?url=${encodeURIComponent(v)}`,
  v => `https://corsproxy.io/?${encodeURIComponent(v)}`,
  v => `https://proxy.cors.sh/${v}`
];
```
- `fetchJ(url, ps)` — tries direct first, then proxies
- `fetchJProxy(url, ps)` — proxy-only (skips direct, avoids 401s)
- `tickerProxyStart(ticker)` — deterministic proxy assignment per ticker

## When to Use This Skill

- "Update the trading algorithm / scoring"
- "Fix the Test Lab simulator"
- "Add a new feature"
- "Debug why signals are wrong"
- "Validate stock predictions with test trades"
- "Explain what a badge/signal means"
- "Update the $500K Strategy tab"
- "Fix insider activity data"

## Core Files

```
docs/
  index.html            # Main SPA (~4700 lines) — ALL app code is here
  data/
    portfolio.json
    trackedStocks.json
    watchlist.json
.github/skills/stock-scanner/SKILL.md   # This file
analyze_trades.py       # Python performance analyzer
trade_journal_coach.py  # Trade coaching system
```

## Architecture

### Global State Object (`S`)

```javascript
const S = {
  watchlist: [],     // tickers to monitor (DEFAULT_WATCHLIST ~50 stocks)
  data: {},          // {TICKER: enriched stock object from fetchStock()}
  config: {},        // user settings
  sim: { ... },      // Test Lab simulator state
  pinnedTicker: null // searched/pinned stock shown at top
};
```

### Sort Modes (replaces old tab system)

The UI has **3 modes**, switched via nav buttons:

| Button | Mode | What it shows |
|--------|------|---------------|
| ★ Bullish | `'bullish'` | Sorted stock card list by signal tier |
| 📅 Earnings | `'earnings'` | Sorted by nearest upcoming earnings |
| 💰 $500K Strategy | `'strategy'` | Full portfolio plan panel |

**`setSortMode(mode)`** — switches between modes, controls visibility of `#stock-list` vs `#strategy-panel`.

**`renderList()`** — renders all stock cards; has early-return guard: if `_sortMode === 'strategy'`, calls `renderStrategy()` instead. This ensures auto-refresh keeps the strategy panel live.

**`sortStocks(list)`** — sorts by `signalRank` first (badge tier 1–9), then `sortScore` as tiebreaker.

## Signal System (Badge Labels)

**`signal(d)`** function (~line 1430) — returns `{ label, cls, conf, rank }`.

Badge ordering (rank 1 = best, shown first in list):

| Rank | Badge | cls | Meaning |
|------|-------|-----|---------|
| 1 | 🟢 Buy Now · X% | `bg` | All signals aligned: dip confirmed, near week low, trend up, conf ≥ 88% |
| 2 | 🟢 Good Entry · X% | `bg` | Good buy zone: dip detected, lower 50% range, conf ≥ 65% |
| 3 | 👀 Watch · Building · X% | `by` | Score ≥ 4 but confidence/dip not yet confirmed |
| 4 | 👀 Watch · Pullback Soon · X% | `by` | Stock at 50–70% of week range — wait for dip |
| 5 | ⏳ Wait · Overextended · X% | `by` | Stock at top 70%+ of range — don't chase |
| 5 | ⏳ Wait · Near Top · X% | `by` | Score ≥ 7 but at 80%+ of range |
| 6 | 🟡 Neutral · X% | `by` | No clear edge either way |
| 7 | 🟠 Caution · X% | `by` | Slightly negative signals |
| 8 | 🔴 Avoid · X% | `br` | Sellers in control |
| 9 | 🔴 Selling · X% | `br` | Heavy selling pressure |

The **X%** is `conf` — the **Confidence score** from `computeConfidence(d)` (0–99%).

**`signalRank`** is stored on each stock object and used by `sortStocks()` to order the list.

## Scoring Algorithm

### Net Score: `-15` to `+15`

```
netScore = (bullishScore + fundBullAdj + catalystScore) − (bearishScore + fundBearAdj)
```

### Confidence Score — `computeConfidence(d)` (~line 1395)

6-factor weighted score (0–99):
1. Week position — stock near 5-day low (best entry zone)
2. Selling exhaustion — 2+ consecutive red days slowing down
3. Volume character — low-vol dip vs high-vol selloff
4. 20-day trend direction (ret20)
5. Fundamentals score
6. RSI level (not overbought)

### Entry Gates for Strong Signals

**Strong Bullish / 🟢 Buy Now** requires ALL:
- `conf >= 88`
- `hasDip` (real selling exhaustion detected)
- `netScore >= 6`
- `livePos <= 0.35` (bottom 35% of week range)
- `ret20 > 2` (20-day uptrend)
- `rsi < 65 && rsi > 25`
- `fundamentalScore >= -2`
- Not a gap-and-fade

**Bullish / 🟢 Good Entry** requires ALL:
- `conf >= 65`
- `hasDip`
- `netScore >= 4`
- `livePos <= 0.50`
- `ret20 > -3`
- `rsi < 72`

### Catalyst Scoring (adds to `catalystScore`)

- **Insider buying**: 3+ buys 0 sells → +3; 2 buys or net positive → +2; 1 buy → +1
- **Selling exhaustion**: 2+ red days at week low, pace slowing → +3
- **Relative strength vs SPY**: outperforming SPY >8% over 20d → +2
- **Market tailwind**: SPY+QQQ mean score ≥ 6 → +1
- **Earnings proximity**: within -1 to +5 days → +2
- **Volume breakout**: position >80% + volume >1.5x + change >1.5% → +2

### Bearish Scoring (adds to `bearishScore`)

- **Market headwind**: SPY+QQQ mean < -1 → +2; < 2 → +1
- **Relative weakness vs SPY**: underperforming >8% → +2; >4% → +1
- **Insider selling**: 3+ sells 0 buys → +1
- **Overbought**: RSI ≥ 65 → +2
- **Below EMA20**: +2
- **High-vol selloff**: changePct < -3% and volumeRatio > 2.5 → no catalyst allowed

## Insider Activity Feature

### Data Source

Two dedicated Yahoo Finance modules in a **separate fetch** (`insiderUrl`):
- `insiderHolders` — most recent transaction per insider (name, role, buy/sell type, date)
- `netSharePurchaseActivity` — 6-month aggregate (total shares bought vs sold)

**Why separate fetch**: Yahoo Finance silently drops `insiderHolders`/`netSharePurchaseActivity` when combined with `calendarEvents,defaultKeyStatistics,financialData` in a single request.

```javascript
const insiderUrl = `https://query2.finance.yahoo.com/v10/finance/quoteSummary/${ticker}?modules=insiderHolders,netSharePurchaseActivity&formatted=false`;
```

### `insiderActivity` Object (stored on stock record)

```javascript
{
  transactions: [...],  // up to 6 recent insiders with {name, role, type, shares, date, text}
  netValue: N,          // NET shares (buyShares - sellShares) from netSharePurchaseActivity
  buyCount: N,          // from netSharePurchaseActivity.buyInfoCount
  sellCount: N,         // from netSharePurchaseActivity.sellInfoCount
  buyShares: N,         // 6-month aggregate shares purchased
  sellShares: N,        // 6-month aggregate shares sold
}
```

### `buildInsiderSection(d)` (~line 2918)

Renders the 📋 Insider Activity block **always visible on every stock card** (not inside collapsible).
Returns `''` if no buy/sell data (hidden for ETFs which have no Form 4 filers).

Shows:
- Sentiment headline badge (e.g. "▲ 3 buys · 0 sells — strongly bullish")
- Each insider row: `[BUY]/[SELL] Name · Role · Transaction description · Date`
- 6-month aggregate line: `▲ 15K shs bought · ▼ 50K shs sold`

**Note**: ETFs (XLF, SPY, QQQ, etc.) show nothing — they have no individual insider filers.

## $500K Strategy Tab

### Constants

```javascript
const STRATEGY_TOTAL = 500000;

const STRATEGY_PORTFOLIO = [
  { ticker: 'AAPL',  company: 'Apple',           sector: 'Tech',         pct: 9  },
  { ticker: 'MSFT',  company: 'Microsoft',        sector: 'Tech',         pct: 9  },
  { ticker: 'GOOGL', company: 'Alphabet',         sector: 'Tech',         pct: 7  },
  { ticker: 'AMZN',  company: 'Amazon',           sector: 'Tech/Retail',  pct: 7  },
  { ticker: 'NVDA',  company: 'NVIDIA',           sector: 'Semis',        pct: 6  },
  { ticker: 'JPM',   company: 'JPMorgan',         sector: 'Financials',   pct: 6  },
  { ticker: 'V',     company: 'Visa',             sector: 'Financials',   pct: 5  },
  { ticker: 'UNH',   company: 'UnitedHealth',     sector: 'Healthcare',   pct: 5  },
  { ticker: 'JNJ',   company: 'Johnson & Johnson',sector: 'Healthcare',   pct: 5  },
  { ticker: 'WMT',   company: 'Walmart',          sector: 'Consumer',     pct: 5  },
  { ticker: 'COST',  company: 'Costco',           sector: 'Consumer',     pct: 5  },
  { ticker: 'BRK-B', company: 'Berkshire',        sector: 'Diversified',  pct: 8  },
  // + 17% cash buffer = $85,000
];
```

### `renderStrategy()` (~line 2520)

Builds the entire strategy panel HTML:
1. **Market Safety gauge** — reads `S.data['SPY']` + `S.data['QQQ']` scores:
   - `mktMean >= 3` → 🟢 SAFE — deploy normally
   - `mktMean >= 0` → 🟡 CAUTION — reduce size
   - `mktMean < 0`  → 🔴 SELLOFF ALERT — hold cash
2. **Dip alert banner** — shown when `mktMean < -1`
3. **Per-stock cards** — reads `S.data[ticker]`, calls `signal(d)` + `computeConfidence(d)`:
   - Action badge: `ENTER NOW` / `WATCH` / `WAIT` / `AVOID`
   - Entry price, target exit (5-day high), hold note
   - Insider badge from `insiderActivity`
   - Metric chips: confidence %, RSI, 20d trend, week position, volume ratio
4. **Cash buffer card** ($85K) with deploy rules
5. **Disclaimer**

All 12 strategy tickers are in `DEFAULT_WATCHLIST` — so their data is always available in `S.data`.

The strategy panel auto-refreshes with every data cycle because `renderList()` redirects to `renderStrategy()` when `_sortMode === 'strategy'`.

## fetchStock() Data Pipeline

Each call makes **5 parallel fetches**:

```javascript
const [chart, news, nasdaqData, calendarData, insiderData] = await Promise.all([
  fetchJ(chartUrl, ps),                              // v8 chart — price, OHLCV, 2yr history
  fetchJ(newsUrl, ...).catch(() => null),             // v1 news — 3 headlines
  fetchJProxy(nasdaqUrl, ...).catch(() => null),      // Nasdaq earnings-surprise
  fetchJProxy(calendarUrl, ...).catch(() => null),    // v10: calendarEvents + keyStats + financialData
  fetchJProxy(insiderUrl, ...).catch(() => null)      // v10: insiderHolders + netSharePurchaseActivity
]);
```

### Return Object Schema (key fields)

```javascript
{
  ticker, price, change, changePct,
  fetchedAt,
  assetType,              // 'ETF' | 'stock' | etc. (from detectAssetType())
  rsi, macdDiff,          // from calcIndicators()
  ema20, position,        // EMA20 price, week position 0–1
  bullishScore, bearishScore, catalystScore,
  netScore,               // final: -15 to +15
  conviction,             // 0–100 mapped from netScore
  sortScore,              // netScore*100 + bullish*10 - bearish
  signalRank,             // 1–9 from signal() for list ordering
  livePos,                // current position in 5-day range (0=low, 1=high)
  weekHighPct,            // % upside to 5-day high
  ret20, ret5,            // 20-day and 5-day returns
  volumeRatio,            // today's volume / 20-day avg
  consecutiveDownDays,    // for selling exhaustion detection
  hasDip,                 // true if real dip/exhaustion detected
  fundamentals: { forwardPE, pegRatio, debtToEquity, revenueGrowth, earningsGrowth, ... },
  fundamentalScore,       // -3 to +3
  insiderActivity: { transactions, netValue, buyCount, sellCount, buyShares, sellShares },
  nextEarnings,           // Date object or null
  epsSurprise,            // { beat, pct, quarter } or null
  isEarningsDay,          // boolean
  headlines,              // [{title, link, publisher}]
  yearHigh, yearLow,
  wHigh5, wLow5,          // 5-day high/low prices
  atrRatio,               // ATR/price — volatility vs baseline
  dayConviction,          // 'High'|'Medium'|'Low'|'None' — will today's move hold?
}
```

## Key Functions Reference

| Function | ~Line | Purpose |
|----------|-------|---------|
| `fetchStock(ticker)` | 1760 | Full data pipeline — 5 fetches, all scoring |
| `signal(d)` | 1430 | Returns badge label, css class, confidence %, rank 1–9 |
| `computeConfidence(d)` | 1395 | 6-factor weighted confidence 0–99 |
| `sortStocks(list)` | 1116 | Sort by signalRank then sortScore |
| `setSortMode(mode)` | 2667 | Switch between 'bullish'/'earnings'/'strategy' views |
| `renderList()` | 2769 | Render stock cards; redirects to renderStrategy() in strategy mode |
| `renderStrategy()` | 2520 | Build entire $500K strategy panel |
| `buildInsiderSection(d)` | 2918 | Render insider activity block on stock card |
| `buildHoldBar(d)` | 2960 | "Today's Hold" conviction bar |
| `buildFundamentalsRow(d)` | ~2880 | Fundamentals row (PE, PEG, D/E, growth) |
| `buildEarningsRow(d)` | ~2850 | Earnings date + EPS surprise row |
| `buildCard(d, rank, pinned)` | ~3480 | Full stock card HTML |
| `renderAll()` | ~3700 | Re-render the list/strategy panel |
| `loadOne(ticker)` | ~3610 | Load + store a single ticker in S.data |
| `rotateNext()` | ~3620 | Background rolling refresh (5 stocks every 15min) |
| `prediction(d)` | 1505 | Plain-text prediction sentence for the card |

## Test Lab Simulator

### Trading Cycle Logic

**`simRunCycle(force)`** — throttled to 15-min minimum unless forced.

**Flow**:
1. Day detection → reset todayTrades/todayPnL if new day
2. **Sell pass** — check all open positions for exits
3. **Buy pass** — find stocks with signalRank ≤ 2 (Buy Now / Good Entry), buy up to 5 positions at 15% capital each
4. Daily/weekly summaries
5. `simApplyLearning()` — auto-adjust parameters based on last 10 trades

### Exit Conditions

- Target hit: `pnlPct >= targetPct` (default 3.5%)
- Stop loss: `pnlPct <= stopPct` (default -2%)
- Score dropped: `netScore <= sellMaxScore` (default -2)
- Time expired: `hoursHeld >= holdDays * 6.5`
- Overbought: `pnlPct > 1.5% && rsi > 70`

### Tuning Parameters (browser console)

```javascript
S.sim.learn.buyMinScore = 5;   // higher = more selective
S.sim.learn.targetPct   = 4;   // higher profit target
S.sim.learn.stopPct     = -1.5; // tighter stop
save();
```

## Debugging Guide

### Insider Activity Not Showing

1. Check DevTools Network tab — look for the `insiderHolders` quoteSummary request
2. If response is `{}` or 401 → proxy is blocking it; try a different proxy order
3. ETFs (XLF, SPY, etc.) will never show insider data — that is expected
4. Check `S.data['AAPL'].insiderActivity` in console — if `buyCount: 0 && sellCount: 0`, the data came back empty
5. The section is hidden when empty (returns `''`) — only visible when there are actual transactions

### Signal Badges Not Showing / Wrong Order

1. Check `S.data['AAPL'].signalRank` in console — should be 1–9
2. If `signalRank` is `undefined`, the `_sigTmp` pre-computation in fetchStock() failed
3. Verify `signal()` function returns a `rank` property — all return statements must have `rank`

### Simulator Not Trading

```javascript
S.sim.enabled = true;
S.sim.started = true;
save();
location.reload();
```

### Scores All Zero

Check `S.data['AAPL']` in console. If `{err: true}` → all proxies failed. Try refreshing.

### localStorage Full

```javascript
S.sim.log    = S.sim.log.slice(0, 100);
S.sim.closed = S.sim.closed.slice(-100);
save();
```

## Python Analyzer Tools

```bash
python analyze_trades.py sim_trades_YYYY-MM-DD.csv   # 7-section performance report
```

**Targets**: Win rate 50–65%, Profit factor > 1.5

## Deployment Checklist

- [ ] Test in browser — stock cards load, badges appear
- [ ] Check $500K Strategy tab opens and shows market safety gauge
- [ ] Check insider activity on AAPL/MSFT (not ETFs)
- [ ] `git commit` + `git push origin main`
- [ ] GitHub Pages deploys in ~2 min → verify live at https://ipathan-lang.github.io/stock-scanner/
- [ ] Update this skill file if architecture changed

## Daily Learning Log

### 2026-05-13 — Major Architecture Refactor

**Changes made this session:**

1. **Badge labels simplified** — replaced `Strong Bullish/Bullish/Balanced/Cautious/Weak/Bearish` with plain-English emoji badges (🟢 Buy Now, 🟢 Good Entry, 👀 Watch, ⏳ Wait, 🟡 Neutral, 🟠 Caution, 🔴 Avoid, 🔴 Selling)
2. **Signal rank sorting** — list now sorted by badge tier first (`signalRank` 1–9), then `sortScore`. Best opportunities always at top.
3. **Insider Activity feature**:
   - Uses `insiderHolders` + `netSharePurchaseActivity` Yahoo Finance modules
   - Fetched in **dedicated 5th parallel request** — Yahoo drops these when combined with other modules
   - Shows on every stock card **always visible** (moved outside the "Details & News" collapsible)
   - Hidden entirely for ETFs and stocks with no filing data
4. **$500K Strategy tab** — new view with 12-stock portfolio plan, market safety gauge, dip-alert banner, per-stock action badges and entry/exit plans
5. **`setSortMode('strategy')`** — added third mode to the nav toggle; shows `#strategy-panel`, hides `#stock-list`
6. **`renderList()` guard** — early return redirects to `renderStrategy()` when in strategy mode, keeping it live on auto-refresh

### 2026-05-08 — Market Regime Overlay + Relative Strength

**Problem**: False Bullish on CEG/DELL/GILD/JPM (fell 5-6%) + False Balanced on AAPL/GOOGL/AMZN (rallied)

**Fix**: Added Market Regime Overlay and Relative Strength vs SPY scoring in `fetchStock()`:
- SPY+QQQ mean < -1 → +2 bearish headwind
- Outperforming SPY >8% over 20d → +2 catalyst "market leader"
- Underperforming SPY >8% → +2 bearish "sector laggard"

**Rule**: Never go Bullish on an individual stock when SPY+QQQ are both negative AND the stock is underperforming SPY.


# IntelliMarket Analyst — Trading Platform Skill
