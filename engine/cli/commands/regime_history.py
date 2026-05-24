"""
Regime History Command 📅
=========================
Timeline of statistical regime labels across all available history.

At each sample point the command computes Jensen-Shannon divergence
between a "recent" window and the preceding baseline, producing a
STABLE / DRIFT / SHIFT label — the same signal used by the alert and
scan commands for the *current* posture. Sweeping this across history
makes the regime track record visible for the first time.

  STABLE  — JS divergence < 0.02  (recent draws look like the long run)
  DRIFT   — JS divergence 0.02–0.08  (moderate distributional change)
  SHIFT   — JS divergence ≥ 0.08  (notable regime break)

Useful for:
  • Auditing whether GO/NO-GO signals are stable or flip constantly
  • Identifying long SHIFT periods (structural breaks in draw patterns)
  • Correlating regime labels with actual hit rates from ticket logs

Output
------
  Mini-timeline   ASCII row showing regime per sample point
  Monthly table   aggregated regime labels + mean JS per month
  Summary panel   total points, regime breakdown, longest stable streak

Example
-------
  lottery regime-history br/lotofacil
  lottery regime-history br/mega-sena --window 40 --step 5
  lottery regime-history br/lotofacil --export-md regime_log.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_JS_STABLE = 0.02
_JS_DRIFT  = 0.08
_REGIME_SYM = {"STABLE": "■", "DRIFT": "░", "SHIFT": "□", "UNKNOWN": "?"}
_REGIME_COL = {"STABLE": "green", "DRIFT": "yellow", "SHIFT": "red", "UNKNOWN": "dim"}


def _js_divergence(p: list[float], q: list[float]) -> float:
    """Symmetric Jensen-Shannon divergence (squared JS distance)."""
    try:
        from scipy.spatial.distance import jensenshannon
        return float(jensenshannon(p, q)) ** 2
    except Exception:
        return 0.0


def _regime_at(df_slice, lo: int, pool_sz: int, window: int) -> tuple[float, str]:
    """Compute JS regime label for the tail of df_slice."""
    if len(df_slice) < window + 5:
        return 0.0, "STABLE"
    pool_nums = list(range(lo, lo + pool_sz))
    all_vc  = df_slice["numbers"].explode().value_counts(normalize=True).reindex(pool_nums, fill_value=0)
    rec_vc  = df_slice.tail(window)["numbers"].explode().value_counts(normalize=True).reindex(pool_nums, fill_value=0)
    js = _js_divergence(list(all_vc), list(rec_vc))
    if js < _JS_STABLE:
        return js, "STABLE"
    if js < _JS_DRIFT:
        return js, "DRIFT"
    return js, "SHIFT"


def regime_history(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    window: Annotated[int, typer.Option("--window", "-w",
        help="Recent window for JS divergence (draws)")] = 30,
    baseline: Annotated[int, typer.Option("--baseline", "-b",
        help="Minimum preceding draws needed before sampling")] = 60,
    step: Annotated[int, typer.Option("--step", "-s",
        help="Sample every N draws (larger = faster, lower resolution)")] = 10,
    recent: Annotated[int, typer.Option("--recent", "-r",
        help="Show only the last N sample points (0 = all)")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append regime history report to this .md file")] = None,
) -> None:
    """📅 Timeline of GO / DRIFT / SHIFT regime labels across history.

    Sweeps the Jensen-Shannon regime classifier across all available
    draw history and shows how often each regime was active. Audits
    whether the current GO/NO-GO signal is stable or constantly shifting.

    Example: lottery regime-history br/lotofacil
             lottery regime-history br/mega-sena --window 40 --step 5
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pool_sz  = hi - lo + 1

    if len(df) < baseline + window + 5:
        console.print(f"[dim]Need at least {baseline + window + 5} draws; have {len(df)}.[/dim]")
        raise typer.Exit(0)

    all_rows = list(df.itertuples())

    # ── Sample regime at each step ─────────────────────────────────────────
    sample_points: list[tuple] = []  # (draw_idx, date_str, js, regime)
    for i in range(baseline, len(all_rows), step):
        slice_df = df.iloc[: i + 1]
        js, regime = _regime_at(slice_df, lo, pool_sz, window)
        row = all_rows[i]
        date_str = str(row.date)[:10] if hasattr(row, "date") and row.date is not None else "—"
        sample_points.append((row.draw_id, date_str, js, regime))

    if not sample_points:
        console.print("[dim]No sample points computed.[/dim]")
        raise typer.Exit(0)

    if recent > 0:
        sample_points = sample_points[-recent:]

    # ── Monthly aggregation ────────────────────────────────────────────────
    months: dict[str, list] = {}
    for draw_id, date_str, js, regime in sample_points:
        month_key = date_str[:7] if len(date_str) >= 7 else "unknown"
        months.setdefault(month_key, []).append((js, regime))

    # ── ASCII mini-timeline ────────────────────────────────────────────────
    symbols = "".join(_REGIME_SYM.get(r, "?") for _, _, _, r in sample_points)
    # Chunk into rows of 60
    chunk_size = 60
    timeline_rows = [symbols[i: i + chunk_size] for i in range(0, len(symbols), chunk_size)]

    console.print()
    console.print(f"  [bold]Regime Timeline[/bold]  "
                  f"[green]■[/green]=STABLE  [yellow]░[/yellow]=DRIFT  [red]□[/red]=SHIFT  "
                  f"(step={step} draws each)")
    for row_str in timeline_rows:
        colored = (
            row_str
            .replace("■", "[green]■[/green]")
            .replace("░", "[yellow]░[/yellow]")
            .replace("□", "[red]□[/red]")
        )
        console.print(f"  {colored}")
    console.print()

    # ── Monthly summary table ──────────────────────────────────────────────
    tbl = Table(
        title=f"📅 Regime History — {rules.name}  (window={window}, step={step})",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Month",    justify="center", style="bold yellow")
    tbl.add_column("Points",   justify="right",  style="dim")
    tbl.add_column("Dominant", justify="center")
    tbl.add_column("Stable%",  justify="right")
    tbl.add_column("Drift%",   justify="right")
    tbl.add_column("Shift%",   justify="right")
    tbl.add_column("Avg JS",   justify="right",  style="dim")

    for month in sorted(months):
        pts = months[month]
        regimes = [r for _, r in pts]
        dominant = Counter(regimes).most_common(1)[0][0]
        n = len(pts)
        st_pct = regimes.count("STABLE") / n * 100
        dr_pct = regimes.count("DRIFT")  / n * 100
        sh_pct = regimes.count("SHIFT")  / n * 100
        avg_js = sum(j for j, _ in pts) / n
        col = _REGIME_COL.get(dominant, "dim")
        tbl.add_row(
            month,
            str(n),
            f"[{col}]{dominant}[/{col}]",
            f"{st_pct:.0f}%",
            f"{dr_pct:.0f}%",
            f"{sh_pct:.0f}%",
            f"{avg_js:.4f}",
        )

    console.print(tbl)

    # ── Summary stats ──────────────────────────────────────────────────────
    all_regimes = [r for _, _, _, r in sample_points]
    total = len(all_regimes)
    st_n  = all_regimes.count("STABLE")
    dr_n  = all_regimes.count("DRIFT")
    sh_n  = all_regimes.count("SHIFT")

    # Longest stable streak
    longest_stable = cur = 0
    for r in all_regimes:
        cur = cur + 1 if r == "STABLE" else 0
        longest_stable = max(longest_stable, cur)

    latest_regime = all_regimes[-1] if all_regimes else "UNKNOWN"
    lat_col = _REGIME_COL.get(latest_regime, "dim")

    console.print()
    console.print(Panel(
        f"[{lat_col}]Latest regime: {latest_regime}[/{lat_col}]\n\n"
        f"[dim]Stable: {st_n}/{total} ({st_n/total*100:.0f}%)  ·  "
        f"Drift: {dr_n}/{total} ({dr_n/total*100:.0f}%)  ·  "
        f"Shift: {sh_n}/{total} ({sh_n/total*100:.0f}%)\n"
        f"Longest stable streak: {longest_stable} points  ·  "
        f"Total draws analysed: {len(df)}  ·  Step: {step}[/dim]",
        title="📅 Regime Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            window, step, total, st_n, dr_n, sh_n, longest_stable,
            latest_regime, sample_points[-10:],
        )
        console.print(f"\n[green]✔ Regime history report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    window: int, step: int, total: int,
    st_n: int, dr_n: int, sh_n: int,
    longest_stable: int, latest_regime: str,
    recent_points: list,
) -> None:
    rows_md = ""
    for draw_id, date_str, js, regime in recent_points:
        rows_md += f"| {draw_id} | {date_str} | {regime} | {js:.4f} |\n"

    content = f"""
---
type: diagnostic
subtype: regime-history
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
window: {window}
step: {step}
total_points: {total}
stable_pct: {st_n/total*100:.1f}
drift_pct: {dr_n/total*100:.1f}
shift_pct: {sh_n/total*100:.1f}
longest_stable_streak: {longest_stable}
latest_regime: {latest_regime}
---

## Regime History: {game_name} ({today.isoformat()})

**Window:** {window}  ·  **Step:** {step}  ·  **Sampled:** {total} points
**Stable:** {st_n/total*100:.0f}%  ·  **Drift:** {dr_n/total*100:.0f}%  ·  **Shift:** {sh_n/total*100:.0f}%
**Latest regime:** {latest_regime}  ·  **Longest stable streak:** {longest_stable}

### Recent sample points

| Draw | Date | Regime | JS |
|------|------|--------|----|
{rows_md}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
