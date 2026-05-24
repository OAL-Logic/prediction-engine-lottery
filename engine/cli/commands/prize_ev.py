"""
Prize EV Command 💰
===================
Expected-value calculator per ticket, across all prize tiers.

For each prize tier the command computes the exact hypergeometric probability
of hitting that tier with a single ticket, multiplies by the prize amount, and
sums to a total EV and ROI%.

The most valuable output is the *breakeven jackpot* — the minimum jackpot that
makes a single ticket mathematically worth buying. Useful for mega-rollover draws.

Algorithm
---------
  P(match k)   = C(pick, k) × C(pool − pick, pick − k) / C(pool, pick)
  EV(tier k)   = P(match k) × prize[k]
  Total EV     = Σ EV(tier) − ticket_cost
  ROI%         = Total EV / ticket_cost × 100
  Breakeven J  = (ticket_cost − Σ lower_tier_EV) / P(jackpot)

Typical lower-tier prizes for BR/US games are baked in as starting defaults;
supply --tier to override any individual tier, and --jackpot for the top prize.

Example
-------
  lottery prize-ev br/mega-sena --jackpot 120000000
  lottery prize-ev br/lotofacil --jackpot 2500000
  lottery prize-ev br/mega-sena --tier 5:40000 --jackpot 80000000
  lottery prize-ev br/lotofacil --export-md ev_log.md
"""

from __future__ import annotations

from datetime import date as _date
from math import comb
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

# Approximate typical lower-tier prizes (pari-mutuel averages in native currency).
# Jackpot tier is always excluded — supply via --jackpot.
_TYPICAL_LOWER: dict[str, dict[int, float]] = {
    "br/mega-sena":  {4: 1_400.0,  5: 36_000.0},
    "br/lotofacil":  {11: 6.0, 12: 25.0, 13: 120.0, 14: 1_200.0},
    "us/powerball":  {3: 7.0,    4: 100.0},
    "us/megamillions": {3: 10.0, 4: 150.0, 5: 1_000_000.0},
}


def _hyp_prob(pool: int, pick: int, match: int) -> float:
    """P(exactly `match` hits) using the hypergeometric distribution."""
    denom = comb(pool, pick)
    if denom == 0:
        return 0.0
    numer = comb(pick, match) * comb(pool - pick, pick - match)
    return numer / denom


def prize_ev(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-J",
        help="Current jackpot prize (top-tier payout)")] = None,
    tier_override: Annotated[Optional[List[str]], typer.Option("--tier", "-T",
        help="Override prize for one tier: match:amount  (e.g. --tier 14:1200)")] = None,
    cost_override: Annotated[Optional[float], typer.Option("--cost", "-c",
        help="Override ticket cost (default from game rules)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append EV report to this .md file")] = None,
) -> None:
    """💰 Expected-value calculator per ticket across all prize tiers.

    Shows P(hit), EV contribution per tier, total EV, ROI%, and the
    breakeven jackpot — the jackpot at which a single ticket turns +EV.

    Example: lottery prize-ev br/mega-sena --jackpot 120000000
             lottery prize-ev br/lotofacil --jackpot 2500000 --tier 14:1500
    """
    adapter = get_adapter(lottery)
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pool    = hi - lo + 1
    pick    = rules.pick_count
    cost    = cost_override if cost_override is not None else rules.ticket_price

    if cost <= 0:
        console.print("[red]Ticket cost is 0 — pass --cost <price>.[/red]")
        raise typer.Exit(2)

    # Build prize map: tier → prize amount (None = unknown)
    prizes: dict[int, Optional[float]] = {t: None for t in rules.prize_tiers}
    for t, v in _TYPICAL_LOWER.get(lottery, {}).items():
        if t in prizes:
            prizes[t] = v

    # Apply --tier overrides
    if tier_override:
        for raw in tier_override:
            try:
                m_str, a_str = raw.split(":", 1)
                prizes[int(m_str)] = float(a_str)
            except (ValueError, AttributeError):
                console.print(f"[red]Bad --tier '{raw}' — use match:amount (e.g. --tier 14:1200)[/red]")
                raise typer.Exit(2)

    jackpot_tier = max(rules.prize_tiers)
    if jackpot is not None:
        prizes[jackpot_tier] = jackpot

    # ── Compute per-tier rows ──────────────────────────────────────────────
    tier_rows: list[tuple] = []
    lower_ev  = 0.0
    jackpot_p = _hyp_prob(pool, pick, jackpot_tier)

    for t in sorted(rules.prize_tiers):
        p        = _hyp_prob(pool, pick, t)
        odds_str = f"1 in {round(1.0 / p):,}" if p > 0 else "—"
        prize_v  = prizes.get(t)
        ev_v     = p * prize_v if prize_v is not None else None
        is_jack  = (t == jackpot_tier)
        if ev_v is not None and not is_jack:
            lower_ev += ev_v
        tier_rows.append((t, p, odds_str, prize_v, ev_v, is_jack))

    # Breakeven jackpot
    breakeven_j: Optional[float] = (
        (cost - lower_ev) / jackpot_p if jackpot_p > 0 else None
    )

    # Total EV and ROI (only when jackpot known)
    total_ev: Optional[float] = None
    roi_pct:  Optional[float] = None
    if prizes.get(jackpot_tier) is not None:
        jackpot_ev = jackpot_p * prizes[jackpot_tier]  # type: ignore[operator]
        total_ev   = lower_ev + jackpot_ev - cost
        roi_pct    = total_ev / cost * 100.0

    currency = rules.currency

    # ── Prize table ────────────────────────────────────────────────────────
    tbl = Table(
        title=f"💰 Prize EV — {rules.name}  (ticket: {currency} {cost:.2f})",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Match",       justify="center", style="bold yellow")
    tbl.add_column("Probability", justify="right")
    tbl.add_column("1-in-X",      justify="right", style="dim")
    tbl.add_column("Prize",       justify="right")
    tbl.add_column("EV contrib",  justify="right")

    for match, p, odds_str, prize_v, ev_v, is_jack in tier_rows:
        label = f"{'★ ' if is_jack else ''}{match}"
        if prize_v is not None:
            prize_str = (
                f"[bold green]{currency} {prize_v:,.0f}[/bold green]"
                if is_jack else f"{currency} {prize_v:,.0f}"
            )
        else:
            prize_str = "[dim]unknown — use --jackpot / --tier[/dim]"

        ev_str = (
            f"{currency} {ev_v:,.4f}" if ev_v is not None else "[dim]—[/dim]"
        )
        tbl.add_row(label, f"{p:.2e}", odds_str, prize_str, ev_str)

    console.print()
    console.print(tbl)

    # ── Summary panel ──────────────────────────────────────────────────────
    lines: list[str] = []

    if total_ev is not None:
        colour  = "bold green" if total_ev >= 0 else "bold red"
        verdict = "+EV ▲ — jackpot justifies a ticket" if total_ev >= 0 else "−EV ▼ — expected loss"
        lines.append(
            f"[{colour}]Total EV: {currency} {total_ev:,.2f}  ·  "
            f"ROI: {roi_pct:+.1f}%  ·  {verdict}[/{colour}]"
        )
    else:
        lines.append("[dim]Total EV: unknown — pass --jackpot <prize amount>[/dim]")

    lines.append(
        f"[dim]Lower-tier EV: {currency} {lower_ev:,.4f}  "
        f"({len(rules.prize_tiers) - 1} tiers below jackpot)[/dim]"
    )

    if breakeven_j is not None:
        lines.append(
            f"Breakeven jackpot: [bold]{currency} {breakeven_j:,.0f}[/bold]"
            f"  ← minimum jackpot for this ticket to be +EV"
        )
    lines.append(
        f"[dim]Pool {pool}  pick {pick}  "
        f"jackpot P = 1 in {round(1.0 / jackpot_p):,}[/dim]"
        if jackpot_p > 0 else "[dim]Pool {pool}  pick {pick}[/dim]"
    )

    console.print()
    console.print(Panel("\n".join(lines), title="💰 EV Summary", border_style="yellow"))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            cost, currency, tier_rows, lower_ev, total_ev, roi_pct, breakeven_j,
        )
        console.print(f"\n[green]✔ EV report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    cost: float, currency: str,
    tier_rows: list, lower_ev: float,
    total_ev: Optional[float], roi_pct: Optional[float],
    breakeven_j: Optional[float],
) -> None:
    tier_md = ""
    for match, p, odds_str, prize_v, ev_v, is_jack in tier_rows:
        prize_str = f"{currency} {prize_v:,.0f}" if prize_v is not None else "unknown"
        ev_str    = f"{currency} {ev_v:,.4f}"    if ev_v   is not None else "unknown"
        tier_md  += f"| {'★ ' if is_jack else ''}{match} | {p:.2e} | {odds_str} | {prize_str} | {ev_str} |\n"

    total_str = f"{currency} {total_ev:,.2f}" if total_ev is not None else "unknown"
    roi_str   = f"{roi_pct:+.1f}%"            if roi_pct  is not None else "unknown"
    be_str    = f"{currency} {breakeven_j:,.0f}" if breakeven_j is not None else "unknown"

    content = f"""
---
type: diagnostic
subtype: prize-ev
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket_cost: {cost}
currency: {currency}
lower_tier_ev: {lower_ev:.4f}
total_ev: {total_str}
roi_pct: {roi_str}
breakeven_jackpot: {be_str}
---

## Prize EV: {game_name} ({today.isoformat()})

**Ticket cost:** {currency} {cost:.2f}  ·  **Total EV:** {total_str}  ·  **ROI:** {roi_str}
**Breakeven jackpot:** {be_str}
**Lower-tier EV:** {currency} {lower_ev:.4f}

| Match | Probability | 1-in-X | Prize | EV Contribution |
|-------|-------------|--------|-------|-----------------|
{tier_md}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
