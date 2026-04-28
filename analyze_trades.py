"""
Trading Performance Analyzer
Analyzes trading performance from CSV file with detailed breakdowns by setup, time, and day.

Usage: python analyze_trades.py [trades_file.csv]
Default: trades.csv

Required columns: Symbol, Entry Date, Entry Time, Entry Price, Exit Date, Exit Time, 
                  Exit Price, Shares, P&L, Setup Type
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime
from pathlib import Path


def load_trades(file_path):
    """Load trades from CSV file with error handling."""
    try:
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = [
            'Symbol', 'Entry Date', 'Entry Time', 'Entry Price', 
            'Exit Date', 'Exit Time', 'Exit Price', 'Shares', 'P&L', 'Setup Type'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Parse dates and times
        df['Entry DateTime'] = pd.to_datetime(
            df['Entry Date'] + ' ' + df['Entry Time'], 
            format='%Y-%m-%d %H:%M', 
            errors='coerce'
        )
        df['Exit DateTime'] = pd.to_datetime(
            df['Exit Date'] + ' ' + df['Exit Time'], 
            format='%Y-%m-%d %H:%M', 
            errors='coerce'
        )
        
        # Extract hour and day of week from entry time
        df['Entry Hour'] = df['Entry DateTime'].dt.hour
        df['Day of Week'] = df['Entry DateTime'].dt.day_name()
        
        # Create time blocks (market hours: 9:30 AM - 4:00 PM EST)
        def get_time_block(hour, minute):
            if pd.isna(hour):
                return 'Unknown'
            time_decimal = hour + minute / 60.0
            
            if 9.5 <= time_decimal < 10.5:
                return '9:30-10:30'
            elif 10.5 <= time_decimal < 11.5:
                return '10:30-11:30'
            elif 11.5 <= time_decimal < 12.5:
                return '11:30-12:30'
            elif 12.5 <= time_decimal < 13.5:
                return '12:30-1:30'
            elif 13.5 <= time_decimal < 14.5:
                return '1:30-2:30'
            elif 14.5 <= time_decimal < 16.0:
                return '2:30-4:00'
            else:
                return 'After Hours'
        
        df['Time Block'] = df.apply(
            lambda row: get_time_block(row['Entry Hour'], row['Entry DateTime'].minute), 
            axis=1
        )
        
        # Classify trades as winners/losers
        df['Outcome'] = df['P&L'].apply(lambda x: 'Win' if x > 0 else ('Loss' if x < 0 else 'Breakeven'))
        
        print(f"✅ Loaded {len(df)} trades from {file_path}")
        return df
    
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        print(f"   Create a CSV file with your trade data or use sample_trades.csv as a template.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading trades: {str(e)}")
        sys.exit(1)


def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def analyze_overall_statistics(df):
    """Calculate and display overall trading statistics."""
    print_section_header("OVERALL STATISTICS")
    
    total_trades = len(df)
    winners = len(df[df['P&L'] > 0])
    losers = len(df[df['P&L'] < 0])
    breakeven = len(df[df['P&L'] == 0])
    
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
    
    winning_trades = df[df['P&L'] > 0]['P&L']
    losing_trades = df[df['P&L'] < 0]['P&L']
    
    avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
    
    largest_win = df['P&L'].max()
    largest_loss = df['P&L'].min()
    
    total_pnl = df['P&L'].sum()
    avg_pnl = df['P&L'].mean()
    
    # Calculate expectancy: (Win% × Avg Win) + (Loss% × Avg Loss)
    expectancy = (win_rate / 100 * avg_win) + ((100 - win_rate) / 100 * avg_loss)
    
    # Calculate profit factor: Gross Profit / Gross Loss
    gross_profit = winning_trades.sum() if len(winning_trades) > 0 else 0
    gross_loss = abs(losing_trades.sum()) if len(losing_trades) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    
    stats = pd.DataFrame({
        'Metric': [
            'Total Trades',
            'Winning Trades',
            'Losing Trades',
            'Breakeven Trades',
            'Win Rate',
            '─────────────',
            'Average Win',
            'Average Loss',
            'Largest Win',
            'Largest Loss',
            '─────────────',
            'Total P&L',
            'Average P&L per Trade',
            'Expectancy',
            'Profit Factor'
        ],
        'Value': [
            f"{total_trades}",
            f"{winners}",
            f"{losers}",
            f"{breakeven}",
            f"{win_rate:.2f}%",
            '─────────────',
            f"${avg_win:,.2f}",
            f"${avg_loss:,.2f}",
            f"${largest_win:,.2f}",
            f"${largest_loss:,.2f}",
            '─────────────',
            f"${total_pnl:,.2f}",
            f"${avg_pnl:,.2f}",
            f"${expectancy:,.2f}",
            f"{profit_factor:.2f}" if profit_factor != np.inf else "∞"
        ]
    })
    
    print(stats.to_string(index=False))
    
    return {
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'expectancy': expectancy,
        'profit_factor': profit_factor
    }


def analyze_by_setup_type(df):
    """Analyze performance broken down by setup type."""
    print_section_header("PERFORMANCE BY SETUP TYPE")
    
    setup_stats = []
    
    for setup in df['Setup Type'].unique():
        setup_trades = df[df['Setup Type'] == setup]
        
        total = len(setup_trades)
        winners = len(setup_trades[setup_trades['P&L'] > 0])
        losers = len(setup_trades[setup_trades['P&L'] < 0])
        win_rate = (winners / total * 100) if total > 0 else 0
        
        winning_trades = setup_trades[setup_trades['P&L'] > 0]['P&L']
        losing_trades = setup_trades[setup_trades['P&L'] < 0]['P&L']
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
        
        total_pnl = setup_trades['P&L'].sum()
        
        setup_stats.append({
            'Setup Type': setup,
            'Trades': total,
            'Win Rate': f"{win_rate:.1f}%",
            'Avg Win': f"${avg_win:,.2f}",
            'Avg Loss': f"${avg_loss:,.2f}",
            'Total P&L': f"${total_pnl:,.2f}"
        })
    
    setup_df = pd.DataFrame(setup_stats)
    setup_df = setup_df.sort_values('Total P&L', 
                                     key=lambda x: x.str.replace('$', '').str.replace(',', '').astype(float), 
                                     ascending=False)
    
    print(setup_df.to_string(index=False))
    
    return setup_df


def analyze_by_time_block(df):
    """Analyze performance by time of day (hourly blocks)."""
    print_section_header("PERFORMANCE BY TIME OF DAY")
    
    # Define time block order
    time_order = ['9:30-10:30', '10:30-11:30', '11:30-12:30', 
                  '12:30-1:30', '1:30-2:30', '2:30-4:00', 'After Hours']
    
    time_stats = []
    
    for time_block in time_order:
        block_trades = df[df['Time Block'] == time_block]
        
        if len(block_trades) == 0:
            continue
        
        total = len(block_trades)
        winners = len(block_trades[block_trades['P&L'] > 0])
        losers = len(block_trades[block_trades['P&L'] < 0])
        win_rate = (winners / total * 100) if total > 0 else 0
        
        winning_trades = block_trades[block_trades['P&L'] > 0]['P&L']
        losing_trades = block_trades[block_trades['P&L'] < 0]['P&L']
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
        
        total_pnl = block_trades['P&L'].sum()
        
        time_stats.append({
            'Time Block': time_block,
            'Trades': total,
            'Win Rate': f"{win_rate:.1f}%",
            'Avg Win': f"${avg_win:,.2f}",
            'Avg Loss': f"${avg_loss:,.2f}",
            'Total P&L': f"${total_pnl:,.2f}"
        })
    
    time_df = pd.DataFrame(time_stats)
    
    print(time_df.to_string(index=False))
    
    return time_df


def analyze_by_day_of_week(df):
    """Analyze performance by day of week."""
    print_section_header("PERFORMANCE BY DAY OF WEEK")
    
    # Define day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    day_stats = []
    
    for day in day_order:
        day_trades = df[df['Day of Week'] == day]
        
        if len(day_trades) == 0:
            continue
        
        total = len(day_trades)
        winners = len(day_trades[day_trades['P&L'] > 0])
        losers = len(day_trades[day_trades['P&L'] < 0])
        win_rate = (winners / total * 100) if total > 0 else 0
        
        winning_trades = day_trades[day_trades['P&L'] > 0]['P&L']
        losing_trades = day_trades[day_trades['P&L'] < 0]['P&L']
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
        
        total_pnl = day_trades['P&L'].sum()
        
        day_stats.append({
            'Day': day,
            'Trades': total,
            'Win Rate': f"{win_rate:.1f}%",
            'Avg Win': f"${avg_win:,.2f}",
            'Avg Loss': f"${avg_loss:,.2f}",
            'Total P&L': f"${total_pnl:,.2f}"
        })
    
    day_df = pd.DataFrame(day_stats)
    
    print(day_df.to_string(index=False))
    
    return day_df


def detect_patterns(df, setup_df, time_df, day_df):
    """Identify key patterns and trends in trading performance."""
    print_section_header("PATTERN DETECTION & INSIGHTS")
    
    insights = []
    
    # Best/worst performing setup
    if not setup_df.empty:
        setup_pnl = setup_df.copy()
        setup_pnl['PNL_Value'] = setup_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        
        best_setup = setup_pnl.iloc[0]
        worst_setup = setup_pnl.iloc[-1]
        
        insights.append(f"🏆 Best Setup: {best_setup['Setup Type']} ({best_setup['Win Rate']} win rate, {best_setup['Total P&L']} total P&L)")
        insights.append(f"❌ Worst Setup: {worst_setup['Setup Type']} ({worst_setup['Win Rate']} win rate, {worst_setup['Total P&L']} total P&L)")
    
    # Best/worst performing time block
    if not time_df.empty:
        time_pnl = time_df.copy()
        time_pnl['PNL_Value'] = time_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        time_pnl = time_pnl.sort_values('PNL_Value', ascending=False)
        
        best_time = time_pnl.iloc[0]
        worst_time = time_pnl.iloc[-1]
        
        insights.append(f"⏰ Best Time Block: {best_time['Time Block']} ({best_time['Win Rate']} win rate, {best_time['Total P&L']} total P&L)")
        insights.append(f"⏰ Worst Time Block: {worst_time['Time Block']} ({worst_time['Win Rate']} win rate, {worst_time['Total P&L']} total P&L)")
    
    # Best/worst performing day
    if not day_df.empty:
        day_pnl = day_df.copy()
        day_pnl['PNL_Value'] = day_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        day_pnl = day_pnl.sort_values('PNL_Value', ascending=False)
        
        best_day = day_pnl.iloc[0]
        worst_day = day_pnl.iloc[-1]
        
        insights.append(f"📅 Best Day: {best_day['Day']} ({best_day['Win Rate']} win rate, {best_day['Total P&L']} total P&L)")
        insights.append(f"📅 Worst Day: {worst_day['Day']} ({worst_day['Win Rate']} win rate, {worst_day['Total P&L']} total P&L)")
    
    # Identify losing time periods (win rate < 40%)
    losing_periods = []
    
    for _, row in time_df.iterrows():
        win_rate_val = float(row['Win Rate'].replace('%', ''))
        if win_rate_val < 40:
            losing_periods.append(f"{row['Time Block']} ({row['Win Rate']} win rate)")
    
    if losing_periods:
        insights.append(f"⚠️  Consistently Losing Time Blocks: {', '.join(losing_periods)}")
    
    for insight in insights:
        print(f"  {insight}")
    
    return insights


def generate_recommendations(df, overall_stats, setup_df, time_df, day_df):
    """Generate actionable recommendations based on analysis."""
    print_section_header("RECOMMENDATIONS")
    
    recommendations = []
    
    # Win rate recommendations
    if overall_stats['win_rate'] < 50:
        recommendations.append(
            "🔴 Overall win rate is below 50%. Focus on improving trade selection and entry timing."
        )
    elif overall_stats['win_rate'] > 60:
        recommendations.append(
            "🟢 Strong win rate above 60%. Consider increasing position size on high-confidence setups."
        )
    
    # Expectancy recommendations
    if overall_stats['expectancy'] < 0:
        recommendations.append(
            "🔴 CRITICAL: Negative expectancy means you're losing money per trade on average. "
            "Stop trading this strategy until you identify and fix the problem."
        )
    elif overall_stats['expectancy'] > 50:
        recommendations.append(
            "🟢 Positive expectancy is strong. This strategy has an edge."
        )
    
    # Setup-specific recommendations
    if not setup_df.empty:
        setup_pnl = setup_df.copy()
        setup_pnl['PNL_Value'] = setup_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        
        # Find profitable setups
        profitable_setups = setup_pnl[setup_pnl['PNL_Value'] > 0]
        losing_setups = setup_pnl[setup_pnl['PNL_Value'] < 0]
        
        if not profitable_setups.empty:
            best = profitable_setups.iloc[0]
            recommendations.append(
                f"📈 Focus more on {best['Setup Type']} setups - your most profitable pattern "
                f"({best['Total P&L']} total P&L, {best['Win Rate']} win rate)."
            )
        
        if not losing_setups.empty:
            worst = losing_setups.iloc[-1]
            recommendations.append(
                f"📉 AVOID {worst['Setup Type']} setups - consistent money loser "
                f"({worst['Total P&L']} total P&L). Either eliminate or drastically improve this pattern."
            )
    
    # Time-specific recommendations (Golden Hour focus)
    if not time_df.empty:
        time_pnl = time_df.copy()
        time_pnl['PNL_Value'] = time_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        time_pnl = time_pnl.sort_values('PNL_Value', ascending=False)
        
        best_time = time_pnl.iloc[0]
        worst_time = time_pnl.iloc[-1]
        
        recommendations.append(
            f"⏰ GOLDEN HOUR: Trade most actively during {best_time['Time Block']} "
            f"({best_time['Total P&L']} total P&L). This is your most profitable window."
        )
        
        if worst_time['PNL_Value'] < -100:
            recommendations.append(
                f"⏰ DANGER ZONE: Consider avoiding {worst_time['Time Block']} "
                f"({worst_time['Total P&L']} total P&L). This time block is costing you money."
            )
    
    # Day-specific recommendations
    if not day_df.empty:
        day_pnl = day_df.copy()
        day_pnl['PNL_Value'] = day_pnl['Total P&L'].str.replace('$', '').str.replace(',', '').astype(float)
        
        losing_days = day_pnl[day_pnl['PNL_Value'] < -100]
        if not losing_days.empty:
            worst_day = losing_days.iloc[-1]
            recommendations.append(
                f"📅 Consider reducing position size or avoiding trades on {worst_day['Day']} "
                f"({worst_day['Total P&L']} total P&L)."
            )
    
    # Profit factor recommendations
    if overall_stats['profit_factor'] < 1:
        recommendations.append(
            "🔴 Profit factor below 1.0 means gross losses exceed gross profits. "
            "Strategy needs immediate revision."
        )
    elif overall_stats['profit_factor'] > 2:
        recommendations.append(
            f"🟢 Excellent profit factor of {overall_stats['profit_factor']:.2f}. "
            "You're making $2+ for every $1 lost."
        )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")
    
    print("\n")


def main():
    """Main analysis workflow."""
    # Determine input file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'trades.csv'
    
    print("\n" + "=" * 80)
    print("  📊 TRADING PERFORMANCE ANALYZER")
    print("=" * 80)
    print(f"  Analyzing: {file_path}")
    
    # Load trades
    df = load_trades(file_path)
    
    # Run analyses
    overall_stats = analyze_overall_statistics(df)
    setup_df = analyze_by_setup_type(df)
    time_df = analyze_by_time_block(df)
    day_df = analyze_by_day_of_week(df)
    
    # Pattern detection
    insights = detect_patterns(df, setup_df, time_df, day_df)
    
    # Generate recommendations
    generate_recommendations(df, overall_stats, setup_df, time_df, day_df)
    
    print("=" * 80)
    print("  ✅ Analysis complete!")
    print("  💡 Run this weekly on your latest trades to track progress.")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
