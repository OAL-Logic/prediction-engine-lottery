"""
Insights Module 💡
===============
Generates automated, plain-English insights from statistical lottery data.
Used primarily by the Terminal Dashboard and API layers.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Dict, Any

from engine.adapters import DrawRules
from engine.modules import frequency, deviation, sum_range, patterns

def get_automated_insights(df: pd.DataFrame, rules: DrawRules, limit: int = 100) -> List[str]:
    """
    Generate a list of insight strings based on the recent draw history.
    """
    df_recent = df.tail(limit)
    f_res = frequency.analyze(df_recent, rules)
    d_res = deviation.analyze(df, rules) # We use full df for delay context
    
    insights = []
    
    # 1. Fairness / Regime Insight
    if f_res.chi2_p_value < 0.05:
        insights.append("[red]●[/red] [bold]Fairness Alert:[/bold] Distribution is non-uniform (p < 0.05).")
    else:
        insights.append("[green]●[/green] [bold]Regime:[/bold] Statistical distribution appears stable.")
        
    # 2. Hotspot Insight
    sig_hot = f_res.table[f_res.table["z_score"] > 2.0]
    if not sig_hot.empty:
        top_hot = sig_hot.iloc[0]
        insights.append(f"[yellow]●[/yellow] [bold]Hotspot:[/bold] Number {int(top_hot['number'])} is over-performing (Z={top_hot['z_score']:+.2f}).")

    # 3. Overdue / Record Breaker Insight
    sig_overdue = d_res.table[d_res.table["deviation_ratio"] > 2.0]
    if not sig_overdue.empty:
        top_overdue = sig_overdue.iloc[0]
        max_d = d_res.gap_stats.get(top_overdue['number'], {}).get("max", 0)
        curr_d = top_overdue['draws_since_last']
        if curr_d > max_d:
            insights.append(f"[red]●[/red] [bold]Anomaly:[/bold] Number {int(top_overdue['number'])} is at an All-Time High delay ({int(curr_d)}d vs max {int(max_d)}d).")
        else:
            insights.append(f"[orange1]●[/orange1] [bold]Overdue:[/bold] Number {int(top_overdue['number'])} is significantly overdue ({int(curr_d)}d).")

    # 4. Pattern Insight (Row/Column)
    rows = [patterns.get_pattern_string(d, cols=rules.board_cols, max_n=rules.number_range[1]) for d in df_recent["numbers"]]
    from collections import Counter
    row_counts = Counter(rows)
    top_row, top_row_count = row_counts.most_common(1)[0]
    if top_row_count / len(df_recent) > 0.4:
        insights.append(f"[blue]●[/blue] [bold]Pattern:[/bold] Row distribution '{top_row}' is trending (occurs in {top_row_count/len(df_recent)*100:.0f}% of last {limit} draws).")

    # 5. Cycle Insight
    lo_r, hi_r = rules.number_range
    cycle_data = patterns.analyze_cycle(df["numbers"].tolist(), list(range(lo_r, hi_r + 1)))
    prog = cycle_data['current_cycle_progress']
    if prog > 0.85:
        insights.append(f"[magenta]●[/magenta] [bold]Cycle:[/bold] Current cycle is nearly complete ({prog*100:.1f}%). Watch missing numbers: {cycle_data['missing_in_current'][:5]}.")
    
    # 6. Environmental Jitter (Placeholder/Simulation for Dashboard)
    import time
    import hashlib
    jitter_hash = hashlib.sha256(str(int(time.time() // 3600)).encode()).hexdigest()
    jitter_val = int(jitter_hash[:4], 16) / 65535.0
    if jitter_val > 0.8:
        insights.append("[cyan]●[/cyan] [bold]Entropy:[/bold] High Noosphere Jitter detected. Esoteric strategies boosted.")

    return insights
