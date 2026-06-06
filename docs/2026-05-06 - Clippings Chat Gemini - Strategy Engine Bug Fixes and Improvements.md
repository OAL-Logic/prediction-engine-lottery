---
title: Strategy Engine Bug Fixes and Improvements
sources:
  - https://gemini.google.com/app/b5decf3aa9857bbe
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
  - "[[Chat Gemini]]"
handles:
published:
created: 2026-05-06T15:14:13-03:00
description: Gemini conversation with 2 messages
tags:
  - libraries/clippings/chats/gemini
---
# Strategy Engine Bug Fixes and Improvements

saved: 2026-05-06T15-14-13

## User Message

You said

analyze and create a series of tasks to fix the issues and also find improvements to make in the docs or implementation

  

python3 -m engine.cli.main analyze lotofacil

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching ANALYZE                                                                                        │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Module:  dashboard                                                                                     │

│   Top:  10                                                                                               │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ LottoLogic Terminal Dashboard: Lotofácil (Window: last 100)                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────── Automated Insight Ribbon ────────────────────────────────────────╮

│ ● Regime: Statistical distribution appears stable.                                                       │

│ ● Overdue: Number 14 is significantly overdue (4d).                                                      │

│ ● Cycle: Current cycle is nearly complete (96.0%). Watch missing numbers: \[14\].                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Top Performers (Z-Scor─╮╭─ Spatial Voids (Cold Ro─╮╭───────────────── Market Overview ──────────────────╮

│  Rank  Num  Z-Score     ││  Sector  Delay          ││                                                    │

│  1     10     +1.45     ││                         ││ Latest Draw: \[4, 5, 6, 8, 10, 13, 15, 16, 18, 19,  │

│  2     4      +1.05     ││                         ││ 21, 22, 23, 24, 25\]                                │

│  3     6      +1.05     ││                         ││ Latest Sum:  229 (OUT band)                        │

│  4     20     +1.05     ││                         ││                                                    │

│  5     23     +0.79     ││                         ││ Row Pattern: 2-3-2-3-5 (2% rarity)                 │

│                         ││                         ││                                                    │

│                         ││                         ││ Sum History (30d):                                 │

│                         ││                         ││ ▇▃▇▅▅▅▃▅▅▅▅▅▅▅▃▅▅▅▃▅▅▃▅▅▃▅▅▇▅▇                     │

│                         ││                         ││                                                    │

│                         ││                         ││ Cycle Progress:                                    │

│                         │╰─────────────────────────╯│ ████████████████████████░ 96.0%                    │

│                         │╭── Structural Harmony ───╮│   Remaining in cycle: \[14\]...                      │

│                         ││  AC Value  7            ││                                                    │

│                         ││  Root Sum  4            ││                                                    │

│                         ││  Unit Sum  69           ││                                                    │

│                         ││                         ││                                                    │

│                         ││                         ││                                                    │

╰─────────────────────────╯│                         ││                                                    │

╭─ Overdue vs Max Delay ──╮│                         ││                                                    │

│  Num  Delay  Max        ││                         ││                                                    │

│  14      4d   12        ││                         ││                                                    │

│  1       3d    8        ││                         ││                                                    │

│  11      3d    9        ││                         ││                                                    │

│  9       2d    9        │╰─────────────────────────╯│                                                    │

│  20      2d    9        │╭──── Clusters & Gaps ────╮│                                                    │

│                         ││  Max Gap       3        ││                                                    │

│                         ││  Succ. Groups  4        ││                                                    │

│                         ││  Spread        21       ││                                                    │

│                         ││ ─────────────────────── ││                                                    │

│                         ││ Gap History (30d):      ││                                                    │

│                         ││ ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ ││                                                    │

│                         ││ ▃▃▃▃▃▃▃                 ││                                                    │

│                         ││                         ││                                                    │

│                         ││                         ││                                                    │

│                         ││                         ││                                                    │

│                         ││                         ││                                                    │

│                         ││                         ││                                                    │

╰─────────────────────────╯╰─────────────────────────╯╰────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Press Ctrl+C to exit. Data current as of last fetch.                                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main docs

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

        CONFIDENCE SCORE

  

        Every strategy output includes a confidence score (0.0 to 1.0).

        A high confidence means the strategy found strong internal patterns in the

        provided history that match the current state.

  

  

────────────────────────────────────────

  

  

        BOARD ANALYTICS

  

        The board command provides grid-based visualizations of the number pool.

        It supports multiple views like 'balance' (odd/even, high/low), 'frame' (edges vs center),

        and 'coverage' (historical pattern frequencies).

  

  

────────────────────────────────────────

  

  

        HEATMAPS: FREQUENCY VS POSITION

  

        The engine uses two types of heatmaps to identify machine biases.

        1. Frequency Heatmap: Shows which numbers hit most often.

        2. Positional Heatmap: Shows which numbers prefer specific slots in the sorted draw.

  

  

────────────────────────────────────────

  

  

LOTTERIES

  

Lotteries are identified as  <country>/<game>  or by short alias.

  

  br/mega-sena  (alias: mega-sena)

    Brazil — Mega-Sena. Pick 6 from 1–60. Draws: Tue, Thu, Sat.

    Jackpot rolls over until someone matches all 6.

    Data source: Caixa Econômica Federal API + community mirror.

  

  br/lotofacil  (alias: lotofacil)

    Brazil — Lotofácil. Pick 15 from 1–25. Draws: Mon–Sat (6×/week).

    Prizes for matching 11–15 numbers. Highest win-rate lottery in Brazil.

    Jackpot always pays out — no rollover at the top tier.

  

  us/powerball  (alias: powerball)

    USA — Powerball. Pick 5 from 1–69 + 1 Powerball from 1–26.

    Multi-state. Data source: NY Lottery open-data (Socrata).

  

  Data is stored in data/lottery.db (DuckDB) and partitioned JSON.

  Re-run lottery fetch <name> to refresh.

  

  

────────────────────────────────────────

  

  

ANALYSIS MODULES

  

Run with:  lottery analyze <lottery> --module <name>

  

  frequency

    Counts how often each number has appeared across all draws.

    Reports hot numbers (appeared most), cold numbers (appeared least),

    and a chi-squared test to detect if the distribution is non-uniform.

    A low p-value (< 0.05) means the ball frequencies are statistically

    unequal — interesting but does not imply future predictability.

  

  deviation

    Tracks how many draws have passed since each number last appeared.

    Numbers exceeding their expected return interval are flagged as

    "overdue". Expected interval = pool\_size / pick\_count.

    E.g. Mega-Sena: 60 / 6 = every 10 draws on average.

  

  correlation

    Measures pairwise co-occurrence between numbers using lift:

      lift(A, B) = P(A and B in same draw) / (P(A) × P(B))

    Lift > 1  → appear together more than chance.

    Lift < 1  → appear together less than chance.

    Pairs near lift = 1 are independent (expected for a fair lottery).

  

  

────────────────────────────────────────

  

  

PREDICTION STRATEGIES

  

Run with:  lottery suggest <lottery> --strategy <name>

  

All strategies expose one interface:

  score(df, rules) → dict

Higher score = strategy thinks this number is more likely to appear.

  

  Statistical tier  (no extra dependencies)

  

  markov

    First-order Markov chain. Builds a transition matrix T =

    P(y appears in next draw | x appeared in last draw).

    Scores next draw by averaging transition probabilities from

    the numbers in the most recent draw.

  

  bayesian

    Dirichlet-Multinomial posterior. Treats frequency as a probability

    estimate with a prior. Supports recency decay so recent draws

    count more than old ones.

  

  monte\_carlo

    Simulates 10,000 future draws by sampling from a weighted

    distribution, then keeps only draws that match historical

    structural patterns (sum range, odd/even ratio). Numbers that

    appear in kept simulations score higher.

  

  weighted

    Blends three signals: frequency (how hot?), gap (how overdue?),

    and positional tendency. Good default all-round strategy.

  

  pattern

    Scores numbers by how often they participate in combinations that

    match historical structural patterns: sum range, odd/even ratio,

    high/low split, consecutive pair count.

  

  momentum

    RSI-style frequency momentum. Computes recent\_frequency / long\_term\_frequency

    for each number.

  

  spectral

    FFT-based periodicity detection. Builds a binary time series per number,

    applies numpy FFT, finds the dominant cycle.

  

  streak

    Hot/cold streak tracker. Counts appearances in the last N draws.

  

  

────────────────────────────────────────

  

  

TEMPERATURE-BASED SAMPLING

  

Set with:  --temp <float>  (default: 1.0)

  

Temperature controls how deterministic vs. exploratory ticket

generation is. Borrowed from language model sampling.

  

  --temp 0   Deterministic — always picks the top-N scored numbers.

               Every run produces the same ticket.

  

  --temp 1   Proportional — samples randomly weighted by score.

               Higher-scored numbers are more likely but not certain.

  

  --temp 0.5 Sharper — concentrates picks on the top candidates.

  

  --temp 2   Flatter — distributes picks more evenly across all numbers.

  

  

────────────────────────────────────────

  

  

ENSEMBLE STRATEGIES

  

Combining multiple strategies often outperforms any single one.

  

  Implicit voting ensemble  (comma-separated names)

    lottery suggest br/mega-sena --strategy markov,bayesian,weighted

    → Equal-weight average of all three score dicts. Fast, no config.

  

  voting:s1,s2,...

    Explicit version of the above.

  

  prob\_weighted:s1,s2,...

    Each strategy is back-tested on the last N draws. Strategies that

    predicted recent draws better get higher weight in the final blend.

  

  hybrid:s1,s2,...

    Two-stage: prob\_weighted narrows the candidate pool to top-K numbers,

    then the pattern strategy filters to combinations that match

    historical structural distributions.

  

  

────────────────────────────────────────

  

  

DEEP LEARNING STRATEGIES

  

Requires:  pip install "."  (installs PyTorch)

  

  transformer

    GPT-style decoder-only Transformer. Encodes each draw as a multi-hot

    vector, projects to d\_model=128, runs through 3 layers of self-attention.

  

  lstm\_gru

    Bidirectional LSTM + Bidirectional GRU running in parallel.

  

  cnn\_1d

    1D dilated convolutional network. Detection of local sequential

    patterns at multiple time scales.

  

  

────────────────────────────────────────

  

  

FUN / ABSURDITY STRATEGIES

  

These are clearly entertainment. They back-test against real historical

data, so sometimes they produce genuinely interesting correlations.

  

  numerology  🔮

    Pythagorean numerology with three optional vibration layers.

  

  moon\_phase  🌕

    Correlates lottery draws with the lunar phase on the draw date.

  

  weather  ⛅

    Correlates draws with historical temperature, pressure, and

    weather conditions (Open-Meteo).

  

  

────────────────────────────────────────

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main suggest lotofacil                                                              /home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching SUGGESTION ENGINE                                                                              │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  \['weighted'\]                                                                              │

│   Temp:  1.0                                                                                             │

│   Pick:  15                                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

WEIGHTED  confidence=0.295 (29.5%)

  Parameters: w\_frequency=1.0, w\_gap=1.0, w\_position=0.5

  Ticket 1: \[1, 2, 3, 4, 5, 6, 9, 11, 13, 18, 19, 21, 22, 24, 25\]  (sum=183)

            Hist wins: match 11: 330 | match 12: 72 | match 13: 8 | match 14: 0 | match 15: 0

  Top scored: \[1, 25, 24, 2, 4\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                          │

│ 🧠 Noosphere Jitter: Coherent (Jitter Score: 0.691) | Regime: Default Resonance                          │

│ 🌀 Chaos Entropy Boost: +0.3 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main backtest lotofacil

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching BACKTEST                                                                                       │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Count:  1                                                                                              │

│   Temp:  0.0                                                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

⚠ Provide either DRAW\_ID(s) or use --prev/-p.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main backtest lotofacil --help

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main backtest \[OPTIONS\] LOTTERY \[DRAW\_ID\]

  

 Evaluate one or more strategies against one or more historical draws.

  

 This command performs "blind" testing: if you choose strategies, it only

 gives them access to draws that happened BEFORE the one you are testing.

 Supports multiple strategies (comma-separated), IDs, and ranges.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT       Lottery name \[required\]                                                     │

│      draw\_id      \[DRAW\_ID\]  Draw number(s) (concurso), range (e.g. 2990-2999), or comma-separated list  │

│                              to test                                                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --prev      -p                  TEXT     Relative index or range (e.g. 1, 1-5, 1,2,5) from latest        │

│ --strategy  -s                  TEXT     Strategy name(s). Supports comma-separated list (e.g.           │

│                                          'weighted,markov') or 'all'.                                    │

│ --numbers   -n                  TEXT     Specific numbers to check against the draw. E.g. '4 12 23 35 47 │

│                                          60'                                                             │

│ --count     -c                  INTEGER  Number of tickets to generate (if using --strategy)             │

│                                          \[default: 1\]                                                    │

│ --temp      -t                  FLOAT    Sampling temperature (if using --strategy) \[default: 0.0\]       │

│ --limit     -L                  INTEGER  History limit (recency bias): only use the most recent N draws  │

│                                          for scoring                                                     │

│ --summary       --no-summary             Show a summary report at the end when testing multiple draws    │

│                                          \[default: summary\]                                              │

│ --map       -m                           Show board heatmap for each target draw                         │

│ --help                                   Show this message and exit.                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main backtest lotofacil --prev 1-5 -s all -c 1 -m

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching BACKTEST                                                                                       │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  all                                                                                         │

│   Count:  1                                                                                              │

│   Temp:  0.0                                                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

─────────────────────────────── BACKTEST — Lotofácil Draw 3672 (2026-04-28) ────────────────────────────────

  Winning Numbers: 1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 16, 20, 23, 24, 25

  

  

Simulating strategy: numerology

  Result: Avg Rank: 12.6 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: kabbalistic

  Result: Avg Rank: 11.2 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: solar

  Result: Avg Rank: 13.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: moon\_phase

  Result: Avg Rank: 10.8 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: weather

  Result: Avg Rank: 9.9 | Top-15 Hits: 12 | Ticket Hits: \[12\]

  

Simulating strategy: biorhythm

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: fibonacci

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: zodiac

  Result: Avg Rank: 12.5 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: sefirot

  Result: Avg Rank: 11.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: noosphere

  Result: Avg Rank: 12.4 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: iching

  Result: Avg Rank: 12.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: ley\_lines

  Result: Avg Rank: 14.0 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: sentiment

  Result: Avg Rank: 12.9 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: lorentz

  Result: Avg Rank: 13.5 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: reincarnation

  Result: Avg Rank: 12.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: entropy\_global

  Result: Avg Rank: 11.2 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: gematria

  Result: Avg Rank: 15.8 | Top-15 Hits: 6 | Ticket Hits: \[6\]

  

Simulating strategy: refraction

  Result: Avg Rank: 10.7 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: seismic

  Result: Avg Rank: 11.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: vix\_jitter

  Result: Avg Rank: 10.1 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: markov

  Result: Avg Rank: 10.4 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: bayesian

  Result: Avg Rank: 12.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: monte\_carlo

  Result: Avg Rank: 13.6 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: weighted

  Result: Avg Rank: 12.5 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: pattern

  Result: Avg Rank: 15.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: momentum

  Result: Avg Rank: 12.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: spectral

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: streak

  Result: Avg Rank: 12.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: crowd\_avoidance

  Result: Avg Rank: 13.9 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: steiner\_wheel

  Result: Avg Rank: 10.4 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: survival

  Result: Avg Rank: 13.4 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: primes

  Result: Avg Rank: 13.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: quantum\_anneal

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: void

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: copairs

  Result: Avg Rank: 12.9 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: cycle

  Result: Avg Rank: 12.8 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: mutual\_info

  Result: Avg Rank: 12.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: stability

  Result: Avg Rank: 12.5 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: harmonic

  Result: Avg Rank: 15.4 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: fisher

  Result: Avg Rank: 10.7 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: advanced

  Result: Avg Rank: 12.8 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: positional

  Result: Avg Rank: 13.8 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: contagion

  Result: Avg Rank: 10.5 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: hedge

  Result: Avg Rank: 12.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: voting

  Result: Avg Rank: 12.0 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: prob\_weighted

  Result: Avg Rank: 12.0 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: hybrid

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: stacking

Failed: pip install 'lottery-engine' for stacking ensemble

  

Simulating strategy: synapse

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

─────────────────────────────── BACKTEST — Lotofácil Draw 3673 (2026-04-29) ────────────────────────────────

  Winning Numbers: 1, 3, 4, 8, 10, 11, 12, 15, 16, 18, 19, 20, 21, 22, 25

  

  

Simulating strategy: numerology

  Result: Avg Rank: 12.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: kabbalistic

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: solar

  Result: Avg Rank: 13.4 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: moon\_phase

  Result: Avg Rank: 14.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: weather

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: biorhythm

  Result: Avg Rank: 14.0 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: fibonacci

  Result: Avg Rank: 13.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: zodiac

  Result: Avg Rank: 17.1 | Top-15 Hits: 6 | Ticket Hits: \[6\]

  

Simulating strategy: sefirot

  Result: Avg Rank: 11.5 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: noosphere

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: iching

  Result: Avg Rank: 11.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: ley\_lines

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: sentiment

  Result: Avg Rank: 14.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: lorentz

  Result: Avg Rank: 14.5 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: reincarnation

  Result: Avg Rank: 14.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: entropy\_global

  Result: Avg Rank: 13.6 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: gematria

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: refraction

  Result: Avg Rank: 12.9 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: seismic

  Result: Avg Rank: 12.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: vix\_jitter

  Result: Avg Rank: 11.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: markov

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: bayesian

  Result: Avg Rank: 11.3 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: monte\_carlo

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: weighted

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: pattern

  Result: Avg Rank: 14.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: momentum

  Result: Avg Rank: 14.5 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: spectral

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: streak

  Result: Avg Rank: 14.8 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: crowd\_avoidance

  Result: Avg Rank: 13.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: steiner\_wheel

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: survival

  Result: Avg Rank: 12.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: primes

  Result: Avg Rank: 15.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: quantum\_anneal

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: void

  Result: Avg Rank: 12.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: copairs

  Result: Avg Rank: 12.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: cycle

  Result: Avg Rank: 12.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: mutual\_info

  Result: Avg Rank: 13.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: stability

  Result: Avg Rank: 13.0 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: harmonic

  Result: Avg Rank: 15.1 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: fisher

  Result: Avg Rank: 14.0 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: advanced

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: positional

  Result: Avg Rank: 12.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: contagion

  Result: Avg Rank: 11.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: hedge

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: voting

  Result: Avg Rank: 12.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: prob\_weighted

  Result: Avg Rank: 12.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: hybrid

  Result: Avg Rank: 12.9 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: stacking

Failed: pip install 'lottery-engine' for stacking ensemble

  

Simulating strategy: synapse

  Result: Avg Rank: 14.4 | Top-15 Hits: 9 | Ticket Hits: \[9\]

─────────────────────────────────── BACKTEST — Lotofácil Draw 3674 (NaT) ───────────────────────────────────

  Winning Numbers: 2, 6, 7, 8, 9, 10, 15, 17, 19, 20, 21, 22, 23, 24, 25

  

  

Simulating strategy: numerology

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: kabbalistic

  Result: Avg Rank: 15.2 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: solar

  Result: Avg Rank: 13.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: moon\_phase

  Result: Avg Rank: 12.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: weather

  Result: Avg Rank: 15.2 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: biorhythm

  Result: Avg Rank: 12.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: fibonacci

  Result: Avg Rank: 15.0 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: zodiac

  Result: Avg Rank: 13.0 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: sefirot

  Result: Avg Rank: 14.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: noosphere

  Result: Avg Rank: 13.5 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: iching

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: ley\_lines

  Result: Avg Rank: 13.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: sentiment

  Result: Avg Rank: 15.2 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: lorentz

  Result: Avg Rank: 11.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: reincarnation

  Result: Avg Rank: 12.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: entropy\_global

  Result: Avg Rank: 14.6 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: gematria

  Result: Avg Rank: 10.4 | Top-15 Hits: 12 | Ticket Hits: \[12\]

  

Simulating strategy: refraction

  Result: Avg Rank: 14.2 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: seismic

  Result: Avg Rank: 13.4 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: vix\_jitter

  Result: Avg Rank: 13.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: markov

  Result: Avg Rank: 14.2 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: bayesian

  Result: Avg Rank: 12.5 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: monte\_carlo

  Result: Avg Rank: 12.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: weighted

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: pattern

  Result: Avg Rank: 15.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: momentum

  Result: Avg Rank: 14.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: spectral

  Result: Avg Rank: 13.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: streak

  Result: Avg Rank: 14.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: crowd\_avoidance

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: steiner\_wheel

  Result: Avg Rank: 14.4 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: survival

  Result: Avg Rank: 12.6 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: primes

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: quantum\_anneal

  Result: Avg Rank: 13.4 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: void

  Result: Avg Rank: 11.5 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: copairs

  Result: Avg Rank: 13.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: cycle

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: mutual\_info

  Result: Avg Rank: 15.2 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: stability

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: harmonic

  Result: Avg Rank: 15.6 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: fisher

  Result: Avg Rank: 14.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: advanced

  Result: Avg Rank: 12.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: positional

  Result: Avg Rank: 13.6 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: contagion

  Result: Avg Rank: 14.1 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: hedge

  Result: Avg Rank: 16.2 | Top-15 Hits: 6 | Ticket Hits: \[6\]

  

Simulating strategy: voting

  Result: Avg Rank: 13.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: prob\_weighted

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: hybrid

  Result: Avg Rank: 13.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: stacking

Failed: pip install 'lottery-engine' for stacking ensemble

  

Simulating strategy: synapse

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

─────────────────────────────────── BACKTEST — Lotofácil Draw 3675 (NaT) ───────────────────────────────────

  Winning Numbers: 2, 3, 4, 5, 7, 8, 10, 12, 13, 15, 17, 18, 19, 23, 24

  

  

Simulating strategy: numerology

  Result: Avg Rank: 15.0 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: kabbalistic

  Result: Avg Rank: 12.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: solar

Failed: invalid literal for int() with base 10: 'NaT'

  

Simulating strategy: moon\_phase

  Result: Avg Rank: 14.4 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: weather

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=-23.5505&longitude=-46.6333&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 12.4 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: biorhythm

  Result: Avg Rank: 12.9 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: fibonacci

  Result: Avg Rank: 12.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: zodiac

  Result: Avg Rank: 10.8 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: sefirot

  Result: Avg Rank: 13.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: noosphere

  Result: Avg Rank: 12.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: iching

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: ley\_lines

  Result: Avg Rank: 12.1 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: sentiment

  Result: Avg Rank: 10.8 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: lorentz

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: reincarnation

Failed: Invalid isoformat string: 'NaT'

  

Simulating strategy: entropy\_global

  Result: Avg Rank: 11.8 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: gematria

  Result: Avg Rank: 14.1 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: refraction

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=30.4518&longitude=-84.2727&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 14.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: seismic

  Result: Avg Rank: 13.8 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: vix\_jitter

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: markov

  Result: Avg Rank: 14.5 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: bayesian

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: monte\_carlo

  Result: Avg Rank: 14.7 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: weighted

  Result: Avg Rank: 13.6 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: pattern

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: momentum

  Result: Avg Rank: 11.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: spectral

  Result: Avg Rank: 14.7 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: streak

  Result: Avg Rank: 12.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: crowd\_avoidance

  Result: Avg Rank: 14.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: steiner\_wheel

  Result: Avg Rank: 13.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: survival

  Result: Avg Rank: 12.7 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: primes

  Result: Avg Rank: 10.5 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: quantum\_anneal

  Result: Avg Rank: 12.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: void

  Result: Avg Rank: 13.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: copairs

  Result: Avg Rank: 12.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: cycle

  Result: Avg Rank: 12.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: mutual\_info

  Result: Avg Rank: 12.0 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: stability

  Result: Avg Rank: 14.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: harmonic

  Result: Avg Rank: 13.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: fisher

  Result: Avg Rank: 12.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: advanced

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: positional

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: contagion

  Result: Avg Rank: 15.9 | Top-15 Hits: 6 | Ticket Hits: \[6\]

  

Simulating strategy: hedge

  Result: Avg Rank: 12.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: voting

  Result: Avg Rank: 14.4 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: prob\_weighted

  Result: Avg Rank: 14.4 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: hybrid

  Result: Avg Rank: 13.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: stacking

Failed: pip install 'lottery-engine' for stacking ensemble

  

Simulating strategy: synapse

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=30.4518&longitude=-84.2727&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 12.4 | Top-15 Hits: 10 | Ticket Hits: \[10\]

─────────────────────────────────── BACKTEST — Lotofácil Draw 3676 (NaT) ───────────────────────────────────

  Winning Numbers: 4, 5, 6, 8, 10, 13, 15, 16, 18, 19, 21, 22, 23, 24, 25

  

  

Simulating strategy: numerology

  Result: Avg Rank: 14.6 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: kabbalistic

  Result: Avg Rank: 12.5 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: solar

Failed: invalid literal for int() with base 10: 'NaT'

  

Simulating strategy: moon\_phase

  Result: Avg Rank: 12.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: weather

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=-23.5505&longitude=-46.6333&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 12.8 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: biorhythm

  Result: Avg Rank: 11.6 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: fibonacci

  Result: Avg Rank: 14.0 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: zodiac

  Result: Avg Rank: 13.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: sefirot

  Result: Avg Rank: 13.4 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: noosphere

  Result: Avg Rank: 12.4 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: iching

  Result: Avg Rank: 13.4 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: ley\_lines

  Result: Avg Rank: 12.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: sentiment

  Result: Avg Rank: 12.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: lorentz

  Result: Avg Rank: 11.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: reincarnation

Failed: Invalid isoformat string: 'NaT'

  

Simulating strategy: entropy\_global

  Result: Avg Rank: 13.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: gematria

  Result: Avg Rank: 14.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: refraction

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=30.4518&longitude=-84.2727&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: seismic

  Result: Avg Rank: 13.5 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: vix\_jitter

  Result: Avg Rank: 14.4 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: markov

  Result: Avg Rank: 14.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: bayesian

  Result: Avg Rank: 13.2 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: monte\_carlo

  Result: Avg Rank: 11.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: weighted

  Result: Avg Rank: 12.3 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: pattern

  Result: Avg Rank: 13.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: momentum

  Result: Avg Rank: 13.5 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: spectral

  Result: Avg Rank: 12.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: streak

  Result: Avg Rank: 13.2 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: crowd\_avoidance

  Result: Avg Rank: 11.9 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: steiner\_wheel

  Result: Avg Rank: 14.1 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: survival

  Result: Avg Rank: 12.5 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: primes

  Result: Avg Rank: 14.3 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: quantum\_anneal

  Result: Avg Rank: 14.7 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: void

  Result: Avg Rank: 13.5 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: copairs

  Result: Avg Rank: 14.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: cycle

  Result: Avg Rank: 14.9 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: mutual\_info

  Result: Avg Rank: 15.3 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: stability

  Result: Avg Rank: 12.9 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: harmonic

  Result: Avg Rank: 13.1 | Top-15 Hits: 9 | Ticket Hits: \[9\]

  

Simulating strategy: fisher

  Result: Avg Rank: 14.6 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: advanced

  Result: Avg Rank: 11.7 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: positional

  Result: Avg Rank: 12.2 | Top-15 Hits: 11 | Ticket Hits: \[11\]

  

Simulating strategy: contagion

  Result: Avg Rank: 14.2 | Top-15 Hits: 7 | Ticket Hits: \[7\]

  

Simulating strategy: hedge

  Result: Avg Rank: 13.3 | Top-15 Hits: 8 | Ticket Hits: \[8\]

  

Simulating strategy: voting

  Result: Avg Rank: 13.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: prob\_weighted

  Result: Avg Rank: 13.2 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: hybrid

  Result: Avg Rank: 13.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

  

Simulating strategy: stacking

Failed: pip install 'lottery-engine' for stacking ensemble

  

Simulating strategy: synapse

  ⚠ Weather fetch failed: Client error '400 Bad Request' for url 'https://archive-api.open-meteo.com/v1/archive?latitude=30.4518&longitude=-84.2727&start\_date=NaT&end\_date=NaT&daily=temperature\_2m\_mean,precipitation\_sum,windspeed\_10m\_max,surface\_pressure\_mean&timezone=auto'

For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400

  Result: Avg Rank: 12.1 | Top-15 Hits: 10 | Ticket Hits: \[10\]

                         BACKTEST COMPARISON SUMMARY

┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓

┃ Strategy        ┃ Avg Rank ┃ Top-N Capture ┃ Best Hit ┃ Win Rate (min 11) ┃

┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩

│ numerology      │     13.7 │    45 (60.0%) │       10 │              0.0% │

│ kabbalistic     │     12.6 │    47 (62.7%) │       11 │             20.0% │

│ solar           │     13.4 │    27 (60.0%) │       10 │              0.0% │

│ moon\_phase      │     13.0 │    47 (62.7%) │       11 │             20.0% │

│ weather         │     12.4 │    47 (62.7%) │       12 │             20.0% │

│ biorhythm       │     12.8 │    45 (60.0%) │       11 │             20.0% │

│ fibonacci       │     13.5 │    43 (57.3%) │       10 │              0.0% │

│ zodiac          │     13.3 │    44 (58.7%) │       11 │             20.0% │

│ sefirot         │     12.8 │    47 (62.7%) │       10 │              0.0% │

│ noosphere       │     12.7 │    47 (62.7%) │       10 │              0.0% │

│ iching          │     12.8 │    46 (61.3%) │       10 │              0.0% │

│ ley\_lines       │     13.0 │    47 (62.7%) │       11 │             20.0% │

│ sentiment       │     13.1 │    46 (61.3%) │       11 │             20.0% │

│ lorentz         │     12.6 │    46 (61.3%) │       10 │              0.0% │

│ reincarnation   │     13.0 │    27 (60.0%) │       10 │              0.0% │

│ entropy\_global  │     13.0 │    43 (57.3%) │       11 │             20.0% │

│ gematria        │     13.5 │    42 (56.0%) │       12 │             20.0% │

│ refraction      │     13.3 │    44 (58.7%) │       11 │             20.0% │

│ seismic         │     13.0 │    46 (61.3%) │       10 │              0.0% │

│ vix\_jitter      │     12.9 │    44 (58.7%) │       11 │             20.0% │

│ markov          │     13.1 │    43 (57.3%) │       11 │             20.0% │

│ bayesian        │     12.9 │    47 (62.7%) │       11 │             40.0% │

│ monte\_carlo     │     13.0 │    43 (57.3%) │       10 │              0.0% │

│ weighted        │     12.9 │    46 (61.3%) │       10 │              0.0% │

│ pattern         │     14.2 │    41 (54.7%) │        9 │              0.0% │

│ momentum        │     13.3 │    41 (54.7%) │        9 │              0.0% │

│ spectral        │     13.3 │    42 (56.0%) │        9 │              0.0% │

│ streak          │     13.3 │    43 (57.3%) │       10 │              0.0% │

│ crowd\_avoidance │     13.1 │    44 (58.7%) │       10 │              0.0% │

│ steiner\_wheel   │     12.9 │    45 (60.0%) │       11 │             20.0% │

│ survival        │     12.7 │    47 (62.7%) │       10 │              0.0% │

│ primes          │     13.4 │    44 (58.7%) │       11 │             20.0% │

│ quantum\_anneal  │     13.3 │    46 (61.3%) │       10 │              0.0% │

│ void            │     13.1 │    44 (58.7%) │       10 │              0.0% │

│ copairs         │     13.0 │    43 (57.3%) │       10 │              0.0% │

│ cycle           │     12.8 │    44 (58.7%) │       10 │              0.0% │

│ mutual\_info     │     13.8 │    42 (56.0%) │       10 │              0.0% │

│ stability       │     13.4 │    43 (57.3%) │       10 │              0.0% │

│ harmonic        │     14.6 │    38 (50.7%) │        9 │              0.0% │

│ fisher          │     13.2 │    42 (56.0%) │       11 │             20.0% │

│ advanced        │     12.4 │    48 (64.0%) │       10 │              0.0% │

│ positional      │     13.1 │    47 (62.7%) │       11 │             20.0% │

│ contagion       │     13.3 │    41 (54.7%) │       11 │             20.0% │

│ hedge           │     13.5 │    42 (56.0%) │       10 │              0.0% │

│ voting          │     13.1 │    45 (60.0%) │       10 │              0.0% │

│ prob\_weighted   │     13.1 │    45 (60.0%) │       10 │              0.0% │

│ hybrid          │     12.9 │    46 (61.3%) │       10 │              0.0% │

│ synapse         │     12.8 │    48 (64.0%) │       10 │              0.0% │

└─────────────────┴──────────┴───────────────┴──────────┴───────────────────┘

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main backtest wheel --help

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main backtest \[OPTIONS\] LOTTERY \[DRAW\_ID\]

  

 Evaluate one or more strategies against one or more historical draws.

  

 This command performs "blind" testing: if you choose strategies, it only

 gives them access to draws that happened BEFORE the one you are testing.

 Supports multiple strategies (comma-separated), IDs, and ranges.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT       Lottery name \[required\]                                                     │

│      draw\_id      \[DRAW\_ID\]  Draw number(s) (concurso), range (e.g. 2990-2999), or comma-separated list  │

│                              to test                                                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --prev      -p                  TEXT     Relative index or range (e.g. 1, 1-5, 1,2,5) from latest        │

│ --strategy  -s                  TEXT     Strategy name(s). Supports comma-separated list (e.g.           │

│                                          'weighted,markov') or 'all'.                                    │

│ --numbers   -n                  TEXT     Specific numbers to check against the draw. E.g. '4 12 23 35 47 │

│                                          60'                                                             │

│ --count     -c                  INTEGER  Number of tickets to generate (if using --strategy)             │

│                                          \[default: 1\]                                                    │

│ --temp      -t                  FLOAT    Sampling temperature (if using --strategy) \[default: 0.0\]       │

│ --limit     -L                  INTEGER  History limit (recency bias): only use the most recent N draws  │

│                                          for scoring                                                     │

│ --summary       --no-summary             Show a summary report at the end when testing multiple draws    │

│                                          \[default: summary\]                                              │

│ --map       -m                           Show board heatmap for each target draw                         │

│ --help                                   Show this message and exit.                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main backtest wheel

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching BACKTEST                                                                                       │

│   Lottery:  wheel (wheel)                                                                                │

│   Count:  1                                                                                              │

│   Temp:  0.0                                                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Lottery 'wheel' is not available or has no historical data adapter yet.

Available: br/mega-sena, br/lotofacil, us/powerball

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main wheel lotofacil --help

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main wheel \[OPTIONS\] LOTTERY

  

 Generate combinatorial wheels for a pool of numbers.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*  --pool       -p      TEXT     Space/comma-separated list of numbers to wheel \[required\]               │

│    --mode       -m      TEXT     Wheel type: full | key | abbreviated \[default: full\]                    │

│    --keys       -k      TEXT     Numbers that MUST appear in every ticket (for key mode)                 │

│    --guarantee  -g      INTEGER  Match guarantee (e.g. 4 for '4 if 6') \[default: 4\]                      │

│    --test               TEXT     Evaluate wheel against these winning numbers                            │

│    --help                        Show this message and exit.                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main wheel lotofacil --pool 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching WHEEL                                                                                          │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Pool:  1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25                               │

│   Mode:  full                                                                                            │

│   Guarantee:  4                                                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

         Full Wheel (25 numbers → 3268760 tickets)

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓

┃  # ┃ Numbers                                             ┃

┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩

│  1 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15\] │

│  2 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16\] │

│  3 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17\] │

│  4 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18\] │

│  5 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19\] │

│  6 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20\] │

│  7 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21\] │

│  8 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 22\] │

│  9 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 23\] │

│ 10 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24\] │

│ 11 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 25\] │

│ 12 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16\] │

│ 13 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17\] │

│ 14 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 18\] │

│ 15 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 19\] │

│ 16 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 20\] │

│ 17 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 21\] │

│ 18 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 22\] │

│ 19 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 23\] │

│ 20 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 24\] │

│ 21 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 25\] │

│ 22 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17\] │

│ 23 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 18\] │

│ 24 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 19\] │

│ 25 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 20\] │

│ 26 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 21\] │

│ 27 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 22\] │

│ 28 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 23\] │

│ 29 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 24\] │

│ 30 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 25\] │

│ 31 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18\] │

│ 32 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 19\] │

│ 33 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 20\] │

│ 34 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 21\] │

│ 35 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 22\] │

│ 36 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 23\] │

│ 37 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 24\] │

│ 38 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 25\] │

│ 39 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 19\] │

│ 40 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 20\] │

│ 41 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 21\] │

│ 42 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 22\] │

│ 43 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 23\] │

│ 44 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 24\] │

│ 45 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 25\] │

│ 46 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 20\] │

│ 47 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 21\] │

│ 48 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 22\] │

│ 49 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 23\] │

│ 50 │ \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 24\] │

└────┴─────────────────────────────────────────────────────┘

  ... and 3268710 more tickets.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main audit-data --help                                                              /home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main audit-data \[OPTIONS\] LOTTERY

  

 Audit the integrity of cached data for a lottery.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --help          Show this message and exit.                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main audit-data lotofacil

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────────────── Data Audit: Lotofácil ───────────────────────────────────────────

  ✓ Draw Continuity: 3676 sequential draws.

  

  Statistical Anomaly Dashboard (Z-Scores):

    - Global Freq:  Chi2: 23.97 (p=0.4631)

  

  Atmospheric Physics Layer (v12.0):

    - Refractive Index (N): Modeling static charge potential...

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main export --help                                                                  /home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main export \[OPTIONS\] LOTTERY

  

 Export draw history to JSON or CSV.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --format  -f      TEXT  json | csv \[default: json\]                                                       │

│ --output  -o      TEXT  Output filename                                                                  │

│ --help                  Show this message and exit.                                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?2

❯ python3 -m engine.cli.main export lotofacil -f csv

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

✓ Exported 3676 draws to lotofacil\_export.csv

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board --help

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  

 Usage: python -m engine.cli.main board \[OPTIONS\] LOTTERY

  

 Advanced Board Analytics showing Pattern Coverage, Balance, Clusters, Voids, Halves, and Row-of-10.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --view     -v      TEXT     balance | coverage | cluster | heatmap | sparsity | void | halves | row10 |  │

│                             adjacency | advanced | convergence | somas | simulation                      │

│                             \[default: heatmap\]                                                           │

│ --limit    -L      INTEGER  Use only the N most recent draws \[default: 20\]                               │

│ --numbers  -n      TEXT     Mark these numbers on the board (e.g. '1 13 32')                             │

│ --cols     -C      INTEGER  Override number of columns in the grid                                       │

│ --help                      Show this message and exit.                                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (HEATMAP) ──────────────────────────────────

  Board Frequency

 Heatmap: Lotofácil

  

  1   2   3   4   5

  6   7   8   9  10

 11  12  13  14  15

 16  17  18  19  20

 21  22  23  24  25

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v balance

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (BALANCE) ──────────────────────────────────

                                   Recent Draw Balance

 Draw  Numbers                                                   Odd/Even  High/Low  Sum

 3657  \[1, 2, 4, 7, 8, 10, 12, 13, 17, 18, 19, 20, 22, 23, 24\]    6O-9E     7H-8L    200

 3658  \[2, 3, 4, 5, 9, 10, 11, 12, 13, 16, 18, 20, 22, 23, 24\]    6O-9E     6H-9L    192

 3659  \[3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 23, 25\]     10O-5E    6H-9L    182

 3660  \[1, 2, 5, 6, 7, 8, 10, 11, 12, 14, 17, 18, 22, 23, 24\]     6O-9E     6H-9L    180

 3661  \[2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 19, 21, 23, 24\]      7O-8E     6H-9L    173

 3662  \[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 18, 20, 23, 25\]     8O-7E     5H-10L   186

 3663  \[1, 3, 4, 5, 6, 10, 12, 14, 17, 19, 20, 22, 23, 24, 25\]    7O-8E     8H-7L    205

 3664  \[1, 2, 4, 5, 6, 7, 10, 11, 12, 16, 18, 19, 20, 22, 23\]     6O-9E     6H-9L    176

 3665  \[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 16, 18, 22, 23, 25\]      9O-6E     5H-10L   171

 3666  \[1, 4, 6, 7, 9, 12, 14, 15, 16, 17, 19, 20, 21, 22, 23\]    8O-7E     9H-6L    206

 3667  \[1, 3, 4, 5, 6, 7, 9, 11, 14, 15, 19, 21, 22, 23, 25\]      11O-4E    7H-8L    185

 3668  \[1, 2, 3, 5, 7, 8, 9, 10, 11, 13, 15, 17, 18, 21, 24\]      10O-5E    5H-10L   164

 3669  \[2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16, 17, 22, 23, 24\]     7O-8E     6H-9L    181

 3670  \[1, 2, 3, 5, 6, 10, 11, 14, 15, 17, 18, 19, 21, 23, 24\]    9O-6E     8H-7L    189

 3671  \[1, 3, 4, 5, 6, 7, 9, 10, 12, 13, 15, 16, 17, 18, 21\]      9O-6E     5H-10L   157

 3672  \[1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 16, 20, 23, 24, 25\]    9O-6E     6H-9L    193

 3673  \[1, 3, 4, 8, 10, 11, 12, 15, 16, 18, 19, 20, 21, 22, 25\]   7O-8E     8H-7L    205

 3674  \[2, 6, 7, 8, 9, 10, 15, 17, 19, 20, 21, 22, 23, 24, 25\]    8O-7E     9H-6L    228

 3675  \[2, 3, 4, 5, 7, 8, 10, 12, 13, 15, 17, 18, 19, 23, 24\]     8O-7E     6H-9L    180

 3676  \[4, 5, 6, 8, 10, 13, 15, 16, 18, 19, 21, 22, 23, 24, 25\]   7O-8E     9H-6L    229

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v coverage

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (COVERAGE) ─────────────────────────────────

⚠ View 'coverage' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v cluster

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (CLUSTER) ──────────────────────────────────

⚠ View 'cluster' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v heatmap

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (HEATMAP) ──────────────────────────────────

  Board Frequency

 Heatmap: Lotofácil

  

  1   2   3   4   5

  6   7   8   9  10

 11  12  13  14  15

 16  17  18  19  20

 21  22  23  24  25

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v sparsity

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (SPARSITY) ─────────────────────────────────

⚠ View 'sparsity' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v void

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

─────────────────────────────────── Advanced Analytics: Lotofácil (VOID) ───────────────────────────────────

⚠ View 'void' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v halves

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────── Advanced Analytics: Lotofácil (HALVES) ──────────────────────────────────

⚠ View 'halves' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v row10

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────── Advanced Analytics: Lotofácil (ROW10) ───────────────────────────────────

⚠ View 'row10' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v adjacency

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (ADJACENCY) ─────────────────────────────────

⚠ View 'adjacency' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v advanced

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (ADVANCED) ─────────────────────────────────

⚠ View 'advanced' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v convergence

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

─────────────────────────────── Advanced Analytics: Lotofácil (CONVERGENCE) ────────────────────────────────

⚠ View 'convergence' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v somas

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────── Advanced Analytics: Lotofácil (SOMAS) ───────────────────────────────────

⚠ View 'somas' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v simulation

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (SIMULATION) ────────────────────────────────

⚠ View 'simulation' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !21 ?3

❯ python3 -m engine.cli.main board lotofacil -v simulation

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (SIMULATION) ────────────────────────────────

⚠ View 'simulation' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !22 ?3

❯ python3 -m engine.cli.main board lotofacil -v simulation

/home/ag/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py:22: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.9.0' currently installed).

  from pandas.core.computation.check import NUMEXPR\_INSTALLED

/home/ag/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.5' currently installed).

  from pandas.core import (

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (SIMULATION) ────────────────────────────────

⚠ View 'simulation' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !22 ?3

❯ source ./.venv/bin/python

\[2\] 847843

\[3\] 847844

./.venv/bin/python:1: no matches found: ^@^F^@^@^@^D^@^@^@@^@^@^@^@^@^@^@@^@@^@^@^@^@^@@^@@^@^@^@^@^@^P^C^@^@^@^@^@^@^P^C^@^@^@^@^@^@^H^@^@^@^@^@^@^@^C^@^@^@^D^@^@^@P^C^@^@^@^@^@^@P^C@^@^@^@^@^@P^C@^@^@^@^@^@^\\^@^@^@^@^@^@^@^\\^@^@^@^@^@^@^@^A^@^@^@^@^@^@^@^A^@^@^@^D^@^@^@^@^@^@^@^@^@^@^@^@^@@^@^@^@^@^@^@^@@^@^@^@^@^@^@\\M-v^A^@^@^@^@^@^@\\M-v^A^@^@^@^@^@^@^P^@^@^@^@^@^@^A^@^@^@^E^@^@^@^@^@^B^@^@^@^@^@^@^@B^@^@^@^@^@^@^@B^@^@^@^@^@\\M--+.^@^@^@^@^@\\M--+.^@^@^@^@^@^@^P^@^@^@^@^@^@^A^@^@^@^D^@^@^@^@00^@^@^@^@^@^@0p^@^@^@^@^@^@0p^@^@^@^@^@\\M-h?2^@^@^@^@^@\\M-h?2^@^@^@^@^@^@^P^@^@^@^@^@^@^A^@^@^@^F^@^@^@\\M-H}b^@^@^@^@^@\\M-H}\\M-"^@^@^@^@^@\\M-H}\\M-"^@^@^@^@^@\\M-8\\M-Z^W^@^@^@^@^@\\M-@^R^X^@^@^@^@^@^@^P^@^@^@^@^@^@^B^@^@^@^F^@^@^@\\M-X}b^@^@^@^@^@\\M-X}\\M-"^@^@^@^@^@\\M-X}\\M-"^@^@^@^@^@^@^B^@^@^@^@^@^@^@^B^@^@^@^@^@^@^H^@^@^@^@^@^@^@^D^@^@^@^D^@^@^@p^C^@^@^@^@^@^@p^C@^@^@^@^@^@p^C@^@^@^@^@^@

./.venv/bin/python:1: no matches found: Rkt^D^@^@^@^P^@^@^@^A^@^@^@GNU^@^@^@^@^@^C^@^@^@^B^@^@^@^@^@^@^@^@^@^@^@\\M-p^C^@^@\\M-a^A^@^@^@^A^@^@^N^@^@^@^@\\M-^H\\M-^TQ^E^D\\M-H\*^@^@

\[2\]  - 847843 exit 1     ELF      >

\[3\]  + 847844 exit 1

./.venv/bin/python:1: command not found: ^PD

./.venv/bin/python:2: no matches found: P^@^@^E\\M-^L\\M-^A^A^C\\M-^@\\M-H\*^Q^F^TQ^A\\M-H^H^@^H^H^D\\M-^@^@8^@^\[^@^E^@^@^H\\M-^P^A\\M-(@^@\\M-l^D\\M-@\\M-^@!^T^P^@!^P

./.venv/bin/python:3: bad pattern: 822431^A\\M-^@^P^@^@\\M-^B^@\\M-\\t%(^H@ ^D^H@^H^@@\\M-^@^A^B\\M-^A@B^A^H\\M-z^@P^H^ZB^K^@^@^@^H^@^A\\n^@^@\\n^R^B\\M-^@^H^L^Q\\M-^@^@^@\\M-^D\\M-q^@P^@\\M-^@Z^C\\M-^@^Q^C\\M-^SX^@j^@^E^@^B\\M-^U^P\\M-^H^V@^B^U^H^A\\M-^@-^X^B^H^T\\M-\*\\M-1\\M-^P\\M-#\\M-^E\*\\M-^AТ\\M-^P^T^A^@^@@^P\\M- ^@ \\M-^@ \\M-@\\M-^L^P0^@E^H^D0^H^M\\M-^@^T^@\\M-^L^PP^@\\M-^@\\t^@@2\\M-^H1j^@^@$^Q@Ԁ\\M- 0

./.venv/bin/python:5: command not found: \\M-^D\\M-@X^A

./.venv/bin/python:5: command not found: \\M-^A

./.venv/bin/python:1: command not found: AD^H\\M-^D@\\M-^B\\M-^H@\\M-@

./.venv/bin/python:6: command not found: \\t\\M-^D^L^DQ^FDP0͎B^D\\M-X^D^\[C#^HX^Hp@^D

./.venv/bin/python:8: parse error near \`)'

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !22 ?3

❯ lottery --help

zsh: command not found: lottery

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !22 ?3

❯ exit                                                                                                      

\[process exited with code 127 (0x0000007f)\]

You can now close this terminal with Ctrl+D, or press Enter to restart.

 ~

 ~

❯

 ~

❯

 ~

❯ source ./.venv/bin/activate

 ~                                                                                                   ag Py

❯ pip install -e .

Obtaining file:///home/ag

ERROR: file:///home/ag does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.

 ~                                                                                                   ag Py

❯ exit

  

\[process exited with code 1 (0x00000001)\]

You can now close this terminal with Ctrl+D, or press Enter to restart.

 ~

❯ cd "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery"

 /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery  main !1 ?1

❯ cd .gemini/worktrees/2026-04-29-02-45-06-737-l63k

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !24 ?2

❯ source ./.venv/bin/activate

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !24 ?2

❯ pip install -e .

Obtaining file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/%28P%29%20Prediction%20Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k

  Installing build dependencies ... done

  Checking if build backend supports build\_editable ... done

  Getting requirements to build editable ... done

  Preparing editable metadata (pyproject.toml) ... done

Requirement already satisfied: pandas>=2.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (3.0.2)

Requirement already satisfied: numpy>=1.26 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (2.4.4)

Requirement already satisfied: scipy>=1.13 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.17.1)

Requirement already satisfied: httpx>=0.27 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (0.28.1)

Requirement already satisfied: typer>=0.12 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (0.25.0)

Requirement already satisfied: rich>=13 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (15.0.0)

Requirement already satisfied: PyYAML>=6.0 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (6.0.3)

Requirement already satisfied: duckdb>=1.0 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.5.2)

Requirement already satisfied: numexpr>=2.10.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (2.14.1)

Requirement already satisfied: bottleneck>=1.4.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.6.0)

Requirement already satisfied: anyio in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (4.13.0)

Requirement already satisfied: certifi in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (2026.4.22)

Requirement already satisfied: httpcore==1.\* in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (1.0.9)

Requirement already satisfied: idna in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (3.13)

Requirement already satisfied: h11>=0.16 in ./.venv/lib/python3.12/site-packages (from httpcore==1.\*->httpx>=0.27->lottery-engine==0.1.0) (0.16.0)

Requirement already satisfied: python-dateutil>=2.8.2 in ./.venv/lib/python3.12/site-packages (from pandas>=2.2->lottery-engine==0.1.0) (2.9.0.post0)

Requirement already satisfied: six>=1.5 in ./.venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas>=2.2->lottery-engine==0.1.0) (1.17.0)

Requirement already satisfied: markdown-it-py>=2.2.0 in ./.venv/lib/python3.12/site-packages (from rich>=13->lottery-engine==0.1.0) (4.0.0)

Requirement already satisfied: pygments<3.0.0,>=2.13.0 in ./.venv/lib/python3.12/site-packages (from rich>=13->lottery-engine==0.1.0) (2.20.0)

Requirement already satisfied: mdurl~=0.1 in ./.venv/lib/python3.12/site-packages (from markdown-it-py>=2.2.0->rich>=13->lottery-engine==0.1.0) (0.1.2)

Requirement already satisfied: click>=8.2.1 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (8.3.3)

Requirement already satisfied: shellingham>=1.3.0 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (1.5.4)

Requirement already satisfied: annotated-doc>=0.0.2 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (0.0.4)

Requirement already satisfied: typing\_extensions>=4.5 in ./.venv/lib/python3.12/site-packages (from anyio->httpx>=0.27->lottery-engine==0.1.0) (4.15.0)

Building wheels for collected packages: lottery-engine

  Building editable for lottery-engine (pyproject.toml) ... done

  Created wheel for lottery-engine: filename=lottery\_engine-0.1.0-0.editable-py3-none-any.whl size=6111 sha256=d03c41a08e9deba073d8a80036649aed74234d28aa084db58ffccd063265d232

  Stored in directory: /tmp/pip-ephem-wheel-cache-uuz\_rnwd/wheels/b1/eb/2a/8c48ea7712fce4a0a7d4c6403025b823d3866665f91804ea3c

Successfully built lottery-engine

Installing collected packages: lottery-engine

  Attempting uninstall: lottery-engine

    Found existing installation: lottery-engine 0.1.0

    Uninstalling lottery-engine-0.1.0:

      Successfully uninstalled lottery-engine-0.1.0

Successfully installed lottery-engine-0.1.0

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ .venv/bin/pip install -e .

Obtaining file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/%28P%29%20Prediction%20Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k

  Installing build dependencies ... done

  Checking if build backend supports build\_editable ... done

  Getting requirements to build editable ... done

  Preparing editable metadata (pyproject.toml) ... done

Requirement already satisfied: pandas>=2.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (3.0.2)

Requirement already satisfied: numpy>=1.26 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (2.4.4)

Requirement already satisfied: scipy>=1.13 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.17.1)

Requirement already satisfied: httpx>=0.27 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (0.28.1)

Requirement already satisfied: typer>=0.12 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (0.25.0)

Requirement already satisfied: rich>=13 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (15.0.0)

Requirement already satisfied: PyYAML>=6.0 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (6.0.3)

Requirement already satisfied: duckdb>=1.0 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.5.2)

Requirement already satisfied: numexpr>=2.10.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (2.14.1)

Requirement already satisfied: bottleneck>=1.4.2 in ./.venv/lib/python3.12/site-packages (from lottery-engine==0.1.0) (1.6.0)

Requirement already satisfied: anyio in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (4.13.0)

Requirement already satisfied: certifi in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (2026.4.22)

Requirement already satisfied: httpcore==1.\* in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (1.0.9)

Requirement already satisfied: idna in ./.venv/lib/python3.12/site-packages (from httpx>=0.27->lottery-engine==0.1.0) (3.13)

Requirement already satisfied: h11>=0.16 in ./.venv/lib/python3.12/site-packages (from httpcore==1.\*->httpx>=0.27->lottery-engine==0.1.0) (0.16.0)

Requirement already satisfied: python-dateutil>=2.8.2 in ./.venv/lib/python3.12/site-packages (from pandas>=2.2->lottery-engine==0.1.0) (2.9.0.post0)

Requirement already satisfied: six>=1.5 in ./.venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas>=2.2->lottery-engine==0.1.0) (1.17.0)

Requirement already satisfied: markdown-it-py>=2.2.0 in ./.venv/lib/python3.12/site-packages (from rich>=13->lottery-engine==0.1.0) (4.0.0)

Requirement already satisfied: pygments<3.0.0,>=2.13.0 in ./.venv/lib/python3.12/site-packages (from rich>=13->lottery-engine==0.1.0) (2.20.0)

Requirement already satisfied: mdurl~=0.1 in ./.venv/lib/python3.12/site-packages (from markdown-it-py>=2.2.0->rich>=13->lottery-engine==0.1.0) (0.1.2)

Requirement already satisfied: click>=8.2.1 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (8.3.3)

Requirement already satisfied: shellingham>=1.3.0 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (1.5.4)

Requirement already satisfied: annotated-doc>=0.0.2 in ./.venv/lib/python3.12/site-packages (from typer>=0.12->lottery-engine==0.1.0) (0.0.4)

Requirement already satisfied: typing\_extensions>=4.5 in ./.venv/lib/python3.12/site-packages (from anyio->httpx>=0.27->lottery-engine==0.1.0) (4.15.0)

Building wheels for collected packages: lottery-engine

  Building editable for lottery-engine (pyproject.toml) ... done

  Created wheel for lottery-engine: filename=lottery\_engine-0.1.0-0.editable-py3-none-any.whl size=6111 sha256=0194356d084ccf97776e62353332c130326035135313fb4ada3c3ca92f1c2e96

  Stored in directory: /tmp/pip-ephem-wheel-cache-s5n9pcnb/wheels/b1/eb/2a/8c48ea7712fce4a0a7d4c6403025b823d3866665f91804ea3c

Successfully built lottery-engine

Installing collected packages: lottery-engine

  Attempting uninstall: lottery-engine

    Found existing installation: lottery-engine 0.1.0

    Uninstalling lottery-engine-0.1.0:

      Successfully uninstalled lottery-engine-0.1.0

Successfully installed lottery-engine-0.1.0

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ lottery --help

  

 Usage: lottery \[OPTIONS\] COMMAND \[ARGS\]...

  

  

 lottery-engine — statistical analysis & ticket suggestion for lottery draws.

  

  

 QUICK START

 -----------

   lottery fetch br/mega-sena          Download & cache historical draw data

   lottery wizard                      Interactive step-by-step guidance (Recommended)

   lottery analyze br/mega-sena        Frequency analysis (hot/cold numbers)

   lottery suggest br/mega-sena        Generate a ticket using the default strategy

   lottery hedge br/mega-sena          Generate a self-paying lower-tier portfolio (NEW)

   lottery backtest br/mega-sena 2990  Evaluate strategy performance on a past draw

   lottery party                       Multi-persona brainstorming session (NEW)

   lottery daemon br/mega-sena         Start AutoML background optimizer (NEW)

   lottery report config.yaml          Run scheduled/automated reporting pipelines (NEW)

   lottery daily br/lotofacil          Morning digest: regime+scan+EV+ticket+oracle (NEW)

   lottery next br/lotofacil           One-liner: scan + consensus ticket (NEW)

   lottery alert br/lotofacil          Cron monitor: exit 0 if GO, 1 if quiet (NEW)

   lottery watchlist add br/lotofacil  Track a game; run batch daily/alert/scan (NEW)

   lottery combo-rank br/lotofacil             Rank draw-property profiles by historical frequency (NEW)

   lottery draw-clock br/lotofacil             Draws-until-next-expected-hit countdown per number (NEW)

   lottery entropy-scan br/lotofacil           Shannon entropy regime analysis over rolling windows (NEW)

   lottery cold-streak-alert br/lotofacil      Cron alert: exit 0 if any number hits extreme cold streak

 (NEW)

   lottery synergy-map br/lotofacil "1 3..."   Pairwise co-occurrence lift matrix for a given ticket (NEW)

   lottery ticket-dna br/lotofacil "1 3..."    7-dimension structural fingerprint vs draw population (NEW)

   lottery frequency-band br/lotofacil         HOT/WARM/COLD tiers across 3 time horizons per number (NEW)

   lottery multi-ticket br/lotofacil --count 4  Diverse ticket portfolio with maximised pool coverage (NEW)

   lottery oracle br/mega-sena         Consult the high-intelligence oracle (NEW)

   lottery risk br/mega-sena           Kelly Criterion bet sizing analysis (NEW)

   lottery strategies                  List every available prediction strategy

   lottery docs                        Full concept reference (read this first)

  

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --storage                   TEXT  Storage backend: duckdb | json \[default: duckdb\]                       │

│ --install-completion              Install completion for the current shell.                              │

│ --show-completion                 Show completion for the current shell, to copy it or customize the     │

│                                   installation.                                                          │

│ --help                            Show this message and exit.                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────╮

│ docs                Concept reference — explains how the engine works and how to use it effectively.     │

│ fetch               Fetch and cache historical draw data for a lottery.                                  │

│ analyze             Run statistical analysis modules or a unified dashboard.                             │

│ suggest             Generate ticket suggestions using a specific prediction strategy.                    │

│ wizard              Interactive wizard to guide you through lottery analysis and prediction.             │

│ backtest            Evaluate one or more strategies against one or more historical draws.                │

│ dashboard           High-fidelity Terminal Dashboard with real-time multi-panel analysis.                │

│ wheel               Generate combinatorial wheels for a pool of numbers.                                 │

│ audit-data          Audit the integrity of cached data for a lottery.                                    │

│ export              Export draw history to JSON or CSV.                                                  │

│ board               Advanced Board Analytics showing Pattern Coverage, Balance, Clusters, Voids, Halves, │

│                     and Row-of-10.                                                                       │

│ portfolio           Generate a diversified ticket portfolio (Statistical, Chaos, and Deep tiers).        │

│ party               Launch 'Party Mode' to brainstorm and generate a chaotic/math hybrid ticket.         │

│ report              Execute a scheduled report or diagnostic pipeline from a config file.                │

│ signal              📡 Signal-to-Noise rolling window stability analysis.                                │

│ cluster             🔬 Unsupervised clustering of historical draw patterns.                              │

│ stress-test         ⚡ Adversarial stress-test: inject true randomness and compare strategy response.    │

│ detect-patterns     🔭 Esoteric Overlay: detect if esoteric cycle markers correlate with stable signal   │

│                     windows.                                                                             │

│ leaderboard         🏆 Comparative diagnostic leaderboard across multiple strategies.                    │

│ scan                🔬 Unified pre-draw conditions scan — one command for GO/NO-GO.                      │

│ log                 📓 Append a daily diagnostic snapshot to a persistent log file.                      │

│ log-view            📋 View recent entries from the daily log.                                           │

│ forecast            🔮 Weighted ensemble consensus ticket.                                               │

│ compare-draws       🔀 Compare recent draw window against history to detect regime shifts.               │

│ trend               📈 Visualise multi-week diagnostic trends from the daily log.                        │

│ next                ⚡ One-liner: scan conditions + generate consensus ticket if GO.                     │

│ risk                ⚖️ Kelly Criterion bet sizing and Expected Value analysis.                           │

│ oracle              Generate natural-language betting advice based on hard data.                         │

│ daemon              Start the AutoML Background Daemon to continuously optimize strategies.              │

│                     Runs silently in the background and saves the optimal config to                      │

│                     data/daemon\_state.json.                                                              │

│ hedge               Generate an optimized 'Hedge Portfolio' designed to maximize lower-tier returns.     │

│                     Creates a set of tickets where winnings from Match 4/11 are mathematically           │

│                     prioritized to offset the cost of the bet.                                           │

│ daily               📰 Comprehensive morning digest — all diagnostics in one pass.                       │

│ alert               🚨 Condition monitor — outputs only when an alert condition is met.                  │

│ hitcheck            🎯 Compare logged tickets against actual draw results.                               │

│ weekly              📅 Weekly performance summary from JSONL logs.                                       │

│ calibrate           🎯 Empirical strategy calibration — rank by actual out-of-sample hit rates.          │

│ log-export          📤 Export JSONL logs to CSV/TSV/JSON for external analysis.                          │

│ rank-numbers        🔢 Composite per-number ranking across all strategies.                               │

│ picks               🃏 Consensus ticket from recently logged forecasts.                                  │

│ number-timeline     📈 Historical hit pattern for a single pool number.                                  │

│ compare-strategies  ⚖️ Side-by-side ticket comparison across all strategies.                             │

│ streak-report       🔥 All-pool hot/cold streak overview.                                                │

│ pair-analysis       🔗 Co-occurrence frequency analysis for number pairs.                                │

│ draw-summary        🎯 Contextual analysis of a specific draw vs historical patterns.                    │

│ session             🎲 All-in-one pre-draw decision session.                                             │

│ ticket-grade        🎓 Grade a ticket against engine diagnostics.                                        │

│ pool-stats          📊 Distributional statistics for draw outcomes.                                      │

│ history-scan        📅 Retrospective GO/NO-GO timeline across historical draw windows.                   │

│ number-heat         🌡️ Compact heatmap of all pool numbers × recent draws.                               │

│ suggest-swaps       🔄 Suggest best number swaps to improve a ticket.                                    │

│ quick               ⚡ Fastest path to a ticket: scan + forecast in one command.                         │

│ variance-report     📉 Volatility regime analysis — how predictable is the draw process?                 │

│ coverage-check      🗺️ Pool coverage analysis for one or more tickets.                                   │

│ momentum-check      📊 Moving-average momentum indicators for all pool numbers.                          │

│ gap-forecast        🔮 Poisson-based overdue analysis for all pool numbers.                              │

│ combo-rank          🎯 Rank draw-property profiles (sum+parity+consecutive) by frequency.                │

│ draw-clock          ⏰ Draws-until-next-hit countdown for every pool number.                             │

│ entropy-scan        🔬 Shannon entropy analysis of draw distribution over rolling windows.               │

│ cold-streak-alert   🥶 Cron-safe alert when pool numbers reach extreme cold streaks.                     │

│ synergy-map         🕸️ Pairwise co-occurrence lift matrix for a given ticket.                            │

│ ticket-dna          🧬 Structural fingerprint of a ticket vs historical draw population.                 │

│ frequency-band      📡 Multi-horizon frequency tier classification for all pool numbers.                 │

│ multi-ticket        🎟️ Generate a portfolio of N diverse tickets with maximised pool coverage.           │

│ history             Chronological Draw Navigator — browse previous results.                              │

│ compare-bets        Compare your set of numbers against historical draws to see past performance.        │

│ simulate            Run a high-fidelity historical simulation of a specific ticket.                      │

│ savings             Wheel Savings Calculator — compare the cost of a wheel vs. a full large bet.         │

│ optimize            Search for the best strategy configuration.                                          │

│ calendar            Generate a personal Kabbalistic calendar of Favorable Days and Karmic Cycles.        │

│ signature           Analyze Name for Negative Sequences (for entertainment only).                        │

│ check               Check a ticket's structural patterns against historical rules.                       │

│ validate            Quickly check if a set of numbers is valid for a given lottery's rules.              │

│ serve               🚀 Start the FastAPI Sidecar (REST API).                                             │

│ games               List all supported lotteries in the registry.                                        │

│ strategies          List all available prediction strategies.                                            │

│ watchlist           📋 Manage and batch-run tracked lottery games.                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v simulation

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (SIMULATION) ────────────────────────────────

⚠ View 'simulation' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v somas

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────── Advanced Analytics: Lotofácil (SOMAS) ───────────────────────────────────

⚠ View 'somas' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v convergence

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

─────────────────────────────── Advanced Analytics: Lotofácil (CONVERGENCE) ────────────────────────────────

⚠ View 'convergence' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v advanced

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

───────────────────────────────── Advanced Analytics: Lotofácil (ADVANCED) ─────────────────────────────────

⚠ View 'advanced' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v adjacency

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

──────────────────────────────── Advanced Analytics: Lotofácil (ADJACENCY) ─────────────────────────────────

⚠ View 'adjacency' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board lotofacil -v row10

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────── Advanced Analytics: Lotofácil (ROW10) ───────────────────────────────────

⚠ View 'row10' is currently being modularized or is not supported.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main board portfolio --help

  

 Usage: python -m engine.cli.main board \[OPTIONS\] LOTTERY

  

 Advanced Board Analytics showing Pattern Coverage, Balance, Clusters, Voids, Halves, and Row-of-10.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --view     -v      TEXT     balance | coverage | cluster | heatmap | sparsity | void | halves | row10 |  │

│                             adjacency | advanced | convergence | somas | simulation                      │

│                             \[default: heatmap\]                                                           │

│ --limit    -L      INTEGER  Use only the N most recent draws \[default: 20\]                               │

│ --numbers  -n      TEXT     Mark these numbers on the board (e.g. '1 13 32')                             │

│ --cols     -C      INTEGER  Override number of columns in the grid                                       │

│ --help                      Show this message and exit.                                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main portfolio --help

  

 Usage: python -m engine.cli.main portfolio \[OPTIONS\] LOTTERY

  

 Generate a diversified ticket portfolio (Statistical, Chaos, and Deep tiers).

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name \[required\]                                                          │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --full-name         TEXT  Full birth name for Kabbalistic numerology \[default: GEMINI ENGINE\]            │

│ --birth-date        TEXT  Birthday (YYYY-MM-DD) \[default: 1990-01-01\]                                    │

│ --help                    Show this message and exit.                                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main portfolio lotofacil --full-name Operator D --birth-date 1900-01-01

Usage: python -m engine.cli.main portfolio \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main portfolio --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra arguments (Operator D)                                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main portfolio lotofacil --full-name GEMINI ENGINE --birth-date 1900-01-01          Usage: python -m engine.cli.main portfolio \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main portfolio --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (ENGINE)                                                                   │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main portfolio lotofacil --full-name "Operator D" --birth-date "1900-01-01"

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

────────────────────────────────────── Strategic Portfolio: Lotofácil ──────────────────────────────────────

  

  Statistical (Nerd)

    • hybrid          : \[1, 2, 4, 5, 6, 7, 9, 11, 13, 20, 21, 22, 23, 24, 25\]  (conf: 0.38)

    • mutual\_info     : \[4, 5, 6, 8, 10, 13, 15, 16, 18, 19, 21, 22, 23, 24, 25\]  (conf: 0.62)

  

  Chaos (Esoteric)

    • kabbalistic     : \[1, 3, 4, 5, 6, 7, 9, 10, 12, 15, 18, 19, 20, 23, 25\]  (conf: 0.69)

    • reincarnation   : \[1, 2, 3, 5, 7, 9, 10, 12, 14, 16, 17, 19, 23, 24, 25\]  (conf: 0.74)

  

  Deep Learning (AI)

    • transformer     : \[1, 3, 4, 9, 10, 12, 13, 14, 15, 18, 19, 20, 22, 23, 25\]  (conf: 0.57)

    • cnn\_1d          : \[1, 2, 3, 4, 6, 10, 11, 12, 13, 18, 21, 22, 23, 24, 25\]  (conf: 0.58)

  

  🔥 Convergence Detected: Numbers \[1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22,

23, 24, 25\] appear in multiple tiers.

────────────────────────────────────────────────────────────────────────────────────────────────────────────

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main party --help                                                                   

 Usage: python -m engine.cli.main party \[OPTIONS\] \[LOTTERY\]

  

 Launch 'Party Mode' to brainstorm and generate a chaotic/math hybrid ticket.

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│   lottery      \[LOTTERY\]  Lottery name to generate a ticket for \[default: br/mega-sena\]                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --help          Show this message and exit.                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main party

───────────────────────────────────── 🎊 WELCOME TO THE PARTY MODE 🎊 ──────────────────────────────────────

  

Topic: Bridging Real Math, Chaos, and Esoteric Absurdity to find the next winning strategy.

  

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🤓 THE STATISTICIAN: Look, we can add all the chaos we want, but if the Chi-Squared gate doesn't trip,   │

│ we're just painting noise. I'm forcing a 'weighted' frequency baseline.                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🌪️ THE CHAOS ANALYST: Rigorous statistics only work in stable regimes, Nerd! The world is high-entropy   │

│ right now. I'm injecting 'seismic' and 'noosphere' jitter into the mix.                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🔮 THE ESOTERIC EXPERT: You both miss the point. The machines are physical, yes, but they are entrained  │

│ to the synodic month. We need 'moon\_phase' to align the ticket with today's tide.                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🎮 THE GAME DESIGNER: Guys, let's keep it fun! I'll put all of this into a 'Hybrid Ensemble' and see     │

│ what the machine spits out!                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

────────────────────────────────────────

  

🚀 PARTY TICKETS GENERATED:

  Checking for new megasena draws…

  Cache is up to date (Draw 3003).

  Party Ticket 1: \[27, 34, 40, 46, 54, 60\] (sum=261)

  Party Ticket 2: \[10, 17, 24, 54, 58, 59\] (sum=222)

  Party Ticket 3: \[22, 40, 43, 49, 50, 58\] (sum=262)

  

  Consensus built from: weighted, seismic, noosphere, moon\_phase (Conf: 0.31)

  

Party Mode finished. The hangover begins.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main party lotofacil

───────────────────────────────────── 🎊 WELCOME TO THE PARTY MODE 🎊 ──────────────────────────────────────

  

Topic: Bridging Real Math, Chaos, and Esoteric Absurdity to find the next winning strategy.

  

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🤓 THE STATISTICIAN: Look, we can add all the chaos we want, but if the Chi-Squared gate doesn't trip,   │

│ we're just painting noise. I'm forcing a 'weighted' frequency baseline.                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🌪️ THE CHAOS ANALYST: Rigorous statistics only work in stable regimes, Nerd! The world is high-entropy   │

│ right now. I'm injecting 'seismic' and 'noosphere' jitter into the mix.                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🔮 THE ESOTERIC EXPERT: You both miss the point. The machines are physical, yes, but they are entrained  │

│ to the synodic month. We need 'moon\_phase' to align the ticket with today's tide.                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ 🎮 THE GAME DESIGNER: Guys, let's keep it fun! I'll put all of this into a 'Hybrid Ensemble' and see     │

│ what the machine spits out!                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

────────────────────────────────────────

  

🚀 PARTY TICKETS GENERATED:

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  Party Ticket 1: \[3, 4, 7, 8, 10, 11, 12, 13, 14, 17, 18, 19, 21, 22, 24\] (sum=203)

  Party Ticket 2: \[2, 3, 7, 8, 9, 10, 11, 12, 13, 15, 18, 21, 22, 23, 24\] (sum=198)

  Party Ticket 3: \[1, 2, 3, 4, 8, 9, 10, 11, 12, 20, 21, 22, 23, 24, 25\] (sum=195)

  

  Consensus built from: weighted, seismic, noosphere, moon\_phase (Conf: 0.53)

  

Party Mode finished. The hangover begins.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main signal

Usage: python -m engine.cli.main signal \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main signal --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Missing argument 'LOTTERY'.                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main signal lotofacil --help

  

 Usage: python -m engine.cli.main signal \[OPTIONS\] LOTTERY

  

 📡 Signal-to-Noise rolling window stability analysis.

  

 Runs the strategy across overlapping historical windows and tracks

 confidence and score entropy over time. Stable plateaus = detectable

 structure. Wild oscillations = noise dominance.

  

 Example: lottery signal br/lotofacil --strategy weighted --window 50

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name (e.g. br/lotofacil) \[required\]                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --strategy   -s      TEXT     Strategy name \[default: weighted\]                                          │

│ --limit      -L      INTEGER  Rolling window size in draws \[default: 50\]                                 │

│ --step               INTEGER  Step between windows \[default: 10\]                                         │

│ --export-md          TEXT     Export pattern log to this .md file                                        │

│ --help                        Show this message and exit.                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main signal lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching SIGNAL                                                                                         │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  weighted                                                                                    │

│   Window:  50                                                                                            │

│   Step:  10                                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭────────────────────────────────────── 📡 Signal-to-Noise Dashboard ──────────────────────────────────────╮

│ Lotofácil  strategy=weighted  window=50 draws  step=10  snapshots=363                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

Confidence:

▅▄▄▃▃▃▃▃▃▄▃▄▃▃▃▅▄▄▅▄▄▄▄▅▄▄▄▄▄▄▅▂▅▄▃▆▅▃▃▃▂▃▄▅▆▄▃▄▆▅▆▆▄▃▄▃▃▂▂▃▅▅▆▅▅▅▇▇▆▄▃▃▅▅▆▃▂▄▃▅▃▅▆▅▅▃▄▄▁▁▃▃▄▅▅▄▅▃▂▂▃▃▄▄▄▅▆▆

▄▃▄▄▄▅▂▁▂▄▅▃▃▄▄▃▂▃▄▄▃▄▅▄▆▆▅▅▄▃▂▂▃▄▄▂▄▅▆▆▆▆▆▇▅▅▂▃▃▄▅▆▄▅▃▂▄▅▄▃▅▆▅▃▂▄▂▃▄▄▄▅▄▅▃▄▄▅▂▃▃▃▅▄▆▅▇▇▆▅▅▃▂▃▄▃▄▂▂▄▃▄▄▅▄▄▃▄

▃▅▅▆▃▂▄▃▄▅▃▄▂▁▂▁▂▂▄▃▄▄▃▄▃▄▂▁▁▁▃▃▄▃▃▃▃▂▃▄▃▃▃▃▃▅▅█▆▇▆▅▄▄▄▄▃▂▃▃▃▄▄▄▃▄▃▂▂▂▂▃▆▇▅▄▂▄▃▃▃▃▃▂▃▆▄▅▆▅▃▂▄▅▅▅▅▄▃▄▄▄▅▄▄▃▃▄

▄▄▂▃▅▄▄▃▅▄▃▃▄▅▃▅▅▆▅▄▂▃▂▃▄▄▅▄▃▃▃▂▄▄▅▄▃▂▃

  min=0.292  max=0.675  mean=0.475  σ=0.0680

  

Entropy:

▆▅▅▅▅▅▄▅▄▅▅▄▃▄▃▅▄▂▅▄▅▆▆▆▅▅▄▅▄▄▆▃▆▅▄▅▅▄▄▄▂▄▅▆▆▆▄▄▆▅▆▆▆▅▇▆▆▅▄▅▅▅▆▅▅▆▆▇▆▆▄▄▆▆▆▄▃▅▂▆▅▆▆▆▆▆▆▅▄▃▅▅▆▅▄▄▅▅▅▅▆▄▄▅▄▅▆▆

▄▃▅▄▆▆▃▂▄▆▆▅▃▅▆▅▄▄▆▇▇▇▇▆▆▆▆▅▆▁▂▃▄▆▆▃▅▆▆▆▇▇▇█▇▆▃▅▅▅▅▆▅▇▅▄▄▆▅▅▇▆▅▄▄▆▅▆▆▅▅▅▇▆▂▄▄▆▂▅▄▄▆▄▄▄▆▆▆▆▅▄▃▅▆▆▆▅▅▇▄▆▆▆▅▆▆▅

▅▆▅▆▆▅▆▅▆▅▄▆▅▃▃▄▄▄▅▅▃▅▄▆▃▆▄▁▂▂▅▃▆▄▄▄▄▄▄▅▅▅▅▆▄▆▆▇▅▆▆▅▅▅▆▅▅▄▄▄▅▆▆▅▄▅▃▃▄▅▄▄▆▇▅▄▂▅▅▅▅▄▄▃▃▆▆▇▇▆▅▃▅▇▆▇▇▅▅▆▅▅▆▆▆▅▄▄

▅▅▂▄▅▄▅▄▆▆▄▅▅▆▃▆▆▆▇▆▄▅▄▅▅▅▆▅▆▄▄▃▅▄▆▄▄▄▅

  min=2.846  max=3.169  mean=3.052

             Rolling Window Details

  Window end    Confidence    Entropy    Signal

  #50               0.5239     3.0907    STABLE

  #60               0.5071     3.0736    STABLE

  #70               0.4675     3.0693    NOISE

  #80               0.4436     3.0576    STABLE

  #90               0.4166     3.0395    STABLE

  #100              0.4430     3.0583    STABLE

  #110              0.4186     3.0252    STABLE

  #120              0.4472     3.0561    STABLE

  #130              0.4489     3.0286    STABLE

  #140              0.4689     3.0348    STABLE

  #150              0.4393     3.0396    STABLE

  #160              0.4612     3.0272    STABLE

  #170              0.4092     2.9573    STABLE

  #180              0.4227     3.0055    NOISE

  #190              0.4439     2.9709    NOISE

  #200              0.5631     3.0739    NOISE

  #210              0.4966     2.9857    NOISE

  #220              0.4706     2.8972    NOISE

  #230              0.5140     3.0635    STABLE

  #240              0.4710     2.9867    STABLE

  #250              0.5098     3.0761    STABLE

  #260              0.5066     3.0916    STABLE

  #270              0.4941     3.0934    STABLE

  #280              0.5159     3.0900    STABLE

  #290              0.4685     3.0517    STABLE

  #300              0.4904     3.0499    STABLE

  #310              0.4676     3.0208    STABLE

  #320              0.4942     3.0533    STABLE

  #330              0.4825     3.0195    STABLE

  #340              0.4928     3.0007    NOISE

  #350              0.5360     3.0864    NOISE

  #360              0.3881     2.9424    NOISE

  #370              0.5194     3.0792    NOISE

  #380              0.4633     3.0738    NOISE

  #390              0.4047     2.9954    NOISE

  #400              0.5766     3.0738    NOISE

  #410              0.5136     3.0334    NOISE

  #420              0.4081     3.0037    NOISE

  #430              0.4168     3.0035    NOISE

  #440              0.4344     3.0034    STABLE

  #450              0.3644     2.9341    NOISE

  #460              0.4299     3.0147    NOISE

  #470              0.4937     3.0374    NOISE

  #480              0.5382     3.0884    NOISE

  #490              0.5887     3.1190    NOISE

  #500              0.5005     3.0851    NOISE

  #510              0.4129     2.9907    NOISE

  #520              0.4708     3.0242    NOISE

  #530              0.5839     3.0864    NOISE

  #540              0.5404     3.0647    NOISE

  #550              0.5939     3.0884    NOISE

  #560              0.5741     3.0985    NOISE

  #570              0.4852     3.0967    NOISE

  #580              0.4081     3.0650    NOISE

  #590              0.4948     3.1425    NOISE

  #600              0.4327     3.1219    STABLE

  #610              0.4313     3.0957    NOISE

  #620              0.4007     3.0739    STABLE

  #630              0.3789     3.0281    NOISE

  #640              0.4236     3.0649    NOISE

  #650              0.5165     3.0727    NOISE

  #660              0.5118     3.0481    NOISE

  #670              0.5665     3.0819    STABLE

  #680              0.5166     3.0657    STABLE

  #690              0.5524     3.0751    NOISE

  #700              0.5644     3.0844    NOISE

  #710              0.6295     3.1050    NOISE

  #720              0.6542     3.1333    NOISE

  #730              0.5990     3.1191    NOISE

  #740              0.5101     3.1042    NOISE

  #750              0.4323     3.0023    NOISE

  #760              0.4362     2.9984    NOISE

  #770              0.5118     3.0781    NOISE

  #780              0.5254     3.0839    NOISE

  #790              0.5681     3.1109    NOISE

  #800              0.4411     3.0260    NOISE

  #810              0.3978     2.9559    NOISE

  #820              0.4667     3.0667    NOISE

  #830              0.4280     2.9335    NOISE

  #840              0.5147     3.0820    NOISE

  #850              0.4385     3.0517    NOISE

  #860              0.5442     3.0914    NOISE

  #870              0.5671     3.1123    NOISE

  #880              0.5217     3.0974    NOISE

  #890              0.5347     3.1180    NOISE

  #900              0.4394     3.0850    NOISE

  #910              0.4783     3.0975    NOISE

  #920              0.4722     3.0503    NOISE

  #930              0.3278     3.0102    NOISE

  #940              0.3468     2.9402    NOISE

  #950              0.4369     3.0714    NOISE

  #960              0.4473     3.0493    NOISE

  #970              0.4892     3.0793    STABLE

  #980              0.5173     3.0551    STABLE

  #990              0.5114     3.0259    STABLE

  #1000             0.4998     3.0060    NOISE

  #1010             0.5264     3.0695    NOISE

  #1020             0.4191     3.0642    NOISE

  #1030             0.3789     3.0730    NOISE

  #1040             0.3892     3.0506    STABLE

  #1050             0.4442     3.0804    NOISE

  #1060             0.4103     3.0109    NOISE

  #1070             0.4704     3.0243    STABLE

  #1080             0.4838     3.0657    NOISE

  #1090             0.4636     3.0217    NOISE

  #1100             0.5387     3.0329    NOISE

  #1110             0.6144     3.1164    NOISE

  #1120             0.5851     3.0993    NOISE

  #1130             0.4913     2.9889    NOISE

  #1140             0.4102     2.9619    NOISE

  #1150             0.4924     3.0401    NOISE

  #1160             0.4899     3.0127    NOISE

  #1170             0.5024     3.0796    NOISE

  #1180             0.5165     3.1194    NOISE

  #1190             0.3769     2.9654    NOISE

  #1200             0.3239     2.9254    NOISE

  #1210             0.3785     3.0123    NOISE

  #1220             0.4778     3.0863    NOISE

  #1230             0.5269     3.0934    NOISE

  #1240             0.4304     3.0365    NOISE

  #1250             0.4334     2.9724    NOISE

  #1260             0.4748     3.0347    STABLE

  #1270             0.4686     3.0810    NOISE

  #1280             0.4228     3.0751    NOISE

  #1290             0.3683     3.0082    NOISE

  #1300             0.4116     3.0207    NOISE

  #1310             0.4688     3.1188    NOISE

  #1320             0.4930     3.1419    NOISE

  #1330             0.4482     3.1268    STABLE

  #1340             0.5077     3.1537    STABLE

  #1350             0.5413     3.1242    NOISE

  #1360             0.4778     3.1094    NOISE

  #1370             0.5729     3.1055    NOISE

  #1380             0.6195     3.1007    NOISE

  #1390             0.5369     3.0907    NOISE

  #1400             0.5345     3.0680    NOISE

  #1410             0.5015     3.0945    NOISE

  #1420             0.4104     2.8459    NOISE

  #1430             0.3731     2.9344    NOISE

  #1440             0.3897     2.9634    NOISE

  #1450             0.4496     2.9987    NOISE

  #1460             0.4935     3.1152    NOISE

  #1470             0.5095     3.1115    NOISE

  #1480             0.3733     2.9524    NOISE

  #1490             0.4690     3.0502    NOISE

  #1500             0.5446     3.1015    NOISE

  #1510             0.5795     3.1093    NOISE

  #1520             0.6146     3.1034    STABLE

  #1530             0.6199     3.1400    STABLE

  #1540             0.6088     3.1402    STABLE

  #1550             0.5957     3.1465    STABLE

  #1560             0.6544     3.1687    NOISE

  #1570             0.5652     3.1446    NOISE

  #1580             0.5152     3.1148    NOISE

  #1590             0.3479     2.9753    NOISE

  #1600             0.4515     3.0721    NOISE

  #1610             0.4329     3.0547    NOISE

  #1620             0.5011     3.0689    NOISE

  #1630             0.5623     3.0756    NOISE

  #1640             0.6134     3.1009    NOISE

  #1650             0.4904     3.0630    NOISE

  #1660             0.5565     3.1258    NOISE

  #1670             0.4157     3.0610    NOISE

  #1680             0.3974     3.0191    NOISE

  #1690             0.4744     3.0014    NOISE

  #1700             0.5647     3.0862    NOISE

  #1710             0.4748     3.0742    NOISE

  #1720             0.4121     3.0479    NOISE

  #1730             0.5240     3.1238    NOISE

  #1740             0.5682     3.0845    NOISE

  #1750             0.5117     3.0703    NOISE

  #1760             0.4350     3.0284    NOISE

  #1770             0.3725     3.0228    NOISE

  #1780             0.4705     3.0957    NOISE

  #1790             0.3784     3.0467    NOISE

  #1800             0.4312     3.0774    NOISE

  #1810             0.4626     3.0860    NOISE

  #1820             0.4853     3.0520    STABLE

  #1830             0.4698     3.0571    STABLE

  #1840             0.5322     3.0696    STABLE

  #1850             0.5074     3.1259    NOISE

  #1860             0.5124     3.0924    NOISE

  #1870             0.4124     2.9291    NOISE

  #1880             0.4843     3.0239    NOISE

  #1890             0.4705     3.0082    NOISE

  #1900             0.5459     3.0990    NOISE

  #1910             0.3792     2.9232    NOISE

  #1920             0.4428     3.0390    NOISE

  #1930             0.4378     3.0126    NOISE

  #1940             0.4058     2.9852    NOISE

  #1950             0.5113     3.0813    NOISE

  #1960             0.4769     3.0085    NOISE

  #1970             0.5803     3.0240    NOISE

  #1980             0.5393     3.0095    NOISE

  #1990             0.6584     3.1195    NOISE

  #2000             0.6362     3.0914    NOISE

  #2010             0.5838     3.0863    NOISE

  #2020             0.5272     3.1058    NOISE

  #2030             0.5211     3.0559    NOISE

  #2040             0.4390     2.9978    NOISE

  #2050             0.3840     2.9664    NOISE

  #2060             0.4563     3.0647    STABLE

  #2070             0.4724     3.0917    NOISE

  #2080             0.4494     3.1075    NOISE

  #2090             0.5044     3.1157    NOISE

  #2100             0.4001     3.0642    NOISE

  #2110             0.3704     3.0637    NOISE

  #2120             0.4869     3.1477    NOISE

  #2130             0.4044     3.0205    NOISE

  #2140             0.4957     3.0927    NOISE

  #2150             0.4989     3.1062    NOISE

  #2160             0.5383     3.1085    STABLE

  #2170             0.4749     3.0736    STABLE

  #2180             0.4890     3.0985    STABLE

  #2190             0.4469     3.1061    STABLE

  #2200             0.5093     3.0653    NOISE

  #2210             0.4546     3.0644    NOISE

  #2220             0.5355     3.0955    NOISE

  #2230             0.5605     3.0656    NOISE

  #2240             0.6125     3.0832    NOISE

  #2250             0.4241     3.0834    NOISE

  #2260             0.3950     3.0552    NOISE

  #2270             0.4849     3.0874    NOISE

  #2280             0.4083     3.0509    NOISE

  #2290             0.4889     3.0824    NOISE

  #2300             0.5474     3.0601    NOISE

  #2310             0.4095     2.9979    NOISE

  #2320             0.4811     3.0914    NOISE

  #2330             0.3874     3.0721    NOISE

  #2340             0.3388     2.9423    NOISE

  #2350             0.3540     2.9634    STABLE

  #2360             0.3417     3.0199    STABLE

  #2370             0.3956     3.0269    NOISE

  #2380             0.3787     3.0084    NOISE

  #2390             0.4800     3.0748    NOISE

  #2400             0.4523     3.0422    NOISE

  #2410             0.4596     2.9838    STABLE

  #2420             0.4745     3.0340    STABLE

  #2430             0.4562     2.9875    STABLE

  #2440             0.4946     3.0821    STABLE

  #2450             0.4436     2.9651    NOISE

  #2460             0.4974     3.0906    NOISE

  #2470             0.3950     3.0094    NOISE

  #2480             0.2924     2.8832    NOISE

  #2490             0.3174     2.9223    NOISE

  #2500             0.3123     2.8961    NOISE

  #2510             0.4214     3.0729    NOISE

  #2520             0.4072     2.9686    NOISE

  #2530             0.4944     3.0909    STABLE

  #2540             0.4307     3.0230    STABLE

  #2550             0.4368     3.0176    STABLE

  #2560             0.4295     3.0039    STABLE

  #2570             0.4233     2.9903    STABLE

  #2580             0.3847     3.0050    STABLE

  #2590             0.4283     3.0189    STABLE

  #2600             0.4708     3.0696    STABLE

  #2610             0.4500     3.0639    STABLE

  #2620             0.4219     3.0685    STABLE

  #2630             0.4073     3.0392    STABLE

  #2640             0.4530     3.1113    NOISE

  #2650             0.4154     3.0195    NOISE

  #2660             0.5175     3.0903    NOISE

  #2670             0.5487     3.0823    NOISE

  #2680             0.6751     3.1302    NOISE

  #2690             0.6117     3.0362    NOISE

  #2700             0.6242     3.1065    NOISE

  #2710             0.6021     3.1084    NOISE

  #2720             0.5351     3.0587    NOISE

  #2730             0.4968     3.0577    NOISE

  #2740             0.4815     3.0341    STABLE

  #2750             0.4930     3.0821    STABLE

  #2760             0.4887     3.0608    NOISE

  #2770             0.4465     3.0611    NOISE

  #2780             0.3979     3.0034    STABLE

  #2790             0.4184     3.0009    STABLE

  #2800             0.4256     3.0256    NOISE

  #2810             0.4487     3.0594    STABLE

  #2820             0.5102     3.1170    STABLE

  #2830             0.4658     3.0938    NOISE

  #2840             0.4684     3.0605    NOISE

  #2850             0.4036     2.9897    NOISE

  #2860             0.4944     3.0682    NOISE

  #2870             0.4168     2.9585    NOISE

  #2880             0.3816     2.9616    NOISE

  #2890             0.3901     3.0174    STABLE

  #2900             0.3655     3.0616    STABLE

  #2910             0.3714     3.0047    NOISE

  #2920             0.4417     3.0073    NOISE

  #2930             0.5839     3.1094    NOISE

  #2940             0.6324     3.1430    NOISE

  #2950             0.5624     3.0566    NOISE

  #2960             0.4582     2.9875    NOISE

  #2970             0.3486     2.9281    NOISE

  #2980             0.4717     3.0630    NOISE

  #2990             0.4044     3.0337    NOISE

  #3000             0.4564     3.0450    STABLE

  #3010             0.4360     3.0500    STABLE

  #3020             0.4063     2.9856    STABLE

  #3030             0.4201     2.9972    STABLE

  #3040             0.3947     2.9798    NOISE

  #3050             0.4077     2.9796    NOISE

  #3060             0.5663     3.0914    NOISE

  #3070             0.4629     3.0893    NOISE

  #3080             0.5604     3.1307    NOISE

  #3090             0.5671     3.1330    NOISE

  #3100             0.5512     3.0914    NOISE

  #3110             0.4403     3.0512    NOISE

  #3120             0.4015     2.9674    NOISE

  #3130             0.4683     3.0651    NOISE

  #3140             0.5136     3.1319    NOISE

  #3150             0.5210     3.1198    STABLE

  #3160             0.5302     3.1396    STABLE

  #3170             0.5494     3.1427    NOISE

  #3180             0.4852     3.0661    NOISE

  #3190             0.4434     3.0730    NOISE

  #3200             0.4887     3.0771    STABLE

  #3210             0.4668     3.0397    STABLE

  #3220             0.4575     3.0676    STABLE

  #3230             0.5199     3.1117    STABLE

  #3240             0.5055     3.0851    STABLE

  #3250             0.4944     3.0870    STABLE

  #3260             0.4412     3.0417    STABLE

  #3270             0.4441     3.0230    STABLE

  #3280             0.4822     3.0002    STABLE

  #3290             0.4761     3.0318    NOISE

  #3300             0.5021     3.0669    NOISE

  #3310             0.3913     2.9320    NOISE

  #3320             0.4344     3.0275    NOISE

  #3330             0.5260     3.0640    NOISE

  #3340             0.4778     3.0202    NOISE

  #3350             0.4814     3.0571    NOISE

  #3360             0.4024     3.0189    NOISE

  #3370             0.5132     3.1051    NOISE

  #3380             0.4978     3.1074    NOISE

  #3390             0.4407     3.0128    NOISE

  #3400             0.4056     3.0387    NOISE

  #3410             0.4778     3.0652    NOISE

  #3420             0.5140     3.0809    NOISE

  #3430             0.4262     2.9749    NOISE

  #3440             0.5349     3.1083    NOISE

  #3450             0.5388     3.1070    NOISE

  #3460             0.5912     3.1155    NOISE

  #3470             0.5494     3.1232    NOISE

  #3480             0.4778     3.0868    NOISE

  #3490             0.3872     3.0110    NOISE

  #3500             0.4249     3.0376    STABLE

  #3510             0.4015     3.0064    NOISE

  #3520             0.4485     3.0318    NOISE

  #3530             0.5050     3.0561    NOISE

  #3540             0.4572     3.0446    NOISE

  #3550             0.5487     3.1067    NOISE

  #3560             0.5093     3.0647    NOISE

  #3570             0.4474     3.0792    NOISE

  #3580             0.4233     3.0157    NOISE

  #3590             0.4459     3.0265    NOISE

  #3600             0.3936     2.9711    NOISE

  #3610             0.4965     3.0337    NOISE

  #3620             0.4918     3.0136    NOISE

  #3630             0.5550     3.1096    NOISE

  #3640             0.4599     2.9896    NOISE

  #3650             0.4028     3.0073    NOISE

  #3660             0.3956     3.0038    STABLE

  #3670             0.4485     3.0582    STABLE

  

Stability score: 91/363 windows stable (25%)

Peak confidence: 0.6751 at #2680

Lowest entropy:  2.8459 at #1420 (most concentrated scoring)

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main cluster lotofacil --help

  

 Usage: python -m engine.cli.main cluster \[OPTIONS\] LOTTERY

  

 🔬 Unsupervised clustering of historical draw patterns.

  

 Builds a number co-occurrence feature matrix and groups draws into clusters.

 Stable clusters across different windows suggest repeating structural patterns.

  

 Example: lottery cluster br/lotofacil --method kmeans --k 5

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name (e.g. br/lotofacil) \[required\]                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --method       -m      TEXT     kmeans | dbscan \[default: kmeans\]                                        │

│ --k                    INTEGER  Number of clusters (K-Means only) \[default: 5\]                           │

│ --limit        -L      INTEGER  Use only the N most recent draws                                         │

│ --eps                  FLOAT    DBSCAN neighbourhood radius \[default: 3.0\]                               │

│ --min-samples          INTEGER  DBSCAN minimum cluster size \[default: 5\]                                 │

│ --export-md            TEXT     Export pattern log to this .md file                                      │

│ --help                          Show this message and exit.                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main cluster lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching CLUSTER                                                                                        │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Method:  kmeans                                                                                        │

│   K:  5                                                                                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭───────────────────────────────────────── 🔬 Clustering Analysis ─────────────────────────────────────────╮

│ Lotofácil  method=KMEANS  3676 draws  pool=25 numbers                                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

K-Means inertia: 87610.76 (lower = tighter clusters)

                                     Cluster Profiles

  Cluster    Size    Top numbers (most frequent inside cluster)    Avg sum    Even ratio

  C0          765                                                    184.7           40%

  C1          675                                                    212.8           47%

  C2          698                                                    210.1           45%

  C3          776                                                    177.7           49%

  C4          762                                                    194.1           58%

  

Latest draw → Cluster 1  size=675  avg\_sum=212.8  top5=

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil --help

  

 Usage: python -m engine.cli.main stress-test \[OPTIONS\] LOTTERY

  

 ⚡ Adversarial stress-test: inject true randomness and compare strategy response.

  

 Baseline: run the strategy on real historical draws → measure confidence + entropy.

 Adversarial: replace inject-ratio% of draws with uniformly random draws, repeat

 for \`trials\` runs, and compare.

  

 If the strategy cannot distinguish real from random, its patterns may be noise.

  

 Example: lottery stress-test br/lotofacil --strategy weighted --inject-ratio 0.5 --trials 5

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name (e.g. br/lotofacil) \[required\]                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --strategy      -s      TEXT     Strategy name or comma-separated list \[default: weighted\]               │

│ --inject-ratio          FLOAT    Fraction of draws to replace with true random (0.0–1.0) \[default: 0.5\]  │

│ --trials                INTEGER  Number of random injection trials to average over \[default: 5\]          │

│ --limit         -L      INTEGER  Use only the N most recent draws \[default: 100\]                         │

│ --export-md             TEXT     Export adversarial report to this .md file                              │

│ --help                           Show this message and exit.                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching STRESS-TEST                                                                                    │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  weighted                                                                                    │

│   Inject Ratio:  0.5                                                                                     │

│   Trials:  5                                                                                             │

│   Window:  100                                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── ⚡ Adversarial Stress-Test ───────────────────────────────────────╮

│ Lotofácil  strategy=weighted                                                                             │

│ inject\_ratio=50%  trials=5  window=100 draws                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Strategy    Real conf    Random conf     Δ conf    Real entropy    Random entropy        Verdict

  weighted       0.5019         0.4854    +0.0165          3.0648            3.0457    REAL > RANDOM ✔

  

Verdict guide: REAL > RANDOM = strategy detects structure in data | CANNOT DISTINGUISH = patterns may be

hallucinated | RANDOM > REAL = check for inverted logic

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil -strategy some --inject-ratio 0.2

Usage: python -m engine.cli.main stress-test \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main stress-test --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (some)                                                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil --strategy some --inject-ratio 0.2

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching STRESS-TEST                                                                                    │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  some                                                                                        │

│   Inject Ratio:  0.2                                                                                     │

│   Trials:  5                                                                                             │

│   Window:  100                                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── ⚡ Adversarial Stress-Test ───────────────────────────────────────╮

│ Lotofácil  strategy=some                                                                                 │

│ inject\_ratio=20%  trials=5  window=100 draws                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

some: baseline failed — "Unknown strategy 'some'. Available: advanced, bayesian, biorhythm, cnn\_1d,

contagion, copairs, crowd\_avoidance, cycle, entropy\_global, fibonacci, fisher, gematria, gradient\_boost,

harmonic, hedge, hybrid, iching, kabbalistic, knn, ley\_lines, logistic, lorentz, lstm\_gru, markov, momentum,

monte\_carlo, moon\_phase, mutual\_info, noosphere, numerology, pattern, positional, primes, prob\_weighted,

quantum\_anneal, random\_forest, refraction, regime, reincarnation, sefirot, seismic, sentiment, solar,

spectral, stability, stacking, steiner\_wheel, streak, survival, synapse, transformer, vix\_jitter, void,

voting, weather, weighted, zodiac"

  Strategy    Real conf    Random conf    Δ conf    Real entropy    Random entropy    Verdict

  

Verdict guide: REAL > RANDOM = strategy detects structure in data | CANNOT DISTINGUISH = patterns may be

hallucinated | RANDOM > REAL = check for inverted logic

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil --strategy random\_forest --inject-ratio 0.2

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching STRESS-TEST                                                                                    │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  random\_forest                                                                               │

│   Inject Ratio:  0.2                                                                                     │

│   Trials:  5                                                                                             │

│   Window:  100                                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── ⚡ Adversarial Stress-Test ───────────────────────────────────────╮

│ Lotofácil  strategy=random\_forest                                                                        │

│ inject\_ratio=20%  trials=5  window=100 draws                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

  Strategy         Real conf    Random conf     Δ conf    Real entropy    Random entropy       Verdict

  random\_forest       0.5221         0.4902    +0.0320          3.0162            3.0393    REAL > RANDOM

                                                                                                  ✔

  

Verdict guide: REAL > RANDOM = strategy detects structure in data | CANNOT DISTINGUISH = patterns may be

hallucinated | RANDOM > REAL = check for inverted logic

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?2

❯ python3 -m engine.cli.main stress-test lotofacil --strategy random\_forest --inject-ratio 0.2 --limit 500

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching STRESS-TEST                                                                                    │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  random\_forest                                                                               │

│   Inject Ratio:  0.2                                                                                     │

│   Trials:  5                                                                                             │

│   Window:  500                                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── ⚡ Adversarial Stress-Test ───────────────────────────────────────╮

│ Lotofácil  strategy=random\_forest                                                                        │

│ inject\_ratio=20%  trials=5  window=500 draws                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Strategy         Real conf    Random conf     Δ conf    Real entropy    Random entropy       Verdict

  random\_forest       0.3043         0.3838    -0.0795          2.9752            3.0483    RANDOM > REAL

                                                                                                 (!)

  

Verdict guide: REAL > RANDOM = strategy detects structure in data | CANNOT DISTINGUISH = patterns may be

hallucinated | RANDOM > REAL = check for inverted logic

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main detect-patterns lotofacil --help

  

 Usage: python -m engine.cli.main detect-patterns \[OPTIONS\] LOTTERY

  

 🔭 Esoteric Overlay: detect if esoteric cycle markers correlate with stable signal windows.

  

 Runs rolling stability analysis (like \`lottery signal\`) then cross-references

 each window's draw date with lunar phase, solar K-index, and other esoteric

 markers. Buckets with stable% significantly above baseline are flagged as

 High-Probability Nodes.

  

 Example: lottery detect-patterns br/lotofacil --esoteric cyclical --threshold 0.15

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name (e.g. br/lotofacil) \[required\]                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --esoteric   -e      TEXT     Overlay type: cyclical | lunar | solar | all \[default: cyclical\]           │

│ --strategy   -s      TEXT     Strategy whose stability windows are analysed \[default: weighted\]          │

│ --threshold  -t      FLOAT    Minimum |Δ stable%| vs baseline to flag a High-Probability Node            │

│                               \[default: 0.15\]                                                            │

│ --limit      -L      INTEGER  Rolling window size in draws \[default: 50\]                                 │

│ --step               INTEGER  Step between windows \[default: 10\]                                         │

│ --export-md          TEXT     Export pattern log to this .md file                                        │

│ --help                        Show this message and exit.                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main detect-patterns lotofacil -e cyclical

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching DETECT-PATTERNS                                                                                │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Esoteric:  cyclical                                                                                    │

│   Strategy:  weighted                                                                                    │

│   Threshold:  0.15                                                                                       │

│   Window:  50                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭────────────────────────────────────── 🔭 Esoteric Pattern Detector ──────────────────────────────────────╮

│ Lotofácil  strategy=weighted  esoteric=cyclical                                                          │

│ window=50  step=10  threshold=±15%                                                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

Baseline stability: 363 windows  → 91 stable (25%)

  

─────────────────────────────────────────── Lunar Cycle Quintile ───────────────────────────────────────────

  Chi-squared independence test: χ²=2.17  p=0.7045  → not significant

  Lunar Cycle Quintile     n    Stable%    Δ vs baseline    Signal

  Q1 (0–20%)              72        21%              -4%      —

  Q2 (20–40%)             74        28%              +3%      —

  Q3 (40–60%)             69        22%              -3%      —

  Q4 (60–80%)             76        25%              -0%      —

  Q5 (80–100%)            72        29%              +4%      —

  

  No High-Probability Nodes found at threshold ±15%. Try --threshold 0.10 for a looser search.

  

No nodes found across all overlays. The esoteric markers tested show no significant correlation with

strategy stability at this threshold.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main detect-patterns lotofacil -e cyclical -t 0.10 --step 25 --limit 250

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching DETECT-PATTERNS                                                                                │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Esoteric:  cyclical                                                                                    │

│   Strategy:  weighted                                                                                    │

│   Threshold:  0.1                                                                                        │

│   Window:  250                                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭────────────────────────────────────── 🔭 Esoteric Pattern Detector ──────────────────────────────────────╮

│ Lotofácil  strategy=weighted  esoteric=cyclical                                                          │

│ window=250  step=25  threshold=±10%                                                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

Baseline stability: 138 windows  → 35 stable (25%)

  

─────────────────────────────────────────── Lunar Cycle Quintile ───────────────────────────────────────────

  Chi-squared independence test: χ²=5.87  p=0.2094  → not significant

  Lunar Cycle Quintile     n    Stable%    Δ vs baseline         Signal

  Q1 (0–20%)              25        12%             -13%    LOW-PROB ZONE ↓

  Q2 (20–40%)             35        20%              -5%           —

  Q3 (40–60%)             24        25%              -0%           —

  Q4 (60–80%)             32        38%             +12%    HIGH-PROB NODE ↑

  Q5 (80–100%)            22        32%              +6%           —

  

  ★ High-Probability Node: Q1 (0–20%)  stable=12%  (-13% ↓ below baseline)  n=25

  

  ★ High-Probability Node: Q4 (60–80%)  stable=38%  (+12% ↑ above baseline)  n=32

  

─────────────────────────────── CONVERGENCE SUMMARY — High-Probability Nodes ───────────────────────────────

  Lunar Cycle Quintile → Q1 (0–20%)  stable=12%  Δ=-13%  n=25

  Lunar Cycle Quintile → Q4 (60–80%)  stable=38%  Δ=+12%  n=32

  

  These windows show above-baseline predictive stability correlated with the esoteric marker.

Cross-reference with your esoteric framework before acting on them.

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main leaderboard lotofacil --help

  

 Usage: python -m engine.cli.main leaderboard \[OPTIONS\] LOTTERY

  

 🏆 Comparative diagnostic leaderboard across multiple strategies.

  

 Measures two independent quality signals per strategy:

   1. Signal stability %  (rolling window variance analysis)

   2. Discrimination Δ    (real data vs injected random confidence delta)

  

 Then computes a composite rank. High composite = genuine pattern detector.

 Low composite = noise generator.

  

 Example: lottery leaderboard br/lotofacil --strategies default

          lottery leaderboard br/lotofacil --strategies weighted,markov,moon\_phase

  

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮

│ \*    lottery      TEXT  Lottery name (e.g. br/lotofacil) \[required\]                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮

│ --strategies    -s      TEXT     Comma-separated list or group: default | statistical | esoteric | deep  │

│                                  \[default: default\]                                                      │

│ --limit         -L      INTEGER  Rolling window size for stability analysis \[default: 50\]                │

│ --step                  INTEGER  Step between rolling windows \[default: 20\]                              │

│ --inject-ratio          FLOAT    Fraction of draws to randomise in stress-test \[default: 0.5\]            │

│ --trials                INTEGER  Random injection trials per strategy \[default: 3\]                       │

│ --export-md             TEXT     Export leaderboard to this .md file                                     │

│ --help                           Show this message and exit.                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main leaderboard lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching LEADERBOARD                                                                                    │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  default                                                                                   │

│   Window:  50                                                                                            │

│   Trials:  3                                                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────── 🏆 Strategy Diagnostic Leaderboard ───────────────────────────────────╮

│ Lotofácil  8 strategies  stability-window=50  stress-trials=3                                            │

│ inject-ratio=50%  stress-window last 100 draws                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Analysing weighted… stability=25%  Δ=+0.0925  composite=0.626

  Analysing markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

 stability=25%  Δ=-0.0245  composite=0.126

  Analysing bayesian… stability=25%  Δ=+0.0254  composite=0.380

  Analysing monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

 stability=25%  Δ=-0.0326  composite=0.126

  Analysing spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

 stability=25%  Δ=-0.0198  composite=0.126

  Analysing cycle… skip (insufficient history)

  Analysing moon\_phase… stability=25%  Δ=+0.0767  composite=0.626

  Analysing noosphere… stability=100%  Δ=+0.0000  composite=0.500

  

                                   Leaderboard

  Rank    Strategy       Stability%    Δ real/rand    Composite     Assessment

    🥇    weighted              25%        +0.0925        0.626    DISCRIMINATES

    🥈    moon\_phase            25%        +0.0767        0.626    DISCRIMINATES

    🥉    noosphere            100%        +0.0000        0.500    DISCRIMINATES

    #4    bayesian              25%        +0.0254        0.380        NOISE

    #5    markov                25%        -0.0245        0.126      INVERTED

    #6    monte\_carlo           25%        -0.0326        0.126      INVERTED

    #7    spectral              25%        -0.0198        0.126      INVERTED

  

Top strategy: weighted  composite=0.626  stability=25%  Δ=+0.0925

3 strategies cross the 0.50 composite threshold (genuine discriminators): weighted, moon\_phase, noosphere

  

Skipped: cycle

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main scan lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching SCAN                                                                                           │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  bayesian                                                                                    │

│   Window:  50                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭────────────────────────────────────── 🔬 Pre-Draw Conditions Scan ───────────────────────────────────────╮

│ Lotofácil  strategy=bayesian  date=2026-05-05                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

UNIFORM  p=0.9708  (fair distribution)

MIXED  33% of recent windows stable

C0  top=  avg\_sum=203

Layer 4: Esoteric conditions  🌕 Waning Gibbous (63% cycle)  ☀️ Storm (Kp=5.0) ↑

REAL > RANDOM  Δ=+0.0989  (strategy detects structure)

Layer 6: Regime check (JS divergence vs history)  STABLE  JS=0.00138  (recent draws consistent with history)

  

───────────────────────────────────────────────── VERDICT ──────────────────────────────────────────────────

  Fairness          ●●    UNIFORM  p=0.9708  (fair distribution)

  Stability         ●○    MIXED  33% of recent windows stable

  Cluster           ●○    C0  top=  avg\_sum=203

  Esoteric          ○○    🌕 Waning Gibbous (63% cycle)  ☀️ Storm (Kp=5.0) ↑

  Discrimination    ●●    REAL > RANDOM  Δ=+0.0989  (strategy detects structure)

  Regime            ●●    STABLE  JS=0.00138  (recent draws consistent with history)

╭───────────────────────────────────────── Today's Recommendation ─────────────────────────────────────────╮

│ ⚠ CAUTION  (8/12)                                                                                        │

│ Mixed signals. Play conservatively or wait.                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !27 ?1

❯ python3 -m engine.cli.main log lotofacil

python3 -m engine.cli.main log-view lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching LOG                                                                                            │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  bayesian                                                                                    │

│   Fmt:  jsonl                                                                                            │

│   Output:  /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                               │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/data/draw\_log.jsonl                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  ✔ Appended to /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction

Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/data/draw\_log.jsonl

  draw=3676  conf=0.502033  entropy=3.126214  stable=STABLE  moon=Waning Gibbous  kp=5.0  cluster=C1

Usage: python -m engine.cli.main log-view \[OPTIONS\]

Try 'python -m engine.cli.main log-view --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (lotofacil)                                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !28 ?1

❯ python3 -m engine.cli.main log lotofacil  ; python3 -m engine.cli.main log-view lotofacil ; python3 -m engine.cli.maiorecast lotofacil ; python3 -m engine.cli.main compare-draws lotofacil ; python3 -m engine.cli.main trend lotofacil ython3 -m engine.cli.main next lotofacil ; python3 -m engine.cli.main risk lotofacil ; python3 -m engine.cli.main oraclotofacil ; python3 -m engine.cli.main daemon lotofacil ; python3 -m engine.cli.main hedge lotofacil ; python3 -m enginli.main daily lotofacil ; python3 -m engine.cli.main alert lotofacil ; python3 -m engine.cli.main hitcheck lotofacil ython3 -m engine.cli.main weekly lotofacil ; python3 -m engine.cli.main calibrate lotofacil ; python3 -m engine.cli.maiog-export lotofacil ; python3 -m engine.cli.main rank-numbers lotofacil ; python3 -m engine.cli.main picks lotofacil ython3 -m engine.cli.main number-timeline lotofacil ; python3 -m engine.cli.main compare-strategies lotofacil ; pythonm engine.cli.main streak-report lotofacil ; python3 -m engine.cli.main pair-analysis lotofacil ; python3 -m engine.clain draw-summary lotofacil ; python3 -m engine.cli.main session lotofacil ; python3 -m engine.cli.main ticket-gradotofacil ; python3 -m engine.cli.main pool-stats lotofacil ; python3 -m engine.cli.main history-scan lotofacil ; pythonm engine.cli.main number-heat lotofacil ; python3 -m engine.cli.main suggest-swaps lotofacil ; python3 -m engine.clain quick lotofacil ; python3 -m engine.cli.main variance-report lotofacil ; python3 -m engine.cli.main coverage-checotofacil ; python3 -m engine.cli.main momentum-check lotofacil ; python3 -m engine.cli.main gap-forecast lotofacil ython3 -m engine.cli.main combo-rank lotofacil ; python3 -m engine.cli.main draw-clock lotofacil ; python3 -m engine.clain entropy-scan lotofacil ; python3 -m engine.cli.main cold-streak-alert lotofacil ; python3 -m engine.cli.maiynergy-map lotofacil ; python3 -m engine.cli.main ticket-dna lotofacil ; python3 -m engine.cli.main frequency-banotofacil ; python3 -m engine.cli.main multi-ticket lotofacil ; python3 -m engine.cli.main history lotofacil ; python3 -ngine.cli.main compare-bets lotofacil ; python3 -m engine.cli.main simulate lotofacil ; python3 -m engine.cli.maiavings lotofacil ; python3 -m engine.cli.main optimize lotofacil ; python3 -m engine.cli.main calendar lotofacil ython3 -m engine.cli.main signature lotofacil ; python3 -m engine.cli.main check lotofacil ; python3 -m engine.cli.maialidate lotofacil ; python3 -m engine.cli.main serve lotofacil ; python3 -m engine.cli.main games lotofacil ; python3 -ngine.cli.main strategies lotofacil ; python3 -m engine.cli.main watchlist lotofacil

^CTraceback (most recent call last):

  File "<frozen runpy>", line 198, in \_run\_module\_as\_main

  File "<frozen runpy>", line 88, in \_run\_code

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/main.py", line 18, in <module>

    from engine.cli.commands.fetch import fetch

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/fetch.py", line 14, in <module>

    from engine.cli.utils import get\_adapter

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/utils.py", line 20, in <module>

    from engine.adapters.registry import registry

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/adapters/\_\_init\_\_.py", line 22, in <module>

    import pandas as pd

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/lib/python3.12/site-packages/pandas/\_\_init\_\_.py", line 46, in <module>

    from pandas.core.api import (

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/lib/python3.12/site-packages/pandas/core/api.py", line 23, in <module>

    from pandas.core.algorithms import (

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/lib/python3.12/site-packages/pandas/core/algorithms.py", line 83, in <module>

    from pandas.core.array\_algos.take import take\_nd

  File "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/lib/python3.12/site-packages/pandas/core/array\_algos/take.py", line 24, in <module>

    from pandas.core.construction import ensure\_wrapped\_if\_datetimelike

  File "<frozen importlib.\_bootstrap>", line 1360, in \_find\_and\_load

  File "<frozen importlib.\_bootstrap>", line 1331, in \_find\_and\_load\_unlocked

  File "<frozen importlib.\_bootstrap>", line 935, in \_load\_unlocked

  File "<frozen importlib.\_bootstrap\_external>", line 991, in exec\_module

  File "<frozen importlib.\_bootstrap\_external>", line 1087, in get\_code

  File "<frozen importlib.\_bootstrap\_external>", line 1186, in get\_data

KeyboardInterrupt

  

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !28 ?1

❯

python3 -m engine.cli.main log lotofacil  ; python3 -m engine.cli.main log-view lotofacil ; python3 -m engine.cli.maiorecast lotofacil ; python3 -m engine.cli.main compare-draws lotofacil ; python3 -m engine.cli.main trend lotofacil ython3 -m engine.cli.main next lotofacil ; python3 -m engine.cli.main risk lotofacil ; python3 -m engine.cli.main oraclotofacil ; python3 -m engine.cli.main daemon lotofacil ; python3 -m engine.cli.main hedge lotofacil ; python3 -m enginli.main daily lotofacil ; python3 -m engine.cli.main alert lotofacil ; python3 -m engine.cli.main hitcheck lotofacil ython3 -m engine.cli.main weekly lotofacil ; python3 -m engine.cli.main calibrate lotofacil ; python3 -m engine.cli.maiog-export lotofacil ; python3 -m engine.cli.main rank-numbers lotofacil ; python3 -m engine.cli.main picks lotofacil ython3 -m engine.cli.main number-timeline lotofacil ; python3 -m engine.cli.main compare-strategies lotofacil ; python3 -m engine.cli.main streak-report lotofacil ; python3 -m engine.cli.main pair-analysis lotofacil ; python3 -m engine.clain draw-summary lotofacil ; python3 -m engine.cli.main session lotofacil ; python3 -m engine.cli.main ticket-gradotofacil ; python3 -m engine.cli.main pool-stats lotofacil ; python3 -m engine.cli.main history-scan lotofacil ; python3 -m engine.cli.main number-heat lotofacil ; python3 -m engine.cli.main suggest-swaps lotofacil ; python3 -m engine.clain quick lotofacil ; python3 -m engine.cli.main variance-report lotofacil ; python3 -m engine.cli.main coverage-checotofacil ; python3 -m engine.cli.main momentum-check lotofacil ; python3 -m engine.cli.main gap-forecast lotofacil ython3 -m engine.cli.main combo-rank lotofacil ; python3 -m engine.cli.main draw-clock lotofacil ; python3 -m engine.clain entropy-scan lotofacil ; python3 -m engine.cli.main cold-streak-alert lotofacil ; python3 -m engine.cli.maiynergy-map lotofacil ; python3 -m engine.cli.main ticket-dna lotofacil ; python3 -m engine.cli.main frequency-banotofacil ; python3 -m engine.cli.main multi-ticket lotofacil ; python3 -m engine.cli.main history lotofacil ; python3 -ngine.cli.main compare-bets lotofacil ; python3 -m engine.cli.main simulate lotofacil ; python3 -m engine.cli.maiavings lotofacil ; python3 -m engine.cli.main optimize lotofacil ; python3 -m engine.cli.main calendar lotofacil ython3 -m engine.cli.main signature lotofacil ; python3 -m engine.cli.main check lotofacil ; python3 -m engine.cli.maialidate lotofacil ; python3 -m engine.cli.main serve lotofacil ; python3 -m engine.cli.main games lotofacil ; python3 -ngine.cli.main strategies lotofacil ; python3 -m engine.cli.main watchlist lotofacil

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching LOG                                                                                            │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategy:  bayesian                                                                                    │

│   Fmt:  jsonl                                                                                            │

│   Output:  /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                               │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/data/draw\_log.jsonl                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  ✔ Appended to /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction

Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/data/draw\_log.jsonl

  draw=3676  conf=0.502033  entropy=3.126214  stable=STABLE  moon=Waning Gibbous  kp=5.0  cluster=C1

Usage: python -m engine.cli.main log-view \[OPTIONS\]

Try 'python -m engine.cli.main log-view --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (lotofacil)                                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.cli.maiorecast

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching COMPARE-DRAWS                                                                                  │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Recent:  50                                                                                            │

│   Baseline:  all                                                                                         │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── 🔀 Draw Window Comparison ────────────────────────────────────────╮

│ Lotofácil                                                                                                │

│ Recent window: last 50 draws  |  Baseline: 3626 draws                                                    │

│                                                                                                          │

│   Jensen-Shannon divergence : 0.00138  (0=identical, 1=completely different)                             │

│   KL divergence (recent‖base): 0.00553                                                                   │

│   Chi-squared p-value        : 0.9987                                                                    │

│                                                                                                          │

│   Regime verdict: STABLE                                                                                 │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

      Top 10 Movers (recent vs baseline)

 Number  Baseline%  Recent%       Δ  Direction

   10        4.14%    5.20%  +1.06%  ▲ rising

   14        4.04%    3.07%  -0.97%  ▼ falling

   6         3.91%    4.67%  +0.75%  ▲ rising

   9         3.98%    3.33%  -0.65%  ▼ falling

   7         3.94%    4.40%  +0.46%  ▲ rising

   5         3.99%    4.40%  +0.41%  ▲ rising

   2         4.00%    3.60%  -0.40%  ▼ falling

   23        3.90%    4.27%  +0.36%  ▲ rising

   16        3.82%    3.47%  -0.35%  ▼ falling

   19        3.97%    4.27%  +0.29%  ▲ rising

  

Recent draws are statistically consistent with the full history.

Frequency patterns have not shifted — strategy signals remain valid.

Usage: python -m engine.cli.main trend \[OPTIONS\] \[LOTTERY\]

Try 'python -m engine.cli.main trend --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra arguments (ython3 next lotofacil)                                                   │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

───────────────────────────────────────── Risk Analysis: Lotofácil ─────────────────────────────────────────

                           Prize Tiers

    Tier               Odds  Prob per ticket     Breakeven prize

  Match 11          1 in 11        9.090909%              33 BRL

  Match 12          1 in 59        1.694915%             177 BRL

  Match 13         1 in 691        0.144718%           2,073 BRL

  Match 14      1 in 21,791        0.004589%          65,373 BRL

 Match 15 ★  1 in 3,268,760        0.000031%       9,806,280 BRL

  

 Ticket price       3.00 BRL

 Jackpot odds       1 in 3,268,760

 Assumed jackpot    3,922,512 BRL  (heuristic: 40% of prize pool)

 Breakeven jackpot  9,806,280 BRL

 Jackpot EV         -1.8000 BRL

 Return ratio       0.4000  (1.0 = breakeven)

╭─────────────────────────────────────── NEGATIVE EXPECTATION (−EV) ───────────────────────────────────────╮

│ Jackpot EV: -1.8000 BRL                                                                                  │

│ Jackpot needs to reach 9,806,280 BRL to break even (5,883,768 BRL gap from current).                     │

│ Lower prize tiers add positive EV not captured here.                                                     │

│ Play for fun only, or wait for a larger rollover.                                                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

EV shown for jackpot tier only. Excludes taxes and lower-tier prizes.

Usage: python -m engine.cli.main \[OPTIONS\] COMMAND \[ARGS\]...

Try 'python -m engine.cli.main --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such command 'oraclotofacil'.                                                                         │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Starting AutoML Daemon for lotofacil

  Interval: 3600s | Validation Window: 10 draws

  State will be saved to data/daemon\_state.json

  

\[2026-05-05 17:44:05\] Starting optimization cycle...

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'random\_forest' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'pattern' is running near its minimum data floor (50/50 draws). Results may be volatile.

  ✓ Optimal Config Found: weighted (L=50, T=0.0) -> 100.0% capture

\[2026-05-05 17:44:52\] Sleeping for 3600s...

  

^C

Daemon stopped by user.

  

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

─────────────────────────────────── Hedge Portfolio Generator: Lotofácil ───────────────────────────────────

  Budget: 50.00 BRL | Target: 16 tickets

  

                     Self-Paying Portfolio (Balanced)

 #  Numbers                                                 Hedge Strength

 1  \[1, 2, 3, 4, 5, 9, 11, 12, 13, 14, 15, 18, 19, 22, 24\]            0.79

╭────────────────────────────────────────── Financial Projection ──────────────────────────────────────────╮

│ This portfolio covers 15 numbers (60.0% of board).                                                       │

│ Total Investment: 3.00 BRL                                                                               │

│                                                                                                          │

│ Goal: If 11 of the winning numbers fall within your pool of 15, at least one of these tickets is         │

│ guaranteed to hit a prize.                                                                               │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

Hedge Pool: \[24, 1, 4, 14, 13, 3, 12, 5, 2, 22, 15, 11, 19, 9, 18\]

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: Error while finding module specification for 'enginli.main' (ModuleNotFoundError: No module named 'enginli')

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

2026-05-05 lotofacil: no alert conditions met (watching: go-strong,regime-shift)

Usage: python -m engine.cli.main hitcheck \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main hitcheck --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such option: -m                                                                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching CALIBRATE                                                                                      │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  default                                                                                   │

│   Draws:  15                                                                                             │

│   Window:  50                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

Testing 6 strategies over 15 target draws (training window ≤ 50 draws each)...

  

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠋ draw 5/15  strategy weighted…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠙ draw 9/15  strategy monte\_carlo…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠹ draw 13/15  strategy monte\_carlo…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

  

             Strategy Calibration — Lotofácil  (15 draws)

 #  Strategy     Mean hits      ±σ  Hit rate   Lift  Lift %  Best   N

 1  spectral         9.200  ±0.833    0.6133  1.022   +2.2%    11  15

 2  weighted         9.133  ±1.024    0.6089  1.015   +1.5%    11  15

 3  markov           9.133  ±1.147    0.6089  1.015   +1.5%    11  15

 4  bayesian         8.933  ±1.289    0.5956  0.993   -0.7%    11  15

 5  monte\_carlo      8.867  ±1.024    0.5911  0.985   -1.5%    10  15

  

Random baseline: 9.000 expected hits/draw  (pick 15 from 25)  |  Lift > 1.0 = above random

  

╭───────────────────────────────────────── 🎯 Calibration Summary ─────────────────────────────────────────╮

│ Best: spectral  mean hits=9.200  lift=1.022  (above random baseline)                                     │

│ Tested 15 draws  ·  training window ≤ 50                                                                 │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✔ Calibration cached to calibration\_cache.json

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.cli.maiog-export

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching RANK-NUMBERS                                                                                   │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  default                                                                                   │

│   Window:  50                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

Weights: statistical  |  6 strategies

  

⠙ Scoring weighted…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠹ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠸ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠼ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠴ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠦ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠧ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠇ Scoring markov…WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠸ Scoring bayesian…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠼ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠴ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠦ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠧ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠇ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠏ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠋ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠙ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠹ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠸ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠼ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠴ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠦ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠧ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠇ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠏ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠋ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠙ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠹ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠸ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠼ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠴ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠦ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠧ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠇ Scoring monte\_carlo…WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠏ Scoring monte\_carlo…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠋ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠙ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠹ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠸ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠼ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

⠴ Scoring spectral…WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'cycle' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'cycle' is running near its minimum data floor (100/100 draws). Results may be volatile.

WARNING:root:Strategy 'cycle' is running near its minimum data floor (100/100 draws). Results may be volatile.

    Number Rankings — Lotofácil  (5 strategies, statistical

                           weights)

 Rank  Number   Score  Bar       Consensus  Freq%  Trend  Tier

    1    10    0.0664  ████████     4/5     71.0%    ↑    HOT

    2    25    0.0620  ███████░     4/5     62.0%    →    HOT

    3    6     0.0588  ███████░     4/5     68.0%    →    HOT

    4    5     0.0576  ███████░     4/5     57.0%    →    HOT

    5    3     0.0538  ██████░░     4/5     54.0%    →    HOT

    6    23    0.0509  ██████░░     3/5     66.0%    →    HOT

    7    1     0.0504  ██████░░     5/5     61.0%    →    HOT

    8    7     0.0475  ██████░░     3/5     61.0%    →    HOT

    9    24    0.0461  ██████░░     3/5     58.0%    →    HOT

   10    15    0.0453  █████░░░     4/5     63.0%    ↑    HOT

   11    4     0.0450  █████░░░     5/5     68.0%    →    HOT

   12    19    0.0420  █████░░░     4/5     61.0%    →    HOT

   13    13    0.0418  █████░░░     4/5     59.0%    →    HOT

   14    11    0.0418  █████░░░     5/5     63.0%    →    HOT

   15    20    0.0386  █████░░░     3/5     68.0%    →    HOT

   16    21    0.0366  ████░░░░     3/5     61.0%    →    WARM

   17    22    0.0298  ████░░░░     1/5     56.0%    →    WARM

   18    9     0.0278  ███░░░░░     2/5     59.0%    →    WARM

   19    12    0.0273  ███░░░░░     2/5     56.0%    →    WARM

   20    2     0.0258  ███░░░░░     2/5     61.0%    →    WARM

   21    18    0.0244  ███░░░░░     1/5     55.0%    →    WARM

   22    8     0.0235  ███░░░░░     1/5     57.0%    →    WARM

   23    17    0.0210  ███░░░░░     1/5     52.0%    →    WARM

   24    14    0.0186  ██░░░░░░     1/5     46.0%    ↓    WARM

   25    16    0.0172  ██░░░░░░     2/5     57.0%    →    WARM

  

╭─────────────────────────────────── 🔢 Top Numbers → Suggested Ticket ────────────────────────────────────╮

│ 10  25  6  5  3  23  1  7  24  15  4  19  13  11  20                                                     │

│ Top 15 numbers by composite score  ·  statistical weights  ·  5 strategies                               │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main picks \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main picks --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such option: -m                                                                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'spectral' is running near its minimum data floor (50/50 draws). Results may be volatile.

  

                    Strategy Tickets — Lotofácil  (5 strategies)

 Strategy     Ticket                                                 Unique  Shared

 bayesian     1  3  4  5  6  7  10  11  13  15  19  20  23  24  25        0      15

 markov       1  3  4  5  6  7  10  11  13  15  19  20  23  24  25        0      15

 monte\_carlo  1  2  3  8  9  11  13  14  15  16  17  18  21  22  24       5      10

 spectral     1  3  4  5  6  9  10  11  12  13  15  16  19  21  25        1      14

 weighted     1  2  3  4  5  6  7  10  11  19  20  21  23  24  25         0      15

  

  Consensus Heatmap — by agreement count

 Number  Agree   Pct  Bar         In all?

   1       5/5  100%  ██████████     ✔

   3       5/5  100%  ██████████     ✔

   11      5/5  100%  ██████████     ✔

   4       4/5   80%  ████████░░     ·

   5       4/5   80%  ████████░░     ·

   6       4/5   80%  ████████░░     ·

   10      4/5   80%  ████████░░     ·

   19      4/5   80%  ████████░░     ·

   24      4/5   80%  ████████░░     ·

   25      4/5   80%  ████████░░     ·

   13      4/5   80%  ████████░░     ·

   15      4/5   80%  ████████░░     ·

   7       3/5   60%  ██████░░░░     ·

   20      3/5   60%  ██████░░░░     ·

   21      3/5   60%  ██████░░░░     ·

   23      3/5   60%  ██████░░░░     ·

   2       2/5   40%  ████░░░░░░     ·

   9       2/5   40%  ████░░░░░░     ·

   16      2/5   40%  ████░░░░░░     ·

   8       1/5   20%  ██░░░░░░░░     ·

   14      1/5   20%  ██░░░░░░░░     ·

   17      1/5   20%  ██░░░░░░░░     ·

   18      1/5   20%  ██░░░░░░░░     ·

   22      1/5   20%  ██░░░░░░░░     ·

   12      1/5   20%  ██░░░░░░░░     ·

  

╭────────────────────────────────────────── ⚖️ Consensus Ticket ───────────────────────────────────────────╮

│ 1  3  4  5  6  7  10  11  13  15  19  20  21  24  25                                                     │

│ Top 15 numbers by cross-strategy agreement  ·  5 strategies  ·  default group                            │

│ Numbers in all strategies: 3/15  ·  Avg pairwise overlap: 9.9 numbers                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

⚠ 1 strategies failed and were excluded: cycle

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

    🔥 Hottest Numbers — Lotofácil  (last 100 draws)

 Number  Streak  Max Hot  Record?  Recent 20

   10        +9        9     ★     █████████░░█████████

   8         +4        7     ·     █░████░░░░░██░░░████

   15        +4        8     ·     ░░█░██░░░██████░████

   19        +4        8     ·     █░░░█░██░██░░█░░████

   23        +3       11     ·     ███████████░██░█░███

   24        +3        6     ·     ██░██░█░░░░███░█░███

   4         +2       15     ·     ██░░████░██░█░█░█░██

   5         +2        8     ·     ░████████░██████░░██

   13        +2        9     ·     ███░░█░░█░░█░░██░░██

   18        +2        4     ·     ██░█░█░██░░█░██░█░██

  

    ❄️  Coldest Numbers — Lotofácil  (last 100 draws)

 Number  Streak  Max Cold  Record?  Recent 20

   14        -4         5     ★     ░░███░█░░██░░█░█░░░░

   1         -3         3     ★     █░░█░░██████░████░░░

   11        -3         5     ·     ░███░█░██░████░██░░░

   9         -2         8     ·     ░██░░█░░█████░██░█░░

   20        -2         5     ·     ██░░░███░█░░░░░███░░

   2         -1         4     ·     ██░██░░██░░███░░░██░

   3         -1         4     ·     ░██░█░█░█░███████░█░

   7         -1         3     ·     █░████░█████░░██░██░

   12        -1         3     ·     ██░█████░█░░█░███░█░

   17        -1         9     ·     █░██░░█░░█░████░░██░

  

╭───────────────────────────────────────── 🔥❄️  Streak Extremes ──────────────────────────────────────────╮

│ Hottest: #10 (+9 draws)   Coldest: #14 (-4 draws)                                                        │

│ Avg hot streak: 2.7  ·  Avg cold streak: 1.9  ·  Neutral (appeared last draw then missed or vice versa): │

│ 0                                                                                                        │

│ At/near historical record: 1, 10, 14                                                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

   🔗 Most Frequent Pairs — Lotofácil

            (last 100 draws)

 Pair   Count  Expected  Lift  Bar

 4–20      48      35.0  1.37  ████████

 4–23      47      35.0  1.34  ████████

 6–10      47      35.0  1.34  ████████

 10–13     47      35.0  1.34  ████████

 2–10      46      35.0  1.31  ████████

 4–10      46      35.0  1.31  ████████

 10–20     46      35.0  1.31  ████████

  4–6      45      35.0  1.29  ████████

 10–25     45      35.0  1.29  ████████

 20–23     44      35.0  1.26  ███████░

 20–25     44      35.0  1.26  ███████░

 19–20     44      35.0  1.26  ███████░

 10–11     44      35.0  1.26  ███████░

 1–23      43      35.0  1.23  ███████░

 6–23      43      35.0  1.23  ███████░

  

 ⬆️  Highest-Lift Pairs (more

    frequent than chance)

 Pair   Count  Lift  Bar

 4–20      48  1.37  ████████

 4–23      47  1.34  ████████

 6–10      47  1.34  ████████

 10–13     47  1.34  ████████

 2–10      46  1.31  ████████

 4–10      46  1.31  ████████

 10–20     46  1.31  ████████

  4–6      45  1.29  ████████

 10–25     45  1.29  ████████

 20–23     44  1.26  ███████░

 20–25     44  1.26  ███████░

 19–20     44  1.26  ███████░

 10–11     44  1.26  ███████░

 1–23      43  1.23  ███████░

 6–23      43  1.23  ███████░

  

╭──────────────────────────────────────────── 🔗 Pair Summary ─────────────────────────────────────────────╮

│ Most synergistic: 4–20  (lift 1.37, count 48)                                                            │

│ Most repellent:   8–14  (lift 0.60, count 21)                                                            │

│ Expected co-occurrence per draw: 0.3500  (~35.0 times in 100 draws)                                      │

│ Pairs with lift ≥1.5: 0  ·  Pairs with lift ≤0.5: 0                                                      │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.clain

  

╭────────────────────────────────────────── 🎲 Pre-Draw Session ───────────────────────────────────────────╮

│ Lotofácil  ·  2026-05-05  ·  fast strategies                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

────────────────────────────────────── Stage 1 / 5  —  GO/NO-GO Scan ───────────────────────────────────────

  Scan failed: scan() got an unexpected keyword argument 'quiet'

─────────────────────────────────────── Stage 2 / 5  —  Regime Check ───────────────────────────────────────

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching COMPARE-DRAWS                                                                                  │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Recent:  50                                                                                            │

│   Baseline:  all                                                                                         │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────────── 🔀 Draw Window Comparison ────────────────────────────────────────╮

│ Lotofácil                                                                                                │

│ Recent window: last 50 draws  |  Baseline: 3626 draws                                                    │

│                                                                                                          │

│   Jensen-Shannon divergence : 0.00138  (0=identical, 1=completely different)                             │

│   KL divergence (recent‖base): 0.00553                                                                   │

│   Chi-squared p-value        : 0.9987                                                                    │

│                                                                                                          │

│   Regime verdict: STABLE                                                                                 │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

      Top 10 Movers (recent vs baseline)

 Number  Baseline%  Recent%       Δ  Direction

   10        4.14%    5.20%  +1.06%  ▲ rising

   14        4.04%    3.07%  -0.97%  ▼ falling

   6         3.91%    4.67%  +0.75%  ▲ rising

   9         3.98%    3.33%  -0.65%  ▼ falling

   7         3.94%    4.40%  +0.46%  ▲ rising

   5         3.99%    4.40%  +0.41%  ▲ rising

   2         4.00%    3.60%  -0.40%  ▼ falling

   23        3.90%    4.27%  +0.36%  ▲ rising

   16        3.82%    3.47%  -0.35%  ▼ falling

   19        3.97%    4.27%  +0.29%  ▲ rising

  

Recent draws are statistically consistent with the full history.

Frequency patterns have not shifted — strategy signals remain valid.

───────────────────────────────────── Stage 3 / 5  —  Streak Snapshot ──────────────────────────────────────

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

    🔥 Hottest Numbers — Lotofácil  (last 50 draws)

 Number  Streak  Max Hot  Record?  Recent 20

   10        +9        9     ★     █████████░░█████████

   8         +4        7     ·     █░████░░░░░██░░░████

   15        +4        6     ·     ░░█░██░░░██████░████

   19        +4        6     ·     █░░░█░██░██░░█░░████

   23        +3       11     ·     ███████████░██░█░███

  

    ❄️  Coldest Numbers — Lotofácil  (last 50 draws)

 Number  Streak  Max Cold  Record?  Recent 20

   14        -4         4     ★     ░░███░█░░██░░█░█░░░░

   1         -3         3     ★     █░░█░░██████░████░░░

   11        -3         3     ★     ░███░█░██░████░██░░░

   9         -2         8     ·     ░██░░█░░█████░██░█░░

   20        -2         5     ·     ██░░░███░█░░░░░███░░

  

╭───────────────────────────────────────── 🔥❄️  Streak Extremes ──────────────────────────────────────────╮

│ Hottest: #10 (+9 draws)   Coldest: #14 (-4 draws)                                                        │

│ Avg hot streak: 2.7  ·  Avg cold streak: 1.9  ·  Neutral (appeared last draw then missed or vice versa): │

│ 0                                                                                                        │

│ At/near historical record: 1, 10, 11, 14                                                                 │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

─────────────────────────────────── Stage 4 / 5  —  Strategy Comparison ────────────────────────────────────

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

WARNING:root:Strategy 'monte\_carlo' is running near its minimum data floor (50/50 draws). Results may be volatile.

  

                    Strategy Tickets — Lotofácil  (3 strategies)

 Strategy     Ticket                                                  Unique  Shared

 bayesian     1  3  4  5  6  7  10  11  13  15  19  20  23  24  25         0      15

 monte\_carlo  1  2  8  9  11  12  13  14  15  16  17  18  20  21  22       8       7

 weighted     1  2  3  4  5  6  7  10  11  19  20  21  23  24  25          0      15

  

  Consensus Heatmap — by agreement count

 Number  Agree   Pct  Bar         In all?

   1       3/3  100%  ██████████     ✔

   11      3/3  100%  ██████████     ✔

   20      3/3  100%  ██████████     ✔

   3       2/3   67%  ███████░░░     ·

   4       2/3   67%  ███████░░░     ·

   5       2/3   67%  ███████░░░     ·

   6       2/3   67%  ███████░░░     ·

   7       2/3   67%  ███████░░░     ·

   10      2/3   67%  ███████░░░     ·

   13      2/3   67%  ███████░░░     ·

   15      2/3   67%  ███████░░░     ·

   19      2/3   67%  ███████░░░     ·

   23      2/3   67%  ███████░░░     ·

   24      2/3   67%  ███████░░░     ·

   25      2/3   67%  ███████░░░     ·

  

╭────────────────────────────────────────── ⚖️ Consensus Ticket ───────────────────────────────────────────╮

│ 1  3  4  5  6  7  10  11  13  15  19  20  23  24  25                                                     │

│ Top 15 numbers by cross-strategy agreement  ·  3 strategies  ·  fast group                               │

│ Numbers in all strategies: 3/15  ·  Avg pairwise overlap: 7.7 numbers                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

──────────────────────────────── Stage 5 / 5  —  Forecast Consensus Ticket ─────────────────────────────────

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching FORECAST                                                                                       │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  fast                                                                                      │

│   Window:  50                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

  → bayesian  stab=25%  Δ=-0.0110  w=0.126  conf=0.5020

  → weighted  stab=25%  Δ=+0.0912  w=0.626  conf=0.4666

  → markov  WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

stab=25%  Δ=-0.1118  w=0.126  conf=0.5123

  

              Strategy Contributions

 Strategy  Stability%   Δ disc  Weight  Confidence

 weighted         25%  +0.0912   0.626      0.4666

 bayesian         25%  -0.0110   0.126      0.5020

 markov           25%  -0.1118   0.126      0.5123

  

         Consensus Ticket

  Number    Consensus%        ±σ

    1           0.0721    0.0223

    2           0.0352    0.0111

    3           0.0567    0.0028

    4           0.0484    0.0024

    5           0.0632    0.0022

    6           0.0623    0.0033

    7           0.0519    0.0042

    10          0.0681    0.0072

    11          0.0431    0.0045

    15          0.0322    0.0133

    19          0.0339    0.0072

    20          0.0433    0.0023

    23          0.0580    0.0010

    24          0.0526    0.0049

    25          0.0769    0.0146

╭─────────────────────────────────────────── 🔮 Forecast Ticket ───────────────────────────────────────────╮

│ 1  2  3  4  5  6  7  10  11  15  19  20  23  24  25                                                      │

│ consensus\_mass=0.7979  strategies\_used=3  total\_weight=0.879                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

╭─────────────────────────────────────────── 🎲 Session Summary ───────────────────────────────────────────╮

│ Session complete  ·  Verdict: GO  ·  4/5 stages OK                                                       │

│ scan:ERROR  regime:OK  streak:OK  compare-strategies:OK  forecast:OK                                     │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main \[OPTIONS\] COMMAND \[ARGS\]...

Try 'python -m engine.cli.main --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such command 'ticket-gradotofacil'. Did you mean 'ticket-grade', 'ticket-dna'?                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────── Traceback (most recent call last) ────────────────────────────────────╮

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/pool\_stats.py:155 in   │

│ pool\_stats                                                                                               │

│                                                                                                          │

│   152 │   for col in \["Property", "Min", "P10", "Mean", "Median", "P90", "Max", "StdDev"\]:               │

│   153 │   │   stats\_table.add\_column(col, justify="right" if col != "Property" else "left")              │

│   154 │                                                                                                  │

│ ❱ 155 │   stats\_table.add\_row(\*stat\_row("Sum", sums))                                                    │

│   156 │   stats\_table.add\_row(\*stat\_row("Even count", evens))                                            │

│   157 │   stats\_table.add\_row(\*stat\_row("Odd count",  \[pick - e for e in evens\]))                        │

│   158 │   stats\_table.add\_row(\*stat\_row("Consecutive pairs", consec))                                    │

│                                                                                                          │

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/pool\_stats.py:134 in   │

│ stat\_row                                                                                                 │

│                                                                                                          │

│   131 │   │   mx  = max(values)                                                                          │

│   132 │   │   avg = statistics.mean(values)                                                              │

│   133 │   │   med = statistics.median(values)                                                            │

│ ❱ 134 │   │   sd  = statistics.stdev(values) if len(values) >= 2 else 0.0                                │

│   135 │   │   p10 = \_pct(values, 10)                                                                     │

│   136 │   │   p90 = \_pct(values, 90)                                                                     │

│   137 │   │   return \[                                                                                   │

│                                                                                                          │

│ /usr/lib/python3.12/statistics.py:974 in stdev                                                           │

│                                                                                                          │

│    971 │   mss = ss / (n - 1)                                                                            │

│    972 │   if issubclass(T, Decimal):                                                                    │

│    973 │   │   return \_decimal\_sqrt\_of\_frac(mss.numerator, mss.denominator)                              │

│ ❱  974 │   return \_float\_sqrt\_of\_frac(mss.numerator, mss.denominator)                                    │

│    975                                                                                                   │

│    976                                                                                                   │

│    977 def pstdev(data, mu=None):                                                                        │

│                                                                                                          │

│ /usr/lib/python3.12/statistics.py:428 in \_float\_sqrt\_of\_frac                                             │

│                                                                                                          │

│    425 def \_float\_sqrt\_of\_frac(n: int, m: int) -> float:                                                 │

│    426 │   """Square root of n/m as a float, correctly rounded."""                                       │

│    427 │   # See principle and proof sketch at: https://bugs.python.org/msg407078                        │

│ ❱  428 │   q = (n.bit\_length() - m.bit\_length() - \_sqrt\_bit\_width) // 2                                  │

│    429 │   if q >= 0:                                                                                    │

│    430 │   │   numerator = \_integer\_sqrt\_of\_frac\_rto(n, m << 2 \* q) << q                                 │

│    431 │   │   denominator = 1                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

AttributeError: 'numpy.int32' object has no attribute 'bit\_length'

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

⠋ Scanning window 1/20…WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

⠙ Scanning window 2/20…WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

⠹ Scanning window 17/20…WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

WARNING:root:Strategy 'bayesian' is running near its minimum data floor (30/30 draws). Results may be volatile.

  

Lotofácil  (oldest → newest, 20 windows of 50 draws each)

  ▓▓▓░░░░░▓▓▓▓▓▓▓▓▓▓▓▓

  ▓=GO  ░=CAUTION  ·=NO-GO

  

         History Scan — Lotofácil  (last 20 windows)

 Draw  Date                 χ²  Stab  Regime  Score  Verdict

 3676  2026-05-04 00:00:00  2    2      2       6/6    GO

 3675  2026-05-02 00:00:00  2    2      2       6/6    GO

 3674  2026-04-30 00:00:00  2    2      2       6/6    GO

 3673  2026-04-29 00:00:00  2    1      2       5/6    GO

 3672  2026-04-28 00:00:00  2    1      2       5/6    GO

 3671  2026-04-27 00:00:00  2    2      2       6/6    GO

 3670  2026-04-25 00:00:00  2    2      2       6/6    GO

 3669  2026-04-24 00:00:00  2    2      2       6/6    GO

 3668  2026-04-23 00:00:00  2    2      2       6/6    GO

 3667  2026-04-22 00:00:00  2    2      2       6/6    GO

 3666  2026-04-20 00:00:00  2    1      2       5/6    GO

 3665  2026-04-18 00:00:00  2    1      2       5/6    GO

 3664  2026-04-17 00:00:00  2    0      2       4/6  CAUTION

 3663  2026-04-16 00:00:00  2    0      2       4/6  CAUTION

 3662  2026-04-15 00:00:00  2    0      2       4/6  CAUTION

 3661  2026-04-14 00:00:00  2    0      2       4/6  CAUTION

 3660  2026-04-13 00:00:00  2    0      2       4/6  CAUTION

 3659  2026-04-11 00:00:00  2    1      2       5/6    GO

 3658  2026-04-10 00:00:00  2    2      2       6/6    GO

 3657  2026-04-09 00:00:00  2    1      2       5/6    GO

  

╭──────────────────────────────────────── 📅 History Scan Summary ─────────────────────────────────────────╮

│ GO: 15 (75%)   CAUTION: 5 (25%)   NO-GO: 0 (0%)                                                          │

│ Avg score: 5.2/6  ·  Current streak: 12× GO                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

Lotofácil  (last 30 draws, oldest → newest)

           |    |    |    |    |    |  freq  streak

   10  █████░█░█░█████████░░█████████   25  ███░  +9

    5  ██░██░░░█░░████████░██████░░██   21  ███░  +2

    6  ░░██░█████░░█████████░░██░░█░█   20  ███░  +1

    7  ░█░█░███░██░████░█████░░██░██░   20  ███░  -1

   11  ░███░█████░███░█░██░████░██░░░   20  ███░  -3

   12  █░████░░████░█████░█░░█░███░█░   20  ███░  -1

   23  ░░░░░█░██░███████████░██░█░███   20  ███░  +3

   15  ███░░█░█░█░░█░██░░░██████░████   19  ███░  +4

   18  ░██░███░████░█░█░██░░█░██░█░██   19  ███░  +2

   24  █░█░██░█████░██░█░░░░███░█░███   19  ███░  +3

    2  ██░██░███░██░██░░██░░███░░░██░   18  ██░░  -1

    3  ░░░░████░█░██░█░█░█░███████░█░   18  ██░░  -1

    4  █░░░░░██████░░████░██░█░█░█░██   18  ██░░  +2

    8  █████░█░░██░████░░░░░██░░░████   18  ██░░  +4

   19  ██░░░██████░░░█░██░██░░█░░████   18  ██░░  +4

   20  ████████░███░░░███░█░░░░░███░░   18  ██░░  -2

   17  █░███░░██░█░██░░█░░█░████░░██░   17  ██░░  -1

   21  █░█████░██░░░░█░░░░███░██░██░█   17  ██░░  +1

   22  ██░█░░░██░██░█░░█████░█░░░██░█   17  ██░░  +1

    1  ░█░░░█░██░█░░█░░██████░████░░░   16  ██░░  -3

   13  ░██████░░░███░░█░░█░░█░░██░░██   16  ██░░  +2

   16  █░░████░░░░██░░░░███░░█░███░░█   15  ██░░  +1

   25  █░███░░█░█░░█░░██░█░█░░░░███░█   15  ██░░  +1

    9  ░██░░░░░░░░██░░█░░█████░██░█░░   13  ██░░  -2

   14  ░██░█░█░░█░░███░█░░██░░█░█░░░░   13  ██░░  -4

  

╭──────────────────────────────────────── 🌡️ Pool Heatmap Summary ─────────────────────────────────────────╮

│ Pool: 25  ·  HOT: 0  WARM: 23  COLD: 2                                                                   │

│ Hottest: #10 (25 hits)  ·  Coldest: #9 (13 hits)                                                         │

│ Longest hot run: #10 (+9)  ·  Longest cold run: #14 (-4)                                                 │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main suggest-swaps \[OPTIONS\] LOTTERY NUMBERS...

Try 'python -m engine.cli.main suggest-swaps --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Missing argument 'NUMBERS...'.                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.clain

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭─────────────────────────────────── Traceback (most recent call last) ────────────────────────────────────╮

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/variance\_report.py:111 │

│ in variance\_report                                                                                       │

│                                                                                                          │

│   108 │   freq\_cv = statistics.stdev(all\_freqs) / (expected\_freq + 1e-9)                                 │

│   109 │                                                                                                  │

│   110 │   # ── Dimension 2: Sum variance (CV of draw sums) ───────────────────────────                   │

│ ❱ 111 │   sum\_cv = statistics.stdev(sums) / (statistics.mean(sums) + 1e-9) if len(sums) >= 2 else 0.0    │

│   112 │                                                                                                  │

│   113 │   # ── Dimension 3: Parity variance ──────────────────────────────────────────                   │

│   114 │   parity\_cv = statistics.stdev(evens) / (statistics.mean(evens) + 1e-9) if len(evens) >= 2 else  │

│       0.0                                                                                                │

│                                                                                                          │

│ /usr/lib/python3.12/statistics.py:974 in stdev                                                           │

│                                                                                                          │

│    971 │   mss = ss / (n - 1)                                                                            │

│    972 │   if issubclass(T, Decimal):                                                                    │

│    973 │   │   return \_decimal\_sqrt\_of\_frac(mss.numerator, mss.denominator)                              │

│ ❱  974 │   return \_float\_sqrt\_of\_frac(mss.numerator, mss.denominator)                                    │

│    975                                                                                                   │

│    976                                                                                                   │

│    977 def pstdev(data, mu=None):                                                                        │

│                                                                                                          │

│ /usr/lib/python3.12/statistics.py:428 in \_float\_sqrt\_of\_frac                                             │

│                                                                                                          │

│    425 def \_float\_sqrt\_of\_frac(n: int, m: int) -> float:                                                 │

│    426 │   """Square root of n/m as a float, correctly rounded."""                                       │

│    427 │   # See principle and proof sketch at: https://bugs.python.org/msg407078                        │

│ ❱  428 │   q = (n.bit\_length() - m.bit\_length() - \_sqrt\_bit\_width) // 2                                  │

│    429 │   if q >= 0:                                                                                    │

│    430 │   │   numerator = \_integer\_sqrt\_of\_frac\_rto(n, m << 2 \* q) << q                                 │

│    431 │   │   denominator = 1                                                                           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

AttributeError: 'numpy.int32' object has no attribute 'bit\_length'

Usage: python -m engine.cli.main \[OPTIONS\] COMMAND \[ARGS\]...

Try 'python -m engine.cli.main --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such command 'coverage-checotofacil'. Did you mean 'coverage-check'?                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

   📊 Momentum — Lotofácil  (short=10, long=30,

                  threshold=±15%)

 Number  Short%  Long%  Ratio   Signal    Bar

   15       90%    63%  1.42×  ▲ RISING   ████████

   9        60%    43%  1.38×  ▲ RISING   ████████

   3        80%    60%  1.33×  ▲ RISING   ████████

   21       70%    57%  1.24×  ▲ RISING   ███████░

   20       30%    60%  0.50×  ▼ FALLING  ███░░░░░

   14       30%    43%  0.69×  ▼ FALLING  ████░░░░

   6        50%    67%  0.75×  ▼ FALLING  ████░░░░

   12       50%    67%  0.75×  ▼ FALLING  ████░░░░

   2        50%    60%  0.83×  ▼ FALLING  █████░░░

  

╭────────────────────────────────────────── 📊 Momentum Summary ───────────────────────────────────────────╮

│ Rising:   #15 (1.42×)  #9 (1.38×)  #3 (1.33×)                                                            │

│ Falling:  #20 (0.50×)  #14 (0.69×)  #6 (0.75×)                                                           │

│ Neutral: 16  ·  Rising: 4  ·  Falling: 5  ·  Baseline rate: 60.0%  ·  Window: short=10 long=30           │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main gap-forecast \[OPTIONS\] LOTTERY

Try 'python -m engine.cli.main gap-forecast --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such option: -m                                                                                       │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

       ⏰ Draw Clock — Lotofácil  (rate window: 100 draws)

 Number  Rate%  Exp. Gap  Gap Now       Due In  Status   Urgency

   1     61.0%       1.6        3  0 (overdue)  DUE NOW  ████████

   9     59.0%       1.7        2  0 (overdue)  DUE NOW  ████████

   11    63.0%       1.6        3  0 (overdue)  DUE NOW  ████████

   14    46.0%       2.2        4  0 (overdue)  DUE NOW  ████████

   20    68.0%       1.5        2  0 (overdue)  DUE NOW  ████████

   2     61.0%       1.6        1            0   SOON    ███████░

   7     61.0%       1.6        1            0   SOON    ███████░

   12    56.0%       1.8        1            0   SOON    ███████░

   3     54.0%       1.9        1            0   SOON    ███████░

   17    52.0%       1.9        1            0   SOON    ███████░

   10    71.0%       1.4        0            1   WAIT    ████░░░░

   4     68.0%       1.5        0            1   WAIT    ████░░░░

   6     68.0%       1.5        0            1   WAIT    ████░░░░

   23    66.0%       1.5        0            1   WAIT    ████░░░░

   15    63.0%       1.6        0            1   WAIT    ███░░░░░

  

╭───────────────────────────────────────── ⏰ Draw Clock Summary ──────────────────────────────────────────╮

│ Due now:   #1  #9  #11  #14  #20                                                                         │

│ Due in 1–2:  #2 (0)  #7 (0)  #12 (0)  #3 (0)  #17 (0)                                                    │

│ Mean expected gap: 1.7 draws  ·  Baseline: 60.0%/draw  ·  Rate window: 100 draws                         │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.clain

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

🥶 QUIET: no numbers cold ≥ 2.5× expected (4 draws). All within normal range.

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.cli.maiynergy-map

Usage: python -m engine.cli.main ticket-dna \[OPTIONS\] LOTTERY TICKET

Try 'python -m engine.cli.main ticket-dna --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Missing argument 'TICKET'.                                                                               │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main \[OPTIONS\] COMMAND \[ARGS\]...

Try 'python -m engine.cli.main --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such command 'frequency-banotofacil'. Did you mean 'frequency-band'?                                  │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

  

       🎟️ Multi-Ticket Portfolio — Lotofácil  (3 tickets)

 Ticket  Numbers                                         Unique?

   T1     1  2  3  4  5  6  7 10 11 12 15 19 20 23 24    0 excl.

   T2     4  6  7  8  9 10 13 14 16 17 18 21 22 23 25   10 excl.

   T3     1  2  3  4  5  6  7 10 11 12 15 19 20 23 24    0 excl.

  

  Green = exclusive to this ticket  Yellow = shared  Dim = in all tickets

  

  Pool coverage: \[████████████████████████████████████████\] 25/25 (100.0%)

  

╭────────────────────────────────────────── 🎟️ Portfolio Summary ──────────────────────────────────────────╮

│ 3 tickets  ·  Pool coverage: 100.0% (25/25 numbers)                                                      │

│ Mean overlap: 8.3 numbers/pair  ·  Max overlap: 15                                                       │

│ Universal (in all tickets): #4  #6  #7  #10  #23                                                         │

│ Diversity weight: 0.6  ·  Score window: 100 draws                                                        │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

          Draw History: Lotofácil

 Draw ID  Date        Winning Numbers  Sum

    3657  2026-04-09                   200

    3658  2026-04-10                   192

    3659  2026-04-11                   182

    3660  2026-04-13                   180

    3661  2026-04-14                   173

    3662  2026-04-15                   186

    3663  2026-04-16                   205

    3664  2026-04-17                   176

    3665  2026-04-18                   171

    3666  2026-04-20                   206

    3667  2026-04-22                   185

    3668  2026-04-23                   164

    3669  2026-04-24                   181

    3670  2026-04-25                   189

    3671  2026-04-27                   157

    3672  2026-04-28                   193

    3673  2026-04-29                   205

    3674  2026-04-30                   228

    3675  2026-05-02                   180

    3676  2026-05-04                   229

Unknown option: -n

usage: python3 \[option\] ... \[-c cmd | -m mod | file | -\] \[arg\] ...

Try \`python -h' for more information.

Usage: python -m engine.cli.main simulate \[OPTIONS\] LOTTERY NUMBERS

Try 'python -m engine.cli.main simulate --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Missing argument 'NUMBERS'.                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.cli.maiavings

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching OPTIMIZE                                                                                       │

│   Lottery:  Lotofácil (lotofacil)                                                                        │

│   Strategies:  weighted,markov,momentum                                                                  │

│   Limits:  50,100,200                                                                                    │

│   Temps:  0.0                                                                                            │

│   Prev:  1-10                                                                                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

⠋ Grid Searching... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0/9WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

WARNING:root:Strategy 'markov' is running near its minimum data floor (50/50 draws). Results may be volatile.

    Optimization Leaderboard: Lotofácil (Top-15 Capture)

┏━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓

┃ Rank ┃ Strategy ┃ Limit ┃ Temp ┃ Capture Rate ┃ Avg Rank ┃

┡━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩

│    1 │ weighted │   200 │  0.0 │        61.3% │     13.0 │

│    2 │ weighted │    50 │  0.0 │        60.7% │     12.8 │

│    3 │ weighted │   100 │  0.0 │        60.7% │     13.1 │

│    4 │ markov   │   200 │  0.0 │        60.7% │     13.1 │

│    5 │ momentum │   100 │  0.0 │        60.7% │     13.0 │

│    6 │ markov   │    50 │  0.0 │        60.0% │     12.9 │

│    7 │ momentum │    50 │  0.0 │        60.0% │     13.0 │

│    8 │ momentum │   200 │  0.0 │        58.7% │     12.9 │

│    9 │ markov   │   100 │  0.0 │        57.3% │     13.2 │

└──────┴──────────┴───────┴──────┴──────────────┴──────────┘

  

Grid search covered 9 combinations over 10 draws.

Usage: python -m engine.cli.main calendar \[OPTIONS\]

Try 'python -m engine.cli.main calendar --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Invalid value for '--month' / '-m': 'engine.cli.main' is not a valid integer.                            │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main check \[OPTIONS\] LOTTERY NUMBERS

Try 'python -m engine.cli.main check --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Missing argument 'NUMBERS'.                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/.venv/bin/python3: No module named engine.cli.maialidate

Usage: python -m engine.cli.main serve \[OPTIONS\]

Try 'python -m engine.cli.main serve --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (lotofacil)                                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: python -m engine.cli.main games \[OPTIONS\]

Try 'python -m engine.cli.main games --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Got unexpected extra argument (lotofacil)                                                                │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Unknown option: -n

usage: python3 \[option\] ... \[-c cmd | -m mod | file | -\] \[arg\] ...

Try \`python -h' for more information.

Usage: python -m engine.cli.main watchlist \[OPTIONS\] COMMAND \[ARGS\]...

Try 'python -m engine.cli.main watchlist --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────╮

│ No such command 'lotofacil'.                                                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

## Model Response

> [!Model Thoughts]

## Gemini said

**TL;DR** Your Strategy Engine is generating impressive insights, but the execution pipeline is currently brittle. You have critical unhandled edge cases regarding future-date predictions (`NaT` crashes), severe type-casting mismatches between `numpy` and Python's standard `statistics` library, and dependency warnings polluting the terminal. Below is a structured, ruthless breakdown of your blind spots and a prioritized task list to drop into your Google Tasks.

---

### Critique & Blind Spots

As your mentor, I need to point out a few architectural flaws in the logs you just generated:

1. **Mixing Native Math with Numpy:** You are passing `numpy.int32` or `numpy.int64` arrays into Python's native `statistics.stdev()`. Python 3.12's `statistics` module relies on `.bit_length()` for integers, which `numpy` types do not possess. This is why the engine completely crashed during `variance-report` and `pool-stats`.
	- *Better Alternative:* Stop using the standard `statistics` library for Pandas/Numpy data. Use `numpy.std(values, ddof=1)` and `numpy.mean()`. It is structurally safer and computationally faster.
2. **Temporal Blindness in Forecasting:** Your engine is designed to backtest and predict *future* draws, but your date-dependent strategies (`weather`, `solar`, `reincarnation`) do not anticipate `pandas.NaT` (Not-a-Time). When the engine tries to fetch weather for a draw that hasn't happened yet, it passes `NaT` to the Open-Meteo API and crashes with a 400 Bad Request or a literal conversion error.
	- *Better Alternative:* Implement a graceful degradation layer. If `draw_date is NaT` or in the future, these specific esoteric strategies should either return a neutral confidence score (`0.5`) or raise a custom `TemporalDataMissing` exception that the engine catches and logs, rather than crashing the whole ensemble.
3. **UX Hazards and Uncapped Outputs:** Running `wheel` with a full pool of 25 numbers generated a table for over 3.2 million tickets directly to standard output.
	- *Better Alternative:* Implement a circuit breaker. If a wheel generates >10,000 combinations, intercept the print and enforce an `--output <file.csv>` flag.

---

### Actionable Execution Plan

Here is the structured task list to implement within your Obsidian `20 Workspaces` environment. Add these to **Google Tasks** or block out time in **Google Calendar** to resolve them.

#### Priority 1: Critical Bug Fixes (The Crashes)

- \[ \] **Task: Eradicate `statistics` module type errors.**
	- *Action:* Refactor `variance_report.py` (line 111) and `pool_stats.py` (line 134). Replace `statistics.mean()`, `statistics.median()`, and `statistics.stdev()` with their `numpy` equivalents (`np.mean`, `np.median`, `np.std(ddof=1)`). Ensure arrays are explicitly cast to float if needed.
- \[ \] **Task: Fix `NaT` crashes in Esoteric Strategies.**
	- *Action:* Add a guard clause in `weather`, `solar`, and `reincarnation` modules. Check `if pd.isna(draw_date): return default_score_dict`.
- \[ \] **Task: Fix the `scan` command signature.**
	- *Action:* The `scan()` function is receiving an unexpected keyword argument `quiet`. Update the function signature in the CLI routing to accept `**kwargs` or specifically define `quiet: bool = False`.

#### Priority 2: Dependency & Environment Health

- \[ \] **Task: Resolve Pandas library deprecations.**
	- *Action:* Your environment is running outdated C-extensions. Run `pip install --upgrade numexpr>=2.10.2 bottleneck>=1.4.2` to clear the terminal warnings and ensure optimal Pandas performance.
- \[ \] **Task: Fix Stacking Ensemble dependencies.**
	- *Action:* Backtests are failing on the `stacking` strategy with "Failed: pip install 'lottery-engine'". Ensure the ML requirements (like `scikit-learn` or whatever your stacking model relies on) are explicitly defined in your `pyproject.toml` under a `[project.optional-dependencies]` block (e.g., `pip install -e .[ml]`).

#### Priority 3: UX & Interface Hardening

- \[ \] **Task: Implement a Wheel Generation Circuit Breaker.**
	- *Action:* In `engine/cli/main.py wheel`, check `len(combinations)`. If > 10,000, print a warning and require the user to pass an `--export` flag instead of attempting to render a Rich table.
- \[ \] **Task: Cleanup WIP Board Views.**
	- *Action:* You currently have 11 views under `board` (e.g., `coverage`, `cluster`, `halves`) that output `⚠ View '<view>' is currently being modularized`. Remove these from the `--help` dialogue using Typer's `hidden=True` parameter until they are actually implemented. Do not advertise broken features.
- \[ \] **Task: Graceful failure for missing Draw IDs.**
	- *Action:* If `backtest` is run without a `DRAW_ID` or `--prev`, do not just print a warning and exit. Raise a `typer.BadParameter` or automatically fallback to `--prev 1`.

#### Priority 4: Documentation Improvements

- \[ \] **Task: Document Esoteric Strategy Limitations.**
	- *Action:* In your core docs (`lottery docs`), explicitly state that `weather`, `solar`, and `moon_phase` require historical dates to function, and document how they behave (neutral weighting) for future predictions.
- \[ \] **Task: Add CLI Quoting Examples.**
	- *Action:* Update the help text for the `portfolio` command to clarify that multi-word strings must be wrapped in quotes (e.g., `--full-name "Your Name"`), as passing it unquoted caused unexpected argument crashes.
- \[ \] **Task: Explain Minimum Data Floors.**
	- *Action:* Document the "minimum data floor" warnings. The engine spams `WARNING:root:Strategy 'markov' is running near its minimum data floor...`. Add a note in the docs on how to suppress this (and consider adding a `--quiet` or `--log-level ERROR` global flag to your CLI).

---

------



