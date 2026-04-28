#!/usr/bin/env python3
"""
Trade Journal & Coaching Analyzer
Evaluates rule adherence, detects behavioral patterns, and provides coaching feedback
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys


class TradeJournalCoach:
    """Analyzes individual trades and provides coaching feedback"""
    
    def __init__(self):
        self.entry_rules = {}
        self.exit_rules = {}
        self.violations = []
        self.patterns = []
        
    def analyze_trade(self, trade_data):
        """
        Analyze a single trade with entry/exit rule checking
        
        trade_data should include:
        - ticker, entry_time, entry_price, exit_time, exit_price
        - setup_type, planned_stop, actual_stop
        - entry_rules_met (dict), exit_rules_met (dict)
        - context (dict): previous_trades_today, emotional_state, etc.
        """
        print(f"\n{'='*80}")
        print(f"TRADE JOURNAL ANALYSIS: {trade_data['ticker']}")
        print(f"{'='*80}\n")
        
        # 1. Trade Overview
        self._print_trade_overview(trade_data)
        
        # 2. Entry Analysis
        self._analyze_entry(trade_data)
        
        # 3. Exit Analysis
        self._analyze_exit(trade_data)
        
        # 4. Behavioral Pattern Detection
        self._detect_patterns(trade_data)
        
        # 5. Coaching Feedback
        self._provide_coaching(trade_data)
        
        # 6. Action Items
        self._generate_action_items(trade_data)
        
    def _print_trade_overview(self, trade):
        """Print basic trade details"""
        pnl = (trade['exit_price'] - trade['entry_price']) * trade.get('shares', 100)
        pnl_pct = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
        
        print("📊 TRADE OVERVIEW")
        print("-" * 80)
        print(f"Symbol:       {trade['ticker']}")
        print(f"Setup Type:   {trade.get('setup_type', 'Unknown')}")
        print(f"Date:         {trade.get('date', 'N/A')}")
        print(f"Entry Time:   {trade.get('entry_time', 'N/A')}")
        print(f"Entry Price:  ${trade['entry_price']:.2f}")
        print(f"Exit Time:    {trade.get('exit_time', 'N/A')}")
        print(f"Exit Price:   ${trade['exit_price']:.2f}")
        print(f"Shares:       {trade.get('shares', 100)}")
        print(f"P&L:          ${pnl:.2f} ({pnl_pct:+.2f}%)")
        print(f"Hold Time:    {trade.get('hold_time', 'N/A')}")
        print()
        
    def _analyze_entry(self, trade):
        """Analyze if entry rules were followed"""
        print("🎯 ENTRY ANALYSIS")
        print("-" * 80)
        
        entry_rules = trade.get('entry_rules', {})
        entry_met = trade.get('entry_rules_met', {})
        
        if not entry_rules:
            print("⚠️  No entry rules defined. Cannot evaluate entry quality.")
            print()
            return
            
        all_rules_met = True
        violations = []
        
        for rule_name, rule_condition in entry_rules.items():
            met = entry_met.get(rule_name, False)
            status = "✅" if met else "❌"
            print(f"{status} {rule_name}: {rule_condition}")
            
            if not met:
                all_rules_met = False
                violations.append(rule_name)
        
        print()
        if all_rules_met:
            print("✅ ENTRY WAS CLEAN - All rules followed")
        else:
            print(f"❌ ENTRY VIOLATED {len(violations)} RULE(S): {', '.join(violations)}")
            print("   This is a RULE VIOLATION. Entry should not have been taken.")
        print()
        
        self.violations.extend(violations)
        
    def _analyze_exit(self, trade):
        """Analyze if exit plan was followed"""
        print("🚪 EXIT ANALYSIS")
        print("-" * 80)
        
        exit_rules = trade.get('exit_rules', {})
        exit_met = trade.get('exit_rules_met', {})
        planned_stop = trade.get('planned_stop', None)
        actual_exit = trade['exit_price']
        exit_reason = trade.get('exit_reason', 'Unknown')
        
        if not exit_rules:
            print("⚠️  No exit rules defined. Cannot evaluate exit discipline.")
            print()
            return
        
        print(f"Exit Reason:   {exit_reason}")
        if planned_stop:
            print(f"Planned Stop:  ${planned_stop:.2f}")
            print(f"Actual Exit:   ${actual_exit:.2f}")
            
            # Check if exit was before stop
            if trade['exit_price'] < trade['entry_price']:  # losing trade
                if actual_exit > planned_stop:
                    print(f"\n❌ EARLY EXIT VIOLATION")
                    print(f"   Exited at ${actual_exit:.2f} before stop at ${planned_stop:.2f}")
                    print(f"   This is EMOTIONAL TRADING - cutting loss too early")
                    self.violations.append("Early exit before stop")
        
        print("\nExit Rule Adherence:")
        followed_plan = True
        
        for rule_name, rule_condition in exit_rules.items():
            met = exit_met.get(rule_name, False)
            status = "✅" if met else "❌"
            print(f"{status} {rule_name}: {rule_condition}")
            
            if not met:
                followed_plan = False
        
        print()
        if followed_plan:
            print("✅ EXIT FOLLOWED PLAN - Good discipline")
        else:
            print("❌ EXIT DID NOT FOLLOW PLAN - This is a discipline issue")
        print()
        
    def _detect_patterns(self, trade):
        """Detect behavioral patterns in trading"""
        print("🔍 BEHAVIORAL PATTERN DETECTION")
        print("-" * 80)
        
        context = trade.get('context', {})
        prev_trades_today = context.get('previous_trades_today', [])
        trade_number = context.get('trade_number', 1)
        
        patterns_found = []
        
        # Pattern 1: Revenge trading (trading after losses)
        if len(prev_trades_today) >= 2:
            recent_losses = sum(1 for t in prev_trades_today[-2:] if t['pnl'] < 0)
            if recent_losses == 2:
                patterns_found.append({
                    'name': 'REVENGE TRADING',
                    'severity': 'HIGH',
                    'description': 'Entering trade after 2 consecutive losses',
                    'advice': 'STOP TRADING for the day. You are emotionally compromised.'
                })
        
        # Pattern 2: Over-trading
        if trade_number > 3:
            patterns_found.append({
                'name': 'OVER-TRADING',
                'severity': 'MEDIUM',
                'description': f'This is trade #{trade_number} today',
                'advice': 'Limit to 3 trades per day maximum. Quality over quantity.'
            })
        
        # Pattern 3: Early exit (exiting before stop without rule)
        if 'Early exit before stop' in self.violations:
            patterns_found.append({
                'name': 'FEAR-BASED TRADING',
                'severity': 'HIGH',
                'description': 'Exiting before stop loss is hit',
                'advice': 'Trust your stop loss. Exiting early shows lack of conviction.'
            })
        
        # Pattern 4: Rule violations on entry
        entry_violations = [v for v in self.violations if 'entry' in v.lower() or v in trade.get('entry_rules', {}).keys()]
        if entry_violations:
            patterns_found.append({
                'name': 'IMPULSIVE ENTRY',
                'severity': 'MEDIUM',
                'description': 'Not waiting for all entry conditions',
                'advice': 'Wait for ALL rules to be met. Patience is key.'
            })
        
        # Pattern 5: Trading in choppy hours (if time provided)
        entry_time = trade.get('entry_time', '')
        if entry_time:
            hour = int(entry_time.split(':')[0])
            if 10 <= hour < 14:  # 10 AM - 2 PM is typically choppy
                patterns_found.append({
                    'name': 'TRADING CHOPPY HOURS',
                    'severity': 'LOW',
                    'description': f'Entered at {entry_time} (midday chop)',
                    'advice': 'Focus on 9:30-10:30 AM or 2:30-4:00 PM for best setups.'
                })
        
        if patterns_found:
            for pattern in patterns_found:
                severity_color = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                print(f"{severity_color[pattern['severity']]} {pattern['name']} ({pattern['severity']} SEVERITY)")
                print(f"   Issue: {pattern['description']}")
                print(f"   Advice: {pattern['advice']}")
                print()
                self.patterns.append(pattern)
        else:
            print("✅ No concerning behavioral patterns detected")
            print()
    
    def _provide_coaching(self, trade):
        """Provide coaching feedback based on trade analysis"""
        print("🎓 COACHING FEEDBACK")
        print("-" * 80)
        
        pnl = (trade['exit_price'] - trade['entry_price']) * trade.get('shares', 100)
        is_winner = pnl > 0
        
        # Determine overall trade quality
        has_violations = len(self.violations) > 0
        has_high_severity_patterns = any(p['severity'] == 'HIGH' for p in self.patterns)
        
        if has_violations or has_high_severity_patterns:
            print("❌ POOR TRADE EXECUTION")
            print()
            print("This trade had significant issues regardless of P&L outcome.")
            print("Even if you made money, you broke your rules. That's gambling, not trading.")
            print()
            
            if has_high_severity_patterns:
                print("⚠️  CRITICAL ISSUES:")
                for pattern in self.patterns:
                    if pattern['severity'] == 'HIGH':
                        print(f"   • {pattern['name']}: {pattern['description']}")
                print()
            
            print("📋 WHAT TO DO NOW:")
            print("   1. STOP TRADING for today")
            print("   2. Review your trading rules")
            print("   3. Identify emotional triggers")
            print("   4. Come back tomorrow with a clear head")
            
        elif len(self.violations) > 0:
            print("⚠️  RULE VIOLATIONS DETECTED")
            print()
            print("You broke your trading rules. This needs to be addressed.")
            print(f"Violations: {', '.join(self.violations)}")
            print()
            print("📋 ACTION ITEMS:")
            print("   1. Review why you broke these rules")
            print("   2. Was it emotional? Impulsive? FOMO?")
            print("   3. Set alerts to enforce rules automatically")
            
        else:
            print("✅ GOOD TRADE EXECUTION")
            print()
            print("You followed your rules and maintained discipline.")
            
            if is_winner:
                print("🏆 Winner with discipline - This is how you build consistency!")
            else:
                print("📉 Small loss with discipline - This is acceptable trading.")
                print("   Losses are part of the game. You controlled your risk.")
        
        print()
        
    def _generate_action_items(self, trade):
        """Generate specific action items for improvement"""
        print("✅ ACTION ITEMS")
        print("-" * 80)
        
        action_items = []
        
        # Based on violations
        if 'Early exit before stop' in self.violations:
            action_items.append("Set stop-loss orders BEFORE entry (use bracket orders)")
            action_items.append("Write down: 'I will trust my stop loss'")
        
        # Based on patterns
        for pattern in self.patterns:
            if pattern['name'] == 'REVENGE TRADING':
                action_items.append("Create a 'Max 2 losses = done for day' rule")
                action_items.append("Set calendar reminder to stop trading after 2 losses")
            
            if pattern['name'] == 'OVER-TRADING':
                action_items.append("Limit to 3 trades per day (set hard limit)")
                action_items.append("Track trade count on sticky note next to screen")
            
            if pattern['name'] == 'IMPULSIVE ENTRY':
                action_items.append("Create entry checklist (print it out)")
                action_items.append("Don't click BUY until ALL boxes checked")
        
        # General improvements
        if trade.get('setup_type') and trade.get('setup_type') != 'Opening range breakout':
            action_items.append("Review why this setup was chosen (vs. your best setups)")
        
        if action_items:
            for i, item in enumerate(action_items, 1):
                print(f"{i}. {item}")
        else:
            print("• Continue following your rules with discipline")
            print("• Document this trade in your journal")
            print("• Review weekly to identify patterns")
        
        print()


def analyze_orb_trade():
    """Analyze the specific ORB trade example provided"""
    
    trade = {
        'ticker': 'TSLA',
        'date': '03/24/2026',
        'setup_type': 'Opening Range Breakout',
        'entry_time': '10:05',
        'entry_price': 386.00,
        'exit_time': '10:20',
        'exit_price': 385.00,
        'shares': 100,
        'planned_stop': 383.00,
        'hold_time': '15 minutes',
        
        'entry_rules': {
            'Break of 30-min high': 'Price > 385',
            'Volume confirmation': 'Volume > 1.5x average on breakout bar',
            'VWAP filter': 'Price > VWAP'
        },
        
        'entry_rules_met': {
            'Break of 30-min high': True,
            'Volume confirmation': True,  # Assuming this was met
            'VWAP filter': True  # Assuming this was met
        },
        
        'exit_rules': {
            'Weak bar exit': 'Exit on first 5-min bar closing in bottom 25%',
            'Stop loss': 'Exit at $383.00 (30-min low)'
        },
        
        'exit_rules_met': {
            'Weak bar exit': False,  # Exited before weak bar
            'Stop loss': False  # Exited before stop
        },
        
        'exit_reason': 'Felt it was rolling over',
        
        'context': {
            'trade_number': 3,
            'previous_trades_today': [
                {'pnl': -200},
                {'pnl': -150}
            ],
            'emotional_state': 'Frustrated after 2 losses'
        }
    }
    
    coach = TradeJournalCoach()
    coach.analyze_trade(trade)
    
    # Add chart analysis note
    print("\n📊 CHART ANALYSIS RECOMMENDATIONS")
    print("=" * 80)
    print("To complete this analysis, review the chart and answer:")
    print("1. Was there actually a weak bar before your exit?")
    print("2. Did price continue higher after you exited?")
    print("3. Where did price eventually stop out?")
    print("4. Was the breakout bar truly 1.5x volume?")
    print("\nUse TradingView or your charting platform to verify these conditions.")
    print()


def load_and_analyze_csv(filepath):
    """Load trades from CSV and analyze with coaching"""
    
    print("Loading trades from CSV...\n")
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Basic validation
    required_cols = ['Symbol', 'Entry Price', 'Exit Price', 'P&L']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns: {missing}")
        return
    
    print(f"Loaded {len(df)} trades from {filepath}\n")
    
    # Analyze each trade for rule violations and patterns
    print("="*80)
    print("TRADE-BY-TRADE COACHING ANALYSIS")
    print("="*80)
    
    for idx, row in df.iterrows():
        # Convert CSV row to trade format
        trade = {
            'ticker': row['Symbol'],
            'entry_price': float(row['Entry Price']),
            'exit_price': float(row['Exit Price']),
            'shares': int(row.get('Shares', 100)),
            'setup_type': row.get('Setup Type', 'Unknown'),
            'date': row.get('Entry Date', 'N/A'),
            'entry_time': row.get('Entry Time', 'N/A'),
            'exit_time': row.get('Exit Time', 'N/A'),
            'hold_time': 'N/A',
            'context': {
                'trade_number': idx + 1,
                'previous_trades_today': []  # Would need more data to populate
            }
        }
        
        # Simplified analysis for CSV data (no rule checking without rule definitions)
        coach = TradeJournalCoach()
        pnl = float(row['P&L'])
        
        print(f"\nTrade #{idx+1}: {trade['ticker']}")
        print(f"Entry: ${trade['entry_price']:.2f} → Exit: ${trade['exit_price']:.2f}")
        print(f"Setup: {trade['setup_type']}, P&L: ${pnl:.2f}")
        
        # Basic pattern detection
        if idx >= 2:  # Check for revenge trading
            prev_pnls = [float(df.iloc[i]['P&L']) for i in range(max(0, idx-2), idx)]
            if all(p < 0 for p in prev_pnls):
                print("⚠️  PATTERN: Possible revenge trading (after 2 losses)")
        
        if idx > 2:
            print(f"⚠️  PATTERN: Trade #{idx+1} - Check for over-trading")
        
        print("-" * 40)
    
    print("\n✅ For detailed coaching analysis, use the trade journal format")
    print("   See analyze_orb_trade() example for complete analysis\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Analyze CSV file
        load_and_analyze_csv(sys.argv[1])
    else:
        # Run example ORB trade analysis
        print("No CSV file provided. Running example ORB trade analysis...\n")
        analyze_orb_trade()
