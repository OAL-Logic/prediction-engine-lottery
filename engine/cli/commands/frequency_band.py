"""
Frequency Band Command 📡
=========================
Multi-horizon frequency tier classification for all pool numbers.

For each number, computes its hit rate over three windows:
  Short  — last S draws  (default 15)
  Mid    — last M draws  (default 50)
  Long   — last L draws  (default 150)

Each window produces a tier based on percentile rank within that window:
  HOT    — top 25% hit rate
  WARM   — middle 50%
  COLD   — bottom 25%

The cross-horizon pattern reveals trajectory:
  COLD→COLD→HOT  = long-term underdog, recently heating up
  HOT→WARM→COLD  = cooling number (was hot, now declining)
  HOT→HOT→HOT    = sustained performer

Useful for:
  • Finding numbers transitioning from cold to hot (momentum candidates)
  • Identifying numbers hot only in the short term (possible regression)
  • Filtering rank-numbers by sustained vs fleeting performance

Output
------
  Band table    all pool numbers × 3 horizons, sorted by short tier
  Trajectory    ASCII summary: S M L column headings, tier symbols
  Summary panel numbers with notable cross-horizon patterns

Example
-------
  lottery frequency-band br/lotofacil
  lottery frequency-band br/lotofacil --short 10 --mid 30 --long 100
  lottery frequency-band br/lotofacil --top 20
  lottery frequency-band br/mega-sena --export-md bands.md
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_TIER_HOT  = ("HOT",  "bold red")
_TIER_WARM = ("WARM", "yellow")
_TIER_COLD = ("COLD", "dim")

_TIER_SYM = {"HOT": "🔴", "WARM": "🟡", "COLD": "🔵"}


def _hit_rates(rows: list, pool: list[int]) -> dict[int, float]:
    n = len(rows)
    if n == 0:
        return {num: 0.0 for num in pool}
    counts = {num: 0 for num in pool}
    for row in rows:
        for n_val in row.numbers:
            if n_val in counts:
                counts[n_val] += 1
    return {num: counts[num] / n for num in pool}


def _tier_from_rates(rates: dict[int, float], pool: list[int]) -> dict[int, str]:
    vals = sorted(rates[n] for n in pool)
    n    = len(vals)
    low_cut  = vals[n // 4]
    high_cut = vals[3 * n // 4]
    tiers: dict[int, str] = {}
    for num in pool:
        r = rates[num]
        if r >= high_cut:
            tiers[num] = "HOT"
        elif r <= low_cut:
            tiers[num] = "COLD"
        else:
            tiers[num] = "WARM"
    return tiers


def frequency_band(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    short:   Annotated[int, typer.Option("--short", "-s",
        help="Short window (draws)")] = 15,
    mid:     Annotated[int, typer.Option("--mid", "-m",
        help="Mid window (draws)")] = 50,
    long:    Annotated[int, typer.Option("--long", "-l",
        help="Long window (draws)")] = 150,
    top:     Annotated[int, typer.Option("--top", "-N",
        help="Show only top-N by short-window rate (0 = all)")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append frequency band report to this .md file")] = None,
) -> None:
    """📡 Multi-horizon frequency tier classification for all pool numbers.

    Classifies every number as HOT/WARM/COLD across three time horizons,
    revealing which numbers are rising, stable, or cooling.

    Example: lottery frequency-band br/lotofacil
             lottery frequency-band br/lotofacil --short 10 --mid 30 --long 100
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pool     = list(range(lo, hi + 1))

    min_req = long + 5
    if len(df) < min_req:
        console.print(f"[dim]Need at least {min_req} draws; have {len(df)}.[/dim]")
        raise typer.Exit(0)

    all_rows = list(df.itertuples())
    rows_s   = all_rows[-short:]
    rows_m   = all_rows[-mid:]
    rows_l   = all_rows[-long:]

    rates_s = _hit_rates(rows_s, pool)
    rates_m = _hit_rates(rows_m, pool)
    rates_l = _hit_rates(rows_l, pool)

    tiers_s = _tier_from_rates(rates_s, pool)
    tiers_m = _tier_from_rates(rates_m, pool)
    tiers_l = _tier_from_rates(rates_l, pool)

    # Sort by short rate descending, then mid
    sorted_pool = sorted(
        pool,
        key=lambda n: (-rates_s[n], -rates_m[n], -rates_l[n])
    )

    n_show  = top if top > 0 else len(pool)
    display = sorted_pool[:n_show]

    # ── Table ──────────────────────────────────────────────────────────────
    tbl = Table(
        title=f"📡 Frequency Band — {rules.name}  "
              f"(S={short}  M={mid}  L={long} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Number",   justify="center", style="bold yellow")
    tbl.add_column(f"Short%",  justify="right")
    tbl.add_column("S-Tier",   justify="center")
    tbl.add_column(f"Mid%",    justify="right")
    tbl.add_column("M-Tier",   justify="center")
    tbl.add_column(f"Long%",   justify="right")
    tbl.add_column("L-Tier",   justify="center")
    tbl.add_column("Pattern",  justify="center", style="dim")

    rising:    list[int] = []
    cooling:   list[int] = []
    sustained: list[int] = []

    def fmt_tier(t: str) -> str:
        name, colour = _TIER_HOT if t == "HOT" else _TIER_WARM if t == "WARM" else _TIER_COLD
        return f"[{colour}]{name}[/{colour}]"

    for num in display:
        ts = tiers_s[num]
        tm = tiers_m[num]
        tl = tiers_l[num]
        pattern = f"{_TIER_SYM[ts]}{_TIER_SYM[tm]}{_TIER_SYM[tl]}"

        # Classify trajectory
        tier_val = {"HOT": 2, "WARM": 1, "COLD": 0}
        if tier_val[ts] > tier_val[tl]:
            rising.append(num)
        elif tier_val[ts] < tier_val[tl]:
            cooling.append(num)
        elif ts == "HOT":
            sustained.append(num)

        tbl.add_row(
            str(num),
            f"{rates_s[num]:.0%}",
            fmt_tier(ts),
            f"{rates_m[num]:.0%}",
            fmt_tier(tm),
            f"{rates_l[num]:.0%}",
            fmt_tier(tl),
            pattern,
        )

    console.print()
    console.print(tbl)
    console.print(
        f"\n  [dim]Pattern key:  {_TIER_SYM['HOT']}=HOT  "
        f"{_TIER_SYM['WARM']}=WARM  {_TIER_SYM['COLD']}=COLD  "
        f"(S=short M=mid L=long)[/dim]"
    )

    # ── Summary panel ──────────────────────────────────────────────────────
    rising_str    = "  ".join(f"#{n}" for n in rising[:8])    or "none"
    cooling_str   = "  ".join(f"#{n}" for n in cooling[:8])   or "none"
    sustained_str = "  ".join(f"#{n}" for n in sustained[:8]) or "none"

    console.print()
    console.print(Panel(
        f"[bold green]Rising (cold→hot):[/bold green]    {rising_str}\n"
        f"[red]Cooling (hot→cold):[/red]   {cooling_str}\n"
        f"[dim]Sustained hot:          {sustained_str}\n"
        f"Rising: {len(rising)}  ·  Cooling: {len(cooling)}  ·  "
        f"Sustained: {len(sustained)}  ·  Windows: S={short} M={mid} L={long}[/dim]",
        title="📡 Frequency Band Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            short, mid, long, rising, cooling, sustained,
        )
        console.print(f"\n[green]✔ Frequency band report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    short: int, mid: int, long: int,
    rising: list, cooling: list, sustained: list,
) -> None:
    rising_str    = " ".join(f"#{n}" for n in rising[:10])    or "none"
    cooling_str   = " ".join(f"#{n}" for n in cooling[:10])   or "none"
    sustained_str = " ".join(f"#{n}" for n in sustained[:10]) or "none"

    content = f"""
---
type: diagnostic
subtype: frequency-band
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
short_window: {short}
mid_window: {mid}
long_window: {long}
rising_count: {len(rising)}
cooling_count: {len(cooling)}
sustained_count: {len(sustained)}
---

## Frequency Band: {game_name} ({today.isoformat()})

**Windows:** S={short}  M={mid}  L={long} draws
**Rising:** {rising_str}
**Cooling:** {cooling_str}
**Sustained hot:** {sustained_str}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
