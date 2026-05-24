"""
Hitcheck Command 🎯
===================
Compare logged tickets against actual draw results to see how many
numbers matched, and which prize tier (if any) was hit.

Reads from data/ticket_log.jsonl (written by forecast and daily commands).
Compares each ticket against the last N draws (or a specific draw ID).

Output
------
  One row per ticket: date generated, ticket numbers, draw ID matched against,
  numbers hit, and prize tier.

Example
-------
  lottery hitcheck br/lotofacil
  lottery hitcheck br/lotofacil --draws 3         # check vs last 3 draws
  lottery hitcheck br/lotofacil --draw-id 3675    # check vs specific draw
  lottery hitcheck br/lotofacil --since 2026-05-01
"""

from __future__ import annotations

import json
from datetime import date as _date, datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.rule import Rule

from engine.cli.utils import get_adapter, DATA_DIR

console = Console()
_TICKET_LOG = DATA_DIR / "ticket_log.jsonl"


def _load_tickets(lottery: str, since: Optional[str]) -> list[dict]:
    if not _TICKET_LOG.exists():
        return []
    records = []
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
        records.append(rec)
    return records


def _prize_tier(hits: int, rules) -> str:
    if not rules.prize_tiers:
        return "—"
    tiers = sorted(rules.prize_tiers, reverse=True)
    for t in tiers:
        if hits >= t:
            return f"Match {t}"
    return "no prize"


def hitcheck(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to check against")] = 1,
    draw_id: Annotated[Optional[int], typer.Option("--draw-id",
        help="Check against this specific draw ID only")] = None,
    since: Annotated[Optional[str], typer.Option("--since",
        help="Only check tickets generated on or after this date (YYYY-MM-DD)")] = None,
    all_tickets: Annotated[bool, typer.Option("--all/--no-all",
        help="Show all tickets including no-prize rows")] = True,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append hit-check report to this .md file")] = None,
) -> None:
    """🎯 Compare logged tickets against actual draw results.

    Reads tickets from data/ticket_log.jsonl (written by forecast/daily).
    Shows how many numbers matched and the prize tier hit for each ticket.

    Example: lottery hitcheck br/lotofacil
             lottery hitcheck br/lotofacil --draws 5
             lottery hitcheck br/lotofacil --since 2026-05-01
             lottery hitcheck br/lotofacil --draw-id 3675
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules

    # Select draws to check against
    if draw_id is not None:
        draw_rows = df[df["draw_id"] == draw_id]
        if draw_rows.empty:
            console.print(f"[red]Draw ID {draw_id} not found for {lottery}.[/red]")
            raise typer.Exit(1)
        check_draws = draw_rows.to_dict("records")
    else:
        check_draws = df.tail(draws).to_dict("records")

    tickets = _load_tickets(lottery, since)
    if not tickets:
        console.print(f"[dim]No logged tickets found for {lottery}. "
                      f"Run [bold]lottery forecast {lottery}[/bold] to generate and log tickets.[/dim]")
        raise typer.Exit(0)

    console.rule(f"[bold cyan]Hit Check: {rules.name}[/bold cyan]")
    console.print(f"[dim]{len(tickets)} ticket(s) in log  |  "
                  f"checking vs {len(check_draws)} draw(s)[/dim]\n")

    table = Table(box=None, padding=(0, 1), header_style="bold")
    table.add_column("Ticket Date",  style="dim")
    table.add_column("Source",       style="dim")
    table.add_column("Ticket",       style="yellow")
    table.add_column("Draw ID",      justify="right", style="dim")
    table.add_column("Hits",         justify="center")
    table.add_column("Tier",         justify="center")

    best_hits = 0

    for rec in tickets:
        ticket: list[int] = rec.get("ticket", [])
        ticket_set = set(ticket)
        ticket_str = "  ".join(str(n) for n in sorted(ticket))
        t_date = rec.get("date", "—")
        source = rec.get("source", "—")

        for draw in check_draws:
            draw_nums: list[int] = draw.get("numbers", [])
            draw_num_set = set(draw_nums)
            d_id = draw.get("draw_id", "—")

            hits = len(ticket_set & draw_num_set)
            tier = _prize_tier(hits, rules)
            best_hits = max(best_hits, hits)

            if not all_tickets and tier == "no prize":
                continue

            if hits == len(ticket):
                hits_fmt = f"[bold green]{hits} 🎉[/bold green]"
                tier_fmt = f"[bold green]{tier}[/bold green]"
            elif tier != "no prize" and tier != "—":
                hits_fmt = f"[green]{hits}[/green]"
                tier_fmt = f"[green]{tier}[/green]"
            else:
                hits_fmt = f"[dim]{hits}[/dim]"
                tier_fmt = f"[dim]{tier}[/dim]"

            table.add_row(t_date, source, ticket_str, str(d_id), hits_fmt, tier_fmt)

    console.print(table)

    if best_hits == 0:
        console.print("\n[dim]No matches yet. Keep generating tickets with "
                      "[bold]lottery forecast[/bold] or [bold]lottery daily[/bold].[/dim]")
    else:
        console.print(f"\n[dim]Best result: {best_hits} number(s) matched.[/dim]")

    if export_md:
        _append_md_hitcheck(export_md, lottery, rules.name, len(tickets),
                            len(check_draws), best_hits, since)
        console.print(f"[green]✔ Hit-check report appended to {export_md}[/green]")


def _append_md_hitcheck(
    path: str, lottery: str, game_name: str,
    n_tickets: int, n_draws: int, best_hits: int,
    since: Optional[str],
) -> None:
    today = _date.today().isoformat()
    content = f"""
---
type: diagnostic
subtype: hitcheck
date: {today}
game: {lottery}
game_name: {game_name}
tickets_checked: {n_tickets}
draws_checked: {n_draws}
best_hits: {best_hits}
since: {since or "all"}
tags: [prediction-engine, hitcheck, results, pattern-log]
---

## Hit Check: {game_name} ({today})

**Tickets checked:** {n_tickets}  ·  **Draws checked:** {n_draws}
**Best result:** {best_hits} number(s) matched  ·  **Since:** {since or "all time"}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
