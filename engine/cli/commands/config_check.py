"""
Config Check Command 🩺
=======================
A "doctor" command for the engine's own environment/setup — distinct from
`audit-data` (which checks one game's DRAW data integrity). Read-only:
reports what's available/missing without modifying anything.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import typer
from rich.console import Console

from engine.cli.utils import ui_header, ui_table, Theme

console = Console()

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
OPTIONAL_PACKAGES = ["duckdb", "sklearn", "xgboost", "lightgbm", "catboost", "torch", "fastapi", "PySide6"]


def check_environment() -> dict:
    """Pure, side-effect-free environment probe — easy to unit test."""
    registry_path = DATA_DIR / "registry.yaml"

    game_count = 0
    registry_ok = False
    if registry_path.exists():
        try:
            from engine.adapters.registry import registry
            game_count = len(registry.list_games())
            registry_ok = game_count > 0
        except Exception:
            registry_ok = False

    local_configs = sorted(p.name for p in Path(".").glob("*.local.y*ml"))

    packages = {name: importlib.util.find_spec(name) is not None for name in OPTIONAL_PACKAGES}

    return {
        "data_dir_exists": DATA_DIR.exists(),
        "data_dir_writable": os.access(DATA_DIR, os.W_OK) if DATA_DIR.exists() else False,
        "registry_ok": registry_ok,
        "game_count": game_count,
        "local_configs": local_configs,
        "packages": packages,
    }


def config_check() -> None:
    """🩺 Environment/setup health check — DuckDB, registry, optional ML/UI extras, local config."""

    result = check_environment()
    ui_header("CONFIG CHECK", "engine environment")

    core_table = ui_table(columns=["Check", "Status", "Detail"])

    def _row(label: str, ok: bool, detail: str = "") -> None:
        mark = f"[{Theme.SUCCESS}]✓[/{Theme.SUCCESS}]" if ok else f"[{Theme.DANGER}]✗[/{Theme.DANGER}]"
        core_table.add_row(label, mark, detail)

    _row("data/ directory", result["data_dir_exists"], str(DATA_DIR))
    _row("data/ writable", result["data_dir_writable"])
    _row("registry.yaml loads", result["registry_ok"], f"{result['game_count']} games registered")
    console.print(core_table)

    pkg_table = ui_table(title="Optional packages", columns=["Package", "Installed"])
    for name, installed in result["packages"].items():
        mark = f"[{Theme.SUCCESS}]✓[/{Theme.SUCCESS}]" if installed else "[dim]—[/dim]"
        pkg_table.add_row(name, mark)
    console.print(pkg_table)

    if result["local_configs"]:
        console.print(f"\n[dim]Local config files found ({len(result['local_configs'])}): {', '.join(result['local_configs'])}[/dim]")
    else:
        console.print("\n[dim]No *.local.yaml config files found (personal numerology features will use defaults).[/dim]")

    if not result["registry_ok"] or not result["data_dir_writable"]:
        console.print(f"\n[bold {Theme.DANGER}]✗ Core setup has problems — see above.[/bold {Theme.DANGER}]")
        raise typer.Exit(1)
    console.print(f"\n[bold {Theme.SUCCESS}]✓ Core setup looks healthy.[/bold {Theme.SUCCESS}]")
