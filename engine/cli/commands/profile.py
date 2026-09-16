"""
Profile Command 💾
==================
Save a full CLI invocation under a short name and replay it later —
"bookmarks" for the CLI's option surface. Not a SamLotto feature per se,
but a natural companion to a 100+ command engine: `lottery profile save
weighted3 --command "suggest br/mega-sena --strategy weighted --count 3"`
then `lottery profile run weighted3`.
"""

from __future__ import annotations

import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import typer
from rich.console import Console

from engine.cli.utils import ui_header, ui_table

console = Console()
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
PROFILES_FILE = DATA_DIR / "profiles.json"


def _load() -> dict[str, Any]:
    if PROFILES_FILE.exists():
        try:
            return json.loads(PROFILES_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _write(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_FILE.write_text(json.dumps(data, indent=2))


def save(name: str, command: str, description: str = "") -> None:
    if not command.strip():
        console.print("[red]✗ --command cannot be empty.[/red]")
        raise typer.Exit(1)
    profiles = _load()
    profiles[name] = {
        "command": command.strip(),
        "description": description,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _write(profiles)
    console.print(f"[green]✓[/green] Saved profile [bold]{name}[/bold]: `lottery {command.strip()}`")


def list_cmd() -> None:
    profiles = _load()
    ui_header("PROFILES", f"{len(profiles)} saved")
    if not profiles:
        console.print('[dim]No profiles saved yet. Try: lottery profile save <name> --command "suggest br/mega-sena"[/dim]')
        return
    table = ui_table(columns=["Name", "Command", "Description", "Created"])
    for name, p in sorted(profiles.items()):
        table.add_row(name, p["command"], p.get("description", ""), p["created"][:10])
    console.print(table)


def show(name: str) -> None:
    profiles = _load()
    if name not in profiles:
        console.print(f"[red]✗ No profile named '{name}'.[/red]")
        raise typer.Exit(1)
    p = profiles[name]
    console.print(f"[bold]{name}[/bold]: lottery {p['command']}")
    if p.get("description"):
        console.print(f"[dim]{p['description']}[/dim]")


def delete(name: str) -> None:
    profiles = _load()
    if name not in profiles:
        console.print(f"[red]✗ No profile named '{name}'.[/red]")
        raise typer.Exit(1)
    del profiles[name]
    _write(profiles)
    console.print(f"[green]✓[/green] Deleted profile [bold]{name}[/bold].")


def run(name: str) -> None:
    profiles = _load()
    if name not in profiles:
        console.print(f"[red]✗ No profile named '{name}'.[/red]")
        raise typer.Exit(1)

    command = profiles[name]["command"]
    console.print(f"[dim]$ lottery {command}[/dim]")

    from typer.main import get_command
    from engine.cli.main import app as root_app

    click_cmd = get_command(root_app)
    try:
        click_cmd.main(args=shlex.split(command), prog_name="lottery", standalone_mode=False)
    except click.exceptions.Exit as exc:
        raise typer.Exit(exc.exit_code)
    except click.exceptions.ClickException as exc:
        console.print(f"[red]✗ {exc.format_message()}[/red]")
        raise typer.Exit(exc.exit_code)
    except SystemExit as exc:
        raise typer.Exit(exc.code or 0)
