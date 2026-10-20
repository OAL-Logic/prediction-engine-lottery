"""
Import Lottery Studio Drawings Command 📥
===================================
Lottery Studio's "Import Drawings (TXT)" equivalent (Feature A8):
Ingests flat, space-delimited Lottery Studio draw files (e.g. M/D/YYYY date format)
directly into the high-performance local DuckDB / Partitioned JSON storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table
from engine.modules.storage import storage
from desktop.src.utils.converter import parse_studio_txt

console = Console()


def import_drawings(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena")],
    file_path: Annotated[Path, typer.Argument(help="Path to Lottery Studio space-delimited .txt file")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate and preview only — do not write to storage")] = False,
) -> None:
    """📥 Ingest historical lottery drawings from a Lottery Studio flat .txt file."""

    if not file_path.exists():
        console.print(f"[red]✗ File not found: {file_path}[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    rules = adapter.rules

    content = file_path.read_text(encoding="utf-8", errors="replace")
    parsed_draws = parse_studio_txt(
        file_content=content,
        pick_count=rules.pick_count,
        bonus_count=rules.bonus_count,
    )

    if not parsed_draws:
        console.print(f"[yellow]⚠ No valid draws parsed from {file_path}. Ensure it follows Lottery Studio 'M/D/YYYY N1 N2...' format.[/yellow]")
        raise typer.Exit(1)

    # Ingest into engine storage if not dry run
    if not dry_run:
        storage.save_draws(lottery, parsed_draws)

    status_note = " (dry-run preview)" if dry_run else " ingested"
    ui_header("Lottery Studio DRAWINGS IMPORT", f"{rules.name} · {len(parsed_draws)} records{status_note}")

    table = ui_table("Import Details", ["Property", "Value"])
    table.add_row("Source File", str(file_path))
    table.add_row("Lottery Context", lottery)
    table.add_row("Total Draws Parsed", f"{len(parsed_draws):,}")
    table.add_row("Date Span", f"{parsed_draws[0]['draw_date']} → {parsed_draws[-1]['draw_date']}")
    table.add_row("Storage Policy", storage.policy)
    console.print(table)

    console.print(f"[green]✓ Successfully imported {len(parsed_draws)} draws into engine storage.[/green]")
