"""
Elite PDF Report Command 📄
===========================
Generates a high-fidelity, professional PDF analysis report for a lottery.
Includes executive summaries, strategy breakdowns, and high-quality charts.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Optional, List
from datetime import datetime

import typer
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from fpdf import FPDF
from rich.console import Console

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

class EliteReport(FPDF):
    def header(self):
        # Logo placeholder
        self.set_font('Arial', 'B', 15)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'PREDICTION ENGINE — ELITE REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(127, 140, 141)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(236, 240, 241)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def report_elite(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output PDF path")] = None,
) -> None:
    """📄 Generate a professional PDF diagnostic report for a lottery.

    Compiles historical trends, spatial heatmaps, and multi-strategy 
    consensus into a high-fidelity document suitable for executive review.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    
    if output is None:
        output = f"data/relatorio_elite_{lottery.replace('/', '_')}.pdf"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    temp_dir = Path("data/cache/temp_charts")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with console.status(f"[bold cyan]Generating Elite Report for {rules.name}..."):
        # 1. Generate Charts
        plt.style.use('seaborn-v0_8-muted')
        
        # --- Chart 1: Frequency ---
        plt.figure(figsize=(10, 5))
        all_nums = [n for row in df.tail(100).itertuples() for n in row.numbers]
        from collections import Counter
        counts = Counter(all_nums)
        nums, freq = zip(*sorted(counts.items()))
        
        plt.bar(nums, freq, color='#3498db')
        plt.title(f'Number Frequency (Last 100 Draws) — {rules.name}')
        plt.xlabel('Number')
        plt.ylabel('Hits')
        freq_path = temp_dir / f"freq_{rules.name}.png"
        plt.savefig(freq_path, dpi=300)
        plt.close()
        
        # --- Chart 2: Spatial Heatmap ---
        width = rules.board_cols or 10
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        height = (pool_size + width - 1) // width
        grid = np.zeros((height, width))
        
        for n, f in counts.items():
            r = (n - 1) // width
            c = (n - 1) % width
            if r < height and c < width:
                grid[r, c] = f
                
        plt.figure(figsize=(8, 6))
        sns.heatmap(grid, annot=True, fmt=".0f", cmap="YlOrRd", cbar=False)
        plt.title(f'Spatial Distribution (Grid Map) — {rules.name}')
        heat_path = temp_dir / f"heat_{rules.name}.png"
        plt.savefig(heat_path, dpi=300)
        plt.close()

        # 2. Build PDF
        pdf = EliteReport()
        pdf.add_page()
        
        # --- Executive Summary ---
        pdf.chapter_title("1. EXECUTIVE SUMMARY")
        summary = (
            f"This report presents a comprehensive statistical and algorithmic analysis of the {rules.name} lottery. "
            f"The analysis is based on a primary window of the last 100 draws, identifying significant regimes, "
            f"spatial clusters, and emerging numerical signals.\n\n"
            f"Key metrics for {rules.name}:\n"
            f"• Field Size: {rules.pick_count}/{rules.pool_size}\n"
            f"• Ticket Price: {rules.ticket_price} {rules.currency}\n"
            f"• Sample Size: {len(df)} draws processed."
        )
        pdf.chapter_body(summary)
        
        # --- Frequency Analysis ---
        pdf.chapter_title("2. FREQUENCY SPECTRUM")
        pdf.image(str(freq_path), x=10, w=190)
        pdf.ln(5)
        pdf.chapter_body(
            "The bar chart above illustrates the hit distribution across the entire number pool. "
            "Model stability is measured by the variance in hit rates across the window."
        )
        
        # --- Spatial Analysis ---
        pdf.add_page()
        pdf.chapter_title("3. SPATIAL GRID ANALYSIS")
        pdf.image(str(heat_path), x=30, w=150)
        pdf.ln(5)
        pdf.chapter_body(
            "The spatial heatmap displays the physical density of winning numbers on the bet slip. "
            "Darker regions indicate 'Hot Zones' where clustering is historically persistent. "
            "Significant voids represent areas of high entropy potential."
        )
        
        # --- Strategy Consensus ---
        pdf.chapter_title("4. STRATEGIC CONSENSUS")
        
        cons_strats = ["weighted", "bayesian", "markov", "hurst_memory"]
        consensus_lines = []
        for s_name in cons_strats:
            try:
                strat = get_strategy(s_name)
                res = strat.suggest(df, rules, count=1, history_limit=100)
                ticket = ", ".join(map(str, res.tickets[0]))
                consensus_lines.append(f"• {s_name.upper()}: [{ticket}] (Confidence: {res.confidence:.2f})")
            except:
                continue
        
        pdf.chapter_body("\n".join(consensus_lines))
        
        pdf.output(output)

    console.print(f"\n[bold green]✅ Elite Report generated successfully:[/bold green] [cyan]{output}[/cyan]")

if __name__ == "__main__":
    report_elite("br/lotofacil")
