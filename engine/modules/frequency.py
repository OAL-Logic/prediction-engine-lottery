"""
Frequency Module
================
Counts how often each number has appeared across all draws.

Outputs
-------
- Raw count per number
- Appearance frequency (count / total draws)
- Hot numbers  — top N by frequency
- Cold numbers — bottom N by frequency
- Expected frequency under uniform distribution
- Chi-squared statistic (observed vs. expected)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
from scipy import stats  # type: ignore[import-untyped]

from engine.adapters import DrawRules


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class FrequencyResult:
    """Output of frequency.analyze()."""

    total_draws: int
    table: pd.DataFrame          # columns: number, count, frequency, expected_freq, z_score
    hot: List[int]               # top-N numbers by frequency
    cold: List[int]              # bottom-N numbers by frequency
    chi2_statistic: float
    chi2_p_value: float          # low p → distribution is non-uniform

    def __repr__(self) -> str:
        return (
            f"FrequencyResult(draws={self.total_draws}, "
            f"hot={self.hot[:5]}, cold={self.cold[:5]}, "
            f"chi2_p={self.chi2_p_value:.4f})"
        )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def analyze(
    df: pd.DataFrame,
    rules: DrawRules,
    top_n: int = 10,
    include_bonus: bool = False,
) -> FrequencyResult:
    """
    Compute frequency statistics for all numbers in the draw history.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical draw DataFrame (from any LotteryAdapter).
    rules : DrawRules
        Lottery rules — used to build the full number universe.
    top_n : int
        How many hot/cold numbers to highlight.
    include_bonus : bool
        If True, also count bonus ball appearances in the main frequency table.

    Returns
    -------
    FrequencyResult
    """
    if df.empty:
        raise ValueError("DataFrame is empty — fetch data first.")

    total_draws = len(df)
    lo, hi = rules.number_range
    all_numbers = list(range(lo, hi + 1))

    # Flatten all drawn numbers into a single series
    main_series = pd.Series([n for draw in df["numbers"] for n in draw])

    if include_bonus and "bonus" in df.columns:
        bonus_series = pd.Series([n for draw in df["bonus"] for n in draw if draw])
        combined = pd.concat([main_series, bonus_series], ignore_index=True)
    else:
        combined = main_series

    counts = combined.value_counts().reindex(all_numbers, fill_value=0)

    total_appearances = counts.sum()
    expected_per_number = total_appearances / len(all_numbers)
    expected_freq = 1.0 / len(all_numbers)

    freq = counts / total_appearances
    z_scores = (counts - expected_per_number) / np.sqrt(
        expected_per_number * (1 - expected_freq)
    )

    table = pd.DataFrame(
        {
            "number": all_numbers,
            "count": counts.values,
            "frequency": freq.values.round(6),
            "expected_freq": round(expected_freq, 6),
            "z_score": z_scores.values.round(4),
        }
    ).sort_values("count", ascending=False).reset_index(drop=True)

    # Chi-squared goodness-of-fit
    chi2_stat, chi2_p = stats.chisquare(counts.values)

    hot = table.head(top_n)["number"].tolist()
    cold = table.tail(top_n)["number"].tolist()

    return FrequencyResult(
        total_draws=total_draws,
        table=table,
        hot=hot,
        cold=cold,
        chi2_statistic=float(chi2_stat),
        chi2_p_value=float(chi2_p),
    )


def print_report(res: FrequencyResult) -> None:
    """Print a rich-formatted table of the frequency analysis."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    
    table = Table(
        title=f"Frequency Analysis — top/bottom {len(res.hot)}",
        box=None,
        padding=(0, 2)
    )
    table.add_column("Rank", style="dim")
    table.add_column("Number", style="bold yellow")
    table.add_column("Count", justify="right")
    table.add_column("Freq %", justify="right")
    table.add_column("Z-score", justify="right")

    # Show top N and bottom N
    top_rows = res.table.head(len(res.hot))
    bottom_rows = res.table.tail(len(res.cold))
    
    for i, (_, row) in enumerate(top_rows.iterrows()):
        table.add_row(
            str(i + 1),
            str(int(row["number"])),
            str(int(row["count"])),
            f"{row['frequency']*100:.2f}%",
            f"{row['z_score']:+.3f}"
        )
    
    table.add_section()
    
    for i, (_, row) in enumerate(bottom_rows.iterrows()):
        rank = res.table.shape[0] - len(res.cold) + i + 1
        table.add_row(
            str(rank),
            str(int(row["number"])),
            str(int(row["count"])),
            f"{row['frequency']*100:.2f}%",
            f"{row['z_score']:+.3f}"
        )

    console.print(table)
    console.print(f"\n🔥 [bold]Hot:[/bold]  {res.hot}")
    console.print(f"🧊 [bold]Cold:[/bold] {res.cold}")
    
    p_style = "green" if res.chi2_p_value >= 0.05 else "red"
    console.print(f"\n[dim]Chi-squared P-value:[/dim] [{p_style}]{res.chi2_p_value:.4f}[/{p_style}]")
    if res.chi2_p_value < 0.05:
        console.print("[red]⚠ Significant non-uniformity detected.[/red]")
