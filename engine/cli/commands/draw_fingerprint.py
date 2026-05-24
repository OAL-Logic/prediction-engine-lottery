"""
Draw Fingerprint Command 🔍
===========================
Historical-draw companion to ticket-dna.

Applies the same 7-dimension structural fingerprint that ticket-dna uses
for candidate tickets, but across all historical draws. Useful for two
complementary queries:

  Similar-to mode  (--similar-to "1 2 3 ...")
    Given a candidate ticket, find the K historical draws that are
    structurally most similar. Answers: "Has a draw like mine ever
    happened?" A ticket that looks RARE on ticket-dna might still have
    dozens of real-world analogues — or none at all.

  Atypical mode  (default, no ticket supplied)
    Ranks all draws in the analysis window by how far they deviate
    from the population centroid (highest structural distance first).
    Identifies the structurally strangest draws in history.

The 7 dimensions are identical to ticket-dna:
  Sum · Mean · Parity · Consecutive · Spread · Decade coverage · Symmetry

Distance is Euclidean in percentile-rank space (0–100 per dimension).

Output
------
  Draw table    top-N draws, each with fingerprint + distance
  Summary panel mode, centroid fingerprint, most/least typical

Example
-------
  lottery draw-fingerprint br/lotofacil
  lottery draw-fingerprint br/lotofacil --similar-to "3 12 28 37 41 55" --top 5
  lottery draw-fingerprint br/lotofacil --draws 500 --top 20
  lottery draw-fingerprint br/mega-sena --similar-to "..." --export-md fp.md
"""

from __future__ import annotations

import math
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import (
    get_adapter,
    percentile_rank as _percentile_rank,
    decade_spread as _decade_spread,
    symmetry_score as _symmetry_score,
)

console = Console()

_ABBREVS = ["S", "M", "P", "C", "Sp", "D", "Sy"]


def _draw_vals(nums: list[int], lo: int, hi: int) -> list[float]:
    """Compute the 7 structural values for a draw."""
    s = sorted(nums)
    return [
        float(sum(s)),
        float(sum(s) / len(s)),
        sum(1 for n in s if n % 2 == 0) / len(s),
        float(sum(1 for a, b in zip(s, s[1:]) if b == a + 1)),
        float(s[-1] - s[0]),
        _decade_spread(s, lo, hi),
        _symmetry_score(s, lo, hi),
    ]


def _pct_fingerprint(pcts: list[float]) -> str:
    parts = []
    for abbrev, p in zip(_ABBREVS, pcts):
        arrow = "↑" if p >= 60 else "↓" if p <= 40 else "→"
        parts.append(f"{abbrev}{arrow}")
    return " ".join(parts)


def draw_fingerprint(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    similar_to: Annotated[Optional[str], typer.Option("--similar-to", "-S",
        help="Find draws similar to this ticket (space-separated numbers)")] = None,
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 200,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Number of draws to display")] = 15,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append fingerprint report to this .md file")] = None,
) -> None:
    """🔍 Historical-draw companion to ticket-dna.

    Default: shows the most structurally atypical draws in recent history.
    With --similar-to: finds historical draws closest to your candidate ticket.

    Example: lottery draw-fingerprint br/lotofacil
             lottery draw-fingerprint br/lotofacil --similar-to "3 12 28 37 41 55" --top 5
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)
    all_rows = [r for r in window.itertuples() if r.numbers is not None and len(r.numbers) > 0]

    if not all_rows:
        console.print("[dim]Not enough draw data.[/dim]")
        raise typer.Exit(0)

    # ── Build population arrays ────────────────────────────────────────────
    pop_vals: list[list[float]] = [[] for _ in range(7)]
    draw_data: list[tuple] = []

    for row in all_rows:
        v = _draw_vals(list(row.numbers), lo, hi)
        for i, val in enumerate(v):
            pop_vals[i].append(val)
        draw_data.append((row, v))

    # ── Compute percentile fingerprints ────────────────────────────────────
    fingerprints: list[tuple] = []
    for row, v in draw_data:
        pcts = [_percentile_rank(val, pop_vals[i]) for i, val in enumerate(v)]
        fingerprints.append((row, v, pcts))

    # ── Parse ticket for similar-to mode ──────────────────────────────────
    t_pcts: Optional[list[float]] = None
    t_fp_str = ""
    if similar_to is not None:
        try:
            t_nums = sorted(int(x) for x in similar_to.split() if x.isdigit())
        except ValueError:
            console.print("[red]Invalid --similar-to ticket.[/red]")
            raise typer.Exit(2)
        if not t_nums:
            console.print("[red]No numbers parsed from --similar-to.[/red]")
            raise typer.Exit(2)
        t_v = _draw_vals(t_nums, lo, hi)
        t_pcts = [_percentile_rank(val, pop_vals[i]) for i, val in enumerate(t_v)]
        t_fp_str = _pct_fingerprint(t_pcts)

    # ── Compute distances ─────────────────────────────────────────────────
    if t_pcts is not None:
        # Similar-to: distance from ticket fingerprint (ascending = closest first)
        scored = [
            (row, v, pcts, math.sqrt(sum((p - tp) ** 2 for p, tp in zip(pcts, t_pcts))))
            for row, v, pcts in fingerprints
        ]
        scored.sort(key=lambda x: x[3])
        mode_label = "Closest to ticket"
    else:
        # Atypical: distance from centroid (descending = most atypical first)
        centroid = [
            sum(fp[2][i] for fp in fingerprints) / len(fingerprints)
            for i in range(7)
        ]
        scored = [
            (row, v, pcts, math.sqrt(sum((p - c) ** 2 for p, c in zip(pcts, centroid))))
            for row, v, pcts in fingerprints
        ]
        scored.sort(key=lambda x: x[3], reverse=True)
        mode_label = "Most atypical"

    display = scored[: top]

    # ── Table ─────────────────────────────────────────────────────────────
    dist_label = "Dist (ticket)" if t_pcts is not None else "Dist (centroid)"
    tbl = Table(
        title=f"🔍 Draw Fingerprint — {rules.name}  ({mode_label}, window={n_draws})",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Draw",       justify="right",  style="dim")
    tbl.add_column("Date",       justify="center", style="dim")
    tbl.add_column("Numbers",    justify="left")
    tbl.add_column("Fingerprint",justify="left",   style="dim")
    tbl.add_column(dist_label,   justify="right")

    for row, v, pcts, dist in display:
        nums = sorted(row.numbers)
        nums_str = " ".join(f"{n:2}" for n in nums[:10])
        if len(nums) > 10:
            nums_str += " …"
        fp_str = _pct_fingerprint(pcts)
        date_str = str(row.date)[:10] if hasattr(row, "date") and row.date is not None else "—"
        tbl.add_row(str(row.draw_id), date_str, nums_str, fp_str, f"{dist:.1f}")

    console.print()
    console.print(tbl)
    console.print(f"\n  [dim]Fingerprint key: S=sum M=mean P=parity C=consec Sp=spread D=decade Sy=symmetry  ↑=high ↓=low →=mid[/dim]")

    # ── Summary panel ─────────────────────────────────────────────────────
    if t_pcts is not None:
        ticket_fp_line = f"Ticket fingerprint:   [bold]{t_fp_str}[/bold]\n"
    else:
        ticket_fp_line = ""

    if display:
        best_row, _, best_pcts, best_dist = display[0]
        best_fp  = _pct_fingerprint(best_pcts)
        best_lbl = f"Draw #{best_row.draw_id}" if t_pcts is not None else f"Most atypical: Draw #{best_row.draw_id}"
        worst_row, _, _, worst_dist = display[-1]
        worst_lbl = f"Draw #{worst_row.draw_id}"
    else:
        best_fp = "—"
        best_lbl = "—"
        worst_lbl = "—"
        best_dist = 0.0
        worst_dist = 0.0

    console.print()
    console.print(Panel(
        f"{ticket_fp_line}"
        f"[bold]{best_lbl}[/bold]  ·  fingerprint: {best_fp}  ·  dist={best_dist:.1f}\n"
        f"[dim]Showing {len(display)}/{len(all_rows)} draws  ·  Mode: {mode_label}  ·  "
        f"7-dim Euclidean in percentile space[/dim]",
        title="🔍 Draw Fingerprint Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, mode_label, similar_to, t_fp_str,
            display,
        )
        console.print(f"\n[green]✔ Draw fingerprint report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, mode: str, ticket: Optional[str], ticket_fp: str,
    display: list,
) -> None:
    rows_md = ""
    for row, v, pcts, dist in display:
        nums = " ".join(str(n) for n in sorted(row.numbers))
        fp   = _pct_fingerprint(pcts)
        rows_md += f"| {row.draw_id} | {nums} | {fp} | {dist:.1f} |\n"

    ticket_line = f"ticket: \"{ticket}\"" if ticket else "ticket: null"

    content = f"""
---
type: diagnostic
subtype: draw-fingerprint
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
mode: {mode}
{ticket_line}
ticket_fingerprint: "{ticket_fp}"
rows_shown: {len(display)}
---

## Draw Fingerprint: {game_name} ({today.isoformat()})

**Mode:** {mode}  ·  **Draws analysed:** {n_draws}
{"**Ticket:** " + ticket if ticket else ""}

| Draw | Numbers | Fingerprint | Distance |
|------|---------|-------------|----------|
{rows_md}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
