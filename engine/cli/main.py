"""
lottery-engine CLI 🚀
====================
Main entry point for the modular CLI.
"""

from __future__ import annotations

import logging
import sys
import os
import signal
from typing import Annotated, Optional
from pathlib import Path

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

# --- UI Helpers ---

def _timeout_handler(signum, frame):
    """Global execution guard."""
    Console().print("\n[bold red]☠️ EXECUTION TIMEOUT:[/bold red] Script terminated after 30 minutes of execution.")
    sys.exit(1)

# Set 30 minute alarm (1800 seconds)
if os.name != 'nt': # signal.alarm is not available on Windows
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(1800)

# --- Command Panel Constants ---
PANEL_PRIMARY   = "⭐ Primary Golden Path"
PANEL_ANALYTICS = "🔬 Analytics & Diagnostics"
PANEL_BETTING   = "🎟️ Betting & Tactical Tools"
PANEL_MONITOR   = "📓 Monitoring & Logs"
PANEL_SYSTEM    = "⚙️ System & Optimization"
PANEL_VERIFY    = "✅ Verification & Tools"

# --- UI Helpers ---

def _get_header():
    """Shared visual header."""
    return Text.from_markup(
        "[yellow on black][bold] 🏛️  LOTTERY ENGINE: THE ULTIMATE GUIDE [/bold][/yellow on black]\n"
        "[dim]High-precision statistical forecasting and environmental resonance engine. Demystifying complex numbers for the player who takes the game into another dimension. [/dim]\n"
    )

def _get_strategy_legend(compact: bool = False):
    """Dynamically groups and displays all strategy tiers from the registry."""
    from engine.strategies import list_strategies
    from collections import defaultdict
    
    all_strategies = list_strategies()
    
    tiers = defaultdict(list)
    for s in all_strategies:
        tiers[s["tier"]].append(s["name"])
        
    tier_emojis = {
        "statistical": "📈",
        "ml": "🤖",
        "deep": "🧠",
        "fun": "✨",
        "chaos": "🌪️",
        "esoteric": "🔮",
        "financial": "💸",
        "default": "🎯"
    }

    # Sort tiers: Put 'Primary' ones first, then alphabetical
    priority = ["statistical", "ml", "deep", "fun"]
    sorted_tier_keys = sorted(
        tiers.keys(), 
        key=lambda k: (priority.index(k) if k in priority else 99, k)
    )

    if compact:
        output = ["\n[bold underline]🧠 STRATEGY TIERS[/]"]
        for tier in sorted_tier_keys:
            if tier not in tiers: continue
            emoji = tier_emojis.get(tier, "⚡")
            names = ", ".join(sorted(tiers[tier]))
            output.append(f" {emoji} [bold]{tier.upper()}:[/] [dim]{names}[/]")
        
        return "\n".join(output)

    # High-fidelity Rich Table for the 'help' command
    table = Table(box=None, padding=(0, 2), show_header=False, expand=True)
    table.add_column("Tier", style="bold yellow", width=20)
    table.add_column("Strategies", style="italic dim")

    for tier in sorted_tier_keys:
        emoji = tier_emojis.get(tier, "⚡")
        strat_names = sorted(tiers[tier])
        strat_grid = Columns(strat_names, equal=True, expand=True)
        table.add_row(f"{emoji} {tier.upper()}", strat_grid)

    return Panel(table, title="[bold white]🧠 STRATEGY ALGORITHMS[/bold white]", border_style="bright_black", expand=False)

def _get_help_panel() -> Panel:
    """Generate the high-fidelity structured TUI help panel."""
    from typer.main import get_command
    click_app = get_command(app)
    
    def make_cat_section(title: str, commands: list):
        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2))
        table.add_column("Command", style="bold cyan", width=20)
        table.add_column("Description", style="white")

        for name in commands:
            cmd = click_app.commands.get(name)
            if not cmd: continue
            help_text = (cmd.help or "").split("\n")[0].strip()
            table.add_row(name, help_text)
            
        return Group(
            f"\n[bold reverse yellow] {title} [/bold reverse yellow]",
            table
        )

    header = _get_header()
    
    segments = [
        make_cat_section(PANEL_PRIMARY, ["menu", "wizard", "wizard-pro", "fetch", "suggest", "analyze", "backtest", "backtest-viz", "strategies", "docs"]),
        make_cat_section(PANEL_ANALYTICS, [
            "dashboard", "trend", "board", "scan", "cluster", "signal", "detect-patterns", "entropy-scan", 
            "variance-report", "synergy-map", "ticket-dna", "draw-fingerprint", "markov-table", "outlier-draws",
            "calendar-effect", "bonus-ball", "frequency-band", "combo-rank", "draw-clock", "number-heat", 
            "number-timeline", "momentum-check", "gap-forecast", "pair-analysis", "draw-summary", 
            "history-scan", "pool-stats", "rank-numbers", "streak-report", "leaderboard", "fractal-scan", "sync-check",
            "report-elite", "spectral-3d", "hyper-explorer", "synergy-graph", "space-weather", "global-bench"
            ]),
        make_cat_section(PANEL_BETTING, [
            "wheel", "genetic-wheel", "portfolio", "global-portfolio", "hedge", "auto-hedge", "multi-ticket", "prize-ev", "quick", "next", "forecast", "picks", 
            "suggest-swaps", "party", "oracle", "deliberate", "bio", "resonance", "swarm", "risk", "savings", "simulate"
        ]),
        make_cat_section(PANEL_MONITOR, [

            "daily", "weekly", "report", "alert", "cold-streak-alert", "regime-history", "log", "log-view", 
            "log-export", "watchlist", "hitcheck"
        ]),
        make_cat_section(PANEL_SYSTEM, [
            "serve", "games", "odds", "daemon", "daemon-status", "optimize", "calibrate", "prune", "audit-data", "export", 
            "history", "compare-draws", "compare-strategies", "compare-bets", "stress-test", "tune"
        ]),
        make_cat_section(PANEL_VERIFY, [
            "check", "validate", "ticket-grade", "session", "calendar", "signature", "coverage-check"
        ]),
    ]
    
    full_content = Group(
        header,
        *segments,
        "\n",
        _get_strategy_legend(),
        "\n[dim]💡 [bold]TIP:[/] Use [bold]--detailed-help[/bold] for full parameter documentation.[/dim]"
    )

    return Panel(full_content, border_style="bright_black", padding=(1, 2))

# --- Application Configuration ---

app = typer.Typer(
    name="lottery",
    help="Unified lottery prediction system. Type `lottery help` for the command center.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    epilog="Type `lottery help` for the high-fidelity Command Center."
)

# --- PANEL_PRIMARY Commands ---

@app.command(name="help")
def help_cmd():
    """🏛️ View the high-fidelity command guide."""
    Console().print(_get_help_panel())

@app.command(rich_help_panel=PANEL_PRIMARY)
def fetch(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    limit: Annotated[Optional[int], typer.Option("--limit", "-L", help="Only fetch N most recent draws")] = None,
):
    """📡 Fetch and cache historical draw data for a lottery."""
    from engine.cli.commands.fetch import fetch as impl
    return impl(lottery, limit)

@app.command(rich_help_panel=PANEL_PRIMARY)
def analyze(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    module: Annotated[str, typer.Option("--module", "-m", help="frequency | deviation | correlation | dashboard | summary")] = "dashboard",
    limit: Annotated[Optional[int], typer.Option("--limit", "-n", help="Use only the N most recent draws")] = None,
    top: Annotated[int, typer.Option("--top", help="Number of items to show in tables")] = 10,
    view: Annotated[Optional[str], typer.Option("--view", help="Dashboard view (when module=dashboard): alerts | odd_even | primes | fibonacci | frame | multiples_3 | magic | repeated | complete")] = None,
):
    """📊 Run statistical analysis modules or a unified dashboard."""
    from engine.cli.commands.analyze import analyze as impl
    return impl(lottery, module, limit, top, view)

@app.command(rich_help_panel=PANEL_PRIMARY)
def suggest(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena) [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
                     help="Strategy name or comma-separated list. Run 'lottery strategies' for available options.\n\n"
                          "Statistical: markov | bayesian | weighted | monte_carlo |\n"
                          "             pattern | momentum | spectral | streak\n"
                          "ML:          logistic | random_forest | gradient_boost | knn\n"
                          "Ensemble:    voting:s1,s2 | prob_weighted:s1,s2 | hybrid:s1,s2\n"
                          "Deep:        transformer | lstm_gru | cnn_1d\n"
                          "Fun:         numerology | moon_phase | weather |\n"
                          "             biorhythm | fibonacci | zodiac\n"
                          "Other:       chaos  (pure random)")] = "weighted",
    count:       Annotated[int,   typer.Option("--count",   "-c", help="Number of tickets")] = 1,
    temperature: Annotated[float, typer.Option("--temp",    "-t", help="Sampling temperature (0=deterministic, 1=default, >1=noisy)")] = 1.0,
    limit:           Annotated[int | None, typer.Option("--limit", "-L", help="Use only the N most recent draws")] = None,
    top_scored:      Annotated[int,        typer.Option("--top-scored",      help="How many top-scored numbers to show after each ticket suggestion")] = 5,
    recent_matches:  Annotated[int,        typer.Option("--recent-matches",  help="Max recent matched draws to show in correlation metadata (moon_phase, weather)")] = 5,
    top_numbers:     Annotated[int,        typer.Option("--top-numbers",     help="Max top numbers to show in correlation metadata (moon_phase, weather)")] = 5,
    full_name:       Annotated[Optional[str], typer.Option("--full-name",    help="User full name for personalized numerology strategies")] = None,
    birth_date:      Annotated[Optional[str], typer.Option("--birth-date",   help="User birth date (YYYY-MM-DD) for personalized strategies")] = None,
    topic:           Annotated[Optional[str], typer.Option("--topic",        help="Intentional topic string for seeding randomness")] = None,
    adaptive_window: Annotated[bool,          typer.Option("--adaptive-window", help="Automatically pick optimal history window for the strategy")] = False,
    pool:            Annotated[Optional[str], typer.Option("--pool",         help="Constrain selection to these numbers (comma-separated list)")] = None,
    key:             Annotated[Optional[str], typer.Option("--key",          help="Include these numbers in every ticket (comma-separated list)")] = None,
    filters:         Annotated[Optional[str], typer.Option("--filters",      help="Apply structural filters (comma-separated names or 'all')")] = None,
    k_of_n:          Annotated[int,           typer.Option("--k-of-n",       help="Tolerance for harmony checks (accept if K of N filters pass)")] = 0,
    pick:            Annotated[Optional[int], typer.Option("--pick",         help="Override default pick count (e.g. play 7 numbers in a pick-6 game)")] = None,
    explain:         Annotated[bool,          typer.Option("--explain",       help="Show top-3 contributing features for each prediction")] = False,
    window_check:    Annotated[bool,          typer.Option("--window-check",  help="Abort with a warning if the current signal window is NOISE")] = False,
    filter_anomalies: Annotated[bool, typer.Option("--filter-anomalies", help="Automatically restrict generation to correct statistical pattern anomalies")] = False,
    kelly: Annotated[Optional[float], typer.Option("--kelly", help="Calculate optimal bet size using Kelly Criterion for this bankroll")] = None,
    chaos: Annotated[bool, typer.Option("--chaos", help="Enable Real-time Environmental Jitter (Solar/Seismic)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append suggest report to this .md file")] = None,
):
    """🎟️ Generate ticket suggestions using a specific prediction strategy."""
    from engine.cli.commands.suggest import suggest as impl
    return impl(lottery, strategy, count, temperature, limit, top_scored, recent_matches, top_numbers, full_name, birth_date, topic, adaptive_window, pool, key, filters, k_of_n, pick, explain, window_check, filter_anomalies, kelly, chaos, export_md)

@app.command(rich_help_panel=PANEL_PRIMARY)
def wizard():
    """🧙 Interactive wizard to guide you through lottery analysis and prediction."""
    from engine.cli.commands.wizard import wizard as impl
    return impl()

@app.command(name="wizard-pro", rich_help_panel=PANEL_PRIMARY)
def wizard_pro():
    """🧙‍♂️ Expert Decision Support Wizard for pro configuration."""
    from engine.cli.commands.wizard_pro import wizard_pro as impl
    return impl()

@app.command(rich_help_panel=PANEL_PRIMARY)
def backtest(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draw_id: Annotated[Optional[str], typer.Argument(help="Draw number(s), range (e.g. 2990-2999), or comma-separated list to test")] = None,
    prev:    Annotated[Optional[str], typer.Option("--prev", "-p", help="Relative index or range (e.g. 1, 1-5, 1,2,5) from latest")] = None,
    strategy: Annotated[Optional[str], typer.Option("--strategy", "-s",
                     help="Strategy name(s). Supports comma-separated list (e.g. 'weighted,markov') or 'all'.")] = None,
    numbers: Annotated[Optional[str], typer.Option("--numbers", "-n", help="Specific numbers to check against the draw. E.g. '4 12 23 35 47 60'")] = None,
    count: Annotated[int, typer.Option("--count", "-c", help="Number of tickets to generate (if using --strategy)")] = 1,
    temperature: Annotated[float, typer.Option("--temp", "-t", help="Sampling temperature (if using --strategy)")] = 0.0,
    limit: Annotated[Optional[int], typer.Option("--limit", "-L", help="History limit (recency bias): only use the most recent N draws for scoring")] = None,
    summary: Annotated[bool, typer.Option("--summary/--no-summary", help="Show a summary report at the end when testing multiple draws")] = True,
    show_map: Annotated[bool, typer.Option("--map", "-m", help="Show board heatmap for each target draw")] = False,
    config: Annotated[Optional[Path], typer.Option("--config", help="Path to a YAML configuration file for batch strategy testing")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append backtest report to this .md file")] = None,
):
    """🔬 Evaluate one or more strategies against one or more historical draws."""
    from engine.cli.commands.backtest import backtest as impl
    return impl(lottery, draw_id, prev, strategy, numbers, count, temperature, limit, summary, show_map, config, export_md)

@app.command(name="backtest-viz", rich_help_panel=PANEL_PRIMARY)
def backtest_viz(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to visualize")] = "weighted",
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of draws to backtest")] = 10,
    limit: Annotated[int, typer.Option("--limit", "-L", help="History window for each step")] = 100,
):
    """📉 Visual Confusion Heatmap of strategy performance over time."""
    from engine.cli.commands.backtest_viz import backtest_viz as impl
    return impl(lottery, strategy, draws, limit)

@app.command(rich_help_panel=PANEL_PRIMARY)
def docs(
    topic: Annotated[str, typer.Argument(
        help="Topic: all | lotteries | analysis | strategies | temperature | ensemble | deep | fun"
    )] = "all",
):
    """📚 View the comprehensive TUI documentation and strategy guides."""
    from engine.cli.commands.docs import docs as impl
    return impl(topic)

@app.command(name="strategies", rich_help_panel=PANEL_PRIMARY)
def strategies_cmd() -> None:
    """🧠 List all available prediction strategies."""
    from engine.strategies import list_strategies, bootstrap_registry
    bootstrap_registry()
    table = Table(title="Available Strategies", box=None)
    table.add_column("Name", style="bold cyan")
    table.add_column("Tier")
    table.add_column("Description")
    for s in list_strategies():
        table.add_row(s["name"], s["tier"], s["description"])
    Console().print(table)

# --- PANEL_ANALYTICS Commands ---

@app.command(rich_help_panel=PANEL_ANALYTICS)
def trend(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery filter (e.g. br/lotofacil) — omit for all")] = None,
    log_file: Annotated[str, typer.Option("--log", "-l", help="JSONL log file path")] = "",
    days: Annotated[int, typer.Option("--days", "-d", help="Number of days to show")] = 14,
    metric: Annotated[Optional[str], typer.Option("--metric", "-m", help="Single metric: confidence|entropy|chi2_p|moon_ratio|solar_kp")] = None,
    no_alerts: Annotated[bool, typer.Option("--no-alerts", help="Suppress alert panel")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append trend report to this .md file")] = None,
):
    """📈 View multi-day diagnostic trends for one or all lotteries."""
    from engine.cli.commands.trend import trend as impl
    return impl(lottery, log_file, days, metric, no_alerts, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def dashboard(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Analysis window (last N draws)")] = 100,
    view:    Annotated[Optional[str], typer.Option("--view", "-V", help="View: alerts | odd_even | primes | fibonacci | frame | multiples_3 | magic | repeated | complete")] = "alerts",
):
    """🖥️ High-fidelity Terminal Dashboard with real-time multi-panel analysis."""
    from engine.cli.commands.dashboard import dashboard as impl
    return impl(lottery, limit, view)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def board(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    view: Annotated[str, typer.Option("--view", "-v", help="heatmap | balance")] = "heatmap",
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Use only the N most recent draws")] = 20,
    numbers: Annotated[Optional[str], typer.Option("--numbers", "-n", help="Mark these numbers on the board (e.g. '1 13 32')")] = None,
    cols:    Annotated[Optional[int], typer.Option("--cols", "-C", help="Override number of columns in the grid")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append board analytics report to this .md file")] = None,
):
    """🎲 Visual Board Heatmap — see the distribution of recent draws."""
    from engine.cli.commands.board import board as impl
    return impl(lottery, view, limit, numbers, cols, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil) [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Primary strategy for signal and discrimination checks")] = "bayesian",
    window: Annotated[int, typer.Option("--limit", "-L", help="Rolling window size for stability check")] = 50,
    auto_suggest: Annotated[bool, typer.Option("--suggest/--no-suggest", help="Auto-generate a ticket if the scan verdict is GO")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append condition log to this .md file")] = None,
):
    """📡 Multi-layer GO/NO-GO signal scanner."""
    from engine.cli.commands.scan import scan as impl
    return impl(lottery, strategy, window, auto_suggest, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def cluster(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil) [Required]")],
    method: Annotated[str, typer.Option("--method", "-m", help="kmeans | dbscan")] = "kmeans",
    k: Annotated[int, typer.Option("--k", "-k", help="Number of clusters (for k-means)")] = 5,
    window: Annotated[Optional[int], typer.Option("--limit", "-L", help="Use only the N most recent draws")] = None,
    eps: Annotated[float, typer.Option("--eps", help="DBSCAN neighbourhood radius")] = 3.0,
    min_samples: Annotated[int, typer.Option("--min-samples", help="DBSCAN minimum cluster size")] = 5,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append results to this .md file")] = None,
):
    """🧬 Cluster historical draws to find structural regimes."""
    from engine.cli.commands.cluster import cluster as impl
    return impl(lottery, method, k, window, eps, min_samples, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def signal(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy name")] = "weighted",
    window: Annotated[int, typer.Option("--limit", "-L", help="Rolling window size in draws")] = 50,
    step: Annotated[int, typer.Option("--step", help="Step between windows")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export pattern log to this .md file")] = None,
):
    """📡 Signal-to-Noise analysis for a specific strategy."""
    from engine.cli.commands.signal import signal as impl
    return impl(lottery, strategy, window, step, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def detect_patterns(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    esoteric: Annotated[str, typer.Option("--esoteric", "-e", help="Overlay type: cyclical | lunar | solar | all")] = "cyclical",
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy whose stability windows are analysed")] = "weighted",
    threshold: Annotated[float, typer.Option("--threshold", "-t", help="Correlation threshold to flag a pattern")] = 0.15,
    window: Annotated[int, typer.Option("--limit", "-L", help="Rolling window size in draws")] = 50,
    step: Annotated[int, typer.Option("--step", help="Step between windows")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export pattern log to this .md file")] = None,
):
    """🔍 Search for environmental correlations (Solar/Lunar/Cyclical)."""
    from engine.cli.commands.detect_patterns import detect_patterns as impl
    return impl(lottery, esoteric, strategy, threshold, window, step, export_md)

@app.command(rich_help_panel=PANEL_ANALYTICS)
def entropy_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    window: Annotated[int, typer.Option("--limit", "-L", help="Draws per rolling window")] = 30,
    windows: Annotated[int, typer.Option("--windows", "-k", help="Number of windows to compute (0 = all)")] = 12,
    baseline_draws: Annotated[int, typer.Option("--baseline", help="Draws used to compute baseline entropy mean/std")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append entropy scan report to this .md file")] = None,
):
    """🔬 Shannon entropy analysis of draw distribution over rolling windows."""
    from engine.cli.commands.entropy_scan import entropy_scan as impl
    return impl(lottery, window, windows, baseline_draws, export_md)

@app.command(name="variance-report", rich_help_panel=PANEL_ANALYTICS)
def variance_report(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyse")] = 100,
    rolling: Annotated[int, typer.Option("--rolling", "-r", help="Window size for rolling variance trend")] = 20,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append variance report to this .md file")] = None,
):
    """📉 Volatility regime analysis — how predictable is the draw process?"""
    from engine.cli.commands.variance_report import variance_report as impl
    return impl(lottery, draws, rolling, export_md)

@app.command(name="synergy-map", rich_help_panel=PANEL_ANALYTICS)
def synergy_map(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    ticket:  Annotated[Optional[str], typer.Argument(help="Space-separated ticket numbers (quoted)")] = None,
    draws:   Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to analyse")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append synergy report to this .md file")] = None,
    from_stdin: Annotated[bool, typer.Option("--from-stdin", help="Read tickets from stdin")] = False,
):
    """🕸️ Pairwise co-occurrence lift matrix for a given ticket."""
    from engine.cli.commands.synergy_map import synergy_map as impl
    return impl(lottery, ticket, draws, export_md, from_stdin)

@app.command(name="ticket-dna", rich_help_panel=PANEL_ANALYTICS)
def ticket_dna(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    ticket:  Annotated[Optional[str], typer.Argument(help="Space-separated ticket numbers (quoted)")] = None,
    draws:   Annotated[int, typer.Option("--draws", "-n", help="Historical draws used as population")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append DNA report to this .md file")] = None,
    from_stdin: Annotated[bool, typer.Option("--from-stdin", help="Read tickets from stdin")] = False,
):
    """🧬 Structural fingerprint of a ticket vs historical draw population."""
    from engine.cli.commands.ticket_dna import ticket_dna as impl
    return impl(lottery, ticket, draws, export_md, from_stdin)

@app.command(name="draw-fingerprint", rich_help_panel=PANEL_ANALYTICS)
def draw_fingerprint(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    similar_to: Annotated[Optional[str], typer.Option("--similar-to", "-S",
        help="Find draws similar to this ticket (space-separated numbers)")] = None,
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 200,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Number of draws to display")] = 15,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append fingerprint report to this .md file")] = None,
):
    """🧬 Find historical draws with similar structural characteristics."""
    from engine.cli.commands.draw_fingerprint import draw_fingerprint as impl
    return impl(lottery, similar_to, draws, top, export_md)

@app.command(name="markov-table", rich_help_panel=PANEL_ANALYTICS)
def markov_table(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    from_num: Annotated[Optional[int], typer.Option("--from", "-f",
        help="Show full transition row for this number")] = None,
    stationary: Annotated[bool, typer.Option("--stationary", "-S",
        help="Show stationary distribution instead")] = False,
    last_draw: Annotated[bool, typer.Option("--last-draw", "-l",
        help="Show transitions from the most recent draw")] = False,
    top: Annotated[int, typer.Option("--top", "-k",
        help="Top-K followers to show per number")] = 5,
    score_window: Annotated[int, typer.Option("--limit", "-L",
        help="Draws used to build the matrix")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append Markov table report to this .md file")] = None,
):
    """📊 View the Markov transition matrix for pool numbers."""
    from engine.cli.commands.markov_table import markov_table as impl
    return impl(lottery, from_num, stationary, last_draw, top, score_window, export_md)

@app.command(name="outlier-draws", rich_help_panel=PANEL_ANALYTICS)
def outlier_draws(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    threshold: Annotated[float, typer.Option("--threshold", "-t",
        help="Composite z-score threshold for flagging")] = 2.0,
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 300,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Number of top outliers to display")] = 15,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append outlier report to this .md file")] = None,
):
    """⚠️ Identify historical draws with statistically improbable properties."""
    from engine.cli.commands.outlier_draws import outlier_draws as impl
    return impl(lottery, threshold, draws, top, export_md)

@app.command(name="calendar-effect", rich_help_panel=PANEL_ANALYTICS)
def calendar_effect(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 400,
    effect_threshold: Annotated[float, typer.Option("--effect", "-e",
        help="Cohen's d threshold to flag a notable effect")] = 0.5,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append calendar effect report to this .md file")] = None,
):
    """📆 Weekday and month-of-year bias detector for draw properties."""
    from engine.cli.commands.calendar_effect import calendar_effect as impl
    return impl(lottery, draws, effect_threshold, export_md)

@app.command(name="bonus-ball", rich_help_panel=PANEL_ANALYTICS)
def bonus_ball(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. us/powerball)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to analyse")] = 300,
    top: Annotated[int, typer.Option("--top",
        help="Show only the top N most-frequent bonus numbers")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append bonus-ball report to this .md file")] = None,
):
    """🎱 Isolated frequency and gap analysis for the bonus/special-pool ball."""
    from engine.cli.commands.bonus_ball import bonus_ball as impl
    return impl(lottery, draws, top, export_md)

@app.command(name="frequency-band", rich_help_panel=PANEL_ANALYTICS)
def frequency_band(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    short:   Annotated[int, typer.Option("--short", "-s", help="Short window (draws)")] = 15,
    mid:     Annotated[int, typer.Option("--mid", "-m", help="Mid window (draws)")] = 50,
    long:    Annotated[int, typer.Option("--long", "-l", help="Long window (draws)")] = 150,
    top:     Annotated[int, typer.Option("--top", "-N", help="Show only top-N by short-window rate (0 = all)")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append frequency band report to this .md file")] = None,
):
    """📡 Multi-horizon frequency tier classification for all pool numbers."""
    from engine.cli.commands.frequency_band import frequency_band as impl
    return impl(lottery, short, mid, long, top, export_md)

@app.command(name="combo-rank", rich_help_panel=PANEL_ANALYTICS)
def combo_rank(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyse")] = 200,
    top: Annotated[int, typer.Option("--top", help="Show only top-N profiles (0 = all 27)")] = 15,
    check: Annotated[Optional[str], typer.Option("--check", help="Space-separated ticket to classify and rank")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append combo rank report to this .md file")] = None,
):
    """🎯 Rank draw-property profiles (sum+parity+consecutive) by frequency."""
    from engine.cli.commands.combo_rank import combo_rank as impl
    return impl(lottery, draws, top, check, export_md)

@app.command(name="draw-clock", rich_help_panel=PANEL_ANALYTICS)
def draw_clock(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    top: Annotated[int, typer.Option("--top", "-N", help="Show only top-N most-due numbers (0 = all)")] = 15,
    window: Annotated[int, typer.Option("--limit", "-L", help="Draws to use for hit-rate estimation")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append draw clock report to this .md file")] = None,
):
    """⏰ Draws-until-next-hit countdown for every pool number."""
    from engine.cli.commands.draw_clock import draw_clock as impl
    return impl(lottery, top, window, export_md)

@app.command(name="number-heat", rich_help_panel=PANEL_ANALYTICS)
def number_heat(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to show in the grid")] = 30,
    sort_by: Annotated[str, typer.Option("--sort-by", help="Sort rows by: freq | streak | number")] = "freq",
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append heatmap to this .md file")] = None,
):
    """🌡️ Compact heatmap of all pool numbers × recent draws."""
    from engine.cli.commands.number_heat import number_heat as impl
    return impl(lottery, draws, sort_by, export_md)

@app.command(name="number-timeline", rich_help_panel=PANEL_ANALYTICS)
def number_timeline(
    lottery:  Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    number:   Annotated[int, typer.Argument(help="The pool number to inspect")],
    draws:    Annotated[int,  typer.Option("--draws", "-n", help="How many recent draws to analyse")] = 100,
    show_all: Annotated[bool, typer.Option("--all", "-a", help="Print every draw in the hit table, not just hits")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append timeline report to this .md file")] = None,
):
    """📈 Historical hit pattern for a single pool number."""
    from engine.cli.commands.number_timeline import number_timeline as impl
    return impl(lottery, number, draws, show_all, export_md)

@app.command(name="momentum-check", rich_help_panel=PANEL_ANALYTICS)
def momentum_check(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    short:   Annotated[int, typer.Option("--short", "-s", help="Short moving-average window (draws)")] = 10,
    long:    Annotated[int, typer.Option("--long", "-l", help="Long moving-average window (draws)")] = 30,
    top:     Annotated[int, typer.Option("--top", "-N", help="Show only top-N rising and bottom-N falling (0 = all)")] = 8,
    threshold: Annotated[float, typer.Option("--threshold", help="Signal threshold: SHORT must be > LONG × (1 + threshold)")] = 0.15,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append momentum report to this .md file")] = None,
):
    """📊 Moving-average momentum indicators for all pool numbers."""
    from engine.cli.commands.momentum_check import momentum_check as impl
    return impl(lottery, short, long, top, threshold, export_md)

@app.command(name="gap-forecast", rich_help_panel=PANEL_ANALYTICS)
def gap_forecast(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    top: Annotated[int, typer.Option("--top", "-N", help="Show only top-N most overdue (0 = all)")] = 10,
    min_draws: Annotated[int, typer.Option("--min-draws", help="Minimum draws required to compute gaps")] = 30,
    threshold: Annotated[float, typer.Option("--threshold", help="P(overdue) threshold to flag a number")] = 0.75,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append gap forecast report to this .md file")] = None,
):
    """🔮 Poisson-based overdue analysis for all pool numbers."""
    from engine.cli.commands.gap_forecast import gap_forecast as impl
    return impl(lottery, top, min_draws, threshold, export_md)

@app.command(name="pair-analysis", rich_help_panel=PANEL_ANALYTICS)
def pair_analysis(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to analyse")] = 100,
    top: Annotated[int, typer.Option("--top", "-t", help="How many pairs to show per table")] = 15,
    focus: Annotated[Optional[int], typer.Option("--focus", "-f", help="Show affinity partners for this specific number")] = None,
    min_count: Annotated[int, typer.Option("--min-count", help="Minimum co-occurrence count to include a pair")] = 2,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append pair analysis report to this .md file")] = None,
):
    """🔗 Co-occurrence frequency analysis for number pairs."""
    from engine.cli.commands.pair_analysis import pair_analysis as impl
    return impl(lottery, draws, top, focus, min_count, export_md)

@app.command(name="draw-summary", rich_help_panel=PANEL_ANALYTICS)
def draw_summary(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draw_id: Annotated[Optional[int], typer.Option("--id", "-i", help="Specific draw ID to analyse (default: latest)")] = None,
    context: Annotated[int, typer.Option("--context", "-c", help="How many prior draws to use as frequency baseline")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append draw summary to this .md file")] = None,
):
    """🎯 Contextual analysis of a specific draw vs historical patterns."""
    from engine.cli.commands.draw_summary import draw_summary as impl
    return impl(lottery, draw_id, context, export_md)

@app.command(name="history-scan", rich_help_panel=PANEL_ANALYTICS)
def history_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    windows: Annotated[int, typer.Option("--windows", "-n", help="How many historical scan windows to evaluate")] = 20,
    window_size: Annotated[int, typer.Option("--window-size", "-w", help="Draws per scan window")] = 50,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append history-scan report to this .md file")] = None,
):
    """📅 Retrospective GO/NO-GO timeline across historical draw windows."""
    from engine.cli.commands.history_scan import history_scan as impl
    return impl(lottery, windows, window_size, export_md)

@app.command(name="pool-stats", rich_help_panel=PANEL_ANALYTICS)
def pool_stats(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws:   Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to analyse")] = 100,
    check:   Annotated[Optional[list[int]], typer.Option("--check", "-c", help="Validate a specific ticket against the distribution")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append stats report to this .md file")] = None,
):
    """📊 Distributional statistics for draw outcomes."""
    from engine.cli.commands.pool_stats import pool_stats as impl
    return impl(lottery, draws, check, export_md)

@app.command(name="rank-numbers", rich_help_panel=PANEL_ANALYTICS)
def rank_numbers(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L", help="History window for strategy scoring")] = 50,
    top: Annotated[int, typer.Option("--top", "-N", help="Show only the top N numbers (0 = all)")] = 0,
    temperature: Annotated[float, typer.Option("--temperature", help="Suggestion temperature")] = 0.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append ranking to this .md file")] = None,
):
    """🔢 Composite per-number ranking across all strategies."""
    from engine.cli.commands.rank_numbers import rank_numbers as impl
    return impl(lottery, strategies, window, top, temperature, export_md)

@app.command(name="streak-report", rich_help_panel=PANEL_ANALYTICS)
def streak_report(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to analyse")] = 100,
    top: Annotated[int, typer.Option("--top", "-t", help="How many numbers to show in each table")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append streak report to this .md file")] = None,
):
    """🔥 All-pool hot/cold streak overview."""
    from engine.cli.commands.streak_report import streak_report as impl
    return impl(lottery, draws, top, export_md)

@app.command(name="leaderboard", rich_help_panel=PANEL_ANALYTICS)
def leaderboard(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated list or group: default | statistical | esoteric | deep")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L", help="Rolling window size for stability analysis")] = 50,
    step: Annotated[int, typer.Option("--step", help="Step between stability windows")] = 20,
    inject_ratio: Annotated[float, typer.Option("--inject-ratio", help="Noise injection ratio for stress testing")] = 0.5,
    trials: Annotated[int, typer.Option("--trials", help="Randomisation trials per strategy")] = 3,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append leaderboard to this .md file")] = None,
    seed: Annotated[Optional[int], typer.Option("--seed", help="Random seed for reproducible trials")] = None,
):
    """🏆 Strategy Performance Leaderboard — see which algorithms are winning."""
    from engine.cli.commands.leaderboard import leaderboard as impl
    return impl(lottery, strategies, window, step, inject_ratio, trials, export_md, seed)

@app.command(name="fractal-scan", rich_help_panel=PANEL_ANALYTICS)
def fractal_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 30,
):
    """🌀 Analyze spatial fractal dimension of historical draws."""
    from engine.cli.commands.fractal_scan import fractal_scan as impl
    return impl(lottery, draws)

@app.command(name="report-elite", rich_help_panel=PANEL_ANALYTICS)
def report_elite(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output PDF path")] = None,
):
    """📄 Generate a professional PDF diagnostic report for a lottery."""
    from engine.cli.commands.report_elite import report_elite as impl
    return impl(lottery, output)

@app.command(name="spectral-3d", rich_help_panel=PANEL_ANALYTICS)
def spectral_3d(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 200,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """📊 Generate an interactive 3D Spectral landscape of the lottery."""
    from engine.cli.commands.spectral_3d import spectral_3d as impl
    return impl(lottery, draws, output)

@app.command(name="hyper-explorer", rich_help_panel=PANEL_ANALYTICS)
def hyper_explorer(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 500,
    dim: Annotated[int, typer.Option("--dim", "-d", help="Projection dimensions (2 or 3)")] = 2,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """🚀 'Fly' through the high-dimensional manifold of historical draws."""
    from engine.cli.commands.hyper_explorer import hyper_explorer as impl
    return impl(lottery, draws, dim, output)

@app.command(name="synergy-graph", rich_help_panel=PANEL_ANALYTICS)
def synergy_graph(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 300,
    threshold: Annotated[float, typer.Option("--threshold", "-t", help="Minimum co-occurrence lift to show edge")] = 1.2,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """🕸️ Map the 'Clique Structure' of the lottery number pool."""
    from engine.cli.commands.synergy_graph import synergy_graph as impl
    return impl(lottery, draws, threshold, output)

@app.command(name="space-weather", rich_help_panel=PANEL_ANALYTICS)
def space_weather(
    update_cache: Annotated[bool, typer.Option("--update/--no-update", help="Update the data/solar_k_index.json cache")] = True,
):
    """☀️ Monitor live Geomagnetic and Solar activity."""
    from engine.cli.commands.space_weather import space_weather as impl
    return impl(update_cache)

@app.command(name="global-bench", rich_help_panel=PANEL_ANALYTICS)
def global_bench(
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to test for each lottery")] = 10,
    limit: Annotated[int, typer.Option("--limit", "-L", help="History window for each strategy")] = 50,
):
    """🏆 Exhaustive Backtest of ALL strategies across ALL lotteries."""
    from engine.cli.commands.global_bench import global_bench as impl
    return impl(draws, limit)

@app.command(name="entropy-map", rich_help_panel=PANEL_ANALYTICS)
def entropy_map(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 300,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """🌀 Map the 'Information Density' of the bet slip."""
    from engine.cli.commands.entropy_map import entropy_map as impl
    return impl(lottery, draws, output)

@app.command(name="sync-check", rich_help_panel=PANEL_ANALYTICS)
def sync_check(
    days: Annotated[int, typer.Option("--days", "-d", help="Window for cross-game sync check")] = 7,
):
    """📡 Search for cross-game synchronicity (shared numbers)."""
    from engine.cli.commands.sync_check import sync_check as impl
    return impl(days)

@app.command(name="cluster-walk", rich_help_panel=PANEL_ANALYTICS)
def cluster_walk(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws for manifold base")] = 300,
    path_length: Annotated[int, typer.Option("--path", "-p", help="Length of recent draw path to trace")] = 15,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """🚶‍♂️ Visualize the recent trajectory of draws through the topological manifold."""
    from engine.cli.commands.cluster_walk import cluster_walk as impl
    return impl(lottery, draws, path_length, output)

@app.command(name="pool-evolution", rich_help_panel=PANEL_ANALYTICS)
def pool_evolution(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to trace")] = 100,
    window: Annotated[int, typer.Option("--window", "-w", help="Rolling window size for hot/cold definition")] = 15,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
):
    """🌊 Visualize the dynamic shifts in Hot/Warm/Cold numbers over time."""
    from engine.cli.commands.pool_evolution import pool_evolution as impl
    return impl(lottery, draws, window, output)

# --- PANEL_BETTING Commands ---

@app.command(rich_help_panel=PANEL_BETTING)
def wheel(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    pool: Annotated[Optional[str], typer.Option("--pool", "-p", help="Space/comma-separated list of numbers to wheel")] = None,
    mode: Annotated[str, typer.Option("--mode", "-m", help="Wheel type: full | key | abbreviated")] = "full",
    keys: Annotated[Optional[str], typer.Option("--keys", "-k", help="Numbers that MUST appear in every ticket (for key mode)")] = None,
    guarantee: Annotated[int, typer.Option("--guarantee", "-g", help="Match guarantee (e.g. 4 for '4 if 6')")] = 4,
    test: Annotated[Optional[str], typer.Option("--test", help="Evaluate wheel against these winning numbers")] = None,
    preset: Annotated[Optional[str], typer.Option("--preset", help="Use a predefined number pool (e.g. 'hot-10', 'overdue-12')")] = None,
):
    """🎡 Generate combinatorial wheels for a pool of numbers."""
    from engine.cli.commands.management import wheel as impl
    return impl(lottery, pool, mode, keys, guarantee, test, preset)

@app.command(rich_help_panel=PANEL_BETTING)
def portfolio(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    full_name: Annotated[str, typer.Option("--full-name", help="Full birth name for Kabbalistic numerology (use quotes for multi-word names)")] = "GEMINI ENGINE",
    birth_date: Annotated[str, typer.Option("--birth-date", help="Birthday (YYYY-MM-DD)")] = "1990-01-01",
):
    """💼 Generate a diversified ticket portfolio (Statistical, Chaos, and Deep tiers)."""
    from engine.cli.commands.portfolio import portfolio as impl
    return impl(lottery, full_name, birth_date)

@app.command(rich_help_panel=PANEL_BETTING)
def global_portfolio(
    budget: Annotated[float, typer.Option("--budget", "-b", help="Total budget for all games")] = 100.0,
    jackpots: Annotated[Optional[str], typer.Option("--jackpots", "-J", 
        help="Comma-separated jackpots in order of 'lottery games' list")] = None,
):
    """💼 Optimize budget allocation across the global lottery network."""
    from engine.cli.commands.global_portfolio import global_portfolio as impl
    return impl(budget, jackpots)

@app.command(rich_help_panel=PANEL_BETTING)
def hedge(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    budget:  Annotated[float, typer.Option("--budget", "-b", help="Total budget for this hedge bet")] = 50.0,
    risk_profile: Annotated[str, typer.Option("--risk", "-r", help="conservative | balanced | aggressive")] = "balanced",
):
    """🛡️ Generate an optimized 'Hedge Portfolio' to maximize lower-tier returns."""
    from engine.cli.commands.hedge import hedge as impl
    return impl(lottery, budget, risk_profile)

@app.command(name="multi-ticket", rich_help_panel=PANEL_BETTING)
def multi_ticket(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    count: Annotated[int, typer.Option("--count", "-k", help="Number of tickets to generate")] = 3,
    diversity: Annotated[float, typer.Option("--diversity", "-d", help="Diversity weight 0–1 (higher = more distinct tickets)")] = 0.6,
    score_window: Annotated[int, typer.Option("--limit", "-L", help="Draws used for scoring")] = 100,
    seed: Annotated[Optional[int], typer.Option("--seed", help="Random seed for reproducibility")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append multi-ticket report to this .md file")] = None,
):
    """🎟️ Generate a portfolio of N diverse tickets with maximised pool coverage."""
    from engine.cli.commands.multi_ticket import multi_ticket as impl
    return impl(lottery, count, diversity, score_window, seed, export_md)

@app.command(name="prize-ev", rich_help_panel=PANEL_BETTING)
def prize_ev(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-J",
        help="Current jackpot prize (top-tier payout)")] = None,
    tier_override: Annotated[Optional[list[str]], typer.Option("--tier", "-T",
        help="Override prize for one tier: match:amount  (e.g. --tier 14:1200)")] = None,
    cost_override: Annotated[Optional[float], typer.Option("--cost", "-c",
        help="Override ticket cost (default from game rules)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append EV report to this .md file")] = None,
):
    """⚖️ Expected Value Analysis — is the current jackpot mathematically 'playable'?"""
    from engine.cli.commands.prize_ev import prize_ev as impl
    return impl(lottery, jackpot, tier_override, cost_override, export_md)

@app.command(rich_help_panel=PANEL_BETTING)
def quick(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Generate ticket even if scan is NO-GO")] = False,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Print only the numbers (cron-friendly)")] = False,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Strategy group for forecast")] = "fast",
    window: Annotated[int, typer.Option("--limit", "-L", help="History window")] = 50,
):
    """⚡ Fastest path to a ticket: scan + forecast in one command."""
    from engine.cli.commands.quick import quick as impl
    return impl(lottery, force, quiet, as_json, strategies, window)

@app.command(name="next", rich_help_panel=PANEL_BETTING)
def next_draw(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy for scan layers")] = "bayesian",
    force: Annotated[bool, typer.Option("--force/--no-force", help="Generate ticket even if verdict is not GO")] = False,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet", help="Print only the ticket numbers (no decoration)")] = False,
):
    """⚡ One-liner: scan conditions + generate consensus ticket if GO."""
    from engine.cli.commands.next_draw import next_draw as impl
    return impl(lottery, strategy, force, quiet)

@app.command(rich_help_panel=PANEL_BETTING)
def forecast(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Group or comma list: default | statistical | fast | esoteric | <names>")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for each strategy")] = 50,
    step: Annotated[int, typer.Option("--step",
        help="Step between stability windows")] = 20,
    inject_ratio: Annotated[float, typer.Option("--inject-ratio",
        help="Fraction to randomise in stress-test")] = 0.5,
    trials: Annotated[int, typer.Option("--trials",
        help="Randomisation trials per strategy")] = 3,
    temperature: Annotated[float, typer.Option("--temperature",
        help="Suggestion temperature (0=deterministic)")] = 1.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append forecast to this .md file")] = None,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet")] = False,
    use_calibration: Annotated[bool, typer.Option("--use-calibration/--no-calibration",
        help="Weight strategies by calibrated empirical lift (from calibration cache)")] = False,
    seed: Annotated[Optional[int], typer.Option("--seed",
        help="Random seed for reproducible random injection trials")] = None,
    config: Annotated[Optional[Path], typer.Option("--config",
        help="YAML config from `lottery tune` — overrides --strategies and injects params")] = None,
):
    """🔮 High-fidelity prediction report for the next draw."""
    from engine.cli.commands.forecast import forecast as impl
    return impl(lottery, strategies, window, step, inject_ratio, trials, temperature, export_md, quiet, use_calibration, seed, config)

@app.command(rich_help_panel=PANEL_BETTING)
def picks(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    last: Annotated[int, typer.Option("--last", "-n", help="Use only the last N logged tickets")] = 10,
    since: Annotated[Optional[str], typer.Option("--since", help="Only use tickets logged on or after YYYY-MM-DD")] = None,
    source: Annotated[Optional[str], typer.Option("--source", help="Filter by source: forecast | daily | (any)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append picks report to this .md file")] = None,
    raw: Annotated[bool, typer.Option("--raw", help="Print only numbers")] = False,
):
    """🃏 Consensus ticket from recently logged forecasts."""
    from engine.cli.commands.picks import picks as impl
    return impl(lottery, last, since, source, export_md, raw)

@app.command(name="suggest-swaps", rich_help_panel=PANEL_BETTING)
def suggest_swaps(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    numbers: Annotated[list[int], typer.Argument(help="Your current ticket numbers")],
    swaps: Annotated[int, typer.Option("--swaps", "-k", help="How many swap suggestions to show")] = 5,
    draws: Annotated[int, typer.Option("--draws", "-n", help="How many recent draws for context")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append swap suggestions to this .md file")] = None,
):
    """🔄 Suggest best number swaps to improve a ticket."""
    from engine.cli.commands.suggest_swaps import suggest_swaps as impl
    return impl(lottery, numbers, swaps, draws, export_md)

@app.command(rich_help_panel=PANEL_BETTING)
def party(
    lottery: Annotated[str, typer.Argument(help="Lottery name to generate a ticket for")] = "br/mega-sena",
):
    """🥳 Launch 'Party Mode' to brainstorm and generate a chaotic/math hybrid ticket."""
    from engine.cli.commands.party import party as impl
    return impl(lottery)

@app.command(rich_help_panel=PANEL_BETTING)
def oracle(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    persona: Annotated[str, typer.Option("--persona", "-p", help="quant | mystic | degen")] = "quant",
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
):
    """🔮 Generate natural-language betting advice based on hard data."""
    from engine.cli.commands.oracle import oracle as impl
    return impl(lottery, persona, limit)

@app.command(rich_help_panel=PANEL_BETTING)
def story_teller(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to use")] = "archetypes",
):
    """📖 Tell the 'Story' behind a suggested ticket."""
    from engine.cli.commands.story_teller import story_teller as impl
    return impl(lottery, strategy)

@app.command(rich_help_panel=PANEL_BETTING)
def deliberate(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g., br/mega-sena)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated list of strategies")] = "weighted,bayesian,kabbalistic,noosphere",
    limit: Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
    temp: Annotated[float, typer.Option("--temp", "-T", help="Chaos temperature")] = 0.7,
):
    """⚖️ Summon the Consciousness Council to deliberate on the best path forward."""
    from engine.cli.commands.deliberate import deliberate as impl
    return impl(lottery, strategies, limit, temp)

@app.command(rich_help_panel=PANEL_BETTING)
def bio(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 30,
    metric: Annotated[str, typer.Option("--metric", "-m", help="Beta-diversity metric (jaccard, braycurtis)")] = "jaccard",
):
    """🔬 Biological analysis of lottery draws using scikit-bio."""
    from engine.cli.commands.bio import bio as impl
    return impl(lottery, draws, metric)

@app.command(rich_help_panel=PANEL_BETTING)
def resonance(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", 
        help="Comma-separated strategies to analyze")] = "weighted,markov,bayesian,hurst_memory,graph_influence",
    limit: Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
):
    """💎 Detect multi-strategy resonance and wave interference."""
    from engine.cli.commands.resonance import resonance as impl
    return impl(lottery, strategies, limit)

@app.command(rich_help_panel=PANEL_BETTING)
def swarm(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    generations: Annotated[int, typer.Option("--gens", "-g", help="Evolution generations")] = 50,
    pop_size: Annotated[int, typer.Option("--pop", "-p", help="Population size")] = 100,
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Primary strategy for scoring")] = "weighted",
):
    """🐝 Evolve the 'Alpha Ticket' using Swarm Intelligence."""
    from engine.cli.commands.swarm import swarm as impl
    return impl(lottery, generations, pop_size, strategy)

@app.command(rich_help_panel=PANEL_BETTING)
def risk(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j", help="Current jackpot amount (top prize)")] = None,
    bankroll: Annotated[float, typer.Option("--bankroll", "-b", help="Your total betting bankroll")] = 100.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append report to this .md file")] = None,
):
    """⚖️ Kelly Criterion Analysis — optimal bankroll allocation for current odds."""
    from engine.cli.commands.risk import risk as impl
    return impl(lottery, jackpot, bankroll, export_md)

@app.command(rich_help_panel=PANEL_BETTING)
def savings(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    pool_size: Annotated[int, typer.Option("--pool", "-p", help="Size of your candidate pool")],
):
    """💰 Wheel Savings Calculator — compare the cost of a wheel vs. a full large bet."""
    from engine.cli.commands.management import savings as impl
    return impl(lottery, pool_size)

@app.command(rich_help_panel=PANEL_BETTING)
def simulate(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers")],
    range_str: Annotated[str, typer.Option("--range", "-r", help="Draw ID range (e.g. 1000-2000) or 'all'")] = "all",
):
    """🎮 Run a high-fidelity historical simulation of a specific ticket."""
    from engine.cli.commands.management import simulate as impl
    return impl(lottery, numbers, range_str)

# --- PANEL_MONITOR Commands ---

@app.command(rich_help_panel=PANEL_PRIMARY)
def singularity(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j", help="Current jackpot")] = None,
):
    """🌌 Launch the 'Synapse Architect' Singularity session.
    
    Equivalent to: lottery daily --matrix --narrative
    """
    from engine.cli.commands.daily import daily as impl
    return impl(lottery, matrix=True, narrative=True, jackpot=jackpot)

@app.command(rich_help_panel=PANEL_MONITOR)
def daily(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Primary strategy for scan layers")] = "bayesian",
    persona: Annotated[str, typer.Option("--persona", "-p", help="Oracle persona: quant | mystic | degen")] = "quant",
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j", help="Current jackpot (for EV calculation)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append daily digest to this .md file")] = None,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet", help="Print only the final summary (no per-stage detail)")] = False,
    matrix: Annotated[bool, typer.Option("--matrix", help="Show exhaustive strategy matrix and risk ledger")] = False,
    narrative: Annotated[bool, typer.Option("--narrative", help="Synthesize a 'Daily Intelligence Narrative' (Synapse Architect persona)")] = False,
):
    """📰 Comprehensive morning digest — all diagnostics in one pass."""
    from engine.cli.commands.daily import daily as impl
    return impl(lottery, strategy, persona, jackpot, export_md, quiet, matrix, narrative)

@app.command(rich_help_panel=PANEL_MONITOR)
def weekly(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    weeks: Annotated[int, typer.Option("--weeks", "-w", help="Number of past weeks to cover")] = 1,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append weekly report to this .md file")] = None,
):
    """📅 Weekly performance summary from JSONL logs."""
    from engine.cli.commands.weekly import weekly as impl
    return impl(lottery, weeks, export_md)

@app.command(rich_help_panel=PANEL_MONITOR)
def report(
    config_path: Annotated[Path, typer.Argument(help="Path to report configuration (YAML)")],
    force: Annotated[bool, typer.Option("--force", help="Run even if already updated today")] = False,
    full_name: Annotated[Optional[str], typer.Option("--full-name", help="Override user full name")] = None,
    birth_date: Annotated[Optional[str], typer.Option("--birth-date", help="Override user birth date (YYYY-MM-DD)")] = None,
    topic: Annotated[Optional[str], typer.Option("--topic", help="Override seeding topic")] = None,
):
    """📋 Execute a scheduled report or diagnostic pipeline from a config file."""
    from engine.cli.commands.report import run_report
    overrides = {}
    if full_name: overrides["full_name"] = full_name
    if birth_date: overrides["birth_date"] = birth_date
    if topic: overrides["topic"] = topic
    
    return run_report(str(config_path), force=force, overrides=overrides)

@app.command(rich_help_panel=PANEL_MONITOR)
def alert(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    condition: Annotated[str, typer.Option("--condition", "-c", help="Comma-separated: go-strong | go | regime-shift | chi2-alarm | trend-drop | all")] = "go-strong,regime-shift",
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy for scan layers")] = "bayesian",
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Write alert JSON to this file (for pipeline use)")] = None,
    silent: Annotated[bool, typer.Option("--silent/--no-silent", help="Suppress terminal output (exit code still set)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append alert report to this .md file")] = None,
):
    """🚨 Condition monitor — outputs only when an alert condition is met."""
    from engine.cli.commands.alert import alert as impl
    return impl(lottery, condition, strategy, output, silent, export_md)

@app.command(name="cold-streak-alert", rich_help_panel=PANEL_MONITOR)
def cold_streak_alert(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    threshold: Annotated[float, typer.Option("--threshold", "-t", help="Alert when cold_streak ≥ threshold × expected_gap")] = 2.5,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed table of cold numbers")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append alert report to this .md file")] = None,
):
    """🥶 Cron-safe alert when pool numbers reach extreme cold streaks."""
    from engine.cli.commands.cold_streak_alert import cold_streak_alert as impl
    return impl(lottery, threshold, verbose, export_md)

@app.command(name="regime-history", rich_help_panel=PANEL_MONITOR)
def regime_history(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    window: Annotated[int, typer.Option("--window", "-w",
        help="Recent window for JS divergence (draws)")] = 30,
    baseline: Annotated[int, typer.Option("--baseline", "-b",
        help="Minimum preceding draws needed before sampling")] = 60,
    step: Annotated[int, typer.Option("--step", "-s",
        help="Sample every N draws (larger = faster, lower resolution)")] = 10,
    recent: Annotated[int, typer.Option("--recent", "-r",
        help="Show only the last N sample points (0 = all)")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append regime history to this .md file")] = None,
):
    """📉 Retrospective Jensen-Shannon divergence timeline — see regime shifts."""
    from engine.cli.commands.regime_history import regime_history as impl
    return impl(lottery, window, baseline, step, recent, export_md)

@app.command(rich_help_panel=PANEL_MONITOR)
def log(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to use for signal snapshot")] = "bayesian",
    output: Annotated[str, typer.Option("--output", "-o", help="Log file path")] = "",
    fmt: Annotated[str, typer.Option("--format", "-f", help="Output format: jsonl | csv | md")] = "jsonl",
    window: Annotated[int, typer.Option("--limit", "-L", help="History window for signal snapshot")] = 50,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet", help="Suppress output")] = False,
):
    """📓 Daily Log Snapshot — capture current market signals for the record."""
    from engine.cli.commands.log import log as impl
    return impl(lottery, strategy, output, fmt, window, quiet)

@app.command(name="log-view", rich_help_panel=PANEL_MONITOR)
def log_view(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery game")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Log file to read")] = "",
    last: Annotated[int, typer.Option("--last", "-n", help="Show only the last N records")] = 10,
):
    """📋 View recent entries from the daily log."""
    from engine.cli.commands.log import log_view as impl
    return impl(lottery, output, last)

@app.command(name="log-export", rich_help_panel=PANEL_MONITOR)
def log_export(
    log_type: Annotated[str, typer.Argument(help="Which log to export: draw-log | ticket-log | all")] = "draw-log",
    game: Annotated[Optional[str], typer.Option("--game", "-g", help="Filter to a specific game (e.g. br/lotofacil)")] = None,
    since: Annotated[Optional[str], typer.Option("--since", help="Only include entries on or after this date (YYYY-MM-DD)")] = None,
    fmt: Annotated[str, typer.Option("--format", "-f", help="Output format: csv | tsv | json")] = "csv",
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Write to this file instead of stdout")] = None,
):
    """📤 Export JSONL logs to CSV/TSV/JSON for external analysis."""
    from engine.cli.commands.log_export import log_export as impl
    return impl(log_type, game, since, fmt, output)

# Sub-app watchlist
watchlist_app = typer.Typer(name="watchlist", help="📋 Manage and batch-run tracked lottery games.", rich_help_panel=PANEL_MONITOR)

@watchlist_app.command(name="add")
def watchlist_add(
    game: Annotated[str, typer.Argument(help="Game ID to add, e.g. br/lotofacil")],
):
    """Add a game to the watchlist."""
    from engine.cli.commands.watchlist import add as impl
    return impl(game)

@watchlist_app.command(name="remove")
def watchlist_remove(
    game: Annotated[str, typer.Argument(help="Game ID to remove")],
):
    """Remove a game from the watchlist."""
    from engine.cli.commands.watchlist import remove_cmd as impl
    return impl(game)

@watchlist_app.command(name="list")
def watchlist_list():
    """List all tracked games."""
    from engine.cli.commands.watchlist import list_cmd as impl
    return impl()

@watchlist_app.command(name="status")
def watchlist_status():
    """Show last-logged status for each tracked game (from JSONL log)."""
    from engine.cli.commands.watchlist import status as impl
    return impl()

@watchlist_app.command(name="run")
def watchlist_run(
    mode: Annotated[str, typer.Option("--mode", "-m", help="daily | alert | scan")] = "daily",
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet", help="Compact output (only for scan/alert mode)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append each game's digest to this markdown file (daily mode only)")] = None,
    condition: Annotated[str, typer.Option("--condition", "-c", help="Alert conditions (alert mode only)")] = "go-strong,regime-shift",
    jackpot: Annotated[Optional[str], typer.Option("--jackpot", help="Comma-separated jackpot amounts (one per game, in order)")] = None,
):
    """Run daily/alert/scan across all tracked games."""
    from engine.cli.commands.watchlist import run_cmd as impl
    return impl(mode, quiet, export_md, condition, jackpot)

app.add_typer(watchlist_app, name="watchlist", rich_help_panel=PANEL_MONITOR)

@app.command(rich_help_panel=PANEL_MONITOR)
def hitcheck(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to check against")] = 1,
    draw_id: Annotated[Optional[int], typer.Option("--draw-id", help="Check against this specific draw ID only")] = None,
    since: Annotated[Optional[str], typer.Option("--since", help="Only check tickets generated on or after this date (YYYY-MM-DD)")] = None,
    all_tickets: Annotated[bool, typer.Option("--all/--no-all", help="Show all tickets including no-prize rows")] = True,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append hitcheck report to this .md file")] = None,
):
    """🎯 Compare logged tickets against actual draw results."""
    from engine.cli.commands.hitcheck import hitcheck as impl
    return impl(lottery, draws, draw_id, since, all_tickets, export_md)

# --- PANEL_SYSTEM Commands ---

@app.command(rich_help_panel=PANEL_SYSTEM)
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """🚀 Start the FastAPI Sidecar (REST API)."""
    try:
        import uvicorn
        Console().print(f"\n[bold green]Starting Prediction Engine Sidecar...[/bold green]")
        uvicorn.run("engine.api.main:app", host=host, port=port, reload=reload)
    except ImportError:
        Console().print("[bold red]Error:[/bold red] 'uvicorn' and 'fastapi' are required for this command.")

@app.command(rich_help_panel=PANEL_SYSTEM)
def games() -> None:
    """🎮 List all supported lotteries in the registry."""
    from engine.adapters.registry import registry
    games_list = registry.list_games()
    table = Table(title="Global Lottery Registry", box=None, padding=(0, 2))
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Format", style="green")
    table.add_column("Price", style="dim")
    table.add_column("Status")
    for g in games_list:
        fmt = f"{g.pick_count}/{g.pool_size}"
        if g.bonus_count > 0: fmt += f" + {g.bonus_count}/{g.bonus_pool}"
        status = "[green]● Available[/green]" if g.data_available else "[dim]○ Planned[/dim]"
        price = f"{g.ticket_price:.2f} {g.currency}"
        table.add_row(g.id, g.name, fmt, price, status)
    Console().print(table)

@app.command(rich_help_panel=PANEL_SYSTEM)
def odds(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery name (e.g. br/lotofacil)")] = None,
    compare: Annotated[bool, typer.Option("--compare", "-c", help="Compare all registered lotteries")] = False,
):
    """⚖️ View jackpot odds and compare game efficiency."""
    from engine.cli.commands.odds import odds as impl
    return impl(lottery, compare)

@app.command(rich_help_panel=PANEL_SYSTEM)
def daemon(
    lottery: Annotated[str, typer.Argument(help="Lottery name to monitor")],
    interval: Annotated[int, typer.Option("--interval", "-i", help="Optimization interval in seconds")] = 3600,
    prev: Annotated[int, typer.Option("--prev", "-p", help="Validation window (number of previous draws)")] = 10,
):
    """🤖 Start the AutoML Background Daemon to continuously optimize strategies."""
    from engine.cli.commands.daemon import daemon as impl
    return impl(lottery, interval, prev)

@app.command(name="daemon-status", rich_help_panel=PANEL_SYSTEM)
def daemon_status():
    """📊 View the current state and latest findings of the AutoML Daemon."""
    from engine.cli.commands.daemon import daemon_status as impl
    return impl()

@app.command(rich_help_panel=PANEL_SYSTEM)
def optimize(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated strategies to test. Use 'all' for everything.")] = "weighted,markov,momentum",
    limits: Annotated[str, typer.Option("--limits", "-L", help="Comma-separated history limits to test (e.g. '50,100,200')")] = "50,100,200",
    temps: Annotated[str, typer.Option("--temps", "-t", help="Comma-separated temperatures to test (e.g. '0.0,0.5')")] = "0.0",
    prev: Annotated[str, typer.Option("--prev", "-p", help="Range of draws to use for validation (e.g. '1-10')")] = "1-10",
    top_n: Annotated[int, typer.Option("--top-n", help="Number of top picks to check for capture rate")] = None,
):
    """⚙️ Search for the best strategy configuration."""
    from engine.cli.commands.management import optimize as impl
    return impl(lottery, strategies, limits, temps, prev, top_n)

@app.command(rich_help_panel=PANEL_SYSTEM)
def calibrate(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to test against (more = slower)")] = 15,
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L", help="Training window size (draws before each target)")] = 50,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append calibration report to this .md file")] = None,
    min_training: Annotated[int, typer.Option("--min-training", help="Minimum training draws required; skip earlier targets")] = 30,
):
    """🎯 Empirical strategy calibration — rank by actual out-of-sample hit rates."""
    from engine.cli.commands.calibrate import calibrate as impl
    return impl(lottery, draws, strategies, window, export_md, min_training)

@app.command(rich_help_panel=PANEL_SYSTEM)
def prune(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated strategies to audit. Use 'all' for everything.")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L", help="Backtest window for performance audit")] = 30,
    threshold: Annotated[float, typer.Option("--threshold", "-t", help="Minimum required lift over random baseline")] = 0.02,
    redundancy: Annotated[bool, typer.Option("--redundancy", help="Show Jaccard similarity matrix between strategy outputs")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append pruning report to this .md file")] = None,
):
    """✂️ Identify and 'hibernate' underperforming strategies."""
    from engine.cli.commands.prune import prune as impl
    return impl(lottery, strategies, window, threshold, redundancy, export_md)

@app.command(name="audit-data", rich_help_panel=PANEL_SYSTEM)
def audit_data(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
):
    """🔍 Audit the integrity of cached data for a lottery."""
    from engine.cli.commands.management import audit_data as impl
    return impl(lottery)

@app.command(rich_help_panel=PANEL_SYSTEM)
def export(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    format:  Annotated[str, typer.Option("--format", "-f", help="json | csv")] = "json",
    output:  Annotated[Optional[str], typer.Option("--output", "-o", help="Output filename")] = None,
    console_out: Annotated[bool, typer.Option("--console", "-c", help="Print output to console instead of file")] = False,
):
    """📤 Export draw history to JSON or CSV."""
    from engine.cli.commands.management import export as impl
    return impl(lottery, format, output, console_out)

@app.command(rich_help_panel=PANEL_SYSTEM)
def history(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    limit: Annotated[int, typer.Option("--limit", "-L", help="Number of draws to show")] = 10,
):
    """📅 Chronological Draw Navigator — browse previous results."""
    from engine.cli.commands.management import history as impl
    return impl(lottery, limit)

@app.command(name="compare-draws", rich_help_panel=PANEL_SYSTEM)
def compare_draws(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    recent: Annotated[int, typer.Option("--recent", "-r", help="Size of recent window to compare")] = 50,
    baseline: Annotated[int, typer.Option("--baseline", "-b", help="Size of baseline window (0 = full history)")] = 0,
    top_n: Annotated[int, typer.Option("--top-n", "-N", help="Number of top movers to display")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append regime snapshot to this .md file")] = None,
):
    """⚖️ Compare recent draw window against history to detect regime shifts."""
    from engine.cli.commands.compare_draws import compare_draws as impl
    return impl(lottery, recent, baseline, top_n, export_md)

@app.command(name="compare-strategies", rich_help_panel=PANEL_SYSTEM)
def compare_strategies(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L", help="History window for strategy scoring")] = 50,
    top: Annotated[int, typer.Option("--top", "-N", help="Show top-N consensus numbers (0 = all unique numbers)")] = 0,
    temperature: Annotated[float, typer.Option("--temperature", help="Suggestion temperature")] = 0.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append comparison report to this .md file")] = None,
):
    """⚖️ Side-by-side ticket comparison across all strategies."""
    from engine.cli.commands.compare_strategies import compare_strategies as impl
    return impl(lottery, strategies, window, top, temperature, export_md)

@app.command(name="compare-bets", rich_help_panel=PANEL_SYSTEM)
def compare_bets(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers")],
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Check against last N draws")] = 100,
):
    """⚖️ Compare your set of numbers against historical draws."""
    from engine.cli.commands.management import compare_bets as impl
    return impl(lottery, numbers, limit)

@app.command(name="stress-test", rich_help_panel=PANEL_SYSTEM)
def stress_test(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy name or comma-separated list")] = "weighted",
    inject_ratio: Annotated[float, typer.Option("--inject-ratio", help="Fraction of draws to replace with true random (0.0–1.0)")] = 0.5,
    trials: Annotated[int, typer.Option("--trials", help="Number of random injection trials to average over")] = 5,
    window: Annotated[Optional[int], typer.Option("--limit", "-L", help="Use only the N most recent draws")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export adversarial report to this .md file")] = None,
    seed: Annotated[Optional[int], typer.Option("--seed", help="Random seed for reproducible injection trials")] = None,
):
    """🧪 Stress-test strategies by injecting random noise into historical data."""
    from engine.cli.commands.stress_test import stress_test as impl
    return impl(lottery, strategy, inject_ratio, trials, window, export_md, seed)

@app.command(rich_help_panel=PANEL_SYSTEM)
def tune(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent target draws to test against")] = 30,
    limit: Annotated[int, typer.Option("--limit", "-L",
        help="Training window size (draws before each target)")] = 50,
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Strategies to evaluate: preset (statistical|fast|default) or comma list")] = "statistical",
    no_grid: Annotated[bool, typer.Option("--no-grid",
        help="Skip parameter grids — run each strategy once with defaults (faster)")] = False,
    metric: Annotated[str, typer.Option("--metric",
        help="Ranking metric: lift | hits | capture")] = "lift",
    top: Annotated[int, typer.Option("--top",
        help="How many winners to write to the YAML")] = 1,
    fmt: Annotated[str, typer.Option("--format",
        help="YAML output format: flat (backtest/forecast) | report (lottery report)")] = "flat",
    output: Annotated[Optional[str], typer.Option("--output", "-o",
        help="Output YAML path (default: tuned/<lottery>.yaml)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append tune report to this .md file")] = None,
    min_training: Annotated[int, typer.Option("--min-training",
        help="Minimum training draws required; skip earlier targets")] = 30,
):
    """🎯⚙️ Auto-select the best strategy + parameters from historical evidence."""
    from engine.cli.commands.tune import tune as impl
    return impl(lottery, draws, limit, strategies, no_grid, metric, top, fmt, output, export_md, min_training)

# --- PANEL_VERIFY Commands ---

@app.command(rich_help_panel=PANEL_VERIFY)
def check(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers [Required]")],
    show_range: Annotated[bool, typer.Option("--range", "-r", help="Visualize sum in analytical distribution")] = False,
):
    """✅ Check a ticket's structural patterns against historical rules."""
    from engine.cli.commands.check import check as impl
    return impl(lottery, numbers, show_range)

@app.command(rich_help_panel=PANEL_VERIFY)
def validate(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Argument(help="Numbers to validate [Required]")],
):
    """✔️ Quickly check if a set of numbers is valid for a given lottery's rules."""
    from engine.cli.commands.check import validate as impl
    return impl(lottery, numbers)

@app.command(name="ticket-grade", rich_help_panel=PANEL_VERIFY)
def ticket_grade(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    numbers: Annotated[list[int], typer.Argument(help="Your ticket numbers")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="How many recent draws to use for context")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append grade report to this .md file")] = None,
):
    """🎓 Grade a ticket against engine diagnostics."""
    from engine.cli.commands.ticket_grade import ticket_grade as impl
    return impl(lottery, numbers, draws, export_md)

@app.command(rich_help_panel=PANEL_VERIFY)
def session(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Strategy group: default | fast | statistical")] = "fast",
    window: Annotated[int, typer.Option("--limit", "-L", help="History window for strategy scoring")] = 50,
    force: Annotated[bool, typer.Option("--force", help="Continue session even if scan is NO-GO")] = False,
    skip_oracle: Annotated[bool, typer.Option("--skip-oracle", help="Skip the oracle stage (faster)")] = True,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append session report to this .md file")] = None,
):
    """🎲 All-in-one pre-draw decision session."""
    from engine.cli.commands.session import session as impl
    return impl(lottery, strategies, window, force, skip_oracle, export_md)

@app.command(rich_help_panel=PANEL_VERIFY)
def calendar(
    full_name: Annotated[str, typer.Option("--full-name", help="Full birth name for Kabbalistic numerology")] = "GEMINI ENGINE",
    birth_date: Annotated[str, typer.Option("--birth-date", help="Birthday (YYYY-MM-DD)")] = "1990-01-01",
    month: Annotated[Optional[int], typer.Option("--month", "-m", help="Month (1-12) to generate calendar for")] = None,
    year: Annotated[Optional[int], typer.Option("--year", "-y", help="Year (e.g. 2026)")] = None,
):
    """📅 Generate a personal Kabbalistic calendar of Favorable Days."""
    from engine.cli.commands.personal import calendar as impl
    return impl(full_name, birth_date, month, year)

@app.command(rich_help_panel=PANEL_VERIFY)
def signature(
    name: Annotated[str, typer.Argument(help="Full birth name to analyze")],
):
    """✍️ Analyze Name for Negative Sequences (for entertainment)."""
    from engine.cli.commands.personal import signature as impl
    return impl(name)

@app.command(name="signature-audit", rich_help_panel=PANEL_VERIFY)
def signature_audit(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    ticket: Annotated[str, typer.Argument(help="Space-separated ticket numbers")],
):
    """🔍 Compare ticket structural signature against historical golden average."""
    from engine.cli.commands.signature_audit import signature_audit as impl
    return impl(lottery, ticket)

@app.command(name="coverage-check", rich_help_panel=PANEL_VERIFY)
def coverage_check(
    lottery:  Annotated[str, typer.Argument(help="Lottery name [Required]")],
    tickets:  Annotated[Optional[list[str]], typer.Argument(help="Tickets as quoted space-separated strings [Required]")] = None,
    file:     Annotated[Optional[str], typer.Option("--file", "-f", help="File with one ticket per line")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append coverage report to this .md file")] = None,
):
    """🗺️ Pool coverage analysis for one or more tickets."""
    from engine.cli.commands.coverage_check import coverage_check as impl
    return impl(lottery, tickets, file, export_md)

@app.command(name="property-tests", rich_help_panel=PANEL_VERIFY)
def property_tests(
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to test (or 'all')")] = "all",
):
    """🧪 Run adversarial property-based tests to verify strategy stability."""
    from engine.cli.commands.property_tests import property_tests as impl
    return impl(strategy)

# --- Global Callback ---

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    storage_engine: Annotated[str, typer.Option("--storage", help="Storage backend: duckdb | json")] = "duckdb",
    log_level: Annotated[str, typer.Option("--log-level", help="Logging level: DEBUG | INFO | WARNING | ERROR")] = "WARNING",
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress all non-error output")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed diagnostic logs")] = False,
    detailed_help: Annotated[bool, typer.Option("--detailed-help", help="Show complete manual with all parameters and examples for each command")] = False,
):
    """Global configuration for the Lottery Engine."""
    os.environ["LOTTERY_STORAGE_ENGINE"] = storage_engine.lower()
    
    if detailed_help:
        _print_detailed_help(app)
        raise typer.Exit(0)
    
    if verbose:
        level = logging.INFO
    else:
        level = getattr(logging, log_level.upper(), logging.WARNING)
        
    logging.getLogger().setLevel(level)
    
    if quiet:
        sys.stderr = open(os.devnull, 'w')

def _print_detailed_help(typer_app: typer.Typer):
    """Iterate through all commands and print a full manual."""
    from typer.main import get_command
    import click

    console = Console()
    click_app = get_command(typer_app)
    
    console.print(Panel.fit(
        "[bold cyan]Lottery Engine — Detailed Manual[/bold cyan]\n"
        "[dim]Full listing of commands, parameters, and usage examples.[/dim]",
        border_style="cyan"
    ))

    sorted_commands = sorted(click_app.commands.items())

    for name, cmd in sorted_commands:
        if cmd.hidden: continue
        console.rule(f"[bold green]lottery {name}[/bold green]", align="left")
        desc = cmd.help or "No description available."
        console.print(f"\n[italic]{desc.strip()}[/italic]\n")

        if cmd.params:
            param_table = Table(box=None, padding=(0, 2), header_style="bold dim")
            param_table.add_column("Parameter")
            param_table.add_column("Type")
            param_table.add_column("Required")
            param_table.add_column("Description")

            for param in cmd.params:
                p_type = param.type.name
                if isinstance(param.type, click.types.Choice):
                    p_type = f"choice({', '.join(param.type.choices)})"
                is_required = "[red]Yes[/red]" if param.required else "[dim]No[/dim]"
                p_name = f"--{param.name.replace('_', '-')}" if isinstance(param, click.Option) else param.name
                param_table.add_row(f"[cyan]{p_name}[/cyan]", p_type, is_required, param.help or "")
            console.print(param_table)

        if cmd.help and ("Example" in cmd.help or "Usage" in cmd.help):
            console.print("\n[bold dim]Examples:[/bold dim]")
            for line in cmd.help.split("\n"):
                if any(x in line for x in ["Example", "Usage"]) or (line.strip() and line.startswith("  ")):
                    console.print(f"  [yellow]{line.strip()}[/yellow]")
        console.print("")

    console.rule(style="cyan")
    console.print("[dim]Use [bold]--help[/bold] for simplified summary help.[/dim]\n")


if __name__ == "__main__":
    app()

if __name__ == "__main__":
    app()
