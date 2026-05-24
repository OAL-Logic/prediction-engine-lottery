"""
Combo Rank Command 🎯
=====================
Ranks draw-property combination profiles by historical frequency.

Each draw has three bucketed properties:
  Sum band      — low / mid / high  (thirds of observed sum range)
  Parity mix    — even-heavy / balanced / odd-heavy
  Consecutive   — none / sparse / dense  (0, 1-2, 3+ consecutive pairs)

By counting how often each combination occurred historically, the command
shows which profiles are common vs rare. Users can then check their ticket
against this distribution.

Useful for:
  • Avoiding unusual "profile" tickets that rarely appear in draws
  • Validating that a generated ticket fits normal distribution patterns
  • Understanding which structural properties correlate most with real draws

Output
------
  Profile table    all 27 (3×3×3) combinations ranked by frequency
  Ticket check     if --check provided: classify the ticket + rank its profile
  Summary panel    top and bottom 3 profiles

Example
-------
  lottery combo-rank br/lotofacil
  lottery combo-rank br/lotofacil --draws 200 --top 10
  lottery combo-rank br/lotofacil --check "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
  lottery combo-rank br/mega-sena --export-md profiles.md
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


def _sum_band(s: float, low_cut: float, high_cut: float) -> str:
    if s <= low_cut:
        return "low"
    if s >= high_cut:
        return "high"
    return "mid"


def _parity_mix(nums: list[int], pick: int) -> str:
    evens = sum(1 for n in nums if n % 2 == 0)
    ratio = evens / pick
    if ratio > 0.6:
        return "even-heavy"
    if ratio < 0.4:
        return "odd-heavy"
    return "balanced"


def _consec_band(nums: list[int]) -> str:
    pairs = sum(1 for a, b in zip(sorted(nums), sorted(nums)[1:]) if b == a + 1)
    if pairs == 0:
        return "none"
    if pairs <= 2:
        return "sparse"
    return "dense"


def combo_rank(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to analyse")] = 200,
    top: Annotated[int, typer.Option("--top",
        help="Show only top-N profiles (0 = all 27)")] = 15,
    check: Annotated[Optional[str], typer.Option("--check",
        help="Space-separated ticket to classify and rank")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append combo rank report to this .md file")] = None,
) -> None:
    """🎯 Rank draw-property profiles (sum+parity+consecutive) by frequency.

    Shows which structural combination is most/least common in historical
    draws. Optionally classifies a ticket against the distribution.

    Example: lottery combo-rank br/lotofacil
             lottery combo-rank br/lotofacil --check "1 3 5 7 10 ..."
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pick     = rules.pick_count

    n_draws  = min(draws, len(df))
    window   = df.tail(n_draws)

    # ── Compute sum range thresholds from data ─────────────────────────────
    sums = [sum(row.numbers) for row in window.itertuples() if row.numbers is not None and len(row.numbers) > 0]
    if not sums:
        console.print("[dim]No valid draws found.[/dim]")
        raise typer.Exit(0)

    sums_sorted = sorted(sums)
    low_cut  = sums_sorted[len(sums_sorted) // 3]
    high_cut = sums_sorted[2 * len(sums_sorted) // 3]

    # ── Count profiles ─────────────────────────────────────────────────────
    profile_counts: Counter[tuple] = Counter()

    for row in window.itertuples():
        nums = sorted(row.numbers)
        if nums is None or len(nums) == 0:
            continue
        sb = _sum_band(sum(nums), low_cut, high_cut)
        pm = _parity_mix(nums, pick)
        cb = _consec_band(nums)
        profile_counts[(sb, pm, cb)] += 1

    total = sum(profile_counts.values())

    # Build all 27 profiles (including zero-count ones)
    all_sum_bands   = ["low", "mid", "high"]
    all_parity      = ["even-heavy", "balanced", "odd-heavy"]
    all_consec      = ["none", "sparse", "dense"]

    all_profiles: list[dict] = []
    for sb in all_sum_bands:
        for pm in all_parity:
            for cb in all_consec:
                key   = (sb, pm, cb)
                count = profile_counts.get(key, 0)
                pct   = count / total * 100 if total > 0 else 0.0
                all_profiles.append({
                    "sum_band":  sb,
                    "parity":    pm,
                    "consec":    cb,
                    "count":     count,
                    "pct":       pct,
                    "key":       key,
                })

    ranked = sorted(all_profiles, key=lambda d: -d["count"])

    n_show   = top if top > 0 else len(ranked)
    display  = ranked[:n_show]

    # ── Profile table ──────────────────────────────────────────────────────
    tbl = Table(
        title=f"🎯 Combo Rank — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Rank",     justify="right",  style="dim")
    tbl.add_column("Sum",      justify="center")
    tbl.add_column("Parity",   justify="center")
    tbl.add_column("Consec",   justify="center")
    tbl.add_column("Count",    justify="right",  style="bold yellow")
    tbl.add_column("Freq%",    justify="right")
    tbl.add_column("Bar",      justify="left")

    max_count = ranked[0]["count"] if ranked else 1

    for rank, d in enumerate(display, 1):
        bar_width = round(d["count"] / max_count * 8)
        bar_str   = "█" * bar_width + "░" * (8 - bar_width)
        colour    = "green" if rank <= 3 else "yellow" if rank <= 9 else "dim"
        tbl.add_row(
            str(rank),
            d["sum_band"],
            d["parity"],
            d["consec"],
            str(d["count"]),
            f"{d['pct']:.1f}%",
            f"[{colour}]{bar_str}[/{colour}]",
        )

    console.print()
    console.print(tbl)

    # ── Ticket check ───────────────────────────────────────────────────────
    ticket_rank   = None
    ticket_profile = None

    if check:
        try:
            t_nums = sorted(int(x) for x in check.split() if x.isdigit())
        except ValueError:
            t_nums = []

        if t_nums:
            ts  = _sum_band(sum(t_nums), low_cut, high_cut)
            tp  = _parity_mix(t_nums, pick)
            tc  = _consec_band(t_nums)
            ticket_profile = (ts, tp, tc)

            # Find rank in full list
            for i, d in enumerate(ranked, 1):
                if d["key"] == ticket_profile:
                    ticket_rank = i
                    ticket_d    = d
                    break

            if ticket_rank is not None:
                pct_rank  = ticket_rank / len(ranked) * 100
                rank_colour = "green" if ticket_rank <= 5 else "yellow" if ticket_rank <= 15 else "red"
                console.print()
                console.print(Panel(
                    f"Profile: [bold]{ts}[/bold] sum  ·  [bold]{tp}[/bold] parity  ·  "
                    f"[bold]{tc}[/bold] consecutive\n"
                    f"Rank: [{rank_colour}]#{ticket_rank} / {len(ranked)}[/{rank_colour}]  ·  "
                    f"Historical freq: {ticket_d['pct']:.1f}%  ({ticket_d['count']} draws)\n"
                    f"[dim]Percentile: top {pct_rank:.0f}% most common profiles[/dim]",
                    title="🎯 Ticket Profile Check",
                    border_style="cyan",
                ))

    # ── Summary panel ──────────────────────────────────────────────────────
    top3    = ranked[:3]
    bottom3 = [d for d in ranked[-3:] if d["count"] > 0]

    top_str    = "  ".join(
        f"({d['sum_band']}/{d['parity'][:3]}/{d['consec']}) {d['pct']:.1f}%"
        for d in top3
    )
    bottom_str = "  ".join(
        f"({d['sum_band']}/{d['parity'][:3]}/{d['consec']}) {d['pct']:.1f}%"
        for d in bottom3
    ) or "none above 0"

    console.print()
    console.print(Panel(
        f"[bold green]Most common:[/bold green]  {top_str}\n"
        f"[dim]Least common:[/dim]  {bottom_str}\n"
        f"[dim]Sum range: {sums_sorted[0]}–{sums_sorted[-1]}  ·  "
        f"Low cut: {low_cut}  ·  High cut: {high_cut}  ·  "
        f"Profiles with ≥1 draw: {sum(1 for d in all_profiles if d['count'] > 0)}/27[/dim]",
        title="🎯 Combo Rank Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, low_cut, high_cut, ranked[:10], ticket_rank, ticket_profile,
        )
        console.print(f"\n[green]✔ Combo rank report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, low_cut: float, high_cut: float,
    top_profiles: list, ticket_rank: Optional[int], ticket_profile: Optional[tuple],
) -> None:
    rows = ""
    for i, d in enumerate(top_profiles, 1):
        rows += (f"| {i} | {d['sum_band']} | {d['parity']} | {d['consec']} | "
                 f"{d['count']} | {d['pct']:.1f}% |\n")

    ticket_line = ""
    if ticket_rank and ticket_profile:
        ticket_line = (f"**Ticket profile:** {ticket_profile[0]} / "
                       f"{ticket_profile[1]} / {ticket_profile[2]}  "
                       f"→ Rank #{ticket_rank}\n\n")

    content = f"""
---
type: diagnostic
subtype: combo-rank
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
sum_low_cut: {low_cut}
sum_high_cut: {high_cut}
top1_profile: {top_profiles[0]['key'] if top_profiles else 'n/a'}
---

## Combo Rank: {game_name} ({today.isoformat()})

**Draws analysed:** {n_draws}  ·  **Sum thresholds:** low≤{low_cut} / high≥{high_cut}

{ticket_line}| Rank | Sum | Parity | Consec | Count | Freq% |
|------|-----|--------|--------|-------|-------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
