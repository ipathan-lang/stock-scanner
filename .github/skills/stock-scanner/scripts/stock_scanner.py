# ================================
# Large Cap Bullish Reversal Scanner
# ================================
# Skill: stock-scanner
# See: ../ SKILL.md for full documentation
# ================================

import sys
import os
import subprocess

# --- Auto-install missing packages ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yfinance as yf
    import pandas as pd
    import ta
except ImportError:
    print("Installing required packages...")
    install("yfinance")
    install("pandas")
    install("ta")
    import yfinance as yf
    import pandas as pd
    import ta

# --- CONFIG ---
CAPITAL = 400000
DEPLOY_PCT = 0.60        # 60% deployed at entry (score-weighted)
RESERVE_PCT = 0.40       # 40% held back to average down on dips
MAX_POSITIONS = 8

# Large-cap universe — expand this list to get more results
STOCKS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META",
    "TSLA", "BRK-B", "UNH", "XOM", "LLY", "JPM"
]

# --- SCORING ---
# Each condition adds points; max score = 10
# Score >= 4 → included in allocation plan
SCORE_THRESHOLD = 4

# --- FUNCTIONS ---

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False, auto_adjust=True)

        # yfinance 1.x returns MultiIndex columns for single tickers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 26:
            return None

        close  = df["Close"].squeeze()
        volume = df["Volume"].squeeze()
        low    = df["Low"].squeeze()
        high   = df["High"].squeeze()

        # Indicators
        df["RSI"]        = ta.momentum.RSIIndicator(close, window=14).rsi()
        macd             = ta.trend.MACD(close)
        df["MACD"]       = macd.macd()
        df["MACD_signal"]= macd.macd_signal()
        df["EMA20"]      = close.ewm(span=20).mean()
        df["Vol_Avg"]    = volume.rolling(5).mean()

        latest = df.iloc[-1]

        week_low  = float(low.tail(5).min())
        week_high = float(high.tail(5).max())
        if week_high == week_low:
            return None

        position  = (float(latest["Close"]) - week_low) / (week_high - week_low)
        rsi       = float(latest["RSI"])
        macd_diff = float(latest["MACD"]) - float(latest["MACD_signal"])
        price     = float(latest["Close"])
        ema20     = float(latest["EMA20"])

        # --- Scoring (max 10) ---
        score = 0
        if position < 0.5:      score += 2   # lower half of weekly range
        if 30 < rsi < 65:       score += 2   # RSI not overbought/oversold
        if macd_diff > 0:       score += 2   # MACD bullish crossover
        if price >= ema20*0.97: score += 2   # price near or above EMA20
        if position < 0.35:     score += 1   # bonus: deep dip
        if 35 < rsi < 55:       score += 1   # bonus: RSI recovery zone

        return {
            "Ticker"   : ticker,
            "Price"    : round(price, 2),
            "RSI"      : round(rsi, 2),
            "Position" : round(position, 2),
            "MACD_diff": round(macd_diff, 4),
            "Score"    : score
        }

    except Exception as e:
        print(f"  ⚠ Error processing {ticker}: {e}")
    return None


def write_summary(lines):
    """Write markdown lines to GitHub Actions Job Summary if available."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def market_trend_ok():
    """Returns True if S&P 500 is above its 20 EMA (bullish market)."""
    try:
        df = yf.download("^GSPC", period="30d", interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df["EMA20"] = df["Close"].ewm(span=20).mean()
        return float(df["Close"].iloc[-1]) >= float(df["EMA20"].iloc[-1])
    except:
        return True  # fallback: assume bullish if data unavailable


# --- MAIN ---

def main():
    print("\n🔍 Running Large Cap Bullish Scanner...\n")

    bearish = not market_trend_ok()
    if bearish:
        print("⚠️  Market trend is BEARISH (S&P 500 below 20 EMA).")
        print("    Use caution — showing scan results anyway.\n")

    results = []
    for stock in STOCKS:
        res = analyze_stock(stock)
        if res:
            results.append(res)

    if not results:
        print("❌ Could not fetch data for any stocks.\n")
        write_summary(["## ❌ No data", "Could not fetch data for any stocks."])
        return

    market_banner = ["## ⚠️ Market is BEARISH", "S&P 500 is below its 20 EMA — use caution with new long positions.", ""] if bearish else []

    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)

    print("✅ All Stocks — Ranked by Bullish Score:\n")
    print(df.to_string(index=False))

    # --- Allocation Plan ---
    top = df[df["Score"] >= SCORE_THRESHOLD].head(MAX_POSITIONS)

    if top.empty:
        print(f"\n⚠️  No stocks scored ≥ {SCORE_THRESHOLD} today.")
        print("    Market may be extended. Watch the top of the list for Monday.")
        write_summary(market_banner + [
            "## ⚠️ No qualifying stocks today",
            f"No stocks scored ≥ {SCORE_THRESHOLD}. Market may be extended.",
            "",
            "### All Stocks — Ranked by Score",
            "| Ticker | Score | Price | RSI | Position | MACD diff |",
            "|--------|------:|------:|----:|---------:|----------:|",
        ] + [
            f"| {r['Ticker']} | {int(r['Score'])} | ${r['Price']:.2f} | {r['RSI']:.1f} | {r['Position']:.2f} | {r['MACD_diff']:.4f} |"
            for _, r in df.iterrows()
        ])
        return

    deploy_capital  = CAPITAL * DEPLOY_PCT
    reserve_capital = CAPITAL * RESERVE_PCT
    n               = len(top)
    total_score     = top["Score"].sum()

    print(f"\n{'─'*65}")
    print(f"💼 Capital Plan: ${CAPITAL:,.0f} total")
    print(f"   ├─ Deploy now  (60%): ${deploy_capital:,.0f}  →  {n} position(s)")
    print(f"   └─ Reserve     (40%): ${reserve_capital:,.0f}  →  average down on dips")
    print(f"{'─'*65}")
    print(f"\n{'Ticker':<8} {'Score':>5} {'Price':>8} {'Entry $':>12} {'Shares':>7} {'Stop':>9} {'Target':>9}")
    print("─" * 65)

    for _, row in top.iterrows():
        weight       = row["Score"] / total_score
        entry_amount = deploy_capital * weight
        shares       = int(entry_amount / row["Price"])
        stop         = row["Price"] * 0.98    # -2%
        target       = row["Price"] * 1.035   # +3.5%
        print(f"{row['Ticker']:<8} {int(row['Score']):>5} {row['Price']:>8.2f}"
              f" {entry_amount:>12,.0f} {shares:>7} {stop:>9.2f} {target:>9.2f}")

    # --- Reserve breakdown ---
    reserve_per_position = reserve_capital / n
    print(f"\n{'─'*65}")
    print(f"🔄 Reserve Usage — ${reserve_capital:,.0f} split across {n} positions")
    print(f"   Deploy if stock drops 2–4% after your entry:\n")
    for _, row in top.iterrows():
        avg_price  = row["Price"] * 0.97
        avg_shares = int(reserve_per_position / avg_price)
        print(f"   {row['Ticker']:<6} avg down at ~${avg_price:.2f}"
              f"  with ~${reserve_per_position:,.0f}  →  {avg_shares} more shares")

    print(f"\n{'─'*65}")
    print("📈 Strategy Summary:")
    print("   • Entry:        60% capital, score-weighted per position")
    print("   • Average down: 40% reserve if stock dips 2–4% post-entry")
    print("   • Stop Loss:    -2% from entry price")
    print("   • Target:       +3.5% from entry price")
    print("   • Hold period:  1–3 trading days")
    print(f"{'─'*65}")
    print("\n⚠️  This is not financial advice. Always use risk management.\n")

    # --- GitHub Actions Job Summary ---
    summary = market_banner + [
        f"## 📈 Stock Scanner — {pd.Timestamp.today().strftime('%Y-%m-%d')}",
        "",
        f"**Capital:** ${CAPITAL:,.0f}  |  **Deploy (60%):** ${deploy_capital:,.0f}  |  **Reserve (40%):** ${reserve_capital:,.0f}",
        "",
        "### 🎯 Entry Positions",
        "| Ticker | Score | Price | Entry $ | Shares | Stop | Target |",
        "|--------|------:|------:|--------:|-------:|-----:|-------:|",
    ]
    for _, row in top.iterrows():
        weight       = row["Score"] / total_score
        entry_amount = deploy_capital * weight
        shares       = int(entry_amount / row["Price"])
        stop         = row["Price"] * 0.98
        target       = row["Price"] * 1.035
        summary.append(
            f"| {row['Ticker']} | {int(row['Score'])} | ${row['Price']:.2f}"
            f" | ${entry_amount:,.0f} | {shares} | ${stop:.2f} | ${target:.2f} |"
        )
    summary += [
        "",
        "### 🔄 Reserve / Average-Down Plan",
        "| Ticker | Avg-Down Price | Reserve $ | Extra Shares |",
        "|--------|---------------:|----------:|-------------:|",
    ]
    for _, row in top.iterrows():
        avg_price  = row["Price"] * 0.97
        avg_shares = int(reserve_per_position / avg_price)
        summary.append(
            f"| {row['Ticker']} | ${avg_price:.2f} | ${reserve_per_position:,.0f} | {avg_shares} |"
        )
    summary += [
        "",
        "### 📊 All Stocks — Ranked by Score",
        "| Ticker | Score | Price | RSI | Position | MACD diff |",
        "|--------|------:|------:|----:|---------:|----------:|",
    ]
    for _, r in df.iterrows():
        summary.append(
            f"| {r['Ticker']} | {int(r['Score'])} | ${r['Price']:.2f}"
            f" | {r['RSI']:.1f} | {r['Position']:.2f} | {r['MACD_diff']:.4f} |"
        )
    summary.append("\n> ⚠️ Not financial advice. Always use risk management.")
    write_summary(summary)


if __name__ == "__main__":
    main()
