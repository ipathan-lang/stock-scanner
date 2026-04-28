# 📈 IntelliMarket Analyst

**AI-powered stock scanning and portfolio management with congressional trading intelligence**

[![Live App](https://img.shields.io/badge/Live-App-brightgreen)](https://ipathan-lang.github.io/stock-scanner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🚀 Features

### 📊 **Stock Scanner**
- Real-time technical analysis with 15+ indicators
- RSI, MACD, Moving Averages, Bollinger Bands
- Machine learning-based scoring system
- Bullish/Bearish signal classification

### 🏛️ **Congressional Trading Intelligence**
- Track what Congress members are buying/selling
- Insider trading insights (legal disclosures)
- Filter by party, trade size, and recent activity
- See which politicians are most active traders
- [Full Documentation →](CONGRESSIONAL_TRADES.md)

### ⏰ **Golden Hour Trading**
- Opening Range Breakout (ORB) analysis
- Pre-market movers and volume analysis
- Best time windows for day trading (9:30-10:30 AM)
- Real-time momentum tracking
- [Full Documentation →](GOLDEN_HOUR_TRADING.md)

### 📉 **Trading Performance Analyzer**
- Export trades from portfolio/test mode
- Comprehensive performance metrics
- Win rate, profit factor, expectancy analysis
- Pattern detection by setup type and time
- Actionable recommendations for improvement
- [Full Documentation →](TRADING_ANALYSIS.md) | [Quick Start →](QUICKSTART_TRADING_ANALYSIS.md)

### 🎓 **Trade Journal & Coaching System** ⭐ NEW
- Analyze individual trades for rule adherence
- Detect behavioral patterns (revenge trading, fear-based exits)
- Get specific coaching feedback and action items
- Real-time integration with portfolio exports
- Identify emotional triggers and discipline issues
- [Full Guide →](TRADE_COACHING.md) | [Quick Start →](COACHING_README.md)

### 💼 **Portfolio Management**
- Track positions with real-time P&L
- Test mode for risk-free backtesting
- Automated trading simulation
- Machine learning strategy optimization

### 🤖 **AI Trade Coach**
- Plain-language buy/sell/hold recommendations
- Optimal entry timing suggestions
- Risk management guidance
- Market context awareness

### 📰 **News & Sentiment**
- Earnings dates and analyst ratings
- Market sentiment tracking (bull/bear)
- News-driven price moves
- Social media buzz integration

### 📱 **TradingView Integration**
- 2-bar trailing stop strategy (Pine Script v5)
- Visual entry/exit markers
- Customizable moving averages
- Backtest on any timeframe
- [Pine Script File →](trading_strategy_2bar_trailing.pine)

---

## 🎯 Quick Start

### 1. Open the App

**Live Version**: https://ipathan-lang.github.io/stock-scanner/

No installation needed - runs entirely in your browser!

### 2. Add Stocks to Watchlist

- Click "⚙️ Settings" → "Manage Watchlist"
- Add your favorite tickers (e.g., TSLA, NVDA, AAPL, MSFT)
- Click "Refresh Data" to scan all stocks

### 3. Explore Features

**Congressional Trades**:
- Check "📊 Congressional Trading" section
- See what Nancy Pelosi, Dan Crenshaw, and others are buying
- Filter by party (Democrat/Republican)

**Golden Hour Analysis**:
- Check "☀️ Golden Hour Trading" section
- See pre-market movers and opening range breakouts
- Best window: 9:30-10:30 AM EST

**Portfolio Tracking**:
- Click "+ Add Position" to track your real trades
- Or enable "Test Mode" for automated paper trading
- Export trades to analyze performance

**AI Coach**:
- View "🤖 Trade Coach" section
- Get plain-language buy/sell/hold guidance
- Optimal timing recommendations

---

## 📊 Trading Analysis Workflow

### Step 1: Enable Test Mode
```
1. Click "Test Mode: OFF" to enable
2. Click "🔄 Auto-Refresh: OFF" to enable
3. Let simulation run for 1-2 weeks
```

### Step 2: Export Trade History
```
1. Click "📊 Export Trades" button
2. File downloads as trades_YYYY-MM-DD.csv
```

### Step 3: Analyze Performance
```powershell
# Install dependencies (one time)
pip install pandas numpy

# Run analyzer
cd Downloads\stock-scanner
python analyze_trades.py trades_2026-04-28.csv
```

### Step 4: Review Results
```
✅ Check win rate (goal: >50%)
✅ Check profit factor (goal: >1.5)
✅ Identify best setup types
✅ Identify best time windows
✅ Follow recommendations
```

**Full Guide**: [TRADING_ANALYSIS.md](TRADING_ANALYSIS.md)

---

## 🛠️ Technical Details

### Built With
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Data Storage**: Browser localStorage
- **Styling**: CSS Grid, Flexbox, modern gradients
- **API**: Alpha Vantage (stock data)
- **Deployment**: GitHub Pages

### Data Sources
- Stock prices and technicals: Alpha Vantage API
- Congressional trades: API scraping of official disclosures
- News sentiment: Integrated news feeds
- Market data: Real-time and historical data

### Browser Storage Keys
- `ss_port` - Real portfolio positions
- `ss_sim` - Test mode simulation data
- `ss_watch` - Watchlist tickers
- `ss_config` - User settings and API key

### Performance Analyzer Tech Stack
- **Language**: Python 3
- **Libraries**: pandas (data analysis), numpy (calculations)
- **Input**: CSV export from app
- **Output**: Terminal-based comprehensive report

### Trade Coaching System
- **Language**: Python 3
- **Analysis**: Rule adherence checking, pattern detection
- **Patterns Detected**: Revenge trading, fear-based exits, over-trading
- **Output**: Specific coaching feedback and action items

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| [CONGRESSIONAL_TRADES.md](CONGRESSIONAL_TRADES.md) | Full Congressional Trading Intelligence guide |
| [GOLDEN_HOUR_TRADING.md](GOLDEN_HOUR_TRADING.md) | Opening Range Breakout (ORB) analysis guide |
| [TRADING_ANALYSIS.md](TRADING_ANALYSIS.md) | Complete trading performance analysis documentation |
| [QUICKSTART_TRADING_ANALYSIS.md](QUICKSTART_TRADING_ANALYSIS.md) | Quick reference for trading analysis |
| [TRADE_COACHING.md](TRADE_COACHING.md) | **NEW** - Trade journal and coaching system guide |
| [COACHING_README.md](COACHING_README.md) | **NEW** - Quick start for trade coaching |
| [PORTFOLIO_ANALYSIS_REPORT.md](PORTFOLIO_ANALYSIS_REPORT.md) | Sample analysis report with coaching |
| [trading_strategy_2bar_trailing.pine](trading_strategy_2bar_trailing.pine) | TradingView Pine Script strategy |

---

## 🎓 Learning Resources

### For Beginners
1. Start with Test Mode to practice without risk
2. Focus on high net score stocks (8+)
3. Trade only during Golden Hour (9:30-10:30 AM)
4. Use Range Break and Momentum setups
5. Export and analyze trades weekly

### For Intermediate Traders
1. Track Congressional trades for insider insights
2. Combine multiple signals (ORB + Congressional + Score)
3. Optimize entry timing using Golden Hour analysis
4. Analyze performance by setup type and time
5. Identify and eliminate losing patterns
6. **Use trade journal to check rule adherence**
7. **Detect emotional trading patterns (revenge, fear)**

### For Advanced Traders
1. Use TradingView Pine Script for precise entries
2. Backtest strategies with historical data
3. Optimize position sizing based on win rate
4. Build custom scoring models
5. Automate trade execution (requires broker API)

---

## 📈 Example Results

### Sample Trading Performance (51 trades)
```
✅ Win Rate: 64.71%
✅ Profit Factor: 2.28
✅ Total P&L: $4,854.50
✅ Best Setup: Range Break (100% win rate)
✅ Best Time: 9:30-10:30 AM (95% win rate)
```

**Strategy**: Range Break setups during Golden Hour = High win rate

---

## 🔧 Setup & Configuration

### 1. Get API Key (Free)
1. Visit https://www.alphavantage.co/support/#api-key
2. Sign up for free API key
3. Open app → Settings → Paste API key
4. Click "Save API Key"

### 2. Add Watchlist
```
Settings → Manage Watchlist → Add tickers
Example: TSLA, NVDA, AAPL, MSFT, AMD, META, GOOGL
```

### 3. Enable Features
- **Test Mode**: Safe paper trading with real data
- **Auto-Refresh**: Automatic 10-second data updates
- **Congressional Trades**: Track insider activity
- **Golden Hour**: Pre-market analysis

---

## 🚨 Disclaimers

⚠️ **This tool is for educational and informational purposes only.**

- Not financial advice
- Past performance does not guarantee future results
- Trading involves risk of loss
- Congressional trading data is based on public disclosures (delayed)
- Always do your own research (DYOR)
- Never invest more than you can afford to lose

**Test Mode Recommended**: Practice with paper trading before risking real money.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Live App**: https://ipathan-lang.github.io/stock-scanner/
- **GitHub**: https://github.com/ipathan-lang/stock-scanner
- **Issues**: https://github.com/ipathan-lang/stock-scanner/issues
- **Discussions**: https://github.com/ipathan-lang/stock-scanner/discussions

---

## 🙏 Acknowledgments

- Alpha Vantage for stock data API
- TradingView for charting inspiration
- Congressional trading disclosure websites
- Open source trading community

---

## 📞 Support

**Found a bug?** [Open an issue](https://github.com/ipathan-lang/stock-scanner/issues)

**Feature request?** [Start a discussion](https://github.com/ipathan-lang/stock-scanner/discussions)

**Questions?** Check the documentation files above.

---

**Built with ❤️ for traders who want to make smarter decisions**
