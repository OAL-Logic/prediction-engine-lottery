"""
Docs Command 📚
==============
Concept reference — explains how the engine works, strategies, mathematical filters,
diagrams, and dynamic evaluation.
"""

from __future__ import annotations

from typing import Annotated, Optional
import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.modules.filters import registry
from engine.cli.utils import get_adapter, ui_header, ui_table

console = Console()


def docs(
    topic: Annotated[str, typer.Argument(
        help="Topic: all | lotteries | analysis | strategies | filters | confidence | board | heatmap | expert | temperature | ensemble | deep | fun"
    )] = "all",
    filter_id: Annotated[Optional[str], typer.Option("--filter", "-f", help="Specific filter unique_id to inspect with diagram & dynamic test")] = None,
    ticket: Annotated[Optional[str], typer.Option("--ticket", "-t", help="Comma-separated numbers to evaluate dynamically (e.g. 5,12,23,34,45,56)")] = None,
    game: Annotated[Optional[str], typer.Option("--game", "-g", help="Lottery game identifier (e.g. br/mega-sena, br/lotofacil)")] = None,
    tier: Annotated[Optional[int], typer.Option("--tier", help="Filter tier (1-5) to inspect in catalog")] = None,
) -> None:
    """📚 Concept reference — explains how the engine works and how to use it effectively."""
    topic = topic.lower()

    # If user provided --filter or topic matches a specific filter id, jump to filter inspector
    target_fid = filter_id or (topic if topic not in ("all", "lotteries", "analysis", "strategies", "filters", "confidence", "board", "heatmap", "expert", "temperature", "ensemble", "deep", "fun") else None)
    
    if target_fid:
        f = registry.get(target_fid)
        if not f:
            console.print(f"[red]Filter '{target_fid}' not found in registry.[/red]")
            raise typer.Exit(1)
        
        # Determine rules
        rules = None
        if game:
            try:
                adapter = get_adapter(game)
                rules = adapter.rules
            except Exception:
                rules = None

        # Determine combination
        if ticket:
            nums = sorted([int(x.strip()) for x in ticket.split(",") if x.strip()])
        else:
            k = rules.pick_count if rules else 6
            lo = rules.number_range[0] if rules else 1
            hi = rules.number_range[1] if rules else 60
            step = max(1, (hi - lo) // (k + 1))
            nums = [lo + i * step for i in range(1, k + 1)]

        exp = f.explain(nums, rules)

        ui_header(f"FILTER DOCUMENTATION: {f.display_name.upper()}", f"Tier {f.tier} · {getattr(f, 'category', 'General')}")
        
        table = ui_table(title="Filter Metadata & Formal Specification", columns=["Property", "Specification"])
        table.add_row("Unique ID", f.unique_id)
        table.add_row("Tier", f"Tier {f.tier}")
        table.add_row("Category", getattr(f, "category", "General"))
        table.add_row("Description", getattr(f, "description", ""))
        if getattr(f, "formula", ""):
            table.add_row("Mathematical Formula", getattr(f, "formula", ""))
        console.print(table)

        if getattr(f, "diagram", ""):
            console.print("\n[bold cyan]─── Visual Decision Flow & Bounds ───[/bold cyan]")
            console.print(Panel(f.diagram, style="bright_blue", title="ASCII Circuit Diagram"))

        if getattr(f, "mermaid", ""):
            console.print("\n[dim]Mermaid Architecture Specification:[/dim]")
            console.print(f"[dim]{f.mermaid}[/dim]")

        console.print("\n[bold green]─── Dynamic Evaluation Walkthrough ───[/bold green]")
        res_table = ui_table(title=f"Evaluated Combination: {nums}", columns=["Metric", "Value", "Allowed", "Verdict"])
        res_table.add_row(
            f.display_name,
            str(exp.actual_value),
            exp.allowed_range,
            "[bold green]PASS ✓[/bold green]" if exp.passed else "[bold red]FAIL ✗[/bold red]"
        )
        console.print(res_table)
        console.print(f"\nDynamic ASCII Gauge: [bold]{exp.gauge}[/bold]")
        console.print(f"Summary Statement  : {exp.summary}\n")
        return

    if topic == "filters":
        ui_header("LOTTERY ENGINE FILTER CATALOG", "Consolidated 5-Tier Vectorized & Harmony Filter Framework")
        console.print("[dim]Use 'lottery docs --filter <unique_id>' to see interactive diagrams and dynamic evaluations.[/dim]\n")
        tiers = [tier] if tier else [1, 2, 3, 4, 5]
        for t in tiers:
            filters_in_tier = sorted(registry.list_by_tier(t), key=lambda x: x.unique_id)
            if not filters_in_tier:
                continue
            table = Table(title=f"Tier {t} Filters ({len(filters_in_tier)} total)")
            table.add_column("Unique ID", style="bold cyan", no_wrap=True)
            table.add_column("Name", style="bold")
            table.add_column("Category", style="green")
            table.add_column("Formula", style="dim")
            for f in filters_in_tier:
                table.add_row(
                    f.unique_id,
                    f.display_name,
                    getattr(f, "category", "General"),
                    getattr(f, "formula", "")[:45] + ("..." if len(getattr(f, "formula", "")) > 45 else "")
                )
            console.print(table)
        return

    sections: dict[str, str] = {

        "confidence": """
        [bold underline]CONFIDENCE SCORE[/bold underline]

        Every strategy output includes a [bold]confidence score[/bold] (0.0 to 1.0).
        A high confidence means the strategy found strong internal patterns in the 
        provided history that match the current state.
        """,

        "board": """
        [bold underline]BOARD ANALYTICS[/bold underline]
 
        The [bold]board[/bold] command provides grid-based visualizations of the number pool.
        It supports multiple views like 'balance' (odd/even, high/low), 'frame' (edges vs center),
        'coverage' (historical frequencies), and 'sacred' (non-Euclidean spherical projections and symmetry reports).
        """,

        "heatmap": """
        [bold underline]HEATMAPS: FREQUENCY VS POSITION[/bold underline]

        The engine uses two types of heatmaps to identify machine biases.
        1. Frequency Heatmap: Shows which numbers hit most often.
        2. Positional Heatmap: Shows which numbers prefer specific slots in the sorted draw.
        """,

        "filters": """
[bold underline]MATHEMATICAL FILTERS & COMBINATORIAL GATES[/bold underline]

The engine features a high-performance 5-tier vectorized filter engine (99 total filters)
with dual-mode game adaptability, bi-directional registry bridging, and dynamic visual gauges.

  - [bold]Tier 1 (Structural):[/bold] Parity, High/Low, AC Complexity, Digit/Unit sums, Decades.
  - [bold]Tier 2 (Positional):[/bold] Ordered ball bounds, adjacent gaps, variance, MAD, std dev.
  - [bold]Tier 3 (Algebraic):[/bold] Sum envelopes, digital roots, modular residues (mod 3, mod 4), Div-by-N.
  - [bold]Tier 4 (Historical):[/bold] Dual-mode adaptive bounds, co-occurrence pairs/triplets, repeats from t-1.
  - [bold]Tier 5 (Custom):[/bold] Banker locks, blacklist sets, graph edges (forbidden/required pairs), shells.

[bold yellow]QUICK DISCOVERY EXAMPLES:[/bold yellow]
  [bold]lottery docs filters[/bold]                                    Browse full catalog
  [bold]lottery docs filters --tier 1[/bold]                             Browse Tier 1 only
  [bold]lottery docs --filter structural_ac_value[/bold]                 Inspect AC with formulas & ASCII diagrams
  [bold]lottery docs --filter historical_ac_range --ticket 4,11,23,35,48,59[/bold]
  [bold]lottery docs --filter historical_median_range --game br/lotofacil --ticket 1,2,5,8,10,12,13,14,15,17,19,20,21,23,25[/bold]
  [bold]lottery docs --filter historical_common_pair[/bold]              Inspect co-occurrence graph filter
  [bold]lottery docs --filter positional_gap_1_2[/bold]                   Inspect sequential gap distributions
""",

        "lotteries": """
[bold underline]LOTTERIES[/bold underline]

Lotteries are identified as  [cyan]<country>/<game>[/cyan]  or by short alias.

  [bold]br/mega-sena[/bold]  (alias: mega-sena)
    Brazil — Mega-Sena. Pick 6 from 1–60. Draws: Tue, Thu, Sat.
    Jackpot rolls over until someone matches all 6.
    Data source: Caixa Econômica Federal API + community mirror.

  [bold]br/lotofacil[/bold]  (alias: lotofacil)
    Brazil — Lotofácil. Pick 15 from 1–25. Draws: Mon–Sat (6×/week).
    Prizes for matching 11–15 numbers. Highest win-rate lottery in Brazil.
    Jackpot always pays out — no rollover at the top tier.

  [bold]us/powerball[/bold]  (alias: powerball)
    USA — Powerball. Pick 5 from 1–69 + 1 Powerball from 1–26.
    Multi-state. Data source: NY Lottery open-data (Socrata).

  Data is stored in [dim]data/lottery.db[/dim] (DuckDB) and partitioned JSON.
  Re-run [bold]lottery fetch <name>[/bold] to refresh.
""",

        "analysis": """
[bold underline]ANALYSIS MODULES[/bold underline]

Run with:  [bold]lottery analyze <lottery> --module <name>[/bold]

  [bold]frequency[/bold]
    Counts how often each number has appeared across all draws.
    Reports hot numbers (appeared most), cold numbers (appeared least),
    and a chi-squared test to detect if the distribution is non-uniform.
    A low p-value (< 0.05) means the ball frequencies are statistically
    unequal — interesting but does not imply future predictability.

  [bold]deviation[/bold]
    Tracks how many draws have passed since each number last appeared.
    Numbers exceeding their expected return interval are flagged as
    "overdue". Expected interval = pool_size / pick_count.
    E.g. Mega-Sena: 60 / 6 = every 10 draws on average.

  [bold]correlation[/bold]
    Measures pairwise co-occurrence between numbers using lift:
      lift(A, B) = P(A and B in same draw) / (P(A) × P(B))
    Lift > 1  → appear together more than chance.
    Lift < 1  → appear together less than chance.
    Pairs near lift = 1 are independent (expected for a fair lottery).
""",

        "strategies": """
[bold underline]PREDICTION STRATEGIES[/bold underline]

The engine provides 40+ modular strategies across 5 functional tiers:

  [bold]statistical[/bold]  (fast, mathematical, zero external ML deps)
    frequency       — weights balls by all-time appearance count
    recency         — weights balls inversely by draws since last drawn
    markov          — 1st-order Markov chain: P(ball_i in draw_t | ball_j in draw_{t-1})
    copairs         — weights balls that historically co-occur with recent numbers
    stefan_mandel   — covers high-probability combinatorial clusters (Mandel algorithm)
    primes          — selects mathematically balanced prime subsets
    poisson         — models arrival rate of numbers via Poisson process
    ev_risk         — maximizes expected value while managing downside risk
    hazard_weibull  — parametric & empirical survival hazard modeling for overdue delays
    hurst_memory    — Hurst exponent long-term memory analysis
    spectral        — FFT periodicity detection across draw lags

  [bold]ml[/bold]  (learns non-linear patterns from historical lag features)
    logistic        — binary logistic regression per ball based on lag features
    random_forest   — ensemble of decision trees trained on historical lags
    gradient_boost  — LightGBM / XGBoost gradient boosted decision trees
    knn             — finds historically similar draw contexts (k-nearest neighbors)
    synapse         — neural consensus model across top statistical indicators

  [bold]deep[/bold]  (neural sequence and graph architectures)
    transformer     — self-attention model across chronological drawing series
    lstm / gru      — bidirectional recurrence over sequential multi-hot draws
    lstm_crf        — sequence logic brain modeling joint inter-ball constraints
    gnn             — graph neural network propagating spatial correlations

  [bold]foundation[/bold]  (zero-shot foundation forecasting)
    timesfm         — zero-shot Google TimesFM time-series foundation forecasting
    tabfm           — zero-shot TabPFN tabular classification on draw features

  [bold]fun / esoteric[/bold]  (entertainment, astronomical, and chaos physics)
    numerology, moon_phase, weather, biorhythm, sacred_manifold, trevo_sorte, seismic, solar

  [dim]Tip: See 'lottery docs ensemble', 'lottery docs temperature', 'lottery docs deep', or 'lottery docs fun'.[/dim]
""",

        "temperature": """
[bold underline]TEMPERATURE-BASED SAMPLING[/bold underline]

Borrowing from deep learning generation, temperature controls how scores
are translated into pick probabilities:

  [bold]--temp 0[/bold]   Deterministic — always takes the highest-scored numbers.

  [bold]--temp 1[/bold]   Proportional — picks according to score probabilities (default).
                Top numbers are more likely, but variance is preserved.

  [bold]--temp 0.5[/bold] Sharper — concentrates picks heavily on top candidates.

  [bold]--temp 2.0[/bold] Flatter / Exploratory — distributes picks more evenly across pool.
""",

        "ensemble": """
[bold underline]ENSEMBLE STRATEGIES[/bold underline]

Combining multiple strategies often outperforms any single one.

  [bold]Implicit voting ensemble[/bold] (comma-separated list):
    [cyan]lottery suggest br/mega-sena --strategy markov,bayesian,weighted[/cyan]
    → Equal-weight average of all three score dicts. Fast, zero extra configuration.

  [bold]voting:s1,s2,...[/bold]
    Explicit equal-weight consensus.

  [bold]prob_weighted:s1,s2,...[/bold]
    Each strategy is backtested on the last N draws. Strategies that
    predicted recent draws better get higher weight in the final blend.

  [bold]hybrid:s1,s2,...[/bold]
    Two-stage: prob_weighted narrows the candidate pool to top-K numbers,
    then the pattern strategy filters to combinations that match
    historical structural distributions.

  [bold]stacking:s1,s2,...[/bold]
    Meta-learner stacking ensemble combining strategy outputs via regression.
""",

        "deep": """
[bold underline]DEEP LEARNING ARCHITECTURES[/bold underline]

Requires: [bold]pip install ".[deep]"[/bold] (installs PyTorch / PyG)

  [bold]transformer[/bold]
    Decoder-only Transformer with multi-head self-attention. Encodes each draw
    as a multi-hot vector, projected to d_model=128 across 3 attention layers.

  [bold]lstm / gru[/bold]
    Bidirectional LSTM + Bidirectional GRU running in parallel to capture
    short-term and long-term sequential dependencies.

  [bold]lstm_crf[/bold]
    Sequence Logic Brain combining LSTM recurrent encodings with a Linear Chain
    Conditional Random Field (CRF) to learn legal combination transitions.

  [bold]cnn_1d[/bold]
    1D dilated convolutional network detecting multi-scale draw rhythms.

  [bold]gnn[/bold]
    Graph Neural Network running GCN message-passing over grid topology.
""",

        "fun": """
[bold underline]FUN / ESOTERIC / CHAOS STRATEGIES[/bold underline]

Entertainment and curiosity models that backtest against real historical data:

  [bold]numerology[/bold]       🔮 Pythagorean gematria, Life Path, and personal vibrations
  [bold]trevo_sorte[/bold]      🍀 Marcia Sensitiva & Pythagorean personal day alignment
  [bold]moon_phase[/bold]       🌕 Correlates draw dates with lunar synodic phases
  [bold]planetary_transits[/bold]🪐 Planetary transits, aspects, and Placidus astrological houses
  [bold]weather[/bold]          ⛅ Historical temperature, barometric pressure & precipitation
  [bold]solar / geomagnetic[/bold] ☀️ Space weather & NOAA Geomagnetic K-Index flux
  [bold]seismic[/bold]          🌋 USGS Tectonic plate seismic resonance
  [bold]biorhythm[/bold]        💓 Physical, emotional, and intellectual sinusoidal cycles
  [bold]sacred_manifold[/bold]  🌀 3D unit sphere projections aligned with celestial transit angles

[yellow]Note on Future Predictions:[/yellow]
Historical strategies like `weather`, `solar`, and `moon_phase` find empirical correlations
over historical draws. For future draws, unavailable environmental values revert to
a neutral confidence (0.5) to avoid skewing predictions.
""",

        "expert": """
[bold underline]EXPERT OPTIMIZATION & PORTFOLIO SIMULATION[/bold underline]

The [bold]expert-suggest[/bold] command is a comprehensive pipeline combining:
1. [bold]Zero-Config Backtests:[/bold] Out-of-sample grid-search to find the highest-performing strategy/history limit.
2. [bold]Adaptive Budgeting:[/bold] Maps standard or premium multiple bets under a BRL threshold (LotoFácil 16-pick, Mega-Sena 7-pick).
3. [bold]Portfolio Simulation:[/bold] Runs a financial paper-trading simulation over preceding draws, calculating start/end balances, ROI, and peak drawdown.
4. [bold]ASCII Trend Graph:[/bold] Renders physical sparklines of bankroll growth.
""",
    }

    if topic == "all":
        for k, v in sections.items():
            if k == "all": continue
            console.print(v)
            console.print("\n" + "─" * 40 + "\n")
    elif topic in sections:
        console.print(sections[topic])
    else:
        console.print(f"[red]Unknown topic '{topic}'.[/red] Available: {', '.join(sections.keys())}")
