"""
Picks Command 🃏
================
Consensus ticket from recently logged forecasts.

Reads data/ticket_log.jsonl and aggregates the last N tickets for a game
into a frequency-ranked consensus: the numbers that appeared most often
across recent forecast runs.

Useful for:
  • "What has the engine been recommending lately?"
  • Creating a manually curated ticket from the recent consensus
  • Spotting stability: if the same numbers appear in every forecast, they
    are the engine's most consistent picks

Output
------
  Frequency table of all numbers in recent tickets
  Consensus ticket: top pick_count numbers by appearance count
  Stability score: fraction of tickets that contain all top picks

Example
-------
  lottery picks br/lotofacil
  lottery picks br/lotofacil --last 20
  lottery picks br/lotofacil --since 2026-05-01
  lottery picks br/lotofacil --source forecast   # filter by source
"""

from __future__ import annotations

import json
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

_DATA_DIR   = Path(__file__).parent.parent.parent.parent / "data"
_TICKET_LOG = _DATA_DIR / "ticket_log.jsonl"

_BAR_CHARS = "░▒▓█"


def _bar(count: int, max_count: int, width: int = 12) -> str:
    if max_count == 0:
        return "░" * width
    ratio = count / max_count
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def picks(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    last: Annotated[int, typer.Option("--last", "-n",
        help="Use only the last N logged tickets")] = 10,
    since: Annotated[Optional[str], typer.Option("--since",
        help="Only use tickets logged on or after YYYY-MM-DD")] = None,
    source: Annotated[Optional[str], typer.Option("--source",
        help="Filter by source: forecast | daily | (any)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append picks report to this .md file")] = None,
    raw: Annotated[bool, typer.Option("--raw",
        help="Output only the space-separated ticket numbers (for piping)")] = False,
) -> None:
    """🃏 Consensus ticket from recently logged forecasts.

    Reads ticket_log.jsonl to find the numbers that appear most often
    across the last N forecasts for this game.

    Example: lottery picks br/lotofacil
             lottery picks br/lotofacil --last 20
             lottery picks br/lotofacil --raw | lottery ticket-dna br/lotofacil --from-stdin
    """
    adapter = get_adapter(lottery)
    rules   = adapter.rules
    pick_count = rules.pick_count

    if not _TICKET_LOG.exists():
        console.print(
            f"[dim]No ticket log found. Run [bold]lottery forecast {lottery}[/bold] "
            f"or [bold]lottery daily {lottery}[/bold] first.[/dim]"
        )
        raise typer.Exit(0)

    # Load tickets matching filters
    all_records: list[dict] = []
    for line in _TICKET_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("game") != lottery:
            continue
        if since and rec.get("date", "") < since:
            continue
        if source and rec.get("source", "") != source:
            continue
        all_records.append(rec)

    # Keep only the last N
    records = all_records[-last:]

    if not records:
        console.print(f"[dim]No matching tickets found. Adjust --last or --since filters.[/dim]")
        raise typer.Exit(0)

    # Count number appearances
    freq: Counter[int] = Counter()
    for rec in records:
        ticket = rec.get("ticket", [])
        if isinstance(ticket, str):
            ticket = [int(x) for x in ticket.split() if x.isdigit()]
        for n in ticket:
            freq[n] += 1

    n_tickets  = len(records)
    date_range = f"{records[0].get('date','?')} → {records[-1].get('date','?')}"
    max_count  = max(freq.values()) if freq else 1

    # Ranked display
    sorted_nums = sorted(freq.keys(), key=lambda n: freq[n], reverse=True)

    # --raw: emit only space-separated numbers and exit (for piping)
    if raw:
        top_nums_raw = sorted(sorted_nums[:pick_count])
        typer.echo(" ".join(str(n) for n in top_nums_raw))
        return

    table = Table(
        title=f"Pick Frequency — {rules.name}  ({n_tickets} tickets)",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("Number", justify="center", style="bold yellow")
    table.add_column("Count",  justify="right")
    table.add_column("Pct",    justify="right", style="dim")
    table.add_column("Bar",    justify="left",  style="green")

    for num in sorted_nums:
        c   = freq[num]
        pct = c / n_tickets * 100
        bar = _bar(c, max_count)
        table.add_row(str(num), str(c), f"{pct:.0f}%", bar)

    console.print(table)

    # Consensus ticket: top pick_count numbers
    top_nums = sorted_nums[:pick_count]
    top_nums_sorted = sorted(top_nums)
    ticket_str = "  ".join(str(n) for n in top_nums_sorted)

    # Stability: what fraction of tickets contain ALL top picks?
    top_set = set(top_nums_sorted)
    n_full = 0
    for rec in records:
        t = rec.get("ticket", [])
        if isinstance(t, str):
            nums = {int(x) for x in t.split() if x.isdigit()}
        else:
            nums = set(t)
        if top_set <= nums:
            n_full += 1
    stability = n_full / n_tickets if n_tickets > 0 else 0.0

    # Min appearances in the top picks
    min_top_count = min(freq[n] for n in top_nums) if top_nums else 0

    console.print()
    console.print(Panel(
        f"[bold yellow]{ticket_str}[/bold yellow]\n"
        f"[dim]Top {pick_count} numbers by appearance across {n_tickets} tickets  ·  {date_range}\n"
        f"Stability: {stability:.0%} of tickets contain all top picks  ·  "
        f"Min appearances: {min_top_count}/{n_tickets}[/dim]",
        title="🃏 Consensus Picks",
        border_style="yellow",
    ))

    # Warn if top picks look unreliable
    if min_top_count < n_tickets * 0.5 and n_tickets >= 3:
        console.print(
            "[dim]⚠ Low stability — top picks appear in < 50% of tickets. "
            "Consider running more forecasts or using --strategies statistical for consistency.[/dim]"
        )

    if export_md:
        _append_md(export_md, lottery, rules.name, _date.today(), records,
                   freq, top_nums_sorted, stability, n_tickets, date_range)
        console.print(f"[green]✔ Picks report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    records: list[dict], freq: Counter, top_nums: list[int],
    stability: float, n_tickets: int, date_range: str,
) -> None:
    ticket_str = ", ".join(str(n) for n in top_nums)
    rows = ""
    for num in sorted(freq.keys(), key=lambda n: freq[n], reverse=True)[:20]:
        rows += f"| {num} | {freq[num]} | {freq[num]/n_tickets*100:.0f}% |\n"

    content = f"""
---
type: diagnostic
subtype: picks
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
tickets_sampled: {n_tickets}
period: {date_range}
consensus_ticket: [{ticket_str}]
stability: {stability:.2f}
---

## Consensus Picks: {game_name} ({today.isoformat()})

**Ticket:** {ticket_str}
**Stability:** {stability:.0%}  ·  **Tickets sampled:** {n_tickets}

| Number | Count | % |
|--------|-------|---|
{rows}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
