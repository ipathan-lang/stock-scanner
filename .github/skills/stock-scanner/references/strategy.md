# Strategy Reference — Large Cap Bullish Reversal

## Core Concept

This is a **short-term swing trading** strategy targeting 1–3 day reversals in large-cap US stocks. It identifies stocks that have pulled back within their weekly range while showing early signs of a bullish turn (RSI recovering, MACD crossing, price near EMA support).

## Capital Split Rationale

| Tranche | % | Purpose |
|---|---|---|
| Entry | 60% | Initial positions, deployed at market open |
| Reserve | 40% | Averaging down if price dips further before reversing |

The reserve prevents full capital loss if a position moves against you immediately. Rather than stopping out at -2% on the full position, you use part of the reserve to lower your average cost, then exit the full position at a smaller loss or breakeven.

**Rule:** Only deploy reserve if the stock is still above its weekly low and the original thesis (RSI, MACD) remains intact. Do NOT average down into a broken setup.

## Score Weighting at Entry

Higher-scored stocks receive proportionally more of the 60% deploy tranche:

```
entry_for_stock = (stock_score / sum_of_all_scores) * deploy_capital
```

This means a Score-8 stock gets roughly 2x the capital of a Score-4 stock — concentrating more in the highest-conviction setups.

## Exit Rules

| Condition | Action |
|---|---|
| Price hits +3.5% target | Exit full position, take profit |
| Price hits -2% stop loss | Exit full position, no exceptions |
| Day 3 close | Exit regardless of P&L |
| MACD turns negative intraday | Consider early exit |

## Market Filter

Only trade when S&P 500 is above its 20 EMA. In a bearish market, even high-scored stocks fail more often. The script checks this automatically.

## Known Limitations & Improvements

### Already implemented
- Score-weighted allocation (not equal weight)
- 60/40 deploy/reserve split
- Market trend filter (S&P 500 EMA check)
- Auto-install dependencies

### Recommended next improvements (not yet implemented)

**1. Fix MACD on 15d data**
Use `period="60d"` instead of `period="15d"` to ensure MACD (which needs 26+ periods) calculates correctly.

**2. Expand stock universe**
12 stocks is too small. Add 30–50 tickers across sectors:
```python
STOCKS = [
    # Tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA", "AMD", "INTC", "CRM",
    # Financials
    "JPM", "BAC", "GS", "MS", "WFC", "BRK-B", "V", "MA",
    # Health
    "UNH", "LLY", "JNJ", "PFE", "ABBV", "MRK",
    # Energy
    "XOM", "CVX", "COP", "SLB",
    # Consumer
    "HD", "WMT", "COST", "MCD", "NKE",
    # Industrial
    "CAT", "BA", "GE", "HON",
]
```

**3. Earnings blackout filter**
Skip stocks with earnings within 5 days to avoid gap risk:
```python
import datetime
cal = yf.Ticker(ticker).calendar
if cal is not None:
    earnings_date = cal.get("Earnings Date", [None])[0]
    if earnings_date and (earnings_date - datetime.date.today()).days <= 5:
        return None  # skip
```

**4. ATR-based position sizing**
Size positions by volatility — high-ATR stocks (TSLA) should get smaller positions:
```python
atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1]
risk_per_trade = CAPITAL * 0.01   # risk 1% of capital per trade
shares = int(risk_per_trade / atr)
```

**5. Relative strength filter**
Only buy stocks that are keeping up with or beating SPY over the past month. Weak stocks in strong markets are traps.

**6. Weekly trend confirmation**
Download 3 months of data and check if price is above the 50 EMA. A stock can look like a dip on daily but still be in a weekly downtrend.

## Risk Management Rules

1. **Never risk more than 2% of total capital on a single trade**
2. **Never deploy reserve into a stock that has broken its weekly low**
3. **Stop out at -2% — no exceptions, no "hoping it comes back"**
4. **Skip trading days when S&P 500 is below 20 EMA**
5. **Close all positions before earnings announcements**

## Example Trade Flow

```
Monday 9:30 AM
→ Run scanner
→ AAPL score 7, JPM score 6

Deploy:
→ AAPL: $54,194 → buy 203 shares at $266.73
→ JPM:  $46,452 → buy 148 shares at $312.18
→ Set stop: AAPL $261.40, JPM $305.94

Monday 11 AM — AAPL drops to $258.73 (-3%)
→ Check: still above weekly low? RSI still recovering? MACD still above signal?
→ Yes → deploy reserve: buy 17 more shares at $258.73
→ New avg cost: ~$265.10, new stop: $259.80

Tuesday 2 PM — AAPL hits $276
→ +3.5% target hit → exit full 220 shares
→ Profit: ~$2,400
```
