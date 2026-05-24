"""
Compare-Draws Command 🔀
========================
Window-diff regime-shift detector: compares the frequency distribution of a
recent window against the full history to quantify how much the draw behaviour
has changed.

Metrics
-------
  KL divergence       — information distance between recent and full distributions
  Jensen-Shannon div  — symmetric, bounded [0, 1] variant of KL
  Chi-squared test    — independence test (are the distributions the same?)
  Top movers          — numbers whose relative frequency changed most
  Regime verdict      — STABLE / DRIFT / SHIFT based on JS thresholds

Thresholds (JS divergence)
--------------------------
  < 0.02   → STABLE   — recent window statistically consistent with history
  0.02–0.08 → DRIFT   — mild regime drift, below significance
  ≥ 0.08   → SHIFT    — statistically meaningful regime change

Example
-------
  lottery compare-draws br/lotofacil
  lottery compare-draws br/lotofacil --recent 30 --baseline 500
  lottery compare-draws br/lotofacil --export-md regime.md
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary

console = Console()

_JS_STABLE = 0.02
_JS_DRIFT  = 0.08


def _freq_vector(df, lo: int, pool_size: int) -> np.ndarray:
    counts = np.zeros(pool_size, dtype=float)
    for nums in df["numbers"]:
        for n in nums:
            if lo <= n < lo + pool_size:
                counts[n - lo] += 1
    total = counts.sum()
    return counts / total if total > 0 else counts


def _kl_div(p: np.ndarray, q: np.ndarray) -> float:
    mask = (p > 0) & (q > 0)
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def _js_div(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    return float(0.5 * _kl_div(p, m) + 0.5 * _kl_div(q, m))


def compare_draws(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    recent: Annotated[int, typer.Option("--recent", "-r",
        help="Size of recent window to compare")] = 50,
    baseline: Annotated[int, typer.Option("--baseline", "-b",
        help="Size of baseline window (0 = full history)")] = 0,
    top_n: Annotated[int, typer.Option("--top-n", "-N",
        help="Number of top movers to display")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append regime snapshot to this .md file")] = None,
) -> None:
    """🔀 Compare recent draw window against history to detect regime shifts.

    Jensen-Shannon divergence between recent frequency distribution and
    full history reveals whether the lottery has entered a new statistical
    regime — useful as a pre-scan check.

    Example: lottery compare-draws br/lotofacil
             lottery compare-draws br/lotofacil --recent 30 --baseline 200
    """
    print_command_summary("compare-draws", lottery, recent=recent,
                          baseline=baseline or "all")

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    lo, hi = adapter.rules.number_range
    pool_size = hi - lo + 1

    if len(df) < recent + 10:
        console.print("[red]Not enough draws for comparison.[/red]")
        raise typer.Exit(1)

    recent_df   = df.tail(recent)
    baseline_df = df.iloc[:-recent] if baseline == 0 else df.iloc[-(recent + baseline):-recent]

    if len(baseline_df) < 10:
        console.print("[yellow]Baseline too small — using full history.[/yellow]")
        baseline_df = df.iloc[:-recent]

    p_recent   = _freq_vector(recent_df, lo, pool_size)
    p_baseline = _freq_vector(baseline_df, lo, pool_size)

    # Smooth to avoid zero-division
    eps = 1e-9
    p_r = p_recent   + eps
    p_b = p_baseline + eps
    p_r /= p_r.sum()
    p_b /= p_b.sum()

    js  = _js_div(p_r, p_b)
    kl  = _kl_div(p_r, p_b)

    # Chi-squared test (observed counts vs expected from baseline proportion)
    obs_counts = np.array([sum(1 for nums in recent_df["numbers"] if (n + lo) in nums)
                           for n in range(pool_size)], dtype=float)
    exp_counts = p_baseline * obs_counts.sum()
    from scipy.stats import chisquare  # type: ignore[import-untyped]
    chi2_stat, chi2_p = chisquare(obs_counts + eps, f_exp=exp_counts + eps)

    # Top movers
    deltas = p_recent - p_baseline
    abs_d  = np.abs(deltas)
    top_idx = np.argsort(abs_d)[::-1][:top_n]

    # Verdict
    if js < _JS_STABLE:
        verdict = "[green]STABLE[/green]"
        verdict_plain = "STABLE"
    elif js < _JS_DRIFT:
        verdict = "[yellow]DRIFT[/yellow]"
        verdict_plain = "DRIFT"
    else:
        verdict = "[red]SHIFT[/red]"
        verdict_plain = "SHIFT"

    # ── Display ───────────────────────────────────────────────────────────────
    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]\n"
        f"Recent window: last [bold]{recent}[/bold] draws  |  "
        f"Baseline: [bold]{len(baseline_df)}[/bold] draws\n\n"
        f"  Jensen-Shannon divergence : [bold]{js:.5f}[/bold]  "
        f"(0=identical, 1=completely different)\n"
        f"  KL divergence (recent‖base): [bold]{kl:.5f}[/bold]\n"
        f"  Chi-squared p-value        : [bold]{chi2_p:.4f}[/bold]"
        f"{'  [dim](p<0.05 → significant)[/dim]' if chi2_p < 0.05 else ''}\n\n"
        f"  Regime verdict: {verdict}",
        title="🔀 Draw Window Comparison",
    ))

    table = Table(title=f"Top {top_n} Movers (recent vs baseline)", box=None,
                  header_style="bold", padding=(0, 1))
    table.add_column("Number",   justify="center", style="bold")
    table.add_column("Baseline%", justify="right", style="dim")
    table.add_column("Recent%",   justify="right")
    table.add_column("Δ",         justify="right")
    table.add_column("Direction", justify="center")

    for idx in top_idx:
        num = idx + lo
        b   = p_baseline[idx] * 100
        r   = p_recent[idx] * 100
        d   = deltas[idx] * 100
        direction = "[green]▲ rising[/green]" if d > 0 else "[red]▼ falling[/red]"
        table.add_row(str(num), f"{b:.2f}%", f"{r:.2f}%", f"{d:+.2f}%", direction)

    console.print()
    console.print(table)

    # Interpretation
    if verdict_plain == "STABLE":
        console.print(
            "\n[green]Recent draws are statistically consistent with the full history.[/green]"
            "\n[dim]Frequency patterns have not shifted — strategy signals remain valid.[/dim]"
        )
    elif verdict_plain == "DRIFT":
        console.print(
            "\n[yellow]Mild drift detected — recent draws lean slightly from historical baseline.[/yellow]"
            "\n[dim]Consider using a shorter window in `forecast` (--window 30).[/dim]"
        )
    else:
        console.print(
            "\n[red]Regime SHIFT detected — recent draws look statistically different from history.[/red]"
            "\n[dim]Strategy signals trained on full history may be mis-calibrated. "
            "Run `lottery scan` for full pre-draw conditions check.[/dim]"
        )

    if export_md:
        _export_md(export_md, lottery, adapter.rules.name, recent, len(baseline_df),
                   js, kl, chi2_p, verdict_plain, top_idx, lo, deltas, p_baseline, p_recent)
        console.print(f"\n[green]✔ Regime snapshot appended to {export_md}[/green]")


def _export_md(
    path: str,
    lottery: str,
    game_name: str,
    recent: int,
    baseline_n: int,
    js: float,
    kl: float,
    chi2_p: float,
    verdict: str,
    top_idx: np.ndarray,
    lo: int,
    deltas: np.ndarray,
    p_base: np.ndarray,
    p_rec: np.ndarray,
) -> None:
    today = _date.today().isoformat()
    rows = ""
    for idx in top_idx:
        rows += (
            f"| {idx + lo} | {p_base[idx]*100:.2f}% | {p_rec[idx]*100:.2f}% | "
            f"{deltas[idx]*100:+.2f}% |\n"
        )

    content = f"""---
type: pattern-log
subtype: regime
game: "{game_name}"
lottery: "{lottery}"
recent_window: {recent}
baseline_draws: {baseline_n}
date: {today}
js_divergence: {js:.5f}
kl_divergence: {kl:.5f}
chi2_p: {chi2_p:.4f}
regime_verdict: {verdict}
tags: [prediction-engine, regime, compare-draws, pattern-log]
---

# Regime Check: {game_name} — {today}

**Recent:** last {recent} draws | **Baseline:** {baseline_n} draws

| Metric | Value |
|--------|-------|
| Jensen-Shannon divergence | {js:.5f} |
| KL divergence (recent‖base) | {kl:.5f} |
| Chi-squared p-value | {chi2_p:.4f} |
| **Regime verdict** | **{verdict}** |

## Top Movers

| Number | Baseline% | Recent% | Δ |
|--------|----------|---------|---|
{rows}

---
*Thresholds: JS < 0.02 → STABLE | 0.02–0.08 → DRIFT | ≥ 0.08 → SHIFT*
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
