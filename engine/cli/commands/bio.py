"""
Bioinformatics Analysis Command 🔬
=================================
Analyzes lottery draws as if they were biological samples/sequences.
Uses scikit-bio for diversity and phylogenetic analysis.
"""

from __future__ import annotations

import numpy as np
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import skbio
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.tree import nj
from skbio import DistanceMatrix, TreeNode

from engine.cli.utils import get_adapter

console = Console()

def bio(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 30,
    metric: Annotated[str, typer.Option("--metric", "-m", help="Beta-diversity metric (jaccard, braycurtis)")] = "jaccard",
) -> None:
    """🔬 Biological analysis of lottery draws using scikit-bio.

    Treats each draw as a biological sample and its numbers as species.
    Calculates Alpha Diversity (Evenness), Beta Diversity (Distance),
    and constructs a Phylogenetic Tree (NJ) of recent draws.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws)
    
    if window.empty:
        console.print("[red]No data available for analysis.[/red]")
        return

    # --- 1. Prepare Data for skbio ---
    # We create a community matrix: draws as rows, all possible numbers as columns (species)
    all_numbers = list(range(lo, hi + 1))
    num_to_idx = {n: i for i, n in enumerate(all_numbers)}
    
    matrix = np.zeros((n_draws, len(all_numbers)), dtype=int)
    draw_ids = []
    
    for i, row in enumerate(window.itertuples()):
        draw_ids.append(f"D{row.draw_id}")
        for n in row.numbers:
            if n in num_to_idx:
                matrix[i, num_to_idx[n]] = 1

    # --- 2. Alpha Diversity (Evenness) ---
    # For each draw (though in a single draw it's always 1 of each, 
    # so we'll look at the *aggregate* population to see overall richness/evenness)
    
    aggregate_counts = matrix.sum(axis=0)
    
    shannon = skbio.diversity.alpha.shannon(aggregate_counts)
    simpson = skbio.diversity.alpha.simpson(aggregate_counts)
    richness = skbio.diversity.alpha.observed_otus(aggregate_counts)
    
    # --- 3. Beta Diversity (Distances) ---
    # Distances between individual draws
    try:
        dm = beta_diversity(metric, matrix, draw_ids)
    except Exception as e:
        console.print(f"[red]Error calculating beta diversity: {e}[/red]")
        # Fallback to Jaccard if metric failed
        dm = beta_diversity("jaccard", matrix, draw_ids)

    # --- 4. Phylogeny (NJ Tree) ---
    # Construct a tree from the distance matrix
    tree = nj(dm)
    # Root the tree at the oldest draw in the window for better visualization
    # tree.root_at_midpoint() # Midpoint is usually safe
    
    # --- 5. Display Results ---
    console.rule(f"[bold green]🔬 BIOLOGICAL ANALYSIS — {rules.name}[/bold green]")
    
    # Alpha Table
    alpha_tbl = Table(title="Population Alpha Diversity (Richness & Evenness)", box=None)
    alpha_tbl.add_column("Metric", style="cyan")
    alpha_tbl.add_column("Value", justify="right", style="bold yellow")
    alpha_tbl.add_column("Interpretation", style="dim")
    
    alpha_tbl.add_row("Richness (Observed)", f"{richness}", "How many unique numbers appeared")
    alpha_tbl.add_row("Shannon Entropy", f"{shannon:.3f}", "Uncertainty / Information content")
    alpha_tbl.add_row("Simpson Index", f"{simpson:.3f}", "Probability that two picks are the same")
    
    console.print(alpha_tbl)
    
    # Tree Panel
    # TreeNode.ascii_art() provides a nice text tree
    tree_art = tree.ascii_art()
    console.print(Panel(tree_art, title="🌳 Evolutionary Tree of Draws (NJ)", border_style="green"))
    
    # Insights
    console.print("\n[bold]Insights:[/bold]")
    console.print(f"• Analyzing the last [cyan]{n_draws}[/cyan] draws.")
    console.print(f"• The tree clades show groups of draws that are structurally related.")
    console.print(f"• Average distance between draws ({metric}): [yellow]{dm.data.mean():.3f}[/yellow]")

if __name__ == "__main__":
    # For testing
    bio("br/lotofacil", draws=10)
