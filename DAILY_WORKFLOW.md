# Complete Trading System - Daily Workflow

**How to use IntelliMarket Analyst + Trade Coaching for consistent results**

---

## 🌅 Morning Routine (Before Market Open)

### 1. Review Yesterday's Trades (5 min)
```powershell
# If you traded yesterday, run coaching analysis
python trade_journal_coach.py trades_2026-04-27.csv

# Check for patterns
# - Any revenge trading?
# - Fear-based exits?
# - Over-trading?
```

### 2. Check Your Portfolio (2 min)
Open https://ipathan-lang.github.io/stock-scanner/

**Current Holdings:**
- GLD: -2.30% (down $4,609) - Strong Bullish signal
- VXUS: +0.83% (up $1,890) - Bullish signal

**Action Items:**
- Both showing buy signals for 10:30-11:30 AM window
- Consider if you want to average down (GLD) or add to winner (VXUS)

### 3. Review Congressional Trades (3 min)
**Recent Activity:**
- Nancy Pelosi bought TSLA ($100K-250K) 2 days ago ⭐
- Multiple Congress members buying NVDA, MSFT, GOOGL
- Josh Gottheimer SELLING META ($50K-100K)

**Watchlist Priority:**
- TSLA (Pelosi buying + Strong Bullish AI signal)
- NVDA (Multiple Congress buyers + on watchlist)
- MSFT (Congress buying + Bullish AI signal)

### 4. Golden Hour Pre-Market Setup (5 min)

**Check Market Pulse:**
- Sentiment: NEUTRAL (mixed signals)
- Bullish Setups: 6/10 (60%)
- Bearish Risk: 0/10 (low)

**ORB Prep Checklist:**
- [ ] Identify stocks above VWAP pre-market
- [ ] Check which have news/catalysts today
- [ ] Set alerts for 30-min high breaks
- [ ] Prepare bracket orders (entry + stop + target)

---

## 📈 9:30-10:00 AM - Golden Hour Trading

### ORB Setup Rules
```
Entry: Break of 30-min high
Filter: Volume > 1.5x average + Price > VWAP
Stop: 30-min low
Target: 2R (2x risk) or trailing stop
```

### Today's ORB Candidates
**TSLA** (from your example):
- Pre-market high: ~$385
- 30-min high: Watch for break above $385
- If breaks: Entry $386, Stop $383 (30-min low)
- Target: $389 (2R) or trail with 2-bar low

**Bracket Order Setup:**
```
Buy: $386.00
Stop: $383.00 (-$3 risk)
Target: $389.00 (+$3 reward, 1:1 R/R minimum)
```

### ⚠️ Critical Rules
- [ ] **Max 3 trades today** (track on sticky note)
- [ ] **Stop after 2 losses** (no trade #3 if 2 losses)
- [ ] **Use bracket orders** (every single trade)
- [ ] **No manual exits** (trust your stop)

---

## 🕐 10:00 AM - Trading Window Closes

### Stop Looking for Trades
After 10:00 AM:
- Golden Hour is OVER
- Quality degrades significantly
- Choppy hours begin (10:30 AM - 2:30 PM)

### Exception: AI-Recommended Add-Ons
Both GLD and VXUS show "buy add-on" signals for 10:30-11:30 window.

**Decision Framework:**
- If in profit: Consider small add-on
- If at loss: Wait for price to prove itself first
- Use smaller position size (50% of normal)

---

## 📊 2:30-4:00 PM - Power Hour (Optional)

**If you have < 3 trades today AND no losses:**
- Watch for momentum continuation setups
- Same rules apply (bracket orders, no emotional exits)
- Prefer closing positions before 4:00 PM (avoid overnight risk)

**If you already have 2+ losses:**
- ❌ STOP TRADING
- Do NOT try to "get back" losses
- Review what went wrong, plan for tomorrow

---

## 🌙 After Market Close

### 1. Export Today's Trades
In the app:
1. Click "📊 Export Trades" button
2. File downloads: `trades_2026-04-28.csv`

### 2. Run Coaching Analysis (5 min)
```powershell
python trade_journal_coach.py trades_2026-04-28.csv
```

**What to Look For:**
- ✅ Did I follow all entry rules?
- ✅ Did I follow my exit plan?
- ❌ Any revenge trading patterns?
- ❌ Any fear-based exits?
- ❌ Over-trading (>3 trades)?

### 3. Update Trade Journal (3 min)
For each trade, write down:
```
Trade: TSLA ORB
Entry: $386 (clean, all rules met)
Exit: $385 (VIOLATED - exited before stop)
Pattern: Revenge trading (3rd trade after 2 losses)
Lesson: Stop after 2 losses. Use bracket orders.
Action: Set calendar reminder for 10 AM loss check
```

### 4. Plan for Tomorrow (2 min)
Based on today's analysis:
- What setups worked best?
- What mistakes did I make?
- What will I do differently?

**Example Plan:**
```
Tomorrow's Focus:
• Only trade 9:30-10:00 AM ORB setups
• Use bracket orders (no manual exits)
• STOP after 2 losses (set alarm)
• Max 3 trades total
• Check Congressional trades for TSLA, NVDA
```

---

## 📅 Friday Evening - Weekly Review

### 1. Run Performance Analysis (10 min)
```powershell
python analyze_trades.py trades_week_17.csv
```

**Key Metrics to Track:**
- Win rate (goal: 55%+)
- Profit factor (goal: 1.5+)
- Best setup type
- Best time window
- Worst patterns

### 2. Pattern Review
```powershell
python trade_journal_coach.py trades_week_17.csv
```

**Questions to Answer:**
- How many times did I revenge trade?
- How many times did I exit early?
- How many days did I over-trade (>3 trades)?
- How many rule violations total?

### 3. Update Trading Rules (if needed)
Based on your data:
- Which setups have 60%+ win rate? (FOCUS HERE)
- Which setups have <40% win rate? (ELIMINATE)
- Which time windows are profitable? (TRADE HERE)
- Which time windows lose money? (AVOID)

### 4. Plan Next Week
Set 3 specific goals:
```
Week 18 Goals:
1. Zero revenge trading (stop after 2 losses)
2. Zero early exits (use bracket orders)
3. Only trade Golden Hour ORB setups
```

---

## 🎯 Your Specific Action Plan (Based on TSLA Analysis)

### Immediate (This Week)

**1. Create Hard Stop Rule**
```
"2 LOSSES = DONE FOR DAY"
```
- Write this on sticky note next to monitor
- Set phone reminder at 10:00 AM: "Check loss count"
- If 2 losses: Close platform, go for walk

**2. Set Up Bracket Orders**
In your trading platform:
- Pre-define entry, stop, and target
- Submit as bracket order (all at once)
- Remove ability to manually exit

**3. Golden Hour Only**
```
ONLY TRADE: 9:30 - 10:00 AM
```
- Set phone alarm at 10:00 AM: "STOP LOOKING"
- After 10:00, check existing positions only
- No new entries after 10:00 (except AI add-on signals)

### Ongoing (Daily)

**Before Trading:**
- [ ] Review yesterday's coaching analysis
- [ ] Check for 2+ recent losses (if yes, careful today)
- [ ] Review entry rules checklist
- [ ] Prepare bracket orders

**During Trading:**
- [ ] Only take setups during Golden Hour
- [ ] Use bracket orders (every trade)
- [ ] Track trade count on sticky note
- [ ] STOP after 2 losses (no exceptions)

**After Trading:**
- [ ] Export trades
- [ ] Run coaching analysis
- [ ] Log violations and patterns
- [ ] Plan for tomorrow

### Monthly Review

**Track These Metrics:**
- Win rate trend (improving?)
- Revenge trading frequency (decreasing?)
- Early exit frequency (decreasing?)
- Best setup consistency (increasing?)

**Adjust Strategy:**
- If win rate <45%: Trade only your best setup
- If revenge trading frequent: Reduce max trades to 2
- If early exits frequent: Increase position size confidence
- If over-trading: Set hard 2-trade limit

---

## 📊 Sample Week with System

### Monday
**Morning:** Check Congressional trades (Nancy Pelosi bought TSLA)
**9:35 AM:** TSLA ORB setup, entered $386 with bracket order
**9:50 AM:** Stopped out at $383 (-$300)
**10:00 AM:** Stop looking for trades (1 loss today)
**Evening:** Export trades, coaching analysis = "Clean entry, followed stop"

### Tuesday
**Morning:** Review Monday's trade (good discipline)
**9:40 AM:** NVDA ORB setup, entered $895
**10:15 AM:** Target hit at $901 (+$600)
**11:30 AM:** AI signals buy add-on for GLD, took small position
**2:45 PM:** GLD closed +$200
**Evening:** Export trades, analysis = "2 winners, no violations, great day"

### Wednesday
**Morning:** Feeling confident after Tuesday
**9:35 AM:** AAPL ORB, stopped out (-$250)
**9:45 AM:** MSFT ORB, stopped out (-$300)
**10:00 AM:** 🚨 **2 LOSSES = DONE** (alarm goes off)
**Action:** Closed platform, went for walk
**Evening:** Coaching analysis = "Stopped correctly after 2 losses ✅"

### Thursday
**Morning:** Clear head after stopping yesterday
**9:38 AM:** TSLA ORB, followed all rules, target hit (+$400)
**10:00 AM:** One win, stop looking
**Evening:** Analysis = "Perfect execution, 1 trade, clean exit"

### Friday
**Morning:** Review week's performance
**Trading:** 1 ORB winner (+$350)
**Evening:** 
```powershell
python analyze_trades.py trades_week_17.csv
# Results: 60% win rate, profit factor 1.8
# Best setup: ORB (75% win rate)
# Best time: 9:30-10:00 AM
```

---

## 🎓 Coaching Summary

### What We Learned from Your TSLA Trade

**✅ Strengths:**
- Clean entry (all rules followed)
- Good setup identification (ORB is your best)
- Proper risk definition (stop at 30-min low)

**❌ Areas for Improvement:**
- DISCIPLINE: Exited before stop (fear-based)
- EMOTIONAL CONTROL: Took 3rd trade after 2 losses (revenge)
- TIMING: Entered at 10:05 (after Golden Hour ends at 10:00)

**🎯 Focus Areas:**
1. **Use bracket orders** (removes fear)
2. **Stop after 2 losses** (removes revenge trading)
3. **Golden Hour only** (increases win rate)

---

## 📞 Quick Reference

### Daily Checklist
- [ ] Review yesterday's coaching analysis
- [ ] Check Congressional trades
- [ ] Set up ORB candidates with bracket orders
- [ ] Trade 9:30-10:00 only (Golden Hour)
- [ ] Stop after 2 losses
- [ ] Export and analyze trades after close

### Commands
```powershell
# Export trades (click button in app)
python trade_journal_coach.py trades_2026-04-28.csv    # Daily coaching
python analyze_trades.py trades_week_17.csv            # Weekly stats
```

### Your Hard Rules
1. **Max 2 losses per day** (then STOP)
2. **Max 3 trades per day** (quality over quantity)
3. **Bracket orders only** (no manual exits)
4. **Golden Hour only** (9:30-10:00 AM for new entries)
5. **Daily journal** (export and analyze every day)

---

## 🏆 Success Metrics

### This Month
- [ ] Zero revenge trading days
- [ ] Zero early exits (always follow stop)
- [ ] 55%+ win rate
- [ ] Positive expectancy
- [ ] 3+ consecutive days following rules

### This Quarter
- [ ] 60%+ win rate on ORB setups
- [ ] Profit factor > 1.5
- [ ] Average win > average loss
- [ ] Identify 2-3 best setups
- [ ] Eliminate all losing patterns

### This Year
- [ ] Consistent monthly profits
- [ ] 65%+ win rate (with discipline)
- [ ] Profit factor > 2.0
- [ ] Scale position size safely
- [ ] Help other traders (share your system)

---

**Remember: The market rewards discipline, not predictions.**

Good luck, and follow your rules! 🎯
