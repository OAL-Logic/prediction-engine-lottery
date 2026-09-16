"""
Storage Consistency Command 🗄️🔍
=================================
`LotteryStorage` dual-writes every draw to both DuckDB (speed) and
partitioned JSON files (human-inspectable, policy="cache" source of
truth). Nothing previously cross-checked that the two actually agree.
This command diffs them directly: draws missing from one side, and draws
present in both but with different numbers.
"""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import ui_header, ui_table, Theme
from engine.modules.storage import DB_PATH, INSPECTION_DIR

console = Console()


def load_db_side(lottery_id: str) -> dict[int, list[int]]:
    try:
        import duckdb
    except ImportError:
        return {}
    if not DB_PATH.exists():
        return {}
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        try:
            rows = con.execute("SELECT draw_id, numbers FROM draws WHERE lottery_id = ?", [lottery_id]).fetchall()
        except Exception:
            return {}
    return {int(draw_id): sorted(numbers) for draw_id, numbers in rows}


def load_json_side(lottery_id: str) -> dict[int, list[int]]:
    out: dict[int, list[int]] = {}
    out_dir = INSPECTION_DIR / lottery_id.replace("/", "_")
    if not out_dir.exists():
        return out
    for p in sorted(out_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        for rec in data:
            out[int(rec["draw_id"])] = sorted(rec["numbers"])
    return out


def diff_sources(db_side: dict[int, list[int]], json_side: dict[int, list[int]]) -> dict:
    db_only = sorted(set(db_side) - set(json_side))
    json_only = sorted(set(json_side) - set(db_side))
    mismatched = sorted(i for i in (set(db_side) & set(json_side)) if db_side[i] != json_side[i])
    return {"db_only": db_only, "json_only": json_only, "mismatched": mismatched}


def storage_consistency(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
) -> None:
    """🗄️🔍 Cross-check DuckDB against the JSON partition files for one lottery."""

    db_side = load_db_side(lottery)
    json_side = load_json_side(lottery)

    ui_header("STORAGE CONSISTENCY", f"{lottery} · DB={len(db_side)} draws · JSON={len(json_side)} draws")

    if not db_side and not json_side:
        console.print(f"[yellow]No cached data for {lottery} in either DuckDB or JSON. Run `lottery fetch {lottery}` first.[/yellow]")
        raise typer.Exit(1)

    result = diff_sources(db_side, json_side)
    total_issues = len(result["db_only"]) + len(result["json_only"]) + len(result["mismatched"])

    if total_issues == 0:
        console.print(f"[bold {Theme.SUCCESS}]✓ Consistent — {len(db_side)} draws agree across both storage backends.[/bold {Theme.SUCCESS}]")
        return

    table = ui_table(title=f"{total_issues} discrepancy(ies)", columns=["Kind", "Draw IDs"])
    if result["db_only"]:
        table.add_row("Only in DuckDB", str(result["db_only"][:20]) + (" …" if len(result["db_only"]) > 20 else ""))
    if result["json_only"]:
        table.add_row("Only in JSON", str(result["json_only"][:20]) + (" …" if len(result["json_only"]) > 20 else ""))
    if result["mismatched"]:
        table.add_row("Numbers differ", str(result["mismatched"][:20]) + (" …" if len(result["mismatched"]) > 20 else ""))
    console.print(table)
    console.print(f"\n[bold {Theme.DANGER}]✗ {total_issues} discrepancy(ies) between DuckDB and JSON.[/bold {Theme.DANGER}] Re-run `lottery fetch {lottery}` to resync.")
    raise typer.Exit(1)
