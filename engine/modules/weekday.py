"""
Weekday Bias Module 📅
=====================
Analyses how number frequencies vary by day of the week.
Useful for lotteries that draw on multiple days (e.g. Wednesday/Saturday).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from rich.console import Console
from rich.table import Table

from engine.adapters import DrawRules


@dataclass
class WeekdayResult:
    """Output of weekday.analyze()."""
    lottery_name: str
    counts: Dict[str, Dict[int, int]]  # weekday -> {number: count}
    total_draws: Dict[str, int]        # weekday -> total draws on that day
    
    @property
    def weekdays(self) -> List[str]:
        return sorted(list(self.counts.keys()))


def analyze(df: pd.DataFrame, rules: DrawRules) -> WeekdayResult:
    """
    Calculate number frequencies per weekday.
    """
    if "date" not in df.columns:
        raise ValueError("DataFrame must have a 'date' column for weekday analysis.")

    # Day mapping
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    df["weekday_name"] = df["date"].dt.day_name()
    
    weekday_counts = {}
    weekday_totals = {}
    
    lo, hi = rules.number_range
    
    for day in days:
        day_df = df[df["weekday_name"] == day]
        if day_df.empty:
            continue
            
        totals = {}
        for numbers in day_df["numbers"]:
            for n in numbers:
                totals[n] = totals.get(n, 0) + 1
        
        weekday_counts[day] = totals
        weekday_totals[day] = len(day_df)
        
    return WeekdayResult(
        lottery_name=rules.name,
        counts=weekday_counts,
        total_draws=weekday_totals
    )


def print_report(res: WeekdayResult, top_n: int = 5) -> None:
    """Print a rich table showing top numbers per weekday."""
    console = Console()
    table = Table(title=f"Day-of-Week Bias: {res.lottery_name}", box=None)
    table.add_column("Weekday", style="bold cyan")
    table.add_column("Draws", justify="right", style="dim")
    table.add_column(f"Top {top_n} Hot Numbers", justify="left")

    for day in res.weekdays:
        counts = res.counts[day]
        # Sort by count desc, then number asc
        sorted_nums = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_hot = [str(n) for n, c in sorted_nums[:top_n]]
        
        table.add_row(
            day,
            str(res.total_draws[day]),
            ", ".join(top_hot)
        )

    console.print(table)
    console.print("\n[dim]Note: Certain machines or ball sets may be scheduled for specific days.[/dim]")
