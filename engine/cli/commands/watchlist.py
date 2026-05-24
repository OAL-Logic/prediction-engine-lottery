"""
Watchlist Command 📋
====================
Manage a persistent list of tracked games and run batch daily/alert
across all of them in one command.

Watchlist file: data/watchlist.json
  {"games": ["br/lotofacil", "br/mega-sena"], "added": {"br/lotofacil": "2026-01-01"}}

Sub-commands
------------
  watchlist add <game>       Add a game to the watchlist
  watchlist remove <game>    Remove a game from the watchlist
  watchlist list             Show all tracked games
  watchlist run [--mode]     Run daily/alert/scan across all tracked games
  watchlist status           One-line status summary per game (from JSONL log)

Run modes
---------
  daily   (default)  Full morning digest for each game
  alert              Alert check only (exit 0 if any game triggered)
  scan               GO/NO-GO scan only (compact table output)

Example
-------
  lottery watchlist add br/lotofacil
  lottery watchlist add br/mega-sena
  lottery watchlist list
  lottery watchlist run
  lottery watchlist run --mode alert
  lottery watchlist status
"""

from __future__ import annotations

import json
import sys
from datetime import date as _date
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
_WATCHLIST_FILE = _DATA_DIR / "watchlist.json"
_DEFAULT_LOG = _DATA_DIR / "draw_log.jsonl"

app = typer.Typer(name="watchlist", help="📋 Manage and batch-run tracked lottery games.")


# ── Watchlist persistence ─────────────────────────────────────────────────────

def _load() -> dict:
    if _WATCHLIST_FILE.exists():
        try:
            return json.loads(_WATCHLIST_FILE.read_text())
        except Exception:
            pass
    return {"games": [], "added": {}}


def _save(data: dict) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _WATCHLIST_FILE.write_text(json.dumps(data, indent=2))


# ── Sub-commands ──────────────────────────────────────────────────────────────

@app.command()
def add(
    game: Annotated[str, typer.Argument(help="Game ID to add, e.g. br/lotofacil")],
) -> None:
    """Add a game to the watchlist."""
    data = _load()
    if game in data["games"]:
        console.print(f"[yellow]{game}[/yellow] is already on the watchlist.")
        return
    # Validate game exists
    try:
        get_adapter(game)
    except Exception:
        console.print(f"[red]Unknown game:[/red] {game}. Run [bold]lottery games[/bold] for valid IDs.")
        raise typer.Exit(1)

    data["games"].append(game)
    data["added"][game] = _date.today().isoformat()
    _save(data)
    console.print(f"[green]Added[/green] {game} to watchlist ({len(data['games'])} tracked).")


@app.command(name="remove")
def remove_cmd(
    game: Annotated[str, typer.Argument(help="Game ID to remove")],
) -> None:
    """Remove a game from the watchlist."""
    data = _load()
    if game not in data["games"]:
        console.print(f"[yellow]{game}[/yellow] is not on the watchlist.")
        raise typer.Exit(1)
    data["games"].remove(game)
    data["added"].pop(game, None)
    _save(data)
    console.print(f"[red]Removed[/red] {game} from watchlist ({len(data['games'])} remaining).")


@app.command(name="list")
def list_cmd() -> None:
    """List all tracked games."""
    data = _load()
    games = data.get("games", [])
    if not games:
        console.print("[dim]Watchlist is empty. Use [bold]lottery watchlist add <game>[/bold] to start tracking.[/dim]")
        return

    table = Table(title="Watched Games", box=None, padding=(0, 2))
    table.add_column("Game ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Added", style="dim")

    for gid in games:
        try:
            adapter = get_adapter(gid)
            name = adapter.rules.name
        except Exception:
            name = "[dim]unknown[/dim]"
        added = data["added"].get(gid, "—")
        table.add_row(gid, name, added)

    console.print(table)
    console.print(f"\n[dim]{len(games)} game(s) tracked. Run [bold]lottery watchlist run[/bold] for batch digest.[/dim]")


@app.command()
def status() -> None:
    """Show last-logged status for each tracked game (from JSONL log)."""
    data = _load()
    games = data.get("games", [])
    if not games:
        console.print("[dim]Watchlist is empty.[/dim]")
        return

    # Load log records
    log_records: dict[str, dict] = {}
    if _DEFAULT_LOG.exists():
        for line in _DEFAULT_LOG.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                gid = rec.get("game", "")
                if gid in games:
                    log_records[gid] = rec  # last record wins (file is append-only)
            except Exception:
                pass

    table = Table(title=f"Watchlist Status — {_date.today().isoformat()}", box=None, padding=(0, 2))
    table.add_column("Game", style="cyan")
    table.add_column("Last Run", style="dim")
    table.add_column("Verdict", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Confidence", justify="right")
    table.add_column("Regime", justify="center")

    for gid in games:
        rec = log_records.get(gid)
        if rec is None:
            table.add_row(gid, "—", "[dim]no log[/dim]", "—", "—", "—")
            continue

        ts = rec.get("timestamp", rec.get("date", "—"))[:10]
        verdict = rec.get("verdict", "—")
        score = rec.get("score", "—")
        max_score = rec.get("max_score", "—")
        score_str = f"{score}/{max_score}" if score != "—" else "—"
        conf = rec.get("confidence")
        conf_str = f"{conf:.4f}" if conf is not None else "—"
        regime = rec.get("regime", "—")

        verdict_fmt = (
            f"[green]{verdict}[/green]" if verdict == "GO"
            else f"[yellow]{verdict}[/yellow]" if verdict == "CAUTION"
            else f"[red]{verdict}[/red]" if verdict == "NO-GO"
            else f"[dim]{verdict}[/dim]"
        )
        regime_fmt = (
            f"[green]{regime}[/green]" if regime == "STABLE"
            else f"[yellow]{regime}[/yellow]" if regime == "DRIFT"
            else f"[red]{regime}[/red]" if regime == "SHIFT"
            else f"[dim]{regime}[/dim]"
        )

        table.add_row(gid, ts, verdict_fmt, score_str, conf_str, regime_fmt)

    console.print(table)


@app.command(name="run")
def run_cmd(
    mode: Annotated[str, typer.Option("--mode", "-m",
        help="daily | alert | scan")] = "daily",
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet",
        help="Compact output (only for scan/alert mode)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append each game's digest to this markdown file (daily mode only)")] = None,
    condition: Annotated[str, typer.Option("--condition", "-c",
        help="Alert conditions (alert mode only)")] = "go-strong,regime-shift",
    jackpot: Annotated[Optional[str], typer.Option("--jackpot",
        help="Comma-separated jackpot amounts (one per game, in order)")] = None,
) -> None:
    """Run daily/alert/scan across all tracked games.

    Modes:
      daily   Full morning digest for each game (default)
      alert   Alert check only — prints triggered games; exits 0 if any triggered
      scan    GO/NO-GO scan table (compact)

    Example:
      lottery watchlist run
      lottery watchlist run --mode alert
      lottery watchlist run --mode scan --quiet
      lottery watchlist run --mode daily --export-md digest.md
    """
    data = _load()
    games = data.get("games", [])
    if not games:
        console.print("[dim]Watchlist is empty. Use [bold]lottery watchlist add <game>[/bold] first.[/dim]")
        raise typer.Exit(1)

    valid_modes = {"daily", "alert", "scan"}
    if mode not in valid_modes:
        console.print(f"[red]Invalid mode:[/red] {mode}. Choose: {', '.join(sorted(valid_modes))}")
        raise typer.Exit(1)

    jackpot_map: dict[str, float] = {}
    if jackpot:
        parts = [p.strip() for p in jackpot.split(",")]
        for i, gid in enumerate(games):
            if i < len(parts) and parts[i]:
                try:
                    jackpot_map[gid] = float(parts[i])
                except ValueError:
                    pass

    console.print(Rule(f"[bold cyan]Watchlist Run — {mode.upper()} — {_date.today().isoformat()}[/bold cyan]"))
    console.print(f"[dim]Tracking {len(games)} game(s): {', '.join(games)}[/dim]\n")

    if mode == "daily":
        _run_daily(games, export_md=export_md, jackpot_map=jackpot_map)
    elif mode == "alert":
        _run_alert(games, condition=condition, quiet=quiet)
    elif mode == "scan":
        _run_scan(games, quiet=quiet)


# ── Batch runners ─────────────────────────────────────────────────────────────

def _run_daily(games: list[str], *, export_md: Optional[str], jackpot_map: dict[str, float]) -> None:
    """Run full daily digest for each game."""
    from engine.cli.commands.daily import daily as _daily

    for gid in games:
        console.print(Rule(f"[bold]{gid}[/bold]"))
        jkp = jackpot_map.get(gid)
        try:
            _daily(
                lottery=gid,
                quiet=False,
                export_md=export_md,
                jackpot=jkp,
                persona="analyst",
            )
        except SystemExit:
            pass
        except Exception as exc:
            console.print(f"[red]Error running daily for {gid}:[/red] {exc}")
        console.print()


def _run_alert(games: list[str], *, condition: str, quiet: bool) -> None:
    """Run alert check for each game; show triggered alerts in a table."""
    from engine.cli.commands.alert import alert as _alert_fn

    any_triggered = False
    results: list[tuple[str, bool, str]] = []

    for gid in games:
        if not quiet:
            console.print(f"[dim]Checking {gid}...[/dim]")
        triggered = False
        message = "no conditions met"
        try:
            _alert_fn(
                lottery=gid,
                condition=condition,
                strategy="bayesian",
                output=None,
                silent=True,
            )
            triggered = True
            message = "TRIGGERED"
        except typer.Exit as e:
            if e.exit_code == 0:
                triggered = True
                message = "TRIGGERED"
            elif e.exit_code == 2:
                message = "error"
        except SystemExit as e:
            code = e.code if hasattr(e, "code") and isinstance(e.code, int) else 1
            if code == 0:
                triggered = True
                message = "TRIGGERED"
            elif code == 2:
                message = "error"
        except Exception as exc:
            message = f"error: {exc}"

        results.append((gid, triggered, message))
        if triggered:
            any_triggered = True

    table = Table(title=f"Alert Check — {condition}", box=None, padding=(0, 2))
    table.add_column("Game", style="cyan")
    table.add_column("Status", justify="center")

    for gid, triggered, msg in results:
        if triggered:
            table.add_row(gid, "[bold green]🚨 TRIGGERED[/bold green]")
        else:
            table.add_row(gid, "[dim]quiet[/dim]")

    console.print(table)

    if any_triggered:
        console.print("\n[bold green]At least one game triggered — exit 0.[/bold green]")
        raise typer.Exit(0)
    else:
        console.print("\n[dim]No games triggered — exit 1.[/dim]")
        raise typer.Exit(1)


def _run_scan(games: list[str], *, quiet: bool) -> None:
    """Run GO/NO-GO scan for each game and print a summary table."""
    from engine.cli.commands.scan import (
        _rolling_stable_pct, _stress_delta, _solar_kp, _regime_js,
    )
    from engine.cli.commands.forecast import _composite_weight
    from engine.modules import frequency
    from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name
    from datetime import date as _date

    table = Table(title=f"Watchlist Scan — {_date.today().isoformat()}", box=None, padding=(0, 2))
    table.add_column("Game", style="cyan")
    table.add_column("Verdict", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Regime", justify="center")
    table.add_column("Fairness", justify="center")
    table.add_column("Stability", justify="center")

    for gid in games:
        try:
            adapter = get_adapter(gid)
            df = adapter.fetch()
            rules = adapter.rules
            lo, hi = rules.number_range
            pool_size = hi - lo + 1

            scores: dict[str, int] = {}

            try:
                f_res = frequency.analyze(df.tail(100), rules, top_n=1)
                p = f_res.chi2_p_value
                scores["fairness"] = 2 if p > 0.5 else 1 if p >= 0.05 else 0
                fairness_str = f"p={p:.3f}"
            except Exception:
                scores["fairness"] = 1
                fairness_str = "—"

            stab = _rolling_stable_pct(df, adapter, "bayesian", 50, n_windows=4)
            scores["stability"] = (2 if stab and stab >= 0.5 else
                                   1 if stab and stab >= 0.25 else
                                   0 if stab is not None else 1)
            stab_str = f"{stab*100:.0f}%" if stab is not None else "—"

            scores["cluster"] = 1

            today = _date.today()
            moon_name = phase_name(today)
            kp = _solar_kp()
            es = 2 if moon_name in ("New Moon", "Full Moon") else 1
            if kp is not None:
                es = max(0, es - 1) if kp >= 5 else min(2, es + 1) if kp < 3 else es
            scores["esoteric"] = es

            delta = _stress_delta(df, adapter, "bayesian")
            scores["discrimination"] = (2 if delta and delta > 0.02 else
                                        0 if delta and delta < -0.005 else 1)

            js_val, regime_verdict = _regime_js(df, lo, pool_size, recent=50)
            scores["regime"] = 2 if regime_verdict == "STABLE" else 1 if regime_verdict == "DRIFT" else 0

            total = sum(scores.values())
            max_score = len(scores) * 2
            pct = total / max_score
            verdict = "GO" if pct >= 0.70 else "CAUTION" if pct >= 0.40 else "NO-GO"

            verdict_fmt = (
                f"[green]{verdict}[/green]" if verdict == "GO"
                else f"[yellow]{verdict}[/yellow]" if verdict == "CAUTION"
                else f"[red]{verdict}[/red]"
            )
            regime_fmt = (
                f"[green]{regime_verdict}[/green]" if regime_verdict == "STABLE"
                else f"[yellow]{regime_verdict}[/yellow]" if regime_verdict == "DRIFT"
                else f"[red]{regime_verdict}[/red]"
            )

            table.add_row(
                gid,
                verdict_fmt,
                f"{total}/{max_score}",
                regime_fmt,
                fairness_str,
                stab_str,
            )

        except Exception as exc:
            table.add_row(gid, "[red]ERROR[/red]", "—", "—", "—", f"[dim]{exc}[/dim]")

    console.print(table)
