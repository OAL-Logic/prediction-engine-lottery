"""
Log Command 📓
==============
Lightweight daily tracker — appends a compact structured record to a
JSONL file after each draw. Designed to be run automatically (cron,
report pipeline, post-fetch hook) with no user interaction.

Record fields
-------------
  date          ISO date of recording
  draw_id       latest available draw id
  game          lottery id
  strategy      strategy used for signal check
  confidence    strategy confidence on last 50 draws
  entropy       score entropy (lower = more concentrated)
  chi2_p        chi-squared p-value (fairness)
  moon_phase    current moon phase name
  moon_ratio    0.0–1.0 through the lunar cycle
  solar_kp      NOAA K-index if available else null
  cluster       K-Means cluster of latest draw (if scikit-learn present)
  stable        bool — is current window stable?

Output formats
--------------
  --format jsonl  (default) — one JSON object per line, appended to file
  --format csv    — appended to CSV, header written if file is new
  --format md     — human-readable markdown table row appended to file

Use `lottery log-view` (or `jq` / `csvkit`) to read the log.
"""

from __future__ import annotations

import csv
import json
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console

from engine.cli.utils import get_adapter, calculate_shannon_entropy, print_command_summary
from engine.strategies import get_strategy
from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name
from engine.modules import frequency

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DEFAULT_LOG = _DATA_DIR / "draw_log.jsonl"


def _get_solar_kp() -> float | None:
    path = _DATA_DIR / "solar_k_index.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        today = _date.today().isoformat()
        return data.get(today) or data.get(sorted(data.keys())[-1])
    except Exception:
        return None


def _get_cluster(df, adapter) -> int | None:
    try:
        from sklearn.cluster import KMeans  # type: ignore[import-untyped]
        from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
    except ImportError:
        return None
    lo, hi = adapter.rules.number_range
    pool_size = hi - lo + 1
    n = min(len(df), 150)
    df_sub = df.tail(n)
    X = np.zeros((len(df_sub), pool_size), dtype=float)
    for i, nums in enumerate(df_sub["numbers"]):
        for num in nums:
            if lo <= num <= hi:
                X[i, num - lo] = 1.0
    sums = np.array([sum(d) for d in df_sub["numbers"]], dtype=float)
    parities = np.array([
        sum(1 for num in d if num % 2 == 0) / len(d) for d in df_sub["numbers"]
    ], dtype=float)
    X_aug = np.column_stack([X, sums / (sums.max() or 1.0), parities])
    try:
        from sklearn.preprocessing import StandardScaler
        model = KMeans(n_clusters=5, random_state=42, n_init=5)
        labels = model.fit_predict(StandardScaler().fit_transform(X_aug))
        return int(labels[-1])
    except Exception:
        return None

def log(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Strategy to use for signal snapshot")] = "bayesian",
    output: Annotated[str, typer.Option("--output", "-o",
        help="Log file path")] = "",
    fmt: Annotated[str, typer.Option("--format", "-f",
        help="Output format: jsonl | csv | md")] = "jsonl",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for signal snapshot")] = 50,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet",
        help="Suppress output (for cron/pipeline use)")] = False,
) -> None:
    """📓 Append a daily diagnostic snapshot to a persistent log file.

    Designed for automated/daily use — run after each draw fetch to
    build a historical record of conditions over time.

    Example (manual):   lottery log br/lotofacil
    Example (pipeline): lottery log br/lotofacil --quiet --output my_log.jsonl
    Example (CSV):      lottery log br/lotofacil --format csv --output log.csv
    """

    log_path = Path(output) if output else _DEFAULT_LOG

    if not quiet:
        print_command_summary("log", lottery, strategy=strategy, fmt=fmt, output=str(log_path))

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    today = _date.today()
    latest_draw_id = int(df.iloc[-1]["draw_id"]) if not df.empty else -1

    # ── Signal snapshot ───────────────────────────────────────────────────────
    win_df = df.tail(window)
    confidence: float | None = None
    entropy: float | None = None
    stable: bool | None = None

    try:
        strat = get_strategy(strategy)
        res = strat.suggest(win_df, adapter.rules, count=1, temperature=1.0)
        confidence = round(res.confidence, 6)
        entropy = round(calculate_shannon_entropy(res.scores), 6)
    except Exception:
        pass

    # Rolling stability check (3 quick windows)
    if confidence is not None:
        quick_confs = [confidence]
        for offset in [window, window * 2]:
            pos = len(df) - window - offset
            if pos < 0:
                break
            try:
                s2 = get_strategy(strategy)
                r2 = s2.suggest(df.iloc[pos : pos + window], adapter.rules, count=1, temperature=1.0)
                quick_confs.append(r2.confidence)
            except Exception:
                continue
        if len(quick_confs) >= 2:
            arr = np.array(quick_confs)
            std = float(np.std(arr))
            stable = std <= 0.08

    # ── Fairness ──────────────────────────────────────────────────────────────
    chi2_p: float | None = None
    try:
        f_res = frequency.analyze(df.tail(100), adapter.rules, top_n=1)
        chi2_p = round(f_res.chi2_p_value, 6)
    except Exception:
        pass

    # ── Esoteric ─────────────────────────────────────────────────────────────
    moon_ratio = moon_phase_ratio(today)
    moon_name  = phase_name(today)
    solar_kp   = _get_solar_kp()

    # ── Cluster ───────────────────────────────────────────────────────────────
    cluster_id = _get_cluster(df, adapter)

    # ── Build record ──────────────────────────────────────────────────────────
    record: dict = {
        "date":       today.isoformat(),
        "draw_id":    latest_draw_id,
        "game":       lottery,
        "strategy":   strategy,
        "confidence": confidence,
        "entropy":    entropy,
        "stable":     stable,
        "chi2_p":     chi2_p,
        "moon_phase": moon_name,
        "moon_ratio": round(moon_ratio, 4),
        "solar_kp":   solar_kp,
        "cluster":    cluster_id,
    }

    # ── Write ─────────────────────────────────────────────────────────────────
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "jsonl":
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    elif fmt == "csv":
        is_new = not log_path.exists() or log_path.stat().st_size == 0
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(record.keys()))
            if is_new:
                writer.writeheader()
            writer.writerow(record)

    elif fmt == "md":
        is_new = not log_path.exists() or log_path.stat().st_size == 0
        if is_new:
            header = (
                "| Date | Draw | Confidence | Entropy | Stable | Chi²p | Moon | Kp | Cluster |\n"
                "|------|------|-----------|---------|--------|-------|------|----|---------|\n"
            )
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(header)
        row = (
            f"| {record['date']} | {record['draw_id']} | "
            f"{record['confidence'] or '—':.4f} | "
            f"{record['entropy'] or '—':.4f} | "
            f"{'✓' if record['stable'] else '✗' if record['stable'] is not None else '—'} | "
            f"{record['chi2_p'] or '—':.4f} | "
            f"{record['moon_phase']} | "
            f"{record['solar_kp'] or '—'} | "
            f"{'C' + str(record['cluster']) if record['cluster'] is not None else '—'} |\n"
        )
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(row)
    else:
        console.print(f"[red]Unknown format '{fmt}'. Use: jsonl | csv | md[/red]")
        raise typer.Exit(1)

    if not quiet:
        _stab_str = ("STABLE" if stable else "NOISY") if stable is not None else "UNKNOWN"
        console.print(
            f"  [green]✔[/green] Appended to [cyan]{log_path}[/cyan]\n"
            f"  draw={latest_draw_id}  conf={confidence or '—'}  "
            f"entropy={entropy or '—'}  stable={_stab_str}  "
            f"moon={moon_name}  kp={solar_kp or '—'}  cluster={'C' + str(cluster_id) if cluster_id is not None else '—'}"
        )


def log_view(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery game")] = None,
    output: Annotated[str, typer.Option("--output", "-o",
        help="Log file to read")] = "",
    last: Annotated[int, typer.Option("--last", "-n",
        help="Show only the last N records")] = 10,
) -> None:
    """📋 View recent entries from the daily log.

    Example: lottery log-view br/lotofacil
             lottery log-view --last 30
             lottery log-view br/lotofacil --last 7
    """
    from rich.table import Table as _Table

    log_path = Path(output) if output else _DEFAULT_LOG
    if not log_path.exists():
        console.print(f"[yellow]No log found at {log_path}. Run `lottery log` first.[/yellow]")
        raise typer.Exit(0)

    if log_path.suffix == ".jsonl":
        records = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    else:
        console.print("[yellow]log-view only supports .jsonl files.[/yellow]")
        raise typer.Exit(1)

    if lottery:
        records = [r for r in records if r.get("game") == lottery]

    records = records[-last:]

    table = _Table(header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("Date")
    table.add_column("Draw",    justify="right")
    table.add_column("Conf",    justify="right")
    table.add_column("Entropy", justify="right")
    table.add_column("Stable",  justify="center")
    table.add_column("Chi²p",   justify="right")
    table.add_column("Moon Phase")
    table.add_column("Kp",      justify="right")
    table.add_column("Cluster", justify="center")

    for r in records:
        stab = r.get("stable")
        stab_str = "[green]✓[/green]" if stab else "[red]✗[/red]" if stab is not None else "—"
        c = r.get("cluster")
        table.add_row(
            r.get("date", "?"),
            str(r.get("draw_id", "?")),
            f"{r['confidence']:.4f}" if r.get("confidence") is not None else "—",
            f"{r['entropy']:.4f}"    if r.get("entropy")    is not None else "—",
            stab_str,
            f"{r['chi2_p']:.4f}"    if r.get("chi2_p")     is not None else "—",
            r.get("moon_phase", "—"),
            str(r["solar_kp"])       if r.get("solar_kp")   is not None else "—",
            f"C{c}"                  if c is not None else "—",
        )

    console.print(table)
    console.print(f"[dim]{len(records)} records from {log_path}[/dim]")
