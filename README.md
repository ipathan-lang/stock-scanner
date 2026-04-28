# IntelliMarket Analyst

**Live Platform**: https://ipathan-lang.github.io/stock-scanner/

Web-based trading platform for portfolio tracking, automated test simulations, and stock analysis.

## Features

- **Portfolio Tracking**: Monitor real positions with P&L and insights
- **Test Lab**: Automated intraday simulator with algorithmic trading
- **Stock Analysis**: Net score system (-10 to +10) based on RSI, MACD, EMA20, weekly position
- **Performance Analytics**: Export trades to CSV, analyze with Python tools
- **Real-time Validation**: Test predictions through simulated trading before going live

## Quick Start

1. Visit https://ipathan-lang.github.io/stock-scanner/
2. Add stocks to watchlist
3. Go to Test Lab tab → Start Simulation
4. Click Refresh to trigger automated trading
5. Export CSV after 5-7 days → Analyze performance

## Python Tools

```bash
# Analyze trade performance
python analyze_trades.py sim_trades_2024-01-15.csv

# Get behavioral coaching
python trade_journal_coach.py trades.csv
```

## Documentation

All platform knowledge is captured in the **[Copilot Skill](.github/skills/stock-scanner/SKILL.md)**:
- Architecture & code structure
- Scoring algorithm details
- Simulator logic & entry/exit rules
- Validation protocols
- Debugging guide
- How to modify & extend

## Stack

- Pure HTML/CSS/JavaScript (single-page app)
- localStorage for data persistence
- Yahoo Finance / Alpha Vantage APIs
- Python for analysis (pandas, numpy)

---

**Trading Platform + AI Assistant = Validated Predictions**
