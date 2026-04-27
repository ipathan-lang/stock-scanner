# ================================
# Large Cap Bullish Reversal Scanner
# ================================
# Skill: stock-scanner
# See: ../ SKILL.md for full documentation
# ================================

import sys
import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
# Each condition adds points; max score = 14 (10 technical + 4 earnings)
# Score >= 4 → included in allocation plan
SCORE_THRESHOLD = 4

# --- FUNCTIONS ---

def get_earnings_data(ticker):
    """
    Returns dict with:
      earnings_in_days  : int or None  (days until next earnings; None if unknown)
      last_eps_surprise : float or None (actual - estimate; positive = beat)
      last_eps_beat     : bool          (True if last earnings beat estimate)
    """
    try:
        t = yf.Ticker(ticker)

        # --- Next earnings date ---
        earnings_in_days = None
        cal = t.calendar
        if cal is not None and not cal.empty:
            # calendar is a DataFrame with dates as columns; first column = next event
            earnings_date = cal.iloc[0, 0] if hasattr(cal.iloc[0, 0], 'date') else None
            if earnings_date:
                delta = (pd.Timestamp(earnings_date).date() - pd.Timestamp.today().date()).days
                earnings_in_days = delta
        else:
            # Fallback: earnings_dates property
            ed = t.earnings_dates
            if ed is not None and not ed.empty:
                future = ed[ed.index > pd.Timestamp.today()]
                if not future.empty:
                    earnings_in_days = (future.index[-1].date() - pd.Timestamp.today().date()).days

        # --- Last earnings EPS surprise ---
        last_eps_beat = False
        last_eps_surprise = None
        ed = t.earnings_dates
        if ed is not None and not ed.empty:
            past = ed[
                (ed.index <= pd.Timestamp.today()) &
                ed["EPS Actual"].notna() &
                ed["EPS Estimate"].notna()
            ]
            if not past.empty:
                last = past.iloc[0]  # most recent past earnings
                actual   = float(last["EPS Actual"])
                estimate = float(last["EPS Estimate"])
                last_eps_surprise = round(actual - estimate, 4)
                last_eps_beat = actual > estimate

        return {
            "earnings_in_days" : earnings_in_days,
            "last_eps_surprise": last_eps_surprise,
            "last_eps_beat"    : last_eps_beat,
        }
    except Exception as e:
        return {"earnings_in_days": None, "last_eps_surprise": None, "last_eps_beat": False}


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

        # --- Scoring (max 10 technical + 4 earnings = 14) ---
        score = 0
        if position < 0.5:      score += 2   # lower half of weekly range
        if 30 < rsi < 65:       score += 2   # RSI not overbought/oversold
        if macd_diff > 0:       score += 2   # MACD bullish crossover
        if price >= ema20*0.97: score += 2   # price near or above EMA20
        if position < 0.35:     score += 1   # bonus: deep dip
        if 35 < rsi < 55:       score += 1   # bonus: RSI recovery zone

        # --- Earnings filters (+4 pts) ---
        edata = get_earnings_data(ticker)
        days_to_earnings = edata["earnings_in_days"]
        last_beat        = edata["last_eps_beat"]
        eps_surprise     = edata["last_eps_surprise"]

        earnings_soon = (
            days_to_earnings is not None and 0 <= days_to_earnings <= 5
        )

        # Skip stocks where last earnings were a miss
        if edata["last_eps_surprise"] is not None and not last_beat:
            return None  # last earnings were bad — exclude

        if last_beat:        score += 2   # last earnings beat estimate
        if earnings_soon:    score += 2   # earnings coming in next 5 days

        return {
            "Ticker"         : ticker,
            "Price"          : round(price, 2),
            "RSI"            : round(rsi, 2),
            "Position"       : round(position, 2),
            "MACD_diff"      : round(macd_diff, 4),
            "Score"          : score,
            "EPS_Surprise"   : eps_surprise,
            "Earnings_In"    : days_to_earnings,
            "Earnings_Soon"  : earnings_soon,
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


def send_email(subject, html_body):
    """Send scan results via Gmail. Reads credentials from environment variables."""
    sender    = os.environ.get("EMAIL_SENDER")
    password  = os.environ.get("EMAIL_PASSWORD")
    recipients = os.environ.get("EMAIL_RECIPIENTS", "")  # comma-separated

    if not sender or not password or not recipients:
        return  # silently skip if not configured

    to_list = [r.strip() for r in recipients.split(",") if r.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = ", ".join(to_list)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_list, msg.as_string())
        print(f"📧 Email sent to: {', '.join(to_list)}")
    except Exception as e:
        print(f"⚠️  Email failed: {e}")


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

    # Format earnings columns for display
    df["EPS_Beat"]   = df["last_eps_beat"].map({True: "✅", False: "❌"}) if "last_eps_beat" in df.columns else "?"
    display_cols = ["Ticker", "Price", "RSI", "Position", "MACD_diff", "Score", "EPS_Surprise", "Earnings_In"]

    print("✅ All Stocks — Ranked by Bullish Score (earnings-filtered):\n")
    print(df[display_cols].to_string(index=False))

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

    print(f"\n{'─'*80}")
    print(f"💼 Capital Plan: ${CAPITAL:,.0f} total")
    print(f"   ├─ Deploy now  (60%): ${deploy_capital:,.0f}  →  {n} position(s)")
    print(f"   └─ Reserve     (40%): ${reserve_capital:,.0f}  →  average down on dips")
    print(f"{'─'*80}")
    print(f"\n{'Ticker(Code)':<12} {'Score':>5} {'Price':>8} {'Entry $':>12} {'Shares':>7} {'Stop (Stop loss)':>17} {'Target':>9}")
    print("─" * 80)

    for _, row in top.iterrows():
        weight       = row["Score"] / total_score
        entry_amount = deploy_capital * weight
        shares       = int(entry_amount / row["Price"])
        stop         = row["Price"] * 0.98    # -2%
        target       = row["Price"] * 1.035   # +3.5%
        print(f"{row['Ticker']:<12} {int(row['Score']):>5} {row['Price']:>8.2f}"
              f" {entry_amount:>12,.0f} {shares:>7} {stop:>17.2f} {target:>9.2f}")

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
        "| Ticker(Code) | Score | Price | Entry $ | Shares | Stop (Stop loss) | Target | EPS Surprise | Earnings In |",
        "|--------------|------:|------:|--------:|-------:|----------------:|-------:|-------------:|:-----------:|",
    ]
    for _, row in top.iterrows():
        weight       = row["Score"] / total_score
        entry_amount = deploy_capital * weight
        shares       = int(entry_amount / row["Price"])
        stop         = row["Price"] * 0.98
        target       = row["Price"] * 1.035
        summary.append(
            f"| {row['Ticker']} | {int(row['Score'])} | ${row['Price']:.2f}"
            f" | ${entry_amount:,.0f} | {shares} | ${stop:.2f} | ${target:.2f}"
            f" | {('+' if (row['EPS_Surprise'] or 0) >= 0 else '') + str(row['EPS_Surprise']) if row['EPS_Surprise'] is not None else 'N/A'}"
            f" | {str(row['Earnings_In']) + ' days' + (' 🔔' if row.get('Earnings_Soon') else '') if row['Earnings_In'] is not None else 'N/A'} |"
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
        "| Ticker | Score | Price | RSI | Position | MACD diff | EPS Surprise | Earnings In |",
        "|--------|------:|------:|----:|---------:|----------:|-------------:|:-----------:|",
    ]
    for _, r in df.iterrows():
        eps  = r['EPS_Surprise']
        eday = r['Earnings_In']
        soon = " 🔔" if r.get('Earnings_Soon') else ""
        summary.append(
            f"| {r['Ticker']} | {int(r['Score'])} | ${r['Price']:.2f}"
            f" | {r['RSI']:.1f} | {r['Position']:.2f} | {r['MACD_diff']:.4f}"
            f" | {('+' if (eps or 0) >= 0 else '') + str(eps) if eps is not None else 'N/A'}"
            f" | {str(eday) + ' days' + soon if eday is not None else 'N/A'} |"
        )
    summary.append("\n> ⚠️ Not financial advice. Always use risk management.")
    write_summary(summary)

    # --- Email Results ---
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    bearish_banner = "<p style='color:darkorange;font-weight:bold'>⚠️ Market is BEARISH — S&P 500 below 20 EMA. Use caution.</p>" if bearish else ""

    entry_rows = ""
    for _, row in top.iterrows():
        weight       = row["Score"] / total_score
        entry_amount = deploy_capital * weight
        shares       = int(entry_amount / row["Price"])
        stop         = row["Price"] * 0.98
        target       = row["Price"] * 1.035
        eps  = row['EPS_Surprise']
        eday = row['Earnings_In']
        soon_flag = " 🔔" if row.get('Earnings_Soon') else ""
        entry_rows += (
            f"<tr><td>{row['Ticker']}</td><td>{int(row['Score'])}</td>"
            f"<td>${row['Price']:.2f}</td><td>${entry_amount:,.0f}</td>"
            f"<td>{shares}</td><td>${stop:.2f}</td><td>${target:.2f}</td>"
            f"<td>{('+' if (eps or 0) >= 0 else '') + str(eps) if eps is not None else 'N/A'}</td>"
            f"<td>{str(eday) + 'd' + soon_flag if eday is not None else 'N/A'}</td></tr>"
        )

    reserve_rows = ""
    for _, row in top.iterrows():
        avg_price  = row["Price"] * 0.97
        avg_shares = int(reserve_per_position / avg_price)
        reserve_rows += (
            f"<tr><td>{row['Ticker']}</td><td>${avg_price:.2f}</td>"
            f"<td>${reserve_per_position:,.0f}</td><td>{avg_shares}</td></tr>"
        )

    all_rows = ""
    for _, r in df.iterrows():
        eps  = r['EPS_Surprise']
        eday = r['Earnings_In']
        soon_flag = " 🔔" if r.get('Earnings_Soon') else ""
        all_rows += (
            f"<tr><td>{r['Ticker']}</td><td>{int(r['Score'])}</td>"
            f"<td>${r['Price']:.2f}</td><td>{r['RSI']:.1f}</td>"
            f"<td>{r['Position']:.2f}</td><td>{r['MACD_diff']:.4f}</td>"
            f"<td>{('+' if (eps or 0) >= 0 else '') + str(eps) if eps is not None else 'N/A'}</td>"
            f"<td>{str(eday) + 'd' + soon_flag if eday is not None else 'N/A'}</td></tr>"
        )

    th = "style='background:#1a1a2e;color:#fff;padding:6px 12px;text-align:right'"
    td = "style='padding:5px 12px;border-bottom:1px solid #ddd;text-align:right'"
    tdl = "style='padding:5px 12px;border-bottom:1px solid #ddd;text-align:left'"

    html = f"""
    <html><body style='font-family:Arial,sans-serif;color:#222;max-width:900px;margin:auto'>
    <h2>📈 Stock Scanner — {today}</h2>
    {bearish_banner}
    <p><b>Capital:</b> ${CAPITAL:,.0f} &nbsp;|&nbsp;
       <b>Deploy (60%):</b> ${deploy_capital:,.0f} &nbsp;|&nbsp;
       <b>Reserve (40%):</b> ${reserve_capital:,.0f}</p>

    <h3>🎯 Entry Positions</h3>
    <table style='border-collapse:collapse;width:100%'>
      <tr>
        <th {th} style='text-align:left'>Ticker(Code)</th>
        <th {th}>Score</th><th {th}>Price</th><th {th}>Entry $</th>
        <th {th}>Shares</th><th {th}>Stop (Stop loss)</th><th {th}>Target</th>
        <th {th}>EPS Surprise</th><th {th}>Earnings In</th>
      </tr>
      {entry_rows.replace('<td>', f'<td {td}>').replace('<td>{', f'<td {tdl}>')}
    </table>

    <h3>🔄 Reserve / Average-Down Plan</h3>
    <table style='border-collapse:collapse;width:100%'>
      <tr>
        <th {th} style='text-align:left'>Ticker</th>
        <th {th}>Avg-Down Price</th><th {th}>Reserve $</th><th {th}>Extra Shares</th>
      </tr>
      {reserve_rows.replace('<td>', f'<td {td}>').replace('<td>{', f'<td {tdl}>')}
    </table>

    <h3>📊 All Stocks — Ranked by Score</h3>
    <table style='border-collapse:collapse;width:100%'>
      <tr>
        <th {th} style='text-align:left'>Ticker</th>
        <th {th}>Score</th><th {th}>Price</th><th {th}>RSI</th>
        <th {th}>Position</th><th {th}>MACD diff</th>
        <th {th}>EPS Surprise</th><th {th}>Earnings In</th>
      </tr>
      {all_rows.replace('<td>', f'<td {td}>').replace('<td>{', f'<td {tdl}>')}
    </table>

    <p style='color:gray;font-size:12px;margin-top:20px'>
      ⚠️ Not financial advice. Always use risk management.
    </p>
    </body></html>
    """

    send_email(f"📈 Stock Scan — {today}", html)


if __name__ == "__main__":
    main()
