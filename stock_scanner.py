# ================================
# Large Cap Bullish Reversal Scanner
# ================================

import sys
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
DEPLOY_PCT = 0.60        # 60% deployed at entry
RESERVE_PCT = 0.40       # 40% held back to average down on dips
MAX_POSITIONS = 8

# Large-cap universe (expand as needed)
STOCKS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META",
    "TSLA", "BRK-B", "UNH", "XOM", "LLY", "JPM"
]

# --- FUNCTIONS ---

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="90d", interval="1d", progress=False, auto_adjust=True)

        # yfinance 1.x returns MultiIndex columns for single tickers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 35:
            return None

        close = df["Close"].squeeze()
        volume = df["Volume"].squeeze()
        low = df["Low"].squeeze()
        high = df["High"].squeeze()

        df["RSI"] = ta.momentum.RSIIndicator(close, window=14).rsi()

        macd = ta.trend.MACD(close)
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()

        df["EMA20"] = close.ewm(span=20).mean()
        df["Vol_Avg"] = volume.rolling(5).mean()

        latest = df.iloc[-1]

        week_low = float(low.tail(5).min())
        week_high = float(high.tail(5).max())

        if week_high == week_low:
            return None

        position = (float(latest["Close"]) - week_low) / (week_high - week_low)
        rsi = float(latest["RSI"])
        macd_diff = float(latest["MACD"]) - float(latest["MACD_signal"])
        price = float(latest["Close"])
        ema20 = float(latest["EMA20"])

        bullish_score = 0
        if position < 0.5:
            bullish_score += 2
        if 30 < rsi < 65:
            bullish_score += 2
        if macd_diff > 0:
            bullish_score += 2
        if price >= ema20 * 0.97:
            bullish_score += 2
        if position < 0.35:
            bullish_score += 1
        if 35 < rsi < 55:
            bullish_score += 1

        bearish_pressure = 0
        if position > 0.75:
            bearish_pressure += 2
        if rsi >= 68:
            bearish_pressure += 2
        if macd_diff < 0:
            bearish_pressure += 2
        if price < ema20 * 0.985:
            bearish_pressure += 2

        net_score = bullish_score - bearish_pressure
        if net_score >= 8:
            trend = "Strong Bullish"
        elif net_score >= 4:
            trend = "Bullish"
        elif net_score >= 1:
            trend = "Watch"
        elif net_score >= -2:
            trend = "Caution"
        else:
            trend = "Bearish"

        return {
            "Ticker": ticker,
            "Price": round(price, 2),
            "RSI": round(rsi, 2),
            "Position": round(position, 2),
            "MACD_diff": round(macd_diff, 4),
            "Bullish_Score": bullish_score,
            "Bearish_Pressure": bearish_pressure,
            "Net_Score": net_score,
            "Trend": trend,
        }

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

    return None


def market_trend_ok():
    """Check S&P 500 trend"""
    try:
        df = yf.download("^GSPC", period="30d", interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df["EMA20"] = df["Close"].ewm(span=20).mean()
        return float(df["Close"].iloc[-1]) >= float(df["EMA20"].iloc[-1])
    except:
        return True  # fallback


# --- MAIN ---

def main():
    print("\n🔍 Running Large Cap Bullish Scanner...\n")

    if not market_trend_ok():
        print("⚠️ Market trend is bearish (S&P below 20 EMA). Rankings are still shown below, but position sizing should stay defensive.\n")

    results = []

    for stock in STOCKS:
        res = analyze_stock(stock)
        if res:
            results.append(res)

    if not results:
        print("❌ Could not fetch data for any stocks.\n")
        return

    df = pd.DataFrame(results).sort_values(
        by=["Net_Score", "Bullish_Score", "Bearish_Pressure", "Ticker"],
        ascending=[False, False, True, True],
    )

    print("✅ Ranked From Most Bullish To Most Bearish:\n")
    print(df.to_string(index=False))
    print("\n📘 Ranking model:")
    print("- Bullish score rewards RSI recovery, positive MACD, support-zone pricing, and price holding near EMA20")
    print("- Bearish pressure penalizes overheated RSI, negative MACD, stretched weekly position, and price falling below EMA20")
    print("- Net score = Bullish score - Bearish pressure")

    top = df[df["Net_Score"] >= 4].head(MAX_POSITIONS)
    if top.empty:
        print("\n⚠️ No strong setups today. Showing ranked watchlist above for reference.")
    else:
        deploy_capital = CAPITAL * DEPLOY_PCT
        reserve_capital = CAPITAL * RESERVE_PCT
        n = len(top)
        total_score = top["Score"].sum()

        print(f"\n💼 Capital Plan: ${CAPITAL:,.0f} total")
        print(f"   ├─ Deploy now (60%): ${deploy_capital:,.0f} across {n} position(s)")
        print(f"   └─ Reserve (40%):    ${reserve_capital:,.0f} — held to average down on dips\n")
        total_score = top["Net_Score"].sum()
        print(f"{'Ticker':<8} {'Net':>5} {'Bull':>5} {'Bear':>5} {'Price':>8} {'Entry $':>12} {'Shares':>7} {'Stop Loss':>10} {'Target':>10}")
        print("-" * 84)
        for _, row in top.iterrows():
            weight = row["Net_Score"] / total_score
            entry_amount = deploy_capital * weight
            shares = int(entry_amount / row["Price"])
            stop = row["Price"] * 0.98
            target = row["Price"] * 1.035
            print(f"{row['Ticker']:<8} {int(row['Net_Score']):>5} {int(row['Bullish_Score']):>5} {int(row['Bearish_Pressure']):>5} {row['Price']:>8.2f} {entry_amount:>12,.0f} {shares:>7} {stop:>10.2f} {target:>10.2f}")

        print(f"\n🔄 Reserve Usage (${reserve_capital:,.0f}):")
        print("   If a stock drops 2–4% after entry, use reserve to average down.")
        reserve_per_stock = reserve_capital / n
        for _, row in top.iterrows():
            avg_down_price = row["Price"] * 0.97   # buy more at -3%
            avg_shares = int(reserve_per_stock / avg_down_price)
            print(f"   {row['Ticker']}: avg down at ~${avg_down_price:.2f} with ~${reserve_per_stock:,.0f} → {avg_shares} more shares")

    print("\n📈 Strategy:")
    print("- Entry: 60% capital now, score-weighted")
    print("- Average down: use 40% reserve if stock dips 2-4% after entry")
    print("- Target: +3.5% | Stop Loss: -2%")
    print("- Hold: 1–3 days")

    print("\n⚠️ Reminder: This is not guaranteed. Use risk management.\n")


if __name__ == "__main__":
    main()