"""
Import Historical Drawings Command 📥
=====================================
Ingests historical draw files (.csv, .json, or Lottery Studio space-delimited .txt/.dat)
directly into the high-performance local DuckDB / Partitioned JSON storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table
from engine.modules.storage import storage

console = Console()


def import_drawings(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena")],
    file_path: Annotated[Path, typer.Argument(help="Path to historical drawings file (.csv, .json, .txt, .dat)")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate and preview only — do not write to storage")] = False,
) -> None:
    """📥 Ingest historical lottery drawings from a .csv, .json, or flat .txt file."""

    if not file_path.exists():
        console.print(f"[red]✗ File not found: {file_path}[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    rules = adapter.rules
    canonical_id = getattr(rules, "id", None) or lottery

    parsed_draws = storage.ingest_file(
        file_path=file_path,
        lottery_id=canonical_id,
        rules=rules,
        dry_run=dry_run,
    )

    if not parsed_draws:
        console.print(
            f"[yellow]⚠ No valid draws parsed from {file_path}. "
            f"Supported formats: Caixa/standard .csv, .json, or Lottery Studio 'M/D/YYYY N1 N2...' .txt.[/yellow]"
        )
        raise typer.Exit(1)

    status_note = " (dry-run preview)" if dry_run else " ingested"
    ui_header("HISTORICAL DRAWINGS IMPORT", f"{rules.name} · {len(parsed_draws)} records{status_note}")

    table = ui_table("Import Details", ["Property", "Value"])
    table.add_row("Source File", str(file_path))
    table.add_row("Lottery Context", canonical_id)
    table.add_row("Total Draws Parsed", f"{len(parsed_draws):,}")
    table.add_row("Date Span", f"{parsed_draws[0]['draw_date']} → {parsed_draws[-1]['draw_date']}")
    table.add_row("Storage Policy", storage.policy)
    console.print(table)

    console.print(f"[green]✓ Successfully imported {len(parsed_draws)} draws into engine storage.[/green]")
