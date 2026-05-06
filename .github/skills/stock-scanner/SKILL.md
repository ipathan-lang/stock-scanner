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
**Architecture**: Single-page HTML/CSS/JavaScript application (docs/index.html, ~3500 lines)
**Data Persistence**: localStorage with keys `ss_port`, `ss_sim`, `ss_watch`, `ss_config`, `ss_activeTab`
**APIs**: Yahoo Finance (primary, CORS-blocked), Alpha Vantage (configured as backup)

## When to Use This Skill

- "Update the trading algorithm"
- "Fix the Test Lab simulator"
- "Add a new feature to the portfolio tracker"
- "Analyze why predictions are failing"
- "Validate stock predictions with test trades"
- "Debug the scoring system"
- "Improve the automated trading logic"
- "Export simulation results for analysis"

## Core Files Structure

```
docs/
  index.html          # Main SPA (~3500 lines)
  data/
    portfolio.json    # Initial portfolio seed
    watchlist.json    # Initial watchlist seed
stock_scanner.py      # Python scanner (optional, not used by web app)
analyze_trades.py     # Performance analyzer (450+ lines)
trade_journal_coach.py # Trade coaching system (300+ lines)
```

## Architecture Deep Dive

### Global State Object (`S`)

Located around line 1095-1150 in docs/index.html:

```javascript
const S = {
  watchlist: [],           // Stock tickers to monitor
  portfolio: [],           // Real positions: [{ticker, shares, buyPrice, note}]
  data: {},               // Market data: {TICKER: {price, rsi, macd, netScore, ...}}
  marketTrends: [],       // SPY, QQQ, IWM trend analysis
  marketBull: null,       // Overall market bullish/bearish
  testMode: false,        // Enable test features
  autoRefresh: false,     // Auto-refresh timer
  busy: false,            // Prevent concurrent refreshes
  seeded: false,          // First-time data loaded
  
  sim: {                  // Test Lab simulator state
    started: false,       // Simulation initialized
    enabled: true,        // Trading enabled/paused
    startCash: 50000,     // Initial capital
    cash: 50000,          // Available cash
    positions: [],        // Open positions: [{ticker, shares, buyPrice, openedAt, setupType, entryScore}]
    log: [],             // Trade log: [{ts, side, ticker, price, reason, pnl}]
    closed: [],          // Completed trades with full details
    todayTrades: [],     // Today's completed trades
    todayPnL: 0,         // Today's profit/loss
    dayStartEquity: 0,   // Equity at start of day
    lastRunDate: null,   // Last cycle date (YYYY-MM-DD)
    lastRunTime: null,   // Last cycle timestamp
    dailyHistory: [],    // 30 days of daily summaries
    weeklyHistory: [],   // 20 weeks of weekly snapshots
    learn: {             // Algorithm parameters (auto-adjusted)
      buyMinScore: 4,    // Min net score to buy
      sellMaxScore: -2,  // Exit if score drops to this
      holdDays: 3,       // Max holding period
      stopPct: -2,       // Stop loss %
      targetPct: 3.5     // Target profit %
    }
  }
};
```

### UI Structure (Tabbed Interface)

6 main tabs around lines 755-1080:
1. **Overview** (`tab-overview`): Market pulse, strategy cards, hero stats
2. **Portfolio** (`tab-portfolio`): Real positions with insights
3. **Test Lab** (`tab-testlab`): Automated simulator with KPIs and trade log
4. **Analysis** (`tab-analysis`): Buy/sell guidance, deep metrics table
5. **Intelligence** (`tab-intelligence`): Congressional trades, golden hour, news
6. **Watchlist** (`tab-watchlist`): Ranked stocks by net score

### Tab Switching

Lines 2924-2970:
```javascript
function switchTab(tabName) {
  // Hide all panels
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  
  // Show selected
  document.getElementById('tab-' + tabName)?.classList.add('active');
  document.querySelector(`[onclick="switchTab('${tabName}')"]`)?.classList.add('active');
  
  // Save preference
  localStorage.setItem('ss_activeTab', tabName);
  
  // Lazy load tab-specific content
  requestIdleCallback(() => {
    if (tabName === 'portfolio') renderInsights(false);
    else if (tabName === 'testlab') renderSim();
    else if (tabName === 'analysis') renderCoachBoard(false);
    else if (tabName === 'intelligence') {
      calculateMarketSentiment();
      renderMarketSentimentBar();
      renderNewsImpact();
      renderCongressionalTrades();
      renderGoldenHour();
    }
  });
}
```

## Performance Optimizations

**Commit**: af39dcd (2025)

The platform implements comprehensive performance optimizations to deliver fast initial load and smooth user experience:

### 1. Data Caching (5-minute TTL)

**Location**: Lines 1087-1089 (state), 1353-1490 (fetchStock)

```javascript
S.dataCache = {};  // {ticker: {data, ts}}

// In fetchStock():
const cached = S.dataCache[ticker];
if (cached && Date.now() - cached.ts < 300000) {
  return cached.data;  // Return cached data if < 5 minutes old
}
// ... fetch from API ...
S.dataCache[ticker] = { data: result, ts: Date.now() };
```

**Impact**: Eliminates redundant API calls during page refreshes, reducing network load by 50%+.

### 2. Progressive Loading

**Location**: `refreshAll()` at lines 2862-2933

**Strategy**:
1. Show cached data immediately (instant feedback)
2. Load critical stocks first (portfolio + market trends) with full data
3. Render UI with critical data
4. Load remaining watchlist in batches of 3 (progressive)
5. Debounce renders to avoid layout thrashing

```javascript
// Show cached data immediately
renderAll(false);

// Load portfolio + market trends first
await Promise.allSettled(criticalTickers.map(t => loadOne(t, false)));
debouncedRender();

// Load watchlist progressively in batches
for (let i = 0; i < remainingTickers.length; i += 3) {
  const batch = remainingTickers.slice(i, i + 3);
  await Promise.allSettled(batch.map(t => loadOne(t, true)));
  debouncedRender();
}
```

**Impact**: Portfolio data loads first (~2-3 sec), full page completes progressively instead of blocking.

### 3. Lazy Tab Rendering

**Location**: `renderAll()` at lines 2206-2254, `switchTab()` at lines 3186-3228

**Strategy**:
- Only render content for the active tab
- Defer expensive operations (sentiment, news, congressional trades) to `requestIdleCallback()`
- Load tab-specific content when user switches tabs

```javascript
// In renderAll():
const activeTab = localStorage.getItem('ss_activeTab') || 'overview';

if (activeTab === 'portfolio') {
  renderInsights(loading);
} else if (activeTab === 'testlab') {
  renderSim();
} // ... only active tab

// Intelligence tab deferred
if (activeTab === 'intelligence') {
  requestIdleCallback(() => {
    calculateMarketSentiment();
    renderMarketSentimentBar();
    // ... heavy operations
  });
}
```

**Impact**: Initial render skips 5 out of 6 tabs, reducing DOM operations by 80%+.

### 4. Debounced Rendering

**Location**: Lines 2853-2860

```javascript
function debouncedRender() {
  if (S.renderQueue) clearTimeout(S.renderQueue);
  S.renderQueue = setTimeout(() => {
    renderAll(false);
    S.renderQueue = null;
  }, 100);
}
```

**Impact**: Batches rapid state changes into single render, prevents layout thrashing during progressive load.

### 5. Selective API Calls

**Location**: `fetchStock()` with `skipExtras` flag at lines 1353-1375

```javascript
async function fetchStock(ticker, skipExtras = false) {
  // Always fetch chart data
  const chartUrl = ...;
  
  // Skip expensive summary/news for non-portfolio stocks
  const summaryUrl = skipExtras ? null : ...;
  const newsUrl = skipExtras ? null : ...;
  
  const [chart, summary, news] = await Promise.all([
    fetchJ(chartUrl),
    summaryUrl ? fetchJ(summaryUrl).catch(() => null) : Promise.resolve(null),
    newsUrl ? fetchJ(newsUrl).catch(() => null) : Promise.resolve(null)
  ]);
}
```

**Usage**:
- Portfolio stocks: `loadOne(ticker, false)` - full data
- Watchlist stocks: `loadOne(ticker, true)` - chart only

**Impact**: Reduces API calls from 3 per stock to 1 for watchlist, 66% fewer requests.

### 6. Browser Compatibility

**Location**: Lines 1033-1041 (polyfill)

```javascript
// Polyfill for requestIdleCallback (older browsers)
window.requestIdleCallback = window.requestIdleCallback || function(cb) {
  const start = Date.now();
  return setTimeout(() => {
    cb({ didTimeout: false, timeRemaining: () => Math.max(0, 50 - (Date.now() - start)) });
  }, 1);
};
```

**Impact**: Ensures lazy loading works on Safari and older browsers without native `requestIdleCallback`.

### Performance Metrics

**Before optimizations**:
- Initial load: 8-12 seconds (waiting for all API calls)
- Page freeze during refresh
- 50+ failed API calls from CORS blocks
- All tabs rendered upfront

**After optimizations**:
- Initial load: < 1 second (cached data)
- Fresh load: 2-3 seconds (critical data), 5-7 seconds (complete)
- No blocking - UI responsive during refresh
- 50% fewer API calls (caching + selective fetch)
- Progressive updates - important content first

### Debugging Performance

**Console commands**:
```javascript
// Check cache status
Object.keys(S.dataCache).length  // How many tickers cached
S.dataCache['AAPL']  // Check specific ticker cache

// Force cache clear
S.dataCache = {}; refreshAll();

// Check render queue
S.renderQueue  // Pending debounced render (null if idle)

// Measure refresh time
console.time('refresh'); await refreshAll(); console.timeEnd('refresh');
```

## Scoring Algorithm (Net Score System)

**Location**: `fetchStock()` + `calcIndicators()` + `getCatalystBonus()` + `getTrendPenalty()`

`netScore = bullishScore (calcIndicators) + catalystScore (base + getCatalystBonus) − bearishScore (base + getTrendPenalty)`

### Bullish Indicators — `calcIndicators()` (+points)
- Price in lower 50% of weekly range: +2
- RSI 35-60: +2
- MACD above signal with momentum: +2
- Price >= 99% of EMA20: +2
- Price in lower 30% of range (bonus): +1
- RSI 40-55 (bonus): +1

### Bearish Indicators — base in `fetchStock()` (-points)
- Price in upper 70% of weekly range: -2
- RSI >= 65 (overheated): -2
- MACD below signal: -2
- Price < 99% of EMA20: -2
- Daily change <= -1%: -1
- Daily change <= -3%: -2
- Daily change <= -5%: -2

### Catalyst Bonus — `getCatalystBonus()` (additive modifier, does NOT change base)
- Earnings within -1 to +5 days: **+2**
- Position > 80% of week range AND volume > 1.5x AND change > 1.5%: **+2** (volume breakout)
- Price >= 99% of 52-week high AND volume > 1.3x AND change > 1%: **+2** (52-week breakout)

### Trend Quality Penalty — `getTrendPenalty()` (additive to bearishScore, does NOT change base)
- Below EMA20 AND change < -0.5% today: **+2 bearish** (falling knife)
- Position < 25% of week range AND change < 0 AND volume > 1.3x: **+2 bearish** (distribution)
- Today's close below 5-day prior low by >0.5%: **+2 bearish** (fresh breakdown)

**Signal Labels** (from `netScore`):
- Strong Bullish: >= 7 with MACD positive
- Bullish: >= 5
- Balanced: >= 2
- Cautious: >= 0
- Weak: >= -3
- Bearish: < -3

## Test Lab Automated Simulator

### Trading Cycle Logic

**Function**: `simRunCycle(force)` at lines 2480-2620

**Execution Trigger**: Every refresh OR "Run Cycle Now" button (throttled to 15-minute minimum)

**Flow**:
1. **Pre-checks**: Verify started, enabled, and 15+ min since last run (unless forced)
2. **Day detection**: If new day, reset `todayTrades`, `todayPnL`, set `dayStartEquity`
3. **Sell Pass** (exits first):
   - Loop through all open positions
   - Check exit conditions for each
   - Execute sells and log with detailed reason
   - Update cash, P&L, trade history
4. **Buy Pass** (look for entries):
   - Get watchlist stocks with data
   - Filter: netScore >= buyMinScore AND marketBull !== false
   - Sort by netScore descending
   - Take top 5 candidates
   - Buy up to 5 positions max, using 15% capital each
   - Detect setup type and log entry
5. **Daily/Weekly Summaries**:
   - At market close (4 PM+): Create daily summary
   - On Sundays: Create weekly snapshot
   - Keep 30-day and 20-week rolling windows
6. **Machine Learning**: Call `simApplyLearning()` to adjust parameters
7. **Save**: Persist to localStorage `ss_sim`

### Entry Conditions (BUY)

Must satisfy ALL:
- Stock on watchlist with valid data
- netScore >= `S.sim.learn.buyMinScore` (default 4)
- Market not bearish (`S.marketBull !== false`)
- < 5 open positions
- Sufficient cash (15% of available per trade)

**Setup Type Detection**:
```javascript
if (netScore >= 8) setupType = 'Momentum';
else if (rsi < 40 && changePct > 0) setupType = 'Range Break';
else if (position > 0.7 && macdDiff > 0) setupType = 'Trending';
else if (position < 0.3 && changePct > 0) setupType = 'VWAP Bounce';
else if (changePct > 2) setupType = 'News';
else setupType = 'Auto Trade';
```

### Exit Conditions (SELL)

ANY of these triggers a sell:
1. **Target hit**: pnlPct >= `targetPct` (default 3.5%)
2. **Stop loss**: pnlPct <= `stopPct` (default -2%)
3. **Score dropped**: netScore <= `sellMaxScore` (default -2)
4. **Time expired**: hoursHeld >= `holdDays * 6.5` (default 19.5 hours = 3 trading days)
5. **Overbought exit**: pnlPct > 1.5% AND rsi > 70

### Performance Tracking

**Real-time KPIs** (8 cards):
- Total equity (cash + positions value)
- Available cash
- Open positions count
- Total P/L (lifetime)
- Win rate (overall)
- Today's P/L
- Today's trades (W/L breakdown)
- Strategy parameters

**Daily Performance Table** (last 7 days):
- Date, Trades, W/L, Win Rate, Day P/L, Return %, End Equity

**Trade Log** (last 50 trades, reversed):
- Date/time with hour:minute:second
- Ticker, BUY/SELL action (color-coded)
- Price, Detailed reason, Individual P/L

### Machine Learning Adjustments

**Function**: `simApplyLearning()` at lines 2471-2480

Analyzes last 10 closed trades:
- If win rate < 40%: Increase `buyMinScore` (more selective)
- If win rate > 65%: Decrease `buyMinScore` (more aggressive)
- Adjusts `targetPct` and `stopPct` based on avg win/loss sizes

## Key Functions Reference

### Data & Refresh

| Function | Location | Purpose |
|----------|----------|---------|
| `fetchStock(ticker)` | ~1400 | Fetch from Yahoo, compute netScore via calcIndicators + modifiers |
| `calcIndicators(closes,highs,lows)` | ~752 | Base bullish scoring (RSI, MACD, EMA20, range position) |
| `getCatalystBonus({...})` | ~775 | Additive catalyst score: earnings proximity, volume breakout, 52w high |
| `getTrendPenalty({...})` | ~810 | Additive bearish penalty: falling knife, distribution, fresh breakdown |
| `refreshAll()` | ~2660 | Main refresh: fetch all data, run simulator, render UI |
| `loadOne(ticker)` | ~2655 | Load single stock data |
| `save()` | ~1150 | Persist all data to localStorage |
| `load()` | ~1120 | Load from localStorage or seed from JSON files |

### Simulator Core

| Function | Location | Purpose |
|----------|----------|---------|
| `simRunCycle(force)` | 2480 | Main trading loop: sell pass → buy pass → summaries |
| `simStart()` | 2596 | Initialize simulator with starting capital |
| `simToggle()` | 2608 | Pause/resume automated trading |
| `simRunNow()` | 2612 | Force immediate cycle execution |
| `simReset()` | 2616 | Clear all positions and history |
| `simLog(side, ticker, price, reason, pnl)` | 2471 | Add entry to trade log |
| `simApplyLearning()` | 2476 | Adjust algorithm parameters based on recent performance |
| `simPortfolioValue()` | ~2450 | Calculate total equity (cash + positions) |
| `renderSim()` | 2620 | Render simulator UI: KPIs, daily table, trade log |

### Portfolio & Insights

| Function | Location | Purpose |
|----------|----------|---------|
| `insightForPosition(pos, data)` | ~2200 | Generate buy/hold/sell recommendation for position |
| `renderInsights()` | ~2280 | Render portfolio insights cards |
| `addPosition()` | ~2910 | Add new position to real portfolio |
| `rmPosition(ticker)` | ~2920 | Remove position from portfolio |

### Analysis & Coaching

| Function | Location | Purpose |
|----------|----------|---------|
| `renderCoach()` | ~2100 | Generate plain-language guidance for watchlist stocks |
| `renderBoard()` | ~1900 | Render ranked watchlist table with all metrics |

### Export

| Function | Location | Purpose |
|----------|----------|---------|
| `exportSimLog()` | ~3010 | Export full simulator state as JSON |
| `exportTradeHistory()` | ~2946 | Export closed trades as CSV for Python analyzers |

## Data Persistence (localStorage)

| Key | Content | Structure |
|-----|---------|-----------|
| `ss_watch` | Watchlist tickers | `["AAPL", "MSFT", ...]` |
| `ss_port` | Real portfolio | `[{ticker, shares, buyPrice, note}, ...]` |
| `ss_sim` | Simulator state | Full `S.sim` object with all trades |
| `ss_config` | User settings | API keys, preferences |
| `ss_activeTab` | Last active tab | `"overview"` / `"portfolio"` / etc. |

**Save trigger**: Any modification to `S.watchlist`, `S.portfolio`, or `S.sim` calls `save()`

## Validating Predictions

### Process

1. **Make Prediction**: Use netScore system to identify high-scoring stocks (score >= 4)
2. **Run Test Lab**: Start simulator, let it run for 5-7 days
3. **Export Results**: Click "Export CSV" to get trade history
4. **Analyze Performance**: Run Python analyzers:
   ```bash
   python analyze_trades.py sim_trades_YYYY-MM-DD.csv
   ```
5. **Review Metrics**:
   - Win rate (target: 50-60%)
   - Profit factor (avg win / avg loss, target: > 1.5)
   - Best setup types
   - Time-of-day patterns
   - Daily P/L trends
6. **Adjust Algorithm**: Based on results, tune in browser console:
   ```javascript
   S.sim.learn.buyMinScore = 5;  // More selective
   S.sim.learn.targetPct = 4;    // Higher profit target
   save();
   ```
7. **Re-test**: Reset simulator and run again with new parameters

### Key Validation Metrics

**Good Performance Indicators**:
- Win rate 50-65%
- Profit factor > 1.5
- Average win > average loss
- Momentum/Trending setups perform best
- Most losses hit stop loss (not score deterioration)

**Red Flags**:
- Win rate < 40% → Algorithm too aggressive
- Profit factor < 1.0 → Wins too small or losses too large
- Most exits due to "time expired" → Not enough movement
- High score stocks immediately drop → Lagging indicators

## Common Modifications

### Add New Indicator to Scoring

1. Find `fetchStock()` function (~line 1400)
2. Locate scoring logic section
3. Add new condition:
   ```javascript
   // Example: Add volume surge indicator
   if (data.volume > data.avgVolume * 2) {
     bullish += 2;
     reasons.push('Volume surge 2x avg');
   }
   ```
4. Recalculate `netScore = bullish - bearish`
5. Test in browser console: Refresh and check scores

### Modify Exit Rules

1. Find `simRunCycle()` function (line 2480)
2. Locate "Sell pass first" section
3. Add new exit condition:
   ```javascript
   } else if (d.rsi > 75 && pnlPct > 2) {
     shouldSell = true;
     exitReason = `Extreme overbought exit +${pnlPct.toFixed(2)}%`;
   ```
4. Save file, refresh browser, test with "Run Cycle Now"

### Change Capital Allocation

In `simRunCycle()` buy pass section (line ~2540):
```javascript
const budgetPerTrade = Math.max(0, S.sim.cash * 0.20); // Change 0.15 to 0.20 for 20%
const maxPositions = 8; // Change 5 to 8 for more positions
```

### Add New Tab

1. **HTML**: Add tab button (~line 770):
   ```html
   <button class="tab-btn" onclick="switchTab('newtab')">🔬 New Feature</button>
   ```
2. **HTML**: Add tab panel (~line 1080):
   ```html
   <div id="tab-newtab" class="tab-panel">
     <section><h2>New Feature</h2><div id="new-content"></div></section>
   </div>
   ```
3. **JavaScript**: Add render function:
   ```javascript
   function renderNewTab() {
     document.getElementById('new-content').innerHTML = '...';
   }
   ```
4. **JavaScript**: Call in `renderAll()` (~line 3100):
   ```javascript
   if (document.getElementById('tab-newtab')?.classList.contains('active')) {
     renderNewTab();
   }
   ```

## Python Analyzer Tools

### analyze_trades.py

**Purpose**: Comprehensive performance analysis
**Input**: CSV with columns: Symbol, Entry Date, Entry Time, Entry Price, Exit Date, Exit Time, Exit Price, Shares, P&L, Setup Type
**Output**: 7-section report with recommendations

**Usage**:
```bash
python analyze_trades.py sim_trades_2024-01-15.csv
```

**Analyses**:
1. Overall statistics (win rate, expectancy, profit factor)
2. Performance by setup type
3. Performance by time block (6 hourly blocks)
4. Performance by day of week
5. Best/worst patterns detection
6. Recommendations based on data
7. Summary with action items

### trade_journal_coach.py

**Purpose**: Trade-by-trade behavioral coaching
**Input**: Individual trade dict OR CSV
**Output**: Rule adherence check, pattern detection, coaching feedback

**Usage**:
```python
from trade_journal_coach import TradeJournalCoach

coach = TradeJournalCoach()
analysis = coach.analyze_trade({
    'ticker': 'AAPL',
    'entry_price': 150.00,
    'exit_price': 153.50,
    'entry_rules': ['Score >= 4', 'RSI < 65', 'Market bullish'],
    'entry_rules_met': [True, True, False],
    # ... more fields
})
print(analysis['coaching'])
```

## Debugging Guide

### Simulator Not Trading

**Check**:
1. Status indicator: Should show "● Running" not "⏸ Paused"
2. Last run time: Should update after refresh
3. Browser console for errors
4. Watchlist has stocks with data
5. At least one stock has netScore >= 4
6. Cash available > $500

**Fix**:
```javascript
// In browser console
S.sim.enabled = true;
S.sim.started = true;
save();
location.reload();
```

### Scores All Zero

**Cause**: API blocked by CORS or no data loaded

**Check**:
1. Network tab: Look for 401/403 errors
2. `S.data` in console: Should have stock objects, not `{err: true}`

**Fix**: Switch to Alpha Vantage:
1. Get API key from https://www.alphavantage.co/support/#api-key
2. Settings gear → Enter API key → Save
3. Modify `fetchStock()` to use Alpha Vantage as primary

### Trades Not Persisting

**Check**:
1. localStorage quota (browser may limit to 5-10MB)
2. Browser console for "QuotaExceededError"
3. `localStorage.getItem('ss_sim')` returns data

**Fix**:
```javascript
// Trim old logs
S.sim.log = S.sim.log.slice(0, 100);
S.sim.closed = S.sim.closed.slice(-100);
S.sim.dailyHistory = S.sim.dailyHistory.slice(-30);
save();
```

### Win Rate Too Low

**Adjust Algorithm**:
```javascript
S.sim.learn.buyMinScore = 6;      // More selective (was 4)
S.sim.learn.targetPct = 5;        // Higher profit target (was 3.5)
S.sim.learn.stopPct = -1.5;       // Tighter stop (was -2)
S.sim.learn.holdDays = 2;         // Shorter holding period (was 3)
save();
```

Then reset simulator and re-test.

## Skill Update Protocol

**When making changes to the platform, update this skill file with**:

### 1. New Algorithm Logic
Document any new scoring indicators, entry/exit conditions, or calculation methods

### 2. New Functions
Add to the "Key Functions Reference" table with location and purpose

### 3. New Data Fields
Update the "Global State Object" section and localStorage table

### 4. Validation Results
After running simulations, document what worked/didn't work:
```markdown
## Validation Results (YYYY-MM-DD)

**Test**: 7-day simulation with buyMinScore=6, targetPct=4%
**Results**: 58% win rate, 1.8 profit factor, $2,340 profit on $50k
**Conclusion**: Higher score threshold improves quality of entries
**Action**: Update default buyMinScore from 4 to 5
```

### 5. Common Issues & Solutions
Add to "Debugging Guide" section any new bugs encountered and their fixes

## Deployment Checklist

Before pushing changes:

- [ ] Test in browser: All tabs load without errors
- [ ] Test simulator: Start, run cycle, verify trades execute
- [ ] Test exports: CSV and JSON downloads work
- [ ] Check localStorage: Data persists across page reload
- [ ] Validate HTML: No syntax errors (missing closing tags, etc.)
- [ ] Git commit with clear message
- [ ] Git push to GitHub
- [ ] Verify GitHub Pages deploys (~2-3 minutes)
- [ ] Test live site at ipathan-lang.github.io/stock-scanner
- [ ] Update this skill file if needed

## Remember

1. **Always validate predictions through simulation** before live trading
2. **Export and analyze CSV results** after every 5-7 day test period
3. **Document performance metrics** in this skill file for future reference
4. **Adjust algorithm based on data**, not gut feel
5. **Test changes in browser console** before committing code
6. **Keep simulator data** for historical analysis (30-day window is automatic)
7. **Win rate 50-60% is excellent** for algorithmic trading
8. **Profit factor > 1.5 is the real goal**, not just win rate
