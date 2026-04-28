# Test Lab Quick Start Guide

## How to Test Your Automated Trading System

### Step 1: Start the Simulator
1. Open your scanner at: https://ipathan-lang.github.io/stock-scanner/
2. Click the **Test Lab** tab
3. Enter starting capital (recommended: $50,000)
4. Click **"Start Simulation"**
5. You should see a success message

### Step 2: Trigger First Trading Cycle
1. Go back to the **Overview** tab
2. Click the **"🔄 Refresh"** button at the top
3. Wait for data to load (this also triggers the trading algorithm)
4. Return to **Test Lab** tab

### Step 3: Verify Trading Activity

#### Check KPI Cards (Top Row)
You should see 8 cards showing:
- ✅ Total Equity (should equal your starting amount initially)
- ✅ Available Cash (will decrease as trades execute)
- ✅ Open Positions (should show 0-5 depending on opportunities)
- ✅ Total P/L (lifetime profit/loss)
- ✅ Win Rate (overall percentage)
- ✅ Today P/L (today's profit/loss)
- ✅ Today Trades (count with W/L breakdown)
- ✅ Strategy (current parameters)

#### Check Status Indicator
- **Before trading**: "Simulator not started yet"
- **After start**: "● Running · Last trade: [time]"
- **If paused**: "⏸ Paused · No automatic trades"

#### Review Trade Log
Scroll down to **"📝 Recent Trades"** table:
- Should show BUY entries for stocks with score >= 4
- Each row shows: Date/Time, Stock, BUY/SELL, Price, Reason, P/L
- BUY entries show the setup type and entry conditions
- SELL entries show the exit reason (target hit, stop loss, etc.)

### Step 4: Let It Run Throughout the Day

1. **Trigger more cycles**: Click "Refresh" every 15-30 minutes
   - Or click **"Run Cycle Now"** in Test Lab to force execution
   
2. **Watch positions open and close**:
   - Buys happen when stocks have high net scores
   - Sells happen when targets hit, stops trigger, or time expires
   
3. **Monitor daily P/L**:
   - "Today P/L" card updates with each closed trade
   - Win/Loss count increments automatically

### Step 5: Review Daily Performance (Next Day)

After running for multiple days:
1. Go to Test Lab
2. Scroll to **"📊 Daily Performance (Last 7 Days)"** table
3. Review:
   - Date of each trading day
   - Number of trades executed
   - Win/Loss breakdown
   - Win rate percentage
   - Day P/L in dollars
   - Day return percentage
   - Ending equity

### Step 6: Export and Analyze

Once you have 10+ closed trades:

1. Click **"📊 Export CSV"** button
2. Save the file (e.g., `sim_trades_2024-01-15.csv`)
3. Run Python analysis:
   ```bash
   python analyze_trades.py sim_trades_2024-01-15.csv
   ```
4. Review detailed performance report

## What to Look For

### ✅ Good Signs
- Trades execute automatically when you refresh
- Open positions count increases (up to 5 max)
- Some trades close with profits (green +$XXX)
- Win rate stays above 50%
- Daily P/L shows positive days
- Status shows "Running" with recent timestamp

### ⚠️ Warning Signs
- No trades after multiple refreshes → Check your watchlist has stocks with data
- All positions held too long → May need to adjust target/stop percentages
- Win rate below 40% → Algorithm may need tuning
- Status shows "Paused" → Click "Resume" button

### ❌ Issues to Fix
- "No closed trades to export" after 24 hours → Algorithm too conservative
- Status says "not started yet" → Click "Start Simulation" button
- Cash = $0 with 0 positions → All capital tied up, may need to increase starting amount
- Errors in browser console → Check for JavaScript issues

## Trading Algorithm Summary

The simulator uses this logic every cycle:

### Entry Conditions (BUY)
- Stock must be on your watchlist
- Net score >= 4
- Market must be bullish (or neutral)
- Maximum 5 positions open
- At least 15% of cash available
- Sorted by net score (highest first)

### Exit Conditions (SELL)
Sells happen when **any** of these are true:
1. **Target hit**: Profit >= +3.5%
2. **Stop loss**: Loss <= -2%
3. **Score dropped**: Net score <= -2
4. **Time expired**: Held for 19.5+ market hours (3 days)
5. **Overbought**: Profit > 1.5% AND RSI > 70

### Setup Type Detection
- **Momentum**: Score >= 8
- **Range Break**: RSI < 40 with positive change
- **Trending**: Weekly position > 70% with positive MACD
- **VWAP Bounce**: Weekly position < 30% with positive change
- **News**: Price change > 2%
- **Auto Trade**: Default

## Troubleshooting

### Problem: No trades are executing
**Solutions:**
- Check your watchlist has stocks (go to Watchlist tab)
- Verify stocks are loading data (look for prices in Overview)
- Check if any stocks have net score >= 4
- Try clicking "Run Cycle Now" to force execution
- Make sure simulator is started (not just enabled)

### Problem: Only buying, never selling
**Solutions:**
- Prices may not have moved enough to hit targets/stops
- Wait longer (positions auto-sell after 3 days)
- Manually adjust learn parameters:
  - Reduce `targetPct` from 3.5% to 2%
  - Increase `stopPct` from -2% to -1%

### Problem: Trade log shows "No trades yet"
**Solutions:**
- Simulator not started → Click "Start Simulation"
- Market conditions not met → Refresh data and try "Run Cycle Now"
- No eligible stocks → Add more stocks to watchlist or lower buyMinScore

### Problem: Today P/L not updating
**Solutions:**
- Refresh the page to reload data
- Check that trades are actually closing (not just opening)
- Look at the Trade Log for SELL entries with P/L amounts

### Problem: Status shows "Paused"
**Solutions:**
- Click the **"Resume"** button
- Simulator is enabled but won't trade while paused

## Advanced: Adjust Strategy Parameters

If you want to tune the algorithm:

1. Open browser console (F12)
2. Check current settings:
   ```javascript
   S.sim.learn
   ```
3. Adjust parameters:
   ```javascript
   S.sim.learn.buyMinScore = 5;    // More selective entries
   S.sim.learn.targetPct = 5;      // Higher profit target
   S.sim.learn.stopPct = -1.5;     // Tighter stop loss
   S.sim.learn.holdDays = 2;       // Shorter holding period
   save(); // Save changes
   ```
4. Click "Run Cycle Now" to test new settings

## Expected Results (24 Hour Test)

With a properly configured watchlist (10-20 stocks):

| Metric | Expected Range | Good Performance |
|--------|---------------|------------------|
| Trades executed | 5-15 | 10-20 |
| Open positions | 2-5 | 3-5 |
| Win rate | 45-65% | 55%+ |
| Total P/L | -$500 to +$2000 | +$500+ |
| Avg trade P/L | -$50 to +$150 | +$50+ |
| Today trades | 3-8 | 5-10 |

**Note**: Results vary based on market conditions and watchlist quality.

## Success Checklist

- [ ] Simulator started with capital
- [ ] First BUY trade logged after refresh
- [ ] KPI cards showing real-time data
- [ ] Status shows "Running" with timestamp
- [ ] Open positions count > 0
- [ ] At least one SELL trade completed
- [ ] Today P/L shows non-zero value
- [ ] Win rate calculated (shows X%)
- [ ] Trade log has multiple entries
- [ ] CSV export works with statistics
- [ ] Daily performance table visible (after day 2)

---

**Ready to trade!** 🚀

Your Test Lab is now fully automated. It will evaluate your watchlist, make smart entry/exit decisions based on the algorithm, track all performance metrics, and give you detailed reports to learn from.

**Remember**: This is simulated trading. No real money is at risk. Use this to validate strategies and build confidence before going live.
