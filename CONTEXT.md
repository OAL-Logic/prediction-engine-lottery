# Context — Lottery Prediction Engine & Prophet Desktop Cockpit

## Domain Overview

The **Lottery Prediction Engine** is a high-performance mathematical, statistical, machine-learning, and combinatorial asset-generation framework. It treats lottery tickets not as games of pure chance, but as high-dimensional combinatorial search spaces that can be audited, filtered, optimized, and backtested under strict mathematical criteria.

The project encompasses four main interfaces:
1. **Prophet Desktop Cockpit (`desktop/`)**: A native PySide6 / Qt6 desktop application providing virtualized spreadsheet data management, 6-layer forensic analysis, 105+ combinatorial filters, covering wheels, ticket optimization, and multi-model prediction visualization.
2. **Terminal Engine & OpenTUI (`engine/` + `tui/`)**: A rich, headless command-line interface for rapid scripting, batch execution, and automation.
3. **Mobile Companion App (`app/`)**: An Expo/React Native mobile application for mobile validation and quick picks.
4. **Gateway Microservice (`gateway/`)**: A Go-based telemetry hub implementing Post-Quantum Cryptography (PQC) and real-time state streaming.

---

## Ubiquitous Language & Core Concepts

For the complete canonical vocabulary and local jurisdiction translations, see [GLOSSARY.md](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/PRJ%20Prediction%20Engine/lottery/GLOSSARY.md).

### Lottery Assets & Configurations
- **Lottery Asset / Context (`lottery_id`)**: A specific game identified by country and slug (e.g. `br/mega-sena`, `br/lotofacil`, `br/quina`, `us/powerball`). Defines the game matrix: pool size $N$, draw size $k$, bonus numbers, and prize payout tiers.
- **Global Compatibility & Jurisdiction Isolation**: Core mathematical, analytical, and combinatorial features are strictly game-agnostic and operate against abstract contracts (`DrawRules`, `GameDefinition`). Commercial rules, jurisdiction scrapers, and game idiosyncrasies (e.g., Brazilian Caixa Loterias rules, US MUSL rules) are isolated in `engine/adapters/<country_code>/`. Features provide pluggable hooks for game-specific rule overrides and workarounds while ensuring seamless compatibility with any world lottery.
- **Draw Record**: A single historical event with draw number (`concurso`), date, drawn winning numbers, and prize payout statistics.
- **Candidate Pool**: A chosen subset of numbers ($v$ numbers where $k \le v \le N$) from which tickets will be generated. In legacy Lottery Studio, this pool was artificially restricted to $\le 10$; in this engine, it is completely unrestricted.

### Analytical & Diagnostic Cockpit
- **6-Layer Diagnostic Scan**: A comprehensive health check of the historical draw stream:
  1. *Distribution*: Chi-square goodness-of-fit and frequency uniformity ($p$-value).
  2. *Parity & Balance*: Odd/Even and Low/High decade ratios.
  3. *Spacing & Clusters*: Successive runs, consecutive differences, and AC (Arithmetic Complexity) values.
  4. *Entropy & Information*: Shannon entropy, compression ratio, and Jensen-Shannon divergence.
  5. *Harmonic Resonance*: Digital root sums, modular remainders, and periodic Fourier cycles.
  6. *Regime Detection*: Classification into `STABLE`, `DRIFT`, or `SHIFT` states.
- **Skips (Gaps)**: The count of consecutive drawings since a number last appeared.
  - *Actual Skip*: Current number of draws since last hit.
  - *Average Skip*: Historical mean distance between occurrences: $(T - \text{hits}) / \text{hits}$.
  - *Max Skip*: Worst-case drought for that number.

### Combinatorial Filtering & Pruning (Harmony Gate)
- **Combinatorial Space**: The entire set of $\binom{N}{k}$ possible combinations (e.g., 50,063,860 for Mega-Sena; 3,268,760 for Lotofácil).
- **Harmony Gate**: The 5-tier filtering engine evaluating combinations across 105+ distinct statistical metrics:
  - *Tier 1*: Universal fundamentals (Sum, Parity, Low/High, Prime count).
  - *Tier 2*: Positional bounds ($P_1 \dots P_k$ min/max ranges).
  - *Tier 3*: Structural patterns (Consecutive runs, AC value, Digital Root Sum, Decade spans).
  - *Tier 4*: Historical recurrence (Previous draw repeat count, Cold number count, Skip sum).
  - *Tier 5*: Harmonic & Esoteric (Modular balance, Astro/Lunar aspects, Seismic markers).
- **Fault Tolerance ($N$-of-$M$)**: A safety feature allowing a ticket to fail up to $M - N$ filter criteria while still being retained, preventing accidental elimination of jackpot combinations due to single-filter boundary edge cases.

### Wheeling & Covering Designs
- **Covering Design $C(v, k, t, m) = b$**: A mathematical guarantee that if $m$ of the winning numbers fall within the chosen $v$-number pool, at least one ticket will match at least $t$ numbers, producing $b$ tickets.
- **Abbreviated Wheel**: A mathematically minimized ticket set satisfying the covering guarantee with significantly fewer tickets than a full combinatorial wheel.
- **Power / Key Numbers**: Fixed numbers that are included in every single ticket generated by the wheel.

### Ticket Optimization & Pruning
- **Overlap Reduction (`same_number_reduction`)**: An optimization pass that eliminates ticket redundancy by enforcing that no two tickets share more than $M$ numbers (maximizing combinatorial dispersion).
- **Block Reservation (`reserve_per_block`)**: Partitioning generated candidates into uniform blocks and keeping only the top-scoring candidate per block, ensuring wide structural diversity.
- **Positional Generator**: Generating tickets directly inside the historical empirical probability distribution of each sorted position index ($P_1 < P_2 < \dots < P_k$).

### Prediction & Machine Learning Engine
- **Strategy Families**: Curated model groups (Statistical, ML, Deep Learning, Foundation, Chaos, Esoteric).
- **Hazard & Renewal Modeling (`hazard_weibull`)**: Models draw skips and droughts via dual non-parametric empirical conditional hazard $P(T = d+1 \mid T \ge d+1)$ and continuous Weibull hazard $h(t) = \frac{\gamma}{\lambda}(t/\lambda)^{\gamma - 1}$.
- **Dirichlet-Smoothed Markov Transitions (`markov`)**: Models inter-draw transition graphs with symmetric Dirichlet smoothing prior ($\alpha_{\text{eff}} = \alpha / K$) to eliminate zero-probability states and exponential temporal decay with half-life $\tau_{1/2}$.
- **Entropic Softmax Sampling (`--target-entropy`)**: Shift-invariant Softmax probability calibration solving for thermodynamic temperature $\tau$ via monotone bisection to guarantee that candidate generation matches an exact Shannon entropy budget $H^*$.
- **Combinatorial MILP Covering (`reduce_tickets_milp`)**: Solves the exact Minimum Set Cover problem for combinatorial wheels using Mixed-Integer Linear Programming (HiGHS solver via `scipy.optimize.milp`), guaranteeing minimal ticket cardinality for covering guarantees $C(v, k, t, m)$.
- **Purged Hypergeometric Filtering (`HistoricalSumRangeFilter`)**: Replaces empirical historical window boundaries with exact analytical hypergeometric expectation $\mathbb{E}[\text{Sum}] = \frac{k(N+1)}{2}$ and variance $\text{Var}[\text{Sum}] = \frac{k(N-k)}{N-1}\frac{N^2-1}{12}$, bounding combinations within $\mathbb{E} \pm 2.8\sigma$ without data snooping or lookahead bias.
- **Multi-Model Stacking**: An ensemble combining heterogeneous predictors (e.g. CatBoost gradient trees, Markov transition graphs, LSTM recurrent networks, and astronomical transit resonance) weighted dynamically based on the current diagnostic regime.
- **Pipeline Telemetry**: Real-time visual tracking of data ingestion, diagnostic state, model weight arbitration, filter funnel elimination, and final candidate justification.
- **Backtesting & Verification Leaderboard**: Running simulated blind historical draws across past years to compute real financial ROI, prize hits, and equity drawdowns.

---

## User Experience Archetypes

1. **Simple Usage (Pick & Play)**:
   - For users who want the intuitive, familiar feel of Lottery Studio:
     - Select Game $\to$ View latest results $\to$ Click "Generate Optimized Pick" $\to$ 1-Click Check against recent draws.
2. **Forensic Analysis (Advanced Cockpit)**:
   - For quantitative analysts, mathematicians, and researchers:
     - Full multi-tab drill-down into DuckDB queries, PyQtGraph interactive histograms, 105+ customizable Harmony Gate filters, custom combinatorial wheels, genetic swarm training, and live telemetry signals.
