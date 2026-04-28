# Trading Performance Analysis System 📊

**Complete trading performance analyzer with automated export from IntelliMarket Analyst portfolio tracking.**

---

## Overview

This system provides comprehensive trading performance analysis with:

1. **Automated Trade Tracking** - Portfolio system automatically captures all trade details
2. **One-Click Export** - Export trade history directly from the web app
3. **Deep Performance Analysis** - Analyze by setup type, time of day, day of week
4. **Pattern Detection** - Identify best/worst performing setups and time windows
5. **Actionable Recommendations** - Get specific advice based on your data

---

## How It Works

### Step 1: Track Trades in IntelliMarket Analyst

**Test Mode Trading** (Recommended for learning):
1. Open https://ipathan-lang.github.io/stock-scanner/
2. Click **"Test Mode: OFF"** to enable test trading
3. The app will automatically execute trades based on your watchlist
4. All trades are tracked with:
   - Entry/Exit prices and times
   - Setup type (Range Break, Momentum, News, etc.)
   - Shares and P&L
   - Hold duration

**Manual Portfolio Tracking**:
- Add positions manually via "+ Add Position"
- System tracks entry price and shares
- When you close positions, data is recorded

---

### Step 2: Export Trade History

When you have completed trades in test mode:

1. Click **"📊 Export Trades"** button (visible in test mode)
2. File downloads as `trades_YYYY-MM-DD.csv`
3. Saved to your Downloads folder

**Export Format**:
```csv
Symbol,Entry Date,Entry Time,Entry Price,Exit Date,Exit Time,Exit Price,Shares,P&L,Setup Type
TSLA,2026-04-01,09:35,248.50,2026-04-01,10:45,251.20,100,270.00,Range Break
NVDA,2026-04-01,10:15,895.30,2026-04-01,11:30,892.10,50,-160.00,Trending
...
```

---

### Step 3: Analyze Performance

Run the analyzer on your exported trades:

```powershell
python analyze_trades.py trades_2026-04-28.csv
```

Or use the sample data to see how it works:

```powershell
python analyze_trades.py sample_trades.csv
```

---

## Analysis Output

### 1. Overall Statistics

```
Total Trades: 51
Winning Trades: 33
Losing Trades: 18
Win Rate: 64.71%

Average Win: $262.11
Average Loss: $-210.83
Largest Win: $440.00
Largest Loss: $-440.00

Total P&L: $4,854.50
Average P&L per Trade: $95.19
Expectancy: $95.19
Profit Factor: 2.28
```

**Key Metrics Explained**:
- **Win Rate**: % of trades that made money (aim for 50%+)
- **Expectancy**: Average $ earned per trade (must be positive)
- **Profit Factor**: Gross profit ÷ Gross loss (aim for 2.0+)

---

### 2. Performance by Setup Type

```
Setup Type   Trades  Win Rate  Avg Win   Avg Loss   Total P&L
Range Break      17    100.0%  $247.32      $0.00  $4,204.50
Momentum          8    100.0%  $325.00      $0.00  $2,600.00
News              7     42.9%  $246.67   $-138.75    $185.00
Trending         11     36.4%  $256.25   $-222.86   $-535.00
VWAP Bounce       8     12.5%   $80.00   $-240.00 $-1,600.00
```

**Insights**:
- ✅ **Range Break** is your best setup (100% win rate, $4,204 profit)
- ❌ **VWAP Bounce** is losing money consistently (12.5% win rate)
- **Action**: Focus on Range Break and Momentum setups, avoid VWAP Bounce

---

### 3. Performance by Time of Day (Golden Hour Analysis)

```
Time Block    Trades  Win Rate  Avg Win   Avg Loss   Total P&L
9:30-10:30        20     95.0%  $254.45   $-160.00  $4,674.50  ← BEST
10:30-11:30       13     23.1%  $366.67   $-216.00 $-1,060.00  ← WORST
11:30-12:30        2      0.0%    $0.00   $-340.00   $-680.00
12:30-1:30         3    100.0%  $226.67      $0.00    $680.00
1:30-2:30         10     60.0%  $244.17   $-138.75    $910.00
2:30-4:00          3     66.7%  $285.00   $-240.00    $330.00
```

**Golden Hour Findings**:
- 🏆 **9:30-10:30 AM**: 95% win rate, $4,674 profit → TRADE HERE
- 🚫 **10:30-12:30 PM**: Losing money → AVOID THIS WINDOW
- **Action**: Execute most trades in the first hour after market open

---

### 4. Performance by Day of Week

```
Day        Trades  Win Rate  Avg Win   Avg Loss  Total P&L
Tuesday         9     66.7%  $284.25   $-145.00  $1,270.50
Wednesday      12     66.7%  $281.56   $-213.75  $1,397.50
Thursday       12     66.7%  $260.44   $-208.75  $1,248.50
Friday          9     66.7%  $233.58   $-218.33    $746.50
```

**Insights**:
- Consistent 66.7% win rate across all days
- Wednesday is your most profitable day
- All days are profitable with positive expectancy

---

### 5. Recommendations

The analyzer provides specific, actionable recommendations:

```
1. 🟢 Strong win rate above 60%. Consider increasing position size on 
   high-confidence setups.

2. 📈 Focus more on Range Break setups - your most profitable pattern 
   ($4,204.50 total P&L, 100.0% win rate).

3. 📉 AVOID VWAP Bounce setups - consistent money loser ($-1,600.00 total P&L). 
   Either eliminate or drastically improve this pattern.

4. ⏰ GOLDEN HOUR: Trade most actively during 9:30-10:30 ($4,674.50 total P&L). 
   This is your most profitable window.

5. ⏰ DANGER ZONE: Consider avoiding 10:30-11:30 ($-1,060.00 total P&L). 
   This time block is costing you money.

6. 🟢 Excellent profit factor of 2.28. You're making $2+ for every $1 lost.
```

---

## Setup Types Explained

The app automatically classifies trades into these setup types:

| Setup Type | Criteria | Best For |
|------------|----------|----------|
| **Range Break** | RSI < 40, positive change | Oversold bounces |
| **Momentum** | Net score ≥ 8 | Strong trending moves |
| **Trending** | Position > 70%, MACD+ | Continuation plays |
| **VWAP Bounce** | Position < 30%, positive change | Support bounces |
| **News** | Volume > 1.5x average | Catalyst-driven moves |
| **Auto Trade** | Algorithm-selected | Machine learning picks |

---

## Weekly Workflow

**Recommended routine for continuous improvement**:

### Monday Morning
- Review last week's performance analysis
- Identify best performing setups and times
- Plan trading focus for the week

### During Trading Week
- Run test mode with auto-refresh
- Let the app execute trades automatically
- Monitor Golden Hour section for ORB setups

### Friday Evening
```powershell
# Export this week's trades
# (Click "Export Trades" button in test mode)

# Run analysis
python analyze_trades.py trades_2026-04-28.csv

# Review results and adjust strategy
```

### What to Look For
- ✅ Win rate trending up week-over-week
- ✅ Profit factor staying above 1.5
- ✅ Best time blocks remain consistent
- ❌ Any setup types consistently losing money
- ❌ New losing time periods emerging

---

## Files in This System

| File | Purpose |
|------|---------|
| `analyze_trades.py` | Main performance analyzer script |
| `sample_trades.csv` | Example trade data (51 trades) |
| `trades_YYYY-MM-DD.csv` | Your exported trades from app |
| `trading_strategy_2bar_trailing.pine` | TradingView strategy (optional) |

---

## TradingView Pine Script (Bonus)

**2-Bar Trailing Stop Strategy** included for TradingView users:

### Features
- Entry: Moving average crossover (customizable)
- Stop: Trailing based on 2-bar low
- Visual markers: Entry (▲), Exit (▼)
- Color-coded stop line (red → green when trailing)

### How to Use
1. Copy `trading_strategy_2bar_trailing.pine` contents
2. Open TradingView Pine Editor
3. Paste code and click "Add to Chart"
4. Backtest on your preferred timeframe (5min-1hour recommended)

### Stop Logic
- **Initial**: Lowest low of past 2 bars at entry (RED)
- **Trailing**: Moves to new 2-bar low when price makes new 2-bar high (GREEN)
- **Never moves down**: Protects profits once price runs

---

## Dependencies

### Python Requirements
```powershell
pip install pandas numpy
```

That's it! No other dependencies needed.

---

## Troubleshooting

### "File not found" error
```powershell
# Make sure you're in the stock-scanner directory
cd C:\Users\ImranPathan\Downloads\stock-scanner

# Then run analyzer
python analyze_trades.py trades_2026-04-28.csv
```

### No closed trades to export
- Enter test mode and let the simulation run for a few days
- Or add manual trades using "+ Add Position" and close them

### CSV format errors
- Make sure all required columns are present
- Entry/Exit times should be in HH:MM format (24-hour)
- Dates should be YYYY-MM-DD format

---

## Advanced Usage

### Custom Trade Data

Create your own CSV with this format:
```csv
Symbol,Entry Date,Entry Time,Entry Price,Exit Date,Exit Time,Exit Price,Shares,P&L,Setup Type
```

### Filtering Analysis

Modify `analyze_trades.py` to filter by:
- Date range: `df = df[(df['Entry Date'] >= '2026-04-01') & (df['Entry Date'] <= '2026-04-30')]`
- Specific setups: `df = df[df['Setup Type'] == 'Range Break']`
- Min trade size: `df = df[df['Shares'] >= 100]`

---

## Performance Goals

**Beginner Trader** (First 3 months):
- ✅ Win rate: 45-50%
- ✅ Profit factor: 1.2-1.5
- ✅ Positive expectancy
- ✅ Identify 1-2 working setups

**Intermediate Trader** (3-12 months):
- ✅ Win rate: 50-60%
- ✅ Profit factor: 1.5-2.0
- ✅ Expectancy > $50/trade
- ✅ 3+ profitable setups
- ✅ Avoid losing time periods

**Advanced Trader** (1+ years):
- ✅ Win rate: 60%+
- ✅ Profit factor: 2.0+
- ✅ Expectancy > $100/trade
- ✅ Consistent across all setups
- ✅ Optimized for Golden Hour

---

## Integration with IntelliMarket Analyst

This analysis system is fully integrated with your portfolio tracker:

1. **Congressional Trading Intelligence** - See what Congress is trading
2. **Golden Hour ORB Scanner** - Opening Range Breakout analysis
3. **Market Sentiment** - Bull/bear trend detection
4. **News Impact** - Earnings and catalyst tracking
5. **AI Coach** - Plain-language buy/sell guidance
6. **Test Mode** - Risk-free backtesting with real data

**Synergy**: Use Congressional Trades + Golden Hour ORB + Performance Analysis together:
- Morning: Check Golden Hour pre-market analysis
- Find stocks with congressional activity (insider signal)
- Enter trades in your best performing time window (9:30-10:30)
- Focus on your best setups (Range Break, Momentum)
- Export and analyze results weekly

---

## Next Steps

1. ✅ Run test mode for a week to generate trade data
2. ✅ Export trades and run first analysis
3. ✅ Identify your best setup type and time window
4. ✅ Adjust trading strategy to focus on winners
5. ✅ Repeat weekly and track improvement

---

## Support

For questions or issues:
- GitHub: https://github.com/ipathan-lang/stock-scanner/issues
- Documentation: [GOLDEN_HOUR_TRADING.md](GOLDEN_HOUR_TRADING.md), [CONGRESSIONAL_TRADES.md](CONGRESSIONAL_TRADES.md)

---

**End of Documentation**
