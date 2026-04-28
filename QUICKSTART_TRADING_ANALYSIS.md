# Quick Start: Trading Performance Analysis

**3-step workflow to analyze your trading performance**

---

## Step 1: Collect Trade Data (Test Mode)

```
1. Open https://ipathan-lang.github.io/stock-scanner/
2. Click "Test Mode: OFF" to enable
3. Click "🔄 Auto-Refresh: OFF" to enable
4. Wait 1-2 weeks while simulation runs
5. Click "📊 Export Trades" when you have 20+ closed trades
```

---

## Step 2: Run Analysis

```powershell
cd C:\Users\ImranPathan\Downloads\stock-scanner
python analyze_trades.py trades_2026-04-28.csv
```

**Example with sample data:**
```powershell
python analyze_trades.py sample_trades.csv
```

---

## Step 3: Interpret Results

### What to Look For

✅ **Good Performance:**
- Win rate > 50%
- Profit factor > 1.5
- Positive expectancy
- Clear best setup type

❌ **Warning Signs:**
- Win rate < 45%
- Profit factor < 1.0
- Negative expectancy
- All setups losing money

---

## Key Metrics

| Metric | Formula | Goal |
|--------|---------|------|
| **Win Rate** | Wins ÷ Total Trades | > 50% |
| **Expectancy** | Avg P&L per trade | > $0 |
| **Profit Factor** | Gross Profit ÷ Gross Loss | > 1.5 |

---

## Golden Hour Rule

**Best trading time: 9:30 - 10:30 AM EST**

- Highest win rates (typically 80-95%)
- Best profit factor
- Most liquidity and volatility
- Opening Range Breakouts (ORB)

**Avoid: 10:30 AM - 12:30 PM**
- Choppy price action
- Lower win rates
- Midday doldrums

---

## Setup Types (Ranked Best to Worst)

Based on sample data analysis:

1. 🏆 **Range Break** - 100% win rate, $4,204 profit
2. 🥈 **Momentum** - 100% win rate, $2,600 profit
3. 🥉 **News** - 42.9% win rate, $185 profit
4. ⚠️ **Trending** - 36.4% win rate, -$535 loss
5. 🚫 **VWAP Bounce** - 12.5% win rate, -$1,600 loss

**Action**: Focus on Range Break and Momentum. Avoid VWAP Bounce.

---

## Weekly Review Checklist

**Every Friday Evening:**

- [ ] Export this week's trades from test mode
- [ ] Run analyzer: `python analyze_trades.py trades_YYYY-MM-DD.csv`
- [ ] Check win rate (trending up?)
- [ ] Check profit factor (above 1.5?)
- [ ] Identify best performing setup
- [ ] Identify best performing time block
- [ ] Note any losing patterns to avoid
- [ ] Plan next week's focus

---

## Improvement Framework

### If Win Rate < 50%
1. Focus only on your highest win rate setup
2. Trade only in your best time window
3. Reduce position size by 50%
4. Increase minimum net score threshold

### If Profit Factor < 1.0
1. You're losing money overall - STOP
2. Review all setups - which ones are profitable?
3. Eliminate ALL losing setups completely
4. Only trade profitable patterns

### If Expectancy < 0
1. Reduce losses: Tighten stop loss
2. Let winners run: Increase profit target
3. Trade less: Higher quality over quantity
4. Focus on best time windows only

---

## Sample Results Interpretation

```
Overall Statistics:
- Total Trades: 51
- Win Rate: 64.71%          ✅ GOOD (above 50%)
- Profit Factor: 2.28       ✅ EXCELLENT (above 2.0)
- Expectancy: $95.19        ✅ POSITIVE

Best Setup: Range Break     ✅ USE THIS
Worst Setup: VWAP Bounce    ❌ AVOID THIS

Best Time: 9:30-10:30       ✅ TRADE HERE
Worst Time: 10:30-11:30     ❌ AVOID THIS
```

**Strategy**: Trade Range Break setups between 9:30-10:30 AM only.

---

## TradingView Strategy (Optional)

If you use TradingView charts:

1. Open TradingView Pine Editor
2. Copy `trading_strategy_2bar_trailing.pine`
3. Paste and "Add to Chart"
4. Backtest on 5min-1hour timeframes
5. Use 2-bar trailing stop for trade management

---

## Files Reference

| File | Purpose |
|------|---------|
| `analyze_trades.py` | Run analysis |
| `sample_trades.csv` | Test data (51 trades) |
| `trades_YYYY-MM-DD.csv` | Your exported data |
| `TRADING_ANALYSIS.md` | Full documentation |

---

## Dependencies

```powershell
pip install pandas numpy
```

---

## Common Issues

**"No module named pandas"**
```powershell
pip install pandas numpy
```

**"File not found"**
```powershell
# Make sure you're in the right directory
cd C:\Users\ImranPathan\Downloads\stock-scanner
dir  # Should see analyze_trades.py
```

**"No closed trades to export"**
- Enable test mode and wait for simulation to close trades
- Or manually add and close positions

---

## Next Steps

1. Run test mode for 1-2 weeks
2. Export trades (minimum 20 for meaningful analysis)
3. Run analyzer
4. Focus on best setups and times
5. Repeat weekly and track progress

---

**Full Documentation**: [TRADING_ANALYSIS.md](TRADING_ANALYSIS.md)
