"""
Regime Module 📈
===============
Analyses high-level game dynamics and high-dimensional stability (JS Divergence, Entropy).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy

from engine.adapters import DrawRules

@dataclass
class RegimeResult:
    lottery_name: str
    avg_repeat_rate: float
    avg_consecutive_count: float
    cycle_progress: float
    missing_in_cycle: List[int]
    # v10.0 High-Dimensional Metrics
    js_divergence: float = 0.0
    shannon_entropy: float = 0.0
    regime_verdict: str = "UNKNOWN"
    entropy_trend: List[float] = field(default_factory=list)
    js_trend: List[float] = field(default_factory=list)

def analyze_stability(df: pd.DataFrame, rules: DrawRules, window_a: int = 50, window_b: int = 450) -> RegimeResult:
    """
    STORY 8.1: Calculates JS Divergence and Entropy trends.
    """
    if len(df) < window_a:
         return analyze(df, rules) # Fallback to basic analysis

    lo, hi = rules.number_range
    all_numbers = np.arange(lo, hi + 1)
    
    # 1. Frequency Distribution for Windows
    def get_dist(data: pd.DataFrame) -> np.ndarray:
        # Flatten all numbers in the window
        flat_nums = [n for sublist in data["numbers"] for n in sublist]
        counts = pd.Series(flat_nums).value_counts().reindex(all_numbers, fill_value=0)
        return counts.values / (len(flat_nums) or 1.0)

    # Window A: Recent (last 50)
    dist_a = get_dist(df.iloc[:window_a])
    # Window B: Historical (preceding 450)
    dist_b = get_dist(df.iloc[window_a:window_a + window_b])

    # 2. JS Divergence
    js_div = float(jensenshannon(dist_a, dist_b))
    
    # 3. Shannon Entropy (Recent)
    current_entropy = float(entropy(dist_a))
    
    # 4. Rolling Trends (Last 100 windows)
    js_trend, ent_trend = [], []
    for i in range(0, min(100, len(df) - window_a - 10)):
        d_a = get_dist(df.iloc[i : i + window_a])
        d_b = get_dist(df.iloc[i + window_a : i + window_a + window_a]) # Compare adjacent blocks
        js_trend.append(float(jensenshannon(d_a, d_b)))
        ent_trend.append(float(entropy(d_a)))

    # 5. Verdict
    verdict = "STABLE"
    if js_div > 0.05: verdict = "DECOUPLED"
    elif js_div > 0.02: verdict = "DRIFTING"

    # Base metrics
    base_res = analyze(df, rules)
    base_res.js_divergence = js_div
    base_res.shannon_entropy = current_entropy
    base_res.regime_verdict = verdict
    base_res.js_trend = js_trend[::-1] # Newest last
    base_res.entropy_trend = ent_trend[::-1]
    
    return base_res

def analyze(df: pd.DataFrame, rules: DrawRules) -> RegimeResult:
    if len(df) < 2:
        return RegimeResult(rules.name, 0.0, 0.0, 0.0, [])

    # 1. Repeat Rate
    repeats = []
    for i in range(1, len(df)):
        prev = set(df.iloc[i-1]["numbers"])
        curr = set(df.iloc[i]["numbers"])
        repeats.append(len(curr & prev))
    avg_repeat = sum(repeats) / len(repeats) if repeats else 0.0

    # 2. Consecutive Pairs
    consec_counts = []
    for nums in df["numbers"]:
        sorted_nums = sorted(nums)
        count = 0
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i+1] == sorted_nums[i] + 1:
                count += 1
        consec_counts.append(count)
    avg_consec = sum(consec_counts) / len(consec_counts) if consec_counts else 0.0

    # 3. Cycle Progress
    lo, hi = rules.number_range
    all_n = set(range(lo, hi + 1))
    seen = set()
    for nums in df.iloc[::-1]["numbers"]:
        seen.update(nums)
        if seen == all_n:
            break
    
    missing = sorted(list(all_n - seen))
    progress = len(seen) / len(all_n)

    return RegimeResult(
        lottery_name=rules.name,
        avg_repeat_rate=avg_repeat,
        avg_consecutive_count=avg_consec,
        cycle_progress=progress,
        missing_in_cycle=missing
    )


def print_report(res: RegimeResult) -> None:
    console = Console()
    
    # Dynamics Table
    table = Table(title=f"Game Dynamics: {res.lottery_name}", box=None)
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", justify="right")
    table.add_row("Avg Repeat Rate", f"{res.avg_repeat_rate:.2f} numbers")
    table.add_row("Cycle Progress", f"{res.cycle_progress*100:.1f}%")
    console.print(table)

    # v10.0 Stability Dashboard
    if res.regime_verdict != "UNKNOWN":
        console.print()
        console.rule("[bold]High-Dimensional Stability Dashboard[/bold]")
        
        from engine.cli.utils import ui_sparkline
        
        v_color = "green" if res.regime_verdict == "STABLE" else "yellow" if res.regime_verdict == "DRIFTING" else "red"
        console.print(f"  Regime Verdict : [bold {v_color}]{res.regime_verdict}[/]")
        console.print(f"  JS Divergence  : [bold]{res.js_divergence:.5f}[/] (Drift score)")
        console.print(f"  Shannon Entropy: [bold]{res.shannon_entropy:.4f}[/] (Signal noise)")
        
        if res.js_trend:
            console.print(f"  JS Trend       : {ui_sparkline(res.js_trend)}")
        if res.entropy_trend:
            console.print(f"  Entropy Trend  : {ui_sparkline(res.entropy_trend)}")
