---
name: stock-scanner
description: 'Large-cap bullish reversal scanner with 60/40 capital deployment strategy. Use when scanning for swing trade setups, allocating capital across large-cap stocks, running the stock scanner, finding bullish reversals, or planning entry and average-down levels. Scores stocks by RSI, MACD, EMA20, and weekly position. Deploys 60% at entry (score-weighted) and reserves 40% to average down on dips.'
argument-hint: 'Optional: CAPITAL=500000 or list of tickers to override defaults'
---

# Stock Scanner — Large Cap Bullish Reversal

## What This Skill Does

Scans a large-cap stock universe daily for bullish reversal setups using technical indicators. Outputs a ranked score table and a capital deployment plan split 60% entry / 40% reserve for averaging down.

## When to Use

- "Run the stock scanner"
- "Find bullish setups today"
- "Which large caps are dipping?"
- "Show me allocation plan for $X capital"
- "What stocks should I watch this week?"

## Quick Start

```bash
python .github/skills/stock-scanner/scripts/stock_scanner.py
```

Dependencies are auto-installed on first run (`yfinance`, `pandas`, `ta`).

## Configuration (edit top of script)

| Variable | Default | Description |
|---|---|---|
| `CAPITAL` | `400000` | Total capital to deploy |
| `DEPLOY_PCT` | `0.60` | % deployed at entry |
| `RESERVE_PCT` | `0.40` | % held for averaging down |
| `MAX_POSITIONS` | `8` | Max concurrent positions |
| `STOCKS` | 12 large caps | Universe to scan |

## Scoring System

Each stock is scored out of 10 — higher = stronger bullish setup:

| Condition | Points |
|---|---|
| Price in lower 50% of weekly range | +2 |
| RSI between 30–65 | +2 |
| MACD above signal line | +2 |
| Price ≥ 97% of EMA20 | +2 |
| Price in lower 35% of range (bonus) | +1 |
| RSI between 35–55 (bonus) | +1 |

Stocks scoring **≥ 4** are included in the allocation plan.

## Capital Deployment Strategy

See [strategy reference](./references/strategy.md) for full explanation.

**Entry (60%):** Score-weighted allocation — highest scored stock receives proportionally more capital.

**Reserve (40%):** Held in cash. If any position drops 2–4% after entry, deploy reserve to average down at ~-3% from entry price.

## Output Columns

| Column | Meaning |
|---|---|
| `Ticker` | Stock symbol |
| `Price` | Latest close price |
| `RSI` | 14-period RSI |
| `Position` | 0.0 = weekly low, 1.0 = weekly high |
| `MACD_diff` | MACD minus signal (positive = bullish) |
| `Score` | Bullish score out of 10 |
| `Entry $` | Score-weighted capital allocated |
| `Shares` | Number of shares to buy |
| `Stop Loss` | Exit price at -2% |
| `Target` | Profit target at +3.5% |

## Market Filter

The scanner checks S&P 500 vs its 20 EMA before running. If the market is in a bearish trend, it warns you to avoid trading that day.

## Procedure

1. Run the script: `python .github/skills/stock-scanner/scripts/stock_scanner.py`
2. Review the full ranked table — all stocks shown even if score is low
3. Focus on stocks with **Score ≥ 4** in the allocation plan
4. Enter positions at open using the `Entry $` and `Shares` columns
5. Set stop losses at the `Stop Loss` price immediately after entry
6. Monitor during the day — if any position drops to avg-down price, deploy the reserve
7. Exit at `Target` price or end of day 3, whichever comes first

## Files

- [`scripts/stock_scanner.py`](./scripts/stock_scanner.py) — Main scanner script
- [`references/strategy.md`](./references/strategy.md) — Full strategy explanation and improvement roadmap
