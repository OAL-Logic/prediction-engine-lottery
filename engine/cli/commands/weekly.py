"""
Weekly Command 📅
=================
Weekly performance summary built from JSONL logs.

Reads data/draw_log.jsonl and data/ticket_log.jsonl and renders a
structured 7-day report showing:

  • Draws that occurred during the period
  • Scan condition scores trend (sparkline)
  • Regime stability over the week
  • Tickets generated and their hit counts against the period's draws
  • Alert triggers
  • Key metrics: best hit, avg confidence, chi2 stability

Designed to be run every Sunday or piped into the cron weekly cycle.

Example
-------
  lottery weekly br/lotofacil
  lottery weekly br/lotofacil --weeks 2
  lottery weekly br/lotofacil --export-md reports/week.md
"""

from __future__ import annotations

import json
from datetime import date as _date, timedelta
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DRAW_LOG   = _DATA_DIR / "draw_log.jsonl"
_TICKET_LOG = _DATA_DIR / "ticket_log.jsonl"

_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float]) -> str:
    if not values:
        return "—"
    mn, mx = min(values), max(values)
    rng = mx - mn
    out = []
    for v in values:
        idx = int((v - mn) / rng * 7) if rng > 0 else 4
        out.append(_SPARK[min(idx, 7)])
    return "".join(out)


def _load_jsonl(path: Path, game: str, since: str, until: str) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("game") != game:
            continue
        d = rec.get("date", "") or rec.get("timestamp", "")[:10]
        if since <= d <= until:
            records.append(rec)
    return records


def _prize_tier(hits: int, rules) -> str:
    if not rules.prize_tiers:
        return "no prize" if hits < rules.pick_count else "jackpot"
    tiers = sorted(rules.prize_tiers, reverse=True)
    for t in tiers:
        if hits >= t:
            return f"Match {t}"
    return "no prize"


def weekly(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    weeks: Annotated[int, typer.Option("--weeks", "-w",
        help="Number of past weeks to cover")] = 1,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append weekly report to this .md file")] = None,
) -> None:
    """📅 Weekly performance summary from JSONL logs.

    Reads draw_log.jsonl and ticket_log.jsonl to show condition trends,
    ticket hit rates, and regime stability over the past N weeks.

    Example: lottery weekly br/lotofacil
             lottery weekly br/lotofacil --weeks 2
             lottery weekly br/lotofacil --export-md reports/week.md
    """
    adapter = get_adapter(lottery)
    rules = adapter.rules

    today = _date.today()
    period_end   = today.isoformat()
    period_start = (today - timedelta(weeks=weeks)).isoformat()

    console.rule(f"[bold cyan]Weekly Report: {rules.name}[/bold cyan]")
    console.print(f"[dim]Period: {period_start} → {period_end}  ({weeks} week(s))[/dim]\n")

    _all_draw_recs = _load_jsonl(_DRAW_LOG,   lottery, period_start, period_end)
    ticket_recs    = _load_jsonl(_TICKET_LOG, lottery, period_start, period_end)

    # Deduplicate draw_log: keep latest entry per date (log is append-only)
    seen: dict[str, dict] = {}
    for r in _all_draw_recs:
        d = r.get("date", "")
        seen[d] = r
    draw_recs = list(seen.values())

    if not draw_recs and not ticket_recs:
        console.print(
            "[dim]No log entries found for this period.\n"
            "Run [bold]lottery daily[/bold] each day to build up history.[/dim]"
        )
        return

    # ── Condition trends ──────────────────────────────────────────────────────
    conf_vals    = [r["confidence"] for r in draw_recs if r.get("confidence") is not None]
    entropy_vals = [r["entropy"]    for r in draw_recs if r.get("entropy")    is not None]
    chi2_vals    = [r["chi2_p"]     for r in draw_recs if r.get("chi2_p")     is not None]
    stable_days  = sum(1 for r in draw_recs if r.get("stable") is True)
    regime_counts: dict[str, int] = {}
    for r in draw_recs:
        rv = r.get("regime")
        if rv:
            regime_counts[rv] = regime_counts.get(rv, 0) + 1

    trend_table = Table(title="Signal Trends", box=None, padding=(0, 2), header_style="bold")
    trend_table.add_column("Metric",     style="cyan")
    trend_table.add_column("Sparkline",  style="yellow")
    trend_table.add_column("Min",        justify="right", style="dim")
    trend_table.add_column("Mean",       justify="right")
    trend_table.add_column("Max",        justify="right", style="dim")
    trend_table.add_column("Last",       justify="right")

    def _row(label: str, vals: list[float], fmt: str = ".4f") -> None:
        if not vals:
            trend_table.add_row(label, "—", "—", "—", "—", "—")
            return
        mn, mx, mean, last = min(vals), max(vals), sum(vals)/len(vals), vals[-1]
        trend_table.add_row(
            label,
            _sparkline(vals),
            f"{mn:{fmt}}",
            f"[bold]{mean:{fmt}}[/bold]",
            f"{mx:{fmt}}",
            f"{last:{fmt}}",
        )

    _row("Confidence", conf_vals)
    _row("Entropy",    entropy_vals)
    _row("Chi² p",     chi2_vals)

    console.print(trend_table)

    # ── Scan summary ──────────────────────────────────────────────────────────
    n_stable = stable_days
    n_total  = len(draw_recs)
    if n_total:
        console.print(
            f"\n[dim]Stability: {n_stable}/{n_total} days stable[/dim]  "
            f"[dim]Log entries: {n_total}[/dim]"
        )
    if regime_counts:
        regime_str = "  ".join(
            f"[{'green' if k=='STABLE' else 'yellow' if k=='DRIFT' else 'red'}]{k}×{v}[/]"
            for k, v in sorted(regime_counts.items())
        )
        console.print(f"[dim]Regime: {regime_str}[/dim]")

    # ── Tickets ───────────────────────────────────────────────────────────────
    console.print()
    if not ticket_recs:
        console.print("[dim]No tickets logged this period. "
                      "Run [bold]lottery forecast[/bold] or [bold]lottery daily[/bold] to generate tickets.[/dim]")
    else:
        # Load actual draws for hit comparison
        df = adapter.fetch()
        # Only consider draws in the period
        period_draws = []
        for row in df.to_dict("records"):
            d = str(row.get("draw_date", "") or row.get("date", ""))[:10]
            if period_start <= d <= period_end:
                period_draws.append(row)

        hit_table = Table(title=f"Tickets ({len(ticket_recs)} logged)", box=None, padding=(0, 1), header_style="bold")
        hit_table.add_column("Date",    style="dim")
        hit_table.add_column("Source",  style="dim")
        hit_table.add_column("Ticket",  style="yellow")
        hit_table.add_column("vs Draw", style="dim")
        hit_table.add_column("Hits",    justify="center")
        hit_table.add_column("Tier",    justify="center")

        best_hits   = 0
        total_hits  = 0
        total_pairs = 0

        for rec in ticket_recs:
            ticket     = rec.get("ticket", [])
            ticket_set = set(ticket)
            ticket_str = "  ".join(str(n) for n in sorted(ticket))
            t_date     = rec.get("date", "—")
            source     = rec.get("source", "—")

            if not period_draws:
                hit_table.add_row(t_date, source, ticket_str, "—", "—", "—")
                continue

            # Check against all draws in the period
            for draw in period_draws:
                draw_nums = set(draw.get("numbers", []))
                d_id      = draw.get("draw_id", "—")
                hits      = len(ticket_set & draw_nums)
                tier      = _prize_tier(hits, rules)
                best_hits = max(best_hits, hits)
                total_hits  += hits
                total_pairs += 1

                if tier != "no prize":
                    hits_fmt = f"[green]{hits}[/green]"
                    tier_fmt = f"[green]{tier}[/green]"
                else:
                    hits_fmt = f"[dim]{hits}[/dim]"
                    tier_fmt = f"[dim]{tier}[/dim]"

                hit_table.add_row(t_date, source, ticket_str, str(d_id), hits_fmt, tier_fmt)

        console.print(hit_table)

        if total_pairs:
            avg_hits = total_hits / total_pairs
            console.print(
                f"\n[dim]Best hit: {best_hits}  ·  Avg hits/ticket: {avg_hits:.1f}  ·  "
                f"Tickets: {len(ticket_recs)}  ·  Draw comparisons: {total_pairs}[/dim]"
            )

    # ── Final panel ───────────────────────────────────────────────────────────
    conf_str = f"{sum(conf_vals)/len(conf_vals):.4f}" if conf_vals else "—"
    chi2_str = f"{sum(chi2_vals)/len(chi2_vals):.4f}" if chi2_vals else "—"
    t_count  = len(ticket_recs)
    l_count  = len(draw_recs)

    console.print()
    console.print(Panel(
        f"  Period     : {period_start} → {period_end}\n"
        f"  Log days   : {l_count}\n"
        f"  Avg conf   : {conf_str}\n"
        f"  Avg chi²p  : {chi2_str}\n"
        f"  Tickets    : {t_count}\n"
        f"  Best hit   : {best_hits if ticket_recs else '—'}",
        title=f"📅 Weekly Summary — {rules.name}",
        border_style="cyan",
    ))

    if export_md:
        _append_md(export_md, lottery, rules.name, today, period_start, period_end,
                   draw_recs, ticket_recs, conf_vals, chi2_vals, best_hits)
        console.print(f"[green]✔ Weekly report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    period_start: str, period_end: str,
    draw_recs: list[dict], ticket_recs: list[dict],
    conf_vals: list[float], chi2_vals: list[float],
    best_hits: int,
) -> None:
    conf_str = f"{sum(conf_vals)/len(conf_vals):.4f}" if conf_vals else "—"
    chi2_str = f"{sum(chi2_vals)/len(chi2_vals):.4f}" if chi2_vals else "—"
    spark    = _sparkline(conf_vals) if conf_vals else "—"

    content = f"""
---
type: weekly
subtype: weekly
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
period_start: {period_start}
period_end: {period_end}
log_days: {len(draw_recs)}
avg_confidence: {conf_str}
avg_chi2_p: {chi2_str}
tickets_generated: {len(ticket_recs)}
best_hit: {best_hits}
---

## Weekly Report: {game_name} ({period_start} → {period_end})

| Metric | Value |
|--------|-------|
| Log days | {len(draw_recs)} |
| Avg confidence | {conf_str} |
| Confidence trend | {spark} |
| Avg chi² p | {chi2_str} |
| Tickets generated | {len(ticket_recs)} |
| Best hit | {best_hits} |

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
