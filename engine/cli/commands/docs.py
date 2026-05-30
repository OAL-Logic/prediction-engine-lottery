"""
Docs Command 📚
==============
Concept reference — explains how the engine works and how to use it effectively.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

console = Console()

def docs(
    topic: Annotated[str, typer.Argument(
        help="Topic: all | lotteries | analysis | strategies | temperature | ensemble | deep | fun"
    )] = "all",
) -> None:
    """📚 Concept reference — explains how the engine works and how to use it effectively."""
    topic = topic.lower()

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

Run with:  [bold]lottery suggest <lottery> --strategy <name>[/bold]

All strategies expose one interface:
  score(df, rules) → dict[number → 0..1]
Higher score = strategy thinks this number is more likely to appear.

  [bold cyan]Statistical tier[/bold cyan]  (no extra dependencies)

  [bold]markov[/bold]
    First-order Markov chain. Builds a transition matrix T[x, y] =
    P(y appears in next draw | x appeared in last draw).
    Scores next draw by averaging transition probabilities from
    the numbers in the most recent draw.

  [bold]bayesian[/bold]
    Dirichlet-Multinomial posterior. Treats frequency as a probability
    estimate with a prior. Supports recency decay so recent draws
    count more than old ones.

  [bold]monte_carlo[/bold]
    Simulates 10,000 future draws by sampling from a weighted
    distribution, then keeps only draws that match historical
    structural patterns (sum range, odd/even ratio). Numbers that
    appear in kept simulations score higher.

  [bold]weighted[/bold]
    Blends three signals: frequency (how hot?), gap (how overdue?),
    and positional tendency. Good default all-round strategy.

  [bold]pattern[/bold]
    Scores numbers by how often they participate in combinations that
    match historical structural patterns: sum range, odd/even ratio,
    high/low split, consecutive pair count.

  [bold]momentum[/bold]
    RSI-style frequency momentum. Computes recent_frequency / long_term_frequency
    for each number.

  [bold]spectral[/bold]
    FFT-based periodicity detection. Builds a binary time series per number,
    applies numpy FFT, finds the dominant cycle.

  [bold]streak[/bold]
    Hot/cold streak tracker. Counts appearances in the last N draws.
""",

        "temperature": """
[bold underline]TEMPERATURE-BASED SAMPLING[/bold underline]

Set with:  [bold]--temp <float>[/bold]  (default: 1.0)

Temperature controls how deterministic vs. exploratory ticket
generation is. Borrowed from language model sampling.

  [bold]--temp 0[/bold]   Deterministic — always picks the top-N scored numbers.
               Every run produces the same ticket.

  [bold]--temp 1[/bold]   Proportional — samples randomly weighted by score.
               Higher-scored numbers are more likely but not certain.

  [bold]--temp 0.5[/bold] Sharper — concentrates picks on the top candidates.

  [bold]--temp 2[/bold]   Flatter — distributes picks more evenly across all numbers.
""",

        "ensemble": """
[bold underline]ENSEMBLE STRATEGIES[/bold underline]

Combining multiple strategies often outperforms any single one.

  [bold]Implicit voting ensemble[/bold]  (comma-separated names)
    lottery suggest br/mega-sena --strategy markov,bayesian,weighted
    → Equal-weight average of all three score dicts. Fast, no config.

  [bold]voting:s1,s2,...[/bold]
    Explicit version of the above.

  [bold]prob_weighted:s1,s2,...[/bold]
    Each strategy is back-tested on the last N draws. Strategies that
    predicted recent draws better get higher weight in the final blend.

  [bold]hybrid:s1,s2,...[/bold]
    Two-stage: prob_weighted narrows the candidate pool to top-K numbers,
    then the pattern strategy filters to combinations that match
    historical structural distributions.
""",

        "deep": """
[bold underline]DEEP LEARNING STRATEGIES[/bold underline]

Requires:  [bold]pip install ".[deep]"[/bold]  (installs PyTorch)

  [bold]transformer[/bold]
    GPT-style decoder-only Transformer. Encodes each draw as a multi-hot
    vector, projects to d_model=128, runs through 3 layers of self-attention.

  [bold]lstm_gru[/bold]
    Bidirectional LSTM + Bidirectional GRU running in parallel.

  [bold]cnn_1d[/bold]
    1D dilated convolutional network. Detection of local sequential 
    patterns at multiple time scales.
""",

        "fun": """
[bold underline]FUN / ABSURDITY STRATEGIES[/bold underline]

These are clearly entertainment. They back-test against real historical
data, so sometimes they produce genuinely interesting correlations.

  [bold]numerology[/bold]  🔮
    Pythagorean numerology with three optional vibration layers.

  [bold]moon_phase[/bold]  🌕
    Correlates lottery draws with the lunar phase on the draw date.

  [bold]weather[/bold]  ⛅
    Correlates draws with historical temperature, pressure, and 
    weather conditions (Open-Meteo).

  [bold]sacred_manifold[/bold]  🌀
    Projects standard grid coordinates onto a 3D unit sphere and aligns
    number scores with real-time celestial transit angles (Lunar/Solar azimuth).

        [yellow]Note on Esoteric Strategies:[/yellow]
        `weather`, `solar`, and `moon_phase` rely on historical data to find 
        correlations. When predicting [bold]future[/bold] draws (where data is 
        not yet available), they revert to a [bold]neutral confidence score (0.5)[/bold] 
        to avoid skewing the ensemble with speculative noise.

        [bold underline]LOGGING & WARNINGS[/bold underline]

        The engine may issue [bold yellow]WARNING[/bold yellow] messages if a strategy is run
        near its "minimum data floor" (e.g. fewer draws than recommended for 
        statistical significance).

        To suppress these warnings, use the global [bold]--quiet[/bold] or [bold]-q[/bold] flag:
          lottery --quiet suggest br/lotofacil
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
