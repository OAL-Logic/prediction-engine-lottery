"""
Cluster Command 🔬
=================
Unsupervised clustering of historical draw data (K-Means or DBSCAN).

Finds natural groupings in number co-occurrence without any labels.
Use this to check whether "esoteric windows" align with statistical clusters —
if they do, you have a High-Probability Node rather than a random occurrence.

Requires: pip install 'lottery-engine[ml]'  (scikit-learn)
"""

from __future__ import annotations

from collections import Counter
from typing import Annotated, Optional
from datetime import date as _date

import typer
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary

console = Console()


def cluster(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil) [Required]")],
    method: Annotated[str, typer.Option("--method", "-m", help="kmeans | dbscan")] = "kmeans",
    k: Annotated[int, typer.Option("--k", "-k", help="Number of clusters (for k-means)")] = 5,
    window: Annotated[Optional[int], typer.Option("--limit", "-L", help="Use only the N most recent draws")] = None,
    eps: Annotated[float, typer.Option("--eps", help="DBSCAN neighbourhood radius")] = 3.0,
    min_samples: Annotated[int, typer.Option("--min-samples", help="DBSCAN minimum cluster size")] = 5,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append results to this .md file")] = None,
) -> None:
    """🔬 Unsupervised clustering of historical draw patterns.

    Builds a number co-occurrence feature matrix and groups draws into clusters.
    Stable clusters across different windows suggest repeating structural patterns.

    Example: lottery cluster br/lotofacil --method kmeans --k 5
    """
    try:
        from sklearn.cluster import KMeans, DBSCAN  # type: ignore[import-untyped]
        from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
    except ImportError:
        console.print("[red]scikit-learn is required: pip install 'lottery-engine\\[ml\\]'[/red]")
        raise typer.Exit(1)

    if method not in ["kmeans", "dbscan"]:
        console.print(f"[red]Unknown method '{method}'. Use: kmeans | dbscan[/red]")
        raise typer.Exit(1)

    print_command_summary("cluster", lottery, method=method, k=k, window=window)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch(limit=window)

    if len(df) < 20:
        console.print("[red]Need at least 20 draws for clustering.[/red]")
        raise typer.Exit(1)

    lo, hi = adapter.rules.number_range
    pool = list(range(lo, hi + 1))
    pool_size = len(pool)

    # ── Feature matrix: presence of each number + structural features ────────
    X = np.zeros((len(df), pool_size), dtype=float)
    for i, nums in enumerate(df["numbers"]):
        for n in nums:
            if lo <= n <= hi:
                X[i, n - lo] = 1.0

    sums     = np.array([sum(d) for d in df["numbers"]], dtype=float)
    parities = np.array([
        sum(1 for n in d if n % 2 == 0) / len(d) for d in df["numbers"]
    ], dtype=float)

    X_aug = np.column_stack([X, sums / (sums.max() or 1.0), parities])

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X_aug)

    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]  method=[bold]{method.upper()}[/bold]  "
        f"{len(df)} draws  pool={pool_size} numbers",
        title="🔬 Clustering Analysis",
    ))

    # ── Fit model ─────────────────────────────────────────────────────────────
    if method == "kmeans":
        model  = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        console.print(f"\n[bold]K-Means inertia:[/bold] {model.inertia_:.2f} [dim](lower = tighter clusters)[/dim]")

    elif method == "dbscan":
        model  = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(X_scaled)
        k      = len(set(labels)) - (1 if -1 in labels else 0)
        noise  = int((labels == -1).sum())
        console.print(f"\n[bold]DBSCAN found {k} clusters[/bold], {noise} noise draws")

    else:
        console.print(f"[red]Unknown method '{method}'. Use: kmeans | dbscan[/red]")
        raise typer.Exit(1)

    # ── Profile each cluster ──────────────────────────────────────────────────
    cluster_ids = sorted(c for c in set(labels) if c != -1)
    profiles: dict[int, dict] = {}

    for c_id in cluster_ids:
        mask         = labels == c_id
        cluster_nums = df[mask]["numbers"].tolist()
        all_nums     = [n for draw in cluster_nums for n in draw]
        counts       = Counter(all_nums)
        top_nums     = [n for n, _ in counts.most_common(10)]
        avg_sum      = float(np.mean([sum(d) for d in cluster_nums]))
        avg_even     = float(np.mean([sum(1 for n in d if n % 2 == 0) / len(d) for d in cluster_nums]))
        profiles[c_id] = {
            "size": int(mask.sum()),
            "top_nums": top_nums,
            "avg_sum": avg_sum,
            "avg_even_ratio": avg_even,
        }

    table = Table(title="Cluster Profiles", header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Cluster",    style="cyan")
    table.add_column("Size",       justify="right")
    table.add_column("Top numbers (most frequent inside cluster)")
    table.add_column("Avg sum",    justify="right")
    table.add_column("Even ratio", justify="right")

    for c_id, p in profiles.items():
        table.add_row(
            f"C{c_id}",
            str(p["size"]),
            str(p["top_nums"]),
            f"{p['avg_sum']:.1f}",
            f"{p['avg_even_ratio']:.0%}",
        )

    console.print(table)

    last_label = int(labels[-1])
    if last_label != -1:
        p = profiles[last_label]
        top5_str = ", ".join(map(str, p['top_nums'][:5]))
        console.print(
            f"\n[bold]Latest draw[/bold] → [cyan]Cluster {last_label}[/cyan]  "
            f"size={p['size']}  avg_sum={p['avg_sum']:.1f}  "
            f"top5={top5_str}"
        )
    else:
        console.print("\n[yellow]Latest draw classified as noise (DBSCAN)[/yellow]")

    if export_md:
        _export_md(export_md, adapter.rules.name, method, k, profiles, last_label, len(df))
        console.print(f"\n[green]✔ Pattern log written to {export_md}[/green]")


def _export_md(
    path: str,
    game: str,
    method: str,
    k: int,
    profiles: dict,
    last_cluster: int,
    n_draws: int,
) -> None:
    rows = "\n".join(
        f"| C{c_id} | {p['size']} | {p['top_nums']} | {p['avg_sum']:.1f} | {p['avg_even_ratio']:.0%} |"
        for c_id, p in profiles.items()
    )

    content = f"""---
type: pattern-log
game: {game}
method: {method}
clusters: {k}
n_draws: {n_draws}
date: {_date.today().isoformat()}
latest_draw_cluster: {last_cluster}
tags: [prediction-engine, clustering, pattern-log]
---

# Cluster Analysis: {game}

**Method:** {method.upper()} | **Clusters:** {k} | **Draws analysed:** {n_draws}

## Cluster Profiles

| Cluster | Size | Top Numbers | Avg Sum | Even Ratio |
|---------|------|-------------|---------|------------|
{rows}

## Notes

- Latest draw belongs to **Cluster {last_cluster}**
- Top numbers are the most frequently drawn *within* that cluster
- Cross-reference with esoteric markers (lunar phase, solar K-index, etc.)
  using DataviewJS to test whether esoteric windows align with clusters

> If a specific esoteric cycle consistently corresponds to draws in Cluster X,
> you have found a High-Probability Node rather than a random occurrence.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
