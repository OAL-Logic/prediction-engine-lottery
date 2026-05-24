"""
History Scan Command 📅
=======================
Retrospective GO/NO-GO timeline across historical draw windows.

Moves the analysis window backwards in time — evaluating what the
scan would have returned for each of the last N draw positions.
Uses a lightweight 3-layer approximation:
  Layer 1  Chi-squared fairness (uniform distribution test)
  Layer 2  Rolling signal stability (bayesian confidence std-dev)
  Layer 3  JS regime divergence (recent vs full history)

The output is a sparkline timeline + compact table showing the
evolution of scan conditions over time. Useful for:
  • Understanding how often "GO" conditions occur
  • Identifying structural patterns in condition cycles
  • Backtesting: did GO conditions precede better-than-expected draws?

Output
------
  Timeline sparkline   ▓=GO  ░=CAUTION  ·=NO-GO (oldest → newest)
  Recent table         last-N scan snapshots
  Stats panel          GO%, CAUTION%, NO-GO%, avg score

Example
-------
  lottery history-scan br/lotofacil
  lottery history-scan br/lotofacil --windows 30 --window-size 50
  lottery history-scan br/lotofacil --export-md hscan.md
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

from engine.cli.utils import get_adapter

console = Console()

_SPARK_GO  = "▓"
_SPARK_CAU = "░"
_SPARK_NO  = "·"

_MAX_SCORE = 6  # 3 layers × 2pts each
_GO_PCT    = 0.75
_CAU_PCT   = 0.50


def _chi2_score(df, lo: int, hi: int, pick: int) -> int:
    """Layer 1: chi-squared fairness. Returns 0/1/2."""
    pool = hi - lo + 1
    counts = np.zeros(pool, dtype=float)
    for row in df.itertuples():
        for n in row.numbers:
            if lo <= n <= hi:
                counts[n - lo] += 1
    total = counts.sum()
    if total == 0:
        return 0
    expected = total / pool
    chi2 = float(np.sum((counts - expected) ** 2 / (expected + 1e-9)))
    dof  = pool - 1
    # Normalised chi2: score based on ratio to DOF
    ratio = chi2 / (dof + 1e-9)
    if ratio <= 1.2:
        return 2
    if ratio <= 1.8:
        return 1
    return 0


def _stability_score(df, adapter, window: int) -> int:
    """Layer 2: confidence std-dev stability. Returns 0/1/2."""
    try:
        from engine.strategies import get_strategy
        strat = get_strategy("bayesian")
        n = len(df)
        confs = []
        step = max(1, window // 5)
        for i in range(0, min(5, n // step)):
            end = n - i * step
            start = max(0, end - window)
            sub = df.iloc[start:end]
            if len(sub) < 20:
                break
            try:
                res = strat.suggest(sub, adapter.rules, count=1, temperature=0.0)
                confs.append(res.confidence)
            except Exception:
                pass
        if len(confs) < 2:
            return 1  # neutral
        sd = np.std(confs, ddof=1)
        if sd <= 0.04:
            return 2
        if sd <= 0.10:
            return 1
        return 0
    except Exception:
        return 1


def _regime_score(df, lo: int, hi: int, recent: int) -> int:
    """Layer 3: JS divergence. Returns 0/1/2."""
    pool = hi - lo + 1
    eps = 1e-9

    def _freq(subset):
        counts = np.zeros(pool, dtype=float)
        for row in subset.itertuples():
            for n in row.numbers:
                if lo <= n <= hi:
                    counts[n - lo] += 1
        total = counts.sum()
        return (counts / total + eps) if total > 0 else (counts + eps)

    recent_df   = df.tail(recent)
    baseline_df = df.iloc[:-recent] if len(df) > recent else df
    if len(baseline_df) < 10:
        return 1

    p_r = _freq(recent_df)
    p_b = _freq(baseline_df)
    p_r /= p_r.sum()
    p_b /= p_b.sum()
    m = 0.5 * (p_r + p_b)
    kl_pm = float(np.sum(p_r * np.log(p_r / m)))
    kl_qm = float(np.sum(p_b * np.log(p_b / m)))
    js = 0.5 * kl_pm + 0.5 * kl_qm

    if js < 0.02:
        return 2
    if js < 0.08:
        return 1
    return 0


def _verdict(total: int) -> str:
    pct = total / _MAX_SCORE
    if pct >= _GO_PCT:
        return "GO"
    if pct >= _CAU_PCT:
        return "CAUTION"
    return "NO-GO"


def history_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    windows: Annotated[int, typer.Option("--windows", "-n",
        help="How many historical scan windows to evaluate")] = 20,
    window_size: Annotated[int, typer.Option("--window-size", "-w",
        help="Draws per scan window")] = 50,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append history-scan report to this .md file")] = None,
) -> None:
    """📅 Retrospective GO/NO-GO timeline across historical draw windows.

    Evaluates what the scan would have returned for each recent draw
    position, using a 3-layer (chi-squared + stability + regime) score.
    Shows a sparkline timeline + stats.

    Example: lottery history-scan br/lotofacil
             lottery history-scan br/lotofacil --windows 30 --window-size 50
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count

    n_total = len(df)
    if n_total < window_size + windows:
        console.print(
            f"[dim]Not enough history for {windows} windows of {window_size}. "
            f"Have {n_total} draws; need {window_size + windows}.[/dim]"
        )
        windows = max(1, n_total - window_size)

    scan_results: list[dict] = []

    with console.status("") as status:
        for i in range(windows, 0, -1):
            # Window ends at position n_total - (i - 1) (so newest scan = i=1)
            end   = n_total - (i - 1)
            start = max(0, end - window_size)
            sub   = df.iloc[start:end]

            if len(sub) < 20:
                continue

            status.update(f"[dim]Scanning window {windows - i + 1}/{windows}…[/dim]")

            # Date of the last draw in this window
            try:
                last_row = sub.iloc[-1]
                date_str = str(last_row.draw_date) if str(last_row.draw_date) != "nan" else "?"
                draw_id  = int(last_row.draw_id)
            except Exception:
                date_str = "?"
                draw_id  = 0

            c1 = _chi2_score(sub, lo, hi, pick)
            c2 = _stability_score(sub, adapter, window_size)
            c3 = _regime_score(sub, lo, hi, min(20, len(sub) // 2))
            total = c1 + c2 + c3
            verd  = _verdict(total)

            scan_results.append({
                "draw_id":  draw_id,
                "date":     date_str,
                "c1":       c1,
                "c2":       c2,
                "c3":       c3,
                "total":    total,
                "verdict":  verd,
            })

    if not scan_results:
        console.print("[red]No scan windows produced results.[/red]")
        raise typer.Exit(1)

    # ── Sparkline ─────────────────────────────────────────────────────────────
    spark = ""
    for r in scan_results:
        if r["verdict"] == "GO":
            spark += _SPARK_GO
        elif r["verdict"] == "CAUTION":
            spark += _SPARK_CAU
        else:
            spark += _SPARK_NO

    # Wrap into 60-char lines
    lines = [spark[i:i+60] for i in range(0, len(spark), 60)]
    console.print(f"\n[bold]{rules.name}[/bold]  [dim](oldest → newest, "
                  f"{windows} windows of {window_size} draws each)[/dim]")
    for line in lines:
        coloured = (
            line
            .replace(_SPARK_GO,  f"[green]{_SPARK_GO}[/green]")
            .replace(_SPARK_CAU, f"[yellow]{_SPARK_CAU}[/yellow]")
            .replace(_SPARK_NO,  f"[dim]{_SPARK_NO}[/dim]")
        )
        console.print("  " + coloured)
    console.print(f"  [green]{_SPARK_GO}[/green]=GO  "
                  f"[yellow]{_SPARK_CAU}[/yellow]=CAUTION  "
                  f"[dim]{_SPARK_NO}[/dim]=NO-GO\n")

    # ── Table ─────────────────────────────────────────────────────────────────
    table = Table(
        title=f"History Scan — {rules.name}  (last {len(scan_results)} windows)",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("Draw",    justify="right",  style="dim")
    table.add_column("Date",    justify="left")
    table.add_column("χ²",      justify="center")
    table.add_column("Stab",    justify="center")
    table.add_column("Regime",  justify="center")
    table.add_column("Score",   justify="right")
    table.add_column("Verdict", justify="center")

    for r in reversed(scan_results[-20:]):
        if r["verdict"] == "GO":
            vfmt = "[bold green]GO[/bold green]"
        elif r["verdict"] == "CAUTION":
            vfmt = "[yellow]CAUTION[/yellow]"
        else:
            vfmt = "[red]NO-GO[/red]"
        table.add_row(
            str(r["draw_id"]),
            r["date"],
            str(r["c1"]), str(r["c2"]), str(r["c3"]),
            f"{r['total']}/{_MAX_SCORE}",
            vfmt,
        )

    console.print(table)

    # ── Stats panel ───────────────────────────────────────────────────────────
    n = len(scan_results)
    n_go   = sum(1 for r in scan_results if r["verdict"] == "GO")
    n_cau  = sum(1 for r in scan_results if r["verdict"] == "CAUTION")
    n_no   = n - n_go - n_cau
    avg_score = np.mean([r["total"] for r in scan_results])

    # Run length of current streak
    streak_verdict = scan_results[-1]["verdict"]
    streak_len = 0
    for r in reversed(scan_results):
        if r["verdict"] == "streak_verdict":
            streak_len += 1
        else:
            break
    # correct the streak calculation
    streak_len = 0
    for r in reversed(scan_results):
        if r["verdict"] == streak_verdict:
            streak_len += 1
        else:
            break

    streak_colour = "green" if streak_verdict == "GO" else "yellow" if streak_verdict == "CAUTION" else "red"

    console.print()
    console.print(Panel(
        f"[green]GO:[/green] {n_go} ({n_go/n:.0%})   "
        f"[yellow]CAUTION:[/yellow] {n_cau} ({n_cau/n:.0%})   "
        f"[red]NO-GO:[/red] {n_no} ({n_no/n:.0%})\n"
        f"[dim]Avg score: {avg_score:.1f}/{_MAX_SCORE}  ·  "
        f"Current streak: [{streak_colour}]{streak_len}× {streak_verdict}[/{streak_colour}][/dim]",
        title="📅 History Scan Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            scan_results, windows, window_size, n_go, n_cau, n_no, avg_score,
        )
        console.print(f"\n[green]✔ History scan appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    results: list[dict], n_windows: int, window_size: int,
    n_go: int, n_cau: int, n_no: int, avg_score: float,
) -> None:
    n = len(results)
    recent = results[-10:]
    rows = "".join(
        f"| {r['draw_id']} | {r['date']} | {r['total']}/{_MAX_SCORE} | **{r['verdict']}** |\n"
        for r in recent
    )
    spark = "".join(
        _SPARK_GO if r["verdict"] == "GO"
        else _SPARK_CAU if r["verdict"] == "CAUTION"
        else _SPARK_NO
        for r in results
    )

    content = f"""
---
type: diagnostic
subtype: history-scan
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
windows_evaluated: {n}
window_size: {window_size}
go_count: {n_go}
caution_count: {n_cau}
no_go_count: {n_no}
go_rate: {n_go/n:.2f}
avg_score: {avg_score:.2f}
---

## History Scan: {game_name} ({today.isoformat()})

**Windows:** {n}  ·  **GO:** {n_go} ({n_go/n:.0%})  ·  **CAUTION:** {n_cau} ({n_cau/n:.0%})  ·  **NO-GO:** {n_no} ({n_no/n:.0%})
**Avg score:** {avg_score:.1f}/{_MAX_SCORE}

Timeline (oldest → newest): `{spark}`

### Last 10 Windows

| Draw | Date | Score | Verdict |
|------|------|-------|---------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
