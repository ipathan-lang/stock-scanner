# Test Lab Automation Upgrade

## Overview
The Test Lab has been upgraded from a daily simulator to a **fully automated intraday trading system** that trades continuously throughout market hours, tracks detailed performance metrics, and provides comprehensive profit/loss analysis.

## Key Improvements

### 1. **Intraday Trading**
- **Before**: Ran once per day only
- **After**: Executes multiple trading cycles throughout the day (every refresh during market hours 9:30 AM - 4:00 PM EST)
- **Throttle**: Minimum 15-minute gap between cycles to prevent over-trading
- **How it works**: Click "Refresh" button or it runs automatically when market data updates

### 2. **Enhanced Entry Logic**
- Scans top 5 stocks (increased from 3) with net score >= 4
- Uses 15% capital per trade (optimized from 20%) for better diversification
- Maximum 5 concurrent positions
- Intelligent setup type detection:
  - **Momentum**: Score >= 8
  - **Range Break**: RSI < 40 with positive change
  - **Trending**: Weekly position > 70% with positive MACD
  - **VWAP Bounce**: Weekly position < 30% with positive change
  - **News**: Price change > 2%

### 3. **Smart Exit Rules**
- **Target profit**: +3.5% (configurable)
- **Stop loss**: -2% (configurable)
- **Score deterioration**: Exit if net score drops to -2 or below
- **Time limit**: Exit after holding period expires (default 3 days = 19.5 market hours)
- **Overbought exit**: Take profit if up 1.5%+ with RSI > 70

### 4. **Detailed Profit/Loss Tracking**

#### Real-Time KPIs
- Total equity and available cash
- Open positions count
- Total P/L ($ and %)
- Overall win rate
- **Today's P/L** (new)
- **Today's trade count with W/L breakdown** (new)
- Current strategy parameters

#### Daily Performance Dashboard
Shows last 7 days with:
- Date
- Number of trades
- Win/Loss split
- Win rate %
- Day P/L ($)
- Day return (%)
- End equity

#### Trade Log Enhancements
- Shows last 50 trades (reversed for most recent first)
- Date/time with hour and minute precision
- Stock ticker (bold)
- BUY/SELL action (color-coded)
- Entry/Exit price
- Detailed reason (exit conditions, setup type, scores)
- Individual P/L for each trade

### 5. **Enhanced Data Persistence**

New tracking fields in `S.sim`:
```javascript
{
  todayTrades: [],      // Today's completed trades
  todayPnL: 0,          // Today's profit/loss
  dayStartEquity: 0,    // Equity at start of day
  lastRunTime: null,    // Timestamp of last cycle
  dailyHistory: [],     // 30 days of daily summaries
  // ... existing fields
}
```

Position tracking includes:
- Setup type and entry conditions
- Entry score, RSI, MACD
- Precise timestamps
- Hours held (not just days)

### 6. **CSV Export Improvements**

Enhanced export with coaching-ready format:
```
Symbol, Entry Date, Entry Time, Entry Price, Exit Date, Exit Time, 
Exit Price, Shares, P&L, P&L %, Setup Type, Exit Reason, Hours Held
```

Export includes comprehensive statistics:
- Win rate with W/L breakdown
- Total P/L
- Average win vs. average loss
- Profit factor (avg win / avg loss)

### 7. **User Experience Improvements**

#### Updated Controls
- **Start Simulation**: Initialize with starting capital
- **Pause/Resume**: Toggle automated trading
- **Run Cycle Now**: Force immediate execution
- **Reset**: Clear all data (with confirmation)
- **Export JSON**: Full simulator state
- **Export CSV**: Trade history for Python analyzers

#### Status Indicators
- **Running**: Green dot with last trade time
- **Paused**: Pause symbol with explanation
- Color-coded status for quick visibility

#### Better Descriptions
- Clear explanation of intraday trading
- Emphasis on algorithm-based decisions
- Reminder that no real money is at risk

## How It Works

### Trading Cycle Flow

1. **Check Conditions**
   - Simulator must be started and enabled
   - At least 15 minutes since last cycle (unless forced)
   - New day detection resets daily tracking

2. **Sell Pass** (Execute Exits First)
   - Evaluate each open position
   - Check exit conditions (target, stop, score, time, overbought)
   - Execute sell with detailed reason
   - Update cash, P&L, trade history
   - Log transaction

3. **Buy Pass** (Look for New Opportunities)
   - Get top 5 stocks from watchlist by net score
   - Filter for score >= 4 and bullish market
   - Check available cash (15% per trade)
   - Determine setup type
   - Execute buy and log entry conditions

4. **Daily/Weekly Summaries**
   - At market close: Calculate day's performance
   - Store daily history (30-day rolling window)
   - On Sundays: Create weekly snapshot
   - Apply machine learning adjustments

5. **Save & Render**
   - Persist to localStorage (`ss_sim`)
   - Update all UI elements
   - Show real-time status

## Configuration

### Strategy Parameters (in `S.sim.learn`)
```javascript
{
  buyMinScore: 4,      // Minimum net score to buy
  sellMaxScore: -2,    // Exit if score drops to this
  holdDays: 3,         // Max holding period (days)
  stopPct: -2,         // Stop loss percentage
  targetPct: 3.5       // Target profit percentage
}
```

These parameters are **automatically adjusted** by the `simApplyLearning()` function based on recent performance.

## Testing the Simulator

### Initial Setup
1. Navigate to **Test Lab** tab
2. Enter starting capital (e.g., $50,000)
3. Click **Start Simulation**
4. Ensure your watchlist has stocks configured

### Trigger Trading
- Click **"Run Cycle Now"** to execute immediately
- Click **"Refresh"** button to update market data and trigger cycle
- Wait 15+ minutes and refresh again for next cycle

### Monitor Performance
- Watch KPI cards update in real-time
- Check "Today's P/L" and trade count
- Review daily performance table (last 7 days)
- Scroll through recent trades log

### Export and Analyze
1. Click **"Export CSV"** after multiple trades
2. Run through Python analyzers:
   ```bash
   python analyze_trades.py sim_trades_2024-01-15.csv
   python trade_journal_coach.py sim_trades_2024-01-15.csv
   ```

## Comparison: Before vs. After

| Feature | Before | After |
|---------|--------|-------|
| Trading frequency | Once per day | Multiple times per day |
| Trade execution | Manual refresh only | Automatic + manual |
| P&L tracking | Weekly only | Daily + total |
| Position limit | 3 stocks | 5 stocks |
| Entry detail | Basic | Full setup context |
| Exit reasons | Generic | Specific condition |
| Time tracking | Days only | Hours and minutes |
| Daily summary | None | Last 7 days table |
| Win/Loss stats | Weekly | Today + overall |
| Export format | Basic CSV | Coaching-ready CSV |
| Status indicator | Text only | Color-coded with time |

## Benefits

### For Day Traders
- **Realistic simulation**: Mirrors actual intraday behavior
- **Multiple setups**: Tests different entry patterns
- **Quick feedback**: See results within hours, not days

### For Analysis
- **Rich data**: Every trade has context (setup type, exit reason, scores)
- **Daily summaries**: Track performance trends
- **CSV export**: Compatible with Python analyzers

### For Learning
- **Algorithm transparency**: See exactly why trades are made
- **Performance metrics**: Win rate, profit factor, avg P&L
- **Coaching integration**: Export directly to coaching tools

## Next Steps

1. **Run simulation for at least 5 days** to collect meaningful data
2. **Export CSV** and analyze with Python tools
3. **Review daily summaries** to identify patterns
4. **Adjust strategy parameters** if needed (buyMinScore, targetPct, etc.)
5. **Compare setup types** to see which works best
6. **Track win rate trends** to validate strategy improvements

## Technical Notes

- All data persists in `localStorage` key `ss_sim`
- Simulator state includes 30 days of daily history
- Machine learning adjusts parameters based on last 10 trades
- Market hours check ensures realistic trading times
- Throttle prevents excessive API calls and over-trading

---

**Happy Testing!** 🧪📈

Your Test Lab is now a powerful tool for validating strategies, learning from algorithmic decisions, and building confidence before risking real capital.
