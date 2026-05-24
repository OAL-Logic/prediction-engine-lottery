"""
Risk & Kelly Criterion Command ⚖️
================================
Calculates optimal bet sizing and Expected Value (EV) for lotteries.

EV is computed for the jackpot tier only (the only tier with a known prize).
Lower prize tiers are shown with their odds and breakeven prize requirements
as context — actual lower-tier prizes vary per draw and are not stored in
the adapter, so we do not estimate them.

Kelly Criterion is applied to the jackpot tier:
  f* = (b·p − q) / b
  where b = (jackpot / price) − 1,  p = 1 / odds,  q = 1 − p
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


def risk(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j",
        help="Current jackpot amount (top prize)")] = None,
    bankroll: Annotated[float, typer.Option("--bankroll", "-b",
        help="Your total betting bankroll")] = 100.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append risk report to this .md file")] = None,
) -> None:
    """⚖️ Kelly Criterion bet sizing and Expected Value analysis.

    Shows jackpot-tier EV and breakeven requirements for each prize tier.
    Pass --jackpot to use the real current jackpot amount for accuracy.

    Example: lottery risk br/lotofacil
             lottery risk br/lotofacil --jackpot 50000000
             lottery risk br/mega-sena --bankroll 500
    """
    adapter = get_adapter(lottery)
    rules = adapter.rules

    price = rules.ticket_price
    currency = rules.currency
    jackpot_odds = rules.jackpot_odds

    current_jackpot = jackpot or (price * jackpot_odds * 0.4)

    console.rule(f"[bold cyan]Risk Analysis: {rules.name}[/bold cyan]")

    # ── Prize tier table (odds + breakeven prize) ─────────────────────────────
    if rules.odds:
        tier_table = Table(title="Prize Tiers", box=None, header_style="bold", padding=(0, 1))
        tier_table.add_column("Tier",            justify="center", style="cyan")
        tier_table.add_column("Odds",            justify="right",  style="dim")
        tier_table.add_column("Prob per ticket", justify="right",  style="dim")
        tier_table.add_column("Breakeven prize", justify="right")

        max_tier = max(rules.odds.keys())
        for tier in sorted(rules.odds.keys()):
            tier_odds = rules.odds[tier]
            prob = 1.0 / tier_odds
            # Prize needed for this tier alone to make EV = 0
            breakeven = price / prob  # = price × odds
            is_jackpot = tier == max_tier
            tier_table.add_row(
                f"Match {tier}" + (" ★" if is_jackpot else ""),
                f"1 in {tier_odds:,}",
                f"{prob * 100:.6f}%",
                f"{breakeven:>14,.0f} {currency}",
            )

        console.print(tier_table)

    # ── Jackpot EV & Kelly ────────────────────────────────────────────────────
    p = 1.0 / jackpot_odds
    q = 1.0 - p
    ev = p * current_jackpot - price
    # Return ratio: expected return per ticket cost
    # (EV + price) / price  — 1.0 = breakeven
    return_ratio = (ev + price) / price
    breakeven_jackpot = price * jackpot_odds

    summary = Table(box=None, padding=(0, 1), show_header=False)
    summary.add_column("Metric", style="dim")
    summary.add_column("Value",  style="bold")

    summary.add_row("Ticket price",       f"{price:.2f} {currency}")
    summary.add_row("Jackpot odds",       f"1 in {jackpot_odds:,}")
    summary.add_row("Assumed jackpot",
                    f"{current_jackpot:,.0f} {currency}"
                    + ("" if jackpot else "  [dim](heuristic: 40% of prize pool)[/dim]"))
    summary.add_row("Breakeven jackpot",  f"{breakeven_jackpot:,.0f} {currency}")
    summary.add_row("Jackpot EV",         f"{ev:+.4f} {currency}")
    summary.add_row("Return ratio",       f"{return_ratio:.4f}  [dim](1.0 = breakeven)[/dim]")

    console.print()
    console.print(summary)

    # Kelly & advice panel
    b = (current_jackpot / price) - 1
    kelly_f = max(0.0, (b * p - q) / b) if b > 0 else 0.0

    if ev > 0:
        optimal_tickets = max(1, int(kelly_f * bankroll / price))
        console.print(Panel(
            f"Jackpot EV: [bold]{ev:+.4f} {currency}[/bold]\n"
            f"Kelly fraction: {kelly_f * 100:.6f}% of bankroll\n"
            f"Optimal tickets (bankroll={bankroll:.0f} {currency}): [bold]{optimal_tickets}[/bold]\n"
            f"[dim]Note: lower prize tiers add further EV not shown here.[/dim]",
            title="[bold green]POSITIVE EXPECTATION (+EV)[/bold green]",
            border_style="green",
        ))
    else:
        gap = breakeven_jackpot - current_jackpot
        console.print(Panel(
            f"Jackpot EV: [bold]{ev:+.4f} {currency}[/bold]\n"
            f"Jackpot needs to reach [bold]{breakeven_jackpot:,.0f} {currency}[/bold] to break even "
            f"([bold]{gap:,.0f} {currency}[/bold] gap from current).\n"
            f"[dim]Lower prize tiers add positive EV not captured here.[/dim]\n"
            f"Play for fun only, or wait for a larger rollover.",
            title="[bold red]NEGATIVE EXPECTATION (−EV)[/bold red]",
            border_style="red",
        ))

    console.print(f"\n[dim]EV shown for jackpot tier only. Excludes taxes and lower-tier prizes.[/dim]")

    if export_md:
        _append_md(export_md, lottery, rules.name, _date.today(),
                   price, currency, jackpot_odds, current_jackpot,
                   breakeven_jackpot, ev, return_ratio, kelly_f, bankroll)
        console.print(f"\n[green]✔ Risk report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    price: float, currency: str, jackpot_odds: int, jackpot: float,
    breakeven_jackpot: float, ev: float, return_ratio: float,
    kelly_f: float, bankroll: float,
) -> None:
    verdict = "POSITIVE (+EV)" if ev > 0 else "NEGATIVE (-EV)"
    content = f"""
---
type: diagnostic
subtype: risk
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket_price: {price}
currency: {currency}
jackpot_odds: {jackpot_odds}
jackpot: {jackpot:.0f}
breakeven_jackpot: {breakeven_jackpot:.0f}
jackpot_ev: {ev:.4f}
return_ratio: {return_ratio:.4f}
kelly_fraction: {kelly_f:.6f}
bankroll: {bankroll}
verdict: {verdict}
---

## Risk Analysis: {game_name} ({today.isoformat()})

**Ticket price:** {currency} {price:.2f}  ·  **Jackpot odds:** 1 in {jackpot_odds:,}
**Jackpot (assumed):** {currency} {jackpot:,.0f}  ·  **Breakeven jackpot:** {currency} {breakeven_jackpot:,.0f}
**Jackpot EV:** {currency} {ev:+.4f}  ·  **Return ratio:** {return_ratio:.4f}
**Kelly fraction:** {kelly_f*100:.6f}%  ·  **Verdict:** {verdict}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
