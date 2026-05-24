"""
Log Export Command 📤
=====================
Export JSONL log files to CSV, TSV, or JSON for external analysis.

Exports
-------
  draw-log     data/draw_log.jsonl    → daily diagnostic snapshots
  ticket-log   data/ticket_log.jsonl  → generated tickets + source

Output formats
--------------
  csv    (default)  comma-separated, Excel-compatible
  tsv               tab-separated
  json              pretty-printed JSON array

Deduplication
-------------
  draw-log is deduplicated by (game, date) keeping the latest entry per day.
  ticket-log is not deduplicated (multiple tickets per day are all valid).

Example
-------
  lottery log-export draw-log
  lottery log-export ticket-log --format tsv
  lottery log-export draw-log --game br/lotofacil --output data/draw_log.csv
  lottery log-export draw-log --since 2026-04-01
  lottery log-export all                        # export both logs
"""

from __future__ import annotations

import csv
import io
import json
import sys
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

console = Console()

_DATA_DIR   = Path(__file__).parent.parent.parent.parent / "data"
_DRAW_LOG   = _DATA_DIR / "draw_log.jsonl"
_TICKET_LOG = _DATA_DIR / "ticket_log.jsonl"

_DRAW_COLUMNS = [
    "date", "draw_id", "game", "strategy", "confidence", "entropy",
    "stable", "chi2_p", "moon_phase", "moon_ratio", "solar_kp", "cluster",
    "verdict", "score", "max_score", "regime",
]

_TICKET_COLUMNS = ["date", "game", "ticket", "source", "strategies"]


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            pass
    return records


def _dedup_draw_log(records: list[dict], game: Optional[str]) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for r in records:
        if game and r.get("game") != game:
            continue
        key = (r.get("game", ""), r.get("date", ""))
        seen[key] = r
    return list(seen.values())


def _filter_tickets(records: list[dict], game: Optional[str], since: Optional[str]) -> list[dict]:
    out = []
    for r in records:
        if game and r.get("game") != game:
            continue
        if since and r.get("date", "") < since:
            continue
        # Serialize ticket list to string
        if "ticket" in r and isinstance(r["ticket"], list):
            r = dict(r)
            r["ticket"] = " ".join(str(n) for n in r["ticket"])
        out.append(r)
    return out


def _to_csv(records: list[dict], columns: list[str], sep: str = ",") -> str:
    if not records:
        return ""
    # Union of all keys across records (preserve order with columns as priority)
    all_keys_set = set()
    for r in records:
        all_keys_set.update(r.keys())
    # Use specified columns first, then any remaining keys
    ordered = [c for c in columns if c in all_keys_set] + sorted(
        k for k in all_keys_set if k not in columns
    )

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=ordered, delimiter=sep,
                             extrasaction="ignore", restval="")
    writer.writeheader()
    for r in records:
        writer.writerow(r)
    return buf.getvalue()


def _to_json(records: list[dict]) -> str:
    return json.dumps(records, indent=2, default=str)


def _write_or_print(content: str, output: Optional[str], label: str) -> None:
    if output:
        p = Path(output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        console.print(f"[green]✔ {label} → {output}[/green]")
    else:
        print(content, end="")


def log_export(
    log_type: Annotated[str, typer.Argument(
        help="Which log to export: draw-log | ticket-log | all")] = "draw-log",
    game: Annotated[Optional[str], typer.Option("--game", "-g",
        help="Filter to a specific game (e.g. br/lotofacil)")] = None,
    since: Annotated[Optional[str], typer.Option("--since",
        help="Only include entries on or after this date (YYYY-MM-DD)")] = None,
    fmt: Annotated[str, typer.Option("--format", "-f",
        help="Output format: csv | tsv | json")] = "csv",
    output: Annotated[Optional[str], typer.Option("--output", "-o",
        help="Write to this file instead of stdout")] = None,
) -> None:
    """📤 Export JSONL logs to CSV/TSV/JSON for external analysis.

    draw-log   — daily diagnostic snapshots (deduplicated per day)
    ticket-log — all generated tickets
    all        — both logs (requires --output prefix or separate --output flags)

    Example: lottery log-export draw-log
             lottery log-export draw-log --game br/lotofacil --output data/draws.csv
             lottery log-export ticket-log --format json --since 2026-05-01
             lottery log-export all --output data/export
    """
    valid_types = {"draw-log", "ticket-log", "all"}
    if log_type not in valid_types:
        console.print(f"[red]Unknown log type:[/red] {log_type}. Choose: {', '.join(sorted(valid_types))}")
        raise typer.Exit(1)

    valid_fmts = {"csv", "tsv", "json"}
    if fmt not in valid_fmts:
        console.print(f"[red]Unknown format:[/red] {fmt}. Choose: {', '.join(sorted(valid_fmts))}")
        raise typer.Exit(1)

    sep = "\t" if fmt == "tsv" else ","

    def _export_draw(out_path: Optional[str]) -> None:
        raw = _load_jsonl(_DRAW_LOG)
        records = _dedup_draw_log(raw, game)
        if since:
            records = [r for r in records if r.get("date", "") >= since]
        records.sort(key=lambda r: (r.get("game", ""), r.get("date", "")))

        if not records:
            console.print("[dim]draw-log: no matching entries.[/dim]")
            return

        if fmt == "json":
            content = _to_json(records)
        else:
            content = _to_csv(records, _DRAW_COLUMNS, sep)

        ext = {"csv": "csv", "tsv": "tsv", "json": "json"}[fmt]
        label = f"draw-log ({len(records)} rows)"
        _write_or_print(content, out_path, label)

    def _export_tickets(out_path: Optional[str]) -> None:
        raw  = _load_jsonl(_TICKET_LOG)
        records = _filter_tickets(raw, game, since)

        if not records:
            console.print("[dim]ticket-log: no matching entries.[/dim]")
            return

        if fmt == "json":
            content = _to_json(records)
        else:
            content = _to_csv(records, _TICKET_COLUMNS, sep)

        label = f"ticket-log ({len(records)} rows)"
        _write_or_print(content, out_path, label)

    if log_type == "draw-log":
        _export_draw(output)
    elif log_type == "ticket-log":
        _export_tickets(output)
    elif log_type == "all":
        if output:
            # Use output as a path prefix: {output}_draw_log.csv, {output}_ticket_log.csv
            base = Path(output)
            ext  = fmt
            _export_draw(str(base.parent / f"{base.stem}_draw_log.{ext}"))
            _export_tickets(str(base.parent / f"{base.stem}_ticket_log.{ext}"))
        else:
            console.print("[yellow]Exporting 'all' to stdout — use --output <prefix> to write to files.[/yellow]")
            console.print("[dim]--- draw-log ---[/dim]")
            _export_draw(None)
            console.print("[dim]--- ticket-log ---[/dim]")
            _export_tickets(None)
