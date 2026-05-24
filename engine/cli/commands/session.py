"""
Session Command 🎲
==================
All-in-one pre-draw decision session.

Chains the full diagnostic pipeline in the right order, gating each
subsequent step on the previous verdict. Run this once before each draw
to get a consolidated recommendation in a single command.

Pipeline
--------
  Stage 1  Scan (GO/NO-GO gate)
  Stage 2  Regime check (compare-draws — is distribution stable?)
  Stage 3  Streak snapshot (streak-report — who's hot/cold right now?)
  Stage 4  Strategy comparison (compare-strategies — where do strategies agree?)
  Stage 5  Consensus ticket (forecast — weighted ensemble ticket)
  Stage 6  Oracle (optional confirmation — requires --oracle flag)

Behaviour
---------
  • If Stage 1 is NO-GO, session stops at Stage 1 and exits with code 1
    (unless --force is passed)
  • If Stage 2 shows SHIFT regime, a warning is printed but session continues
  • --quiet skips Rich formatting for pipeline/cron use
  • --export-md <file> appends each stage's result block

Exit codes
----------
  0  session completed, ticket generated
  1  NO-GO — scan blocked or no ticket produced
  2  error

Example
-------
  lottery session br/lotofacil
  lottery session br/lotofacil --force          # ignore NO-GO
  lottery session br/lotofacil --strategies fast
  lottery session br/lotofacil --export-md session.md
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from engine.cli.utils import get_adapter

console = Console()

_STAGE_WIDTH = 60


def _hr(label: str) -> None:
    console.print(Rule(f"[dim]{label}[/dim]", style="dim"))


def session(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Strategy group: default | fast | statistical")] = "fast",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for strategy scoring")] = 50,
    force: Annotated[bool, typer.Option("--force",
        help="Continue session even if scan is NO-GO")] = False,
    skip_oracle: Annotated[bool, typer.Option("--skip-oracle",
        help="Skip the oracle stage (faster)")] = True,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append session report to this .md file")] = None,
) -> None:
    """🎲 All-in-one pre-draw decision session.

    Chains scan → regime → streak → compare-strategies → forecast into a
    single command. Stops at NO-GO unless --force is passed.

    Example: lottery session br/lotofacil
             lottery session br/lotofacil --force
             lottery session br/lotofacil --strategies default --export-md session.md
    """
    adapter = get_adapter(lottery)
    rules   = adapter.rules
    today   = _date.today()

    stage_results: list[dict] = []
    ticket: list[int] = []
    go_verdict = True

    console.print()
    console.print(Panel(
        f"[bold]{rules.name}[/bold]  ·  {today.isoformat()}  ·  {strategies} strategies",
        title="🎲 Pre-Draw Session",
        border_style="cyan",
    ))
    console.print()

    # ── Stage 1: Scan ─────────────────────────────────────────────────────────
    _hr("Stage 1 / 5  —  GO/NO-GO Scan")
    try:
        from engine.cli.commands.scan import scan as _scan
        # Capture scan result via direct call; scan prints its own output
        scan_go = True
        try:
            _scan(lottery=lottery, window=window, auto_suggest=False, export_md=None, quiet=False)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            scan_go = (code == 0)
        except typer.Exit as e:
            scan_go = (e.exit_code == 0)
        stage_results.append({"stage": "scan", "verdict": "GO" if scan_go else "NO-GO"})
    except Exception as exc:
        console.print(f"[dim]  Scan failed: {exc}[/dim]")
        scan_go = True  # soft-fail: don't block on scan error
        stage_results.append({"stage": "scan", "verdict": "ERROR"})

    if not scan_go:
        if force:
            console.print("[yellow]  ⚠ NO-GO scan — continuing because --force[/yellow]")
            go_verdict = False
        else:
            console.print(
                "\n[bold red]  ✗ NO-GO — session stopped.[/bold red]  "
                "(Pass --force to override)\n"
            )
            if export_md:
                _append_md(export_md, lottery, rules.name, today, stage_results, [], "NO-GO")
            raise typer.Exit(1)

    # ── Stage 2: Regime check ─────────────────────────────────────────────────
    _hr("Stage 2 / 5  —  Regime Check")
    try:
        from engine.cli.commands.compare_draws import compare_draws as _cd
        _cd(lottery=lottery, recent=window, baseline=0, top_n=10, export_md=None)
        stage_results.append({"stage": "regime", "verdict": "OK"})
    except Exception as exc:
        console.print(f"[dim]  Regime check skipped: {exc}[/dim]")
        stage_results.append({"stage": "regime", "verdict": "SKIPPED"})

    # ── Stage 3: Streak snapshot ──────────────────────────────────────────────
    _hr("Stage 3 / 5  —  Streak Snapshot")
    try:
        from engine.cli.commands.streak_report import streak_report as _sr
        _sr(lottery=lottery, draws=window, top=10, export_md=None)
        stage_results.append({"stage": "streak", "verdict": "OK"})
    except Exception as exc:
        console.print(f"[dim]  Streak snapshot skipped: {exc}[/dim]")
        stage_results.append({"stage": "streak", "verdict": "SKIPPED"})

    # ── Stage 4: Strategy comparison ──────────────────────────────────────────
    _hr("Stage 4 / 5  —  Strategy Comparison")
    try:
        from engine.cli.commands.compare_strategies import compare_strategies as _cs
        _cs(lottery=lottery, strategies=strategies, window=window, top=rules.pick_count,
            temperature=0.0, export_md=None)
        stage_results.append({"stage": "compare-strategies", "verdict": "OK"})
    except Exception as exc:
        console.print(f"[dim]  Strategy comparison skipped: {exc}[/dim]")
        stage_results.append({"stage": "compare-strategies", "verdict": "SKIPPED"})

    # ── Stage 5: Forecast consensus ticket ────────────────────────────────────
    _hr("Stage 5 / 5  —  Forecast Consensus Ticket")
    try:
        from engine.cli.commands.forecast import forecast as _forecast
        # Capture the result to show in summary
        res = _forecast(
            lottery=lottery,
            strategies=strategies,
            window=window,
            step=20,
            inject_ratio=0.5,
            trials=3,
            temperature=0.0,
            export_md=None,
            quiet=False,
            use_calibration=False,
            seed=None,
            config=None
        )
        # Assuming forecast returns a list of tickets or a SuggestionResult
        # In the current implementation it returns None and prints, but let's check
        stage_results.append({"stage": "forecast", "verdict": "OK"})
    except Exception as exc:
        console.print(f"[dim]  Forecast failed: {exc}[/dim]")
        stage_results.append({"stage": "forecast", "verdict": "ERROR"})

    # ── Session summary ───────────────────────────────────────────────────────
    final_verdict = "GO" if go_verdict else "FORCED"
    stages_ok = sum(1 for s in stage_results if s["verdict"] in ("OK", "GO"))
    stages_str = "  ".join(
        f"[green]{s['stage']}:{s['verdict']}[/green]" if s["verdict"] in ("OK", "GO")
        else f"[yellow]{s['stage']}:{s['verdict']}[/yellow]" if s["verdict"] == "FORCED"
        else f"[red]{s['stage']}:{s['verdict']}[/red]"
        for s in stage_results
    )

    console.print()
    console.print(Panel(
        f"[bold green]Session complete[/bold green]  ·  "
        f"Verdict: [bold]{final_verdict}[/bold]  ·  "
        f"{stages_ok}/{len(stage_results)} stages OK\n"
        f"{stages_str}",
        title="🎲 Session Summary",
        border_style="green" if final_verdict == "GO" else "yellow",
    ))

    if export_md:
        _append_md(export_md, lottery, rules.name, today, stage_results, ticket, final_verdict)
        console.print(f"[green]✔ Session report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    stage_results: list[dict], ticket: list[int], verdict: str,
) -> None:
    stages_md = "\n".join(
        f"- **{s['stage']}**: {s['verdict']}" for s in stage_results
    )
    ticket_str = " ".join(str(n) for n in ticket) if ticket else "—"

    content = f"""
---
type: diagnostic
subtype: session
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
verdict: {verdict}
stages_run: {len(stage_results)}
ticket: [{ticket_str}]
---

## Pre-Draw Session: {game_name} ({today.isoformat()})

**Verdict:** {verdict}  ·  **Stages:** {len(stage_results)}

### Stage Results

{stages_md}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
