"""
Fringe Inspector CLI Command (`engine.cli.commands.fringe_inspect`)
==================================================================
Launches the interactive or snapshot terminal UI dashboard for inspecting
fringe theories, strange attractors, Ising lattices, and quantum branches.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter
from engine.tui.fringe_inspector import FringeTUIApp, export_markdown_snapshot


console = Console()


def fringe_inspect(
    lottery: Annotated[str, typer.Argument(help="Lottery game identifier (e.g. br/mega-sena, br/quina, br/lotofacil)")] = "br/mega-sena",
    mode: Annotated[str, typer.Option("--mode", "-m", help="Inspection focus: 'all', 'lorenz', 'ising', 'tda', 'noosphere', 'quantum'")] = "all",
    draws: Annotated[int, typer.Option("--draws", "-n", help="Historical context draws")] = 50,
    live: Annotated[bool, typer.Option("--live/--once", help="Run live animated TUI loop vs. static one-shot frame")] = False,
    fps: Annotated[float, typer.Option("--fps", help="Frame rate for live animation")] = 4.0,
    duration: Annotated[float, typer.Option("--duration", "-d", help="Max duration in seconds for live loop")] = 10.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export markdown snapshot to file")] = None,
) -> None:
    """🔮 Interactive TUI Fringe Physics & Speculative Theories Inspector."""
    adapter = get_adapter(lottery)
    df = adapter.fetch(limit=draws)

    app = FringeTUIApp(rules=adapter.rules, mode=mode, df=df)

    if export_md:
        out_path = Path(export_md)
        export_markdown_snapshot(app, out_path)
        console.print(f"[green]✓[/green] Fringe TUI snapshot exported to: [bold]{out_path.as_posix()}[/bold]")
        if not live:
            return

    # Auto-detect if interactive TTY is available
    is_interactive = sys.stdout.isatty() and live

    if is_interactive:
        app.run_live(fps=fps, duration=duration)
    else:
        # One-shot static snapshot rendering
        snapshot = app.render_snapshot()
        console.print(snapshot)
