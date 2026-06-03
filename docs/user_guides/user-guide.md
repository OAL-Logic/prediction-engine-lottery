# Absurdity Engine: Master User Guide 🔮

Welcome to the **Universal Synapse** (v10.0). This engine is designed for explorers who believe that the boundary between "random chance" and "ordered chaos" is thinner than it looks.

## 🚀 Quick Start: Top Workflows

### 1. The Daily Pilot (Auto-Selection)
**Best for:** Pragmatic players who want the empirically best setup for today.
```bash
# Step 1: Discover the best configuration for your game
lottery tune br/lotofacil --draws 30 -o tuned/lotofacil.yaml

# Step 2: Generate today's ticket using that tuned winner
lottery forecast br/lotofacil --config tuned/lotofacil.yaml --explain
```
*Why this works:* `tune` runs an out-of-sample sweep across strategies, parameters, and filters to find what actually worked in the last 30 draws. `forecast` then applies those exact winning settings.

### 2. The Daily Diagnostic (The Standard Path)
**Best for:** Most users, every day.
```bash
lottery daily br/lotofacil
```
*Why this works:* It runs a 5-stage pipeline checking for statistical regimes, GO/NO-GO conditions, and an ensemble forecast.

### 3. The Private Profile (Secure Personalization)
**Best for:** Using personal data without leaking it.
1. Create a file named `personal.local.yaml` in the project root.
2. Add your private data:
   ```yaml
   full_name: "Your Full Name"
   birth_date: "1990-01-01"
   ```
3. Run any esoteric strategy:
   ```bash
   lottery suggest br/lotofacil --strategy kabbalistic
   ```
*Why this works:* It creates an **Intentional Seed** based on your name's vibration, your karmic cycle, and your current intent. The engine automatically loads any `*.local.yaml` file (which is git-ignored) and injects the data into relevant strategies like `kabbalistic`, `numerology`, and `biorhythm`.

### 4. The Alpha Pack (Survival Mode)
**Best for:** Pragmatic players who want to follow the winning momentum.
```bash
lottery suggest mega-sena --strategy survival
```
*Why this works:* It looks at the last 10 draws, **prunes** losing strategies, and runs a Monte Carlo simulation to find convergence.

### 5. The Chaos Storm (Environmental OSINT)
**Best for:** When the world feels "jittery" or significant events are happening.
```bash
lottery suggest mega-sena --strategy solar,moon_phase,weather
```
*Why this works:* It blends geomagnetic storms, lunar tides, and atmospheric static.

---

## 📊 Visual Board Mapping
The engine provides deep spatial visualization of draw patterns.

- **`lottery board <game> --view heatmap`**: Shows a global frequency heatmap with color gradients.
  - **[BOLD RED]**: Top 10% most frequent numbers.
  - **[BOLD YELLOW]**: Warm numbers.
  - **[GREEN]**: Normal frequency.
  - **[BLUE]**: Cool numbers.
  - **[DIM]**: Cold numbers.
  - Use **`--numbers "1 13 32"`** to mark specific numbers on the board for visual comparison.

- **`lottery backtest <game> --map`**: Runs a backtest and shows a historical heatmap *for every draw*, highlighting which winners were "hot" or "cold" at that specific moment in time.

---

## 🧙 The Wizard (Recommended)
If you are new, just run `lottery wizard`. It now features:
1. **Numeric Selection**: No more typing long lottery IDs. Just type the index number.
2. **Contextual Help**: Guidance on what each mode (Suggest, Wheel, Backtest) does.
3. **Smart Defaults**: Suggests reasonable parameters based on the lottery's rules.

---

## 🔬 Confidence Scores
Every strategy reports a **Confidence Score (0.0 — 1.0)**.
- **[GREEN] 0.8+**: Extremely strong signal detected.
- **[YELLOW] 0.4 - 0.6**: Average statistical confidence.
- **[RED] < 0.2**: Low signal; lottery is in a high-entropy/random state.

---

## 🛠️ Expert Flag Reference

| Flag | Purpose | Example |
| :--- | :--- | :--- |
| `--count` | Number of tickets to generate | `--count 5` |
| `--temp` | Chaos factor (0=Deterministic, 1=Balanced) | `--temp 0.8` |
| `--draw-date` | Target date for fun strategies | `--draw-date 2026-05-01` |
| `--full-name` | Personalized vibration seeding | `--full-name "Operator D"` |
| `--filters` | Structural harmony rules | `--filters balanced` |
| `--limit` | Focus only on the last N draws | `--limit 30` |
| `--adaptive-window` | Sweeps history limits to find optimal signal | `--adaptive-window` |

### 🔬 The "Backtester" Command
Test how a strategy *would* have performed over a historical range:
```bash
lottery backtest mega-sena --strategy survival --prev 1-10 --map
```

### 📈 Additional Tools & Commands
- **`lottery analyze <game>`**: Generate a 14-chart dashboard (frequency, recency, gap).
- **`lottery portfolio <game>`**: Balanced tickets across Statistical, Chaos, and Deep tiers.
- **`lottery wheel <game>`**: Combinatorial covering designs for guaranteed matches.
- **`lottery optimize <game>`**: Grid-search to find the best Strategy/Limit/Temp combination.

---

## 🔬 Diagnostic Terminal (Advanced)

These commands transform the CLI from a ticket generator into a **pattern diagnostic terminal** — tools that tell you *whether* the data contains detectable structure and *whether today is a good time to play*.

### Morning digest (recommended daily command)
```bash
lottery daily br/lotofacil                    # full 5-stage pipeline: regime+scan+EV+ticket+oracle
lottery daily br/lotofacil --persona mystic   # oracle in mystic persona
```
*Why this works:* It chains every major diagnostic tool into a single sequence, ensuring you never play without checking the statistical regime and current expected value (EV) first.

### Cron alert monitor
```bash
lottery alert br/lotofacil                           # GO-STRONG + regime-shift by default
lottery alert br/lotofacil --condition go,chi2-alarm # custom conditions
```
*Why this works:* It acts as a passive guardian, exiting with a non-zero code unless specific high-confidence conditions are met. Perfect for automation scripts.

### Weekly performance summary
```bash
lottery weekly br/lotofacil               # 7-day summary from logs
lottery weekly br/lotofacil --weeks 2     # last 2 weeks
lottery weekly br/lotofacil --export-md reports/week.md
```

Reads `data/draw_log.jsonl` + `data/ticket_log.jsonl` to show:
- Confidence/entropy/chi² sparkline trends
- Tickets generated and hit counts against actual draws
- Best hit, avg hits, regime stability summary

### Hit-check tickets against actual draws
```bash
lottery hitcheck br/lotofacil             # compare logged tickets vs latest draw
lottery hitcheck br/lotofacil --draws 5  # check vs last 5 draws
lottery hitcheck br/lotofacil --since 2026-05-01
```

`lottery forecast` and `lottery daily` automatically log generated tickets to `data/ticket_log.jsonl`.

### Watchlist — batch tracking across multiple games
```bash
lottery watchlist add br/lotofacil      # track a game
lottery watchlist add br/mega-sena      # add more
lottery watchlist list                  # show all tracked games + added date
lottery watchlist status                # last-logged verdict/score/regime per game
lottery watchlist run                   # full morning digest for each tracked game
lottery watchlist run --mode alert      # alert check across all; exit 0 if any triggered
lottery watchlist run --mode scan       # compact GO/NO-GO table for all games
lottery watchlist remove br/mega-sena   # stop tracking a game
```

### One-liner entry point
```bash
lottery next br/lotofacil          # scan conditions + consensus ticket in one command
lottery next br/lotofacil --quiet  # just the numbers (cron-friendly)
```
*Why this works:* It provides the fastest possible path from data to a high-probability ticket by automatically bypassing the detailed reports and only outputting results if a "GO" condition is met.

### Condition scan (GO/NO-GO)
```bash
lottery scan br/lotofacil                    # 6-layer pre-draw conditions check
lottery scan br/lotofacil --suggest          # auto-generate ticket if GO
```
*Why this works:* It prevents "Blind Betting" by quantifying environmental noise, signal stability, and data fairness across 6 independent analytical layers.

### Weighted ensemble ticket
```bash
lottery forecast br/lotofacil                        # default 6-strategy group
lottery forecast br/lotofacil --strategies fast      # fast 3-strategy group
```
*Why this works:* It mitigates the risk of any single strategy failing by creating a "Wisdom of the Crowd" consensus, where each strategy's contribution is weighted by its recent historical accuracy.

### Strategy diagnostic leaderboard
```bash
lottery leaderboard br/lotofacil                     # default strategy group
lottery leaderboard br/lotofacil --strategies statistical
```
*Why this works:* It identifies which strategies are actually "detecting" a signal versus which ones are just noise, by measuring the variance in their confidence scores over a rolling window.

### Empirical calibration (real hit rates)
```bash
lottery calibrate br/lotofacil                        # default group, 15 draws
lottery calibrate br/calibrate br/lotofacil --draws 30             # more draws = more reliable
```
*Why this works:* It provides a strict "Out-of-Sample" reality check by running a series of mini-backtests to see how many numbers each strategy *actually* matched in previous real-world draws.

### Signal-to-Noise dashboard
```bash
lottery signal br/lotofacil                          # rolling stability sparklines
```
*Why this works:* It visualizes the "Predictability" of the lottery over time, allowing you to see if the current data is in a state of high signal (predictable) or high noise (random).

### Adversarial stress-test
```bash
lottery stress-test br/lotofacil                     # inject random draws, test Δ
```
*Why this works:* It proves the strategy's validity by testing if it can distinguish real historical draws from fake, randomly generated ones. If the performance is the same, the strategy is likely just guessing.

### Unsupervised clustering
```bash
lottery cluster br/lotofacil                         # K-Means draw profiles
```
*Why this works:* It groups historical draws into "Profiles" (e.g., high-sum, cluster-heavy), helping you identify which "flavor" of draw is currently trending.

### Esoteric cycle correlation
```bash
lottery detect-patterns br/lotofacil                 # lunar + solar overlay
```
*Why this works:* It identifies hidden correlations between draw outcomes and planetary or geomagnetic cycles that are often invisible to standard statistical models.

### Regime-shift detection
```bash
lottery compare-draws br/lotofacil                   # JS divergence vs history
```
*Why this works:* It detects when the underlying "Physics" of the draw has changed (e.g., a new machine or ball set), signaling that older historical data may no longer be relevant.

### Passive daily log
```bash
lottery log br/lotofacil                    # append snapshot to data/draw_log.jsonl
```
*Why this works:* It builds a long-term "Diagnostic History" for each game, enabling the engine to track its own performance and signal stability over months and years.

### Explain flag (on suggest)
```bash
lottery suggest br/lotofacil --explain          # show top-3 contributing numbers
lottery suggest br/lotofacil --window-check     # abort if signal is unstable
```

---

## 🧘 Pro-Tip: The "Harmonious" Filter
The engine automatically can discard tickets that are "Mathematically Ugly" via **`--filters balanced`**:
- **Sum-Range Check:** Ensuring the total isn't too high or too low.
- **Parity Balance:** Discarding all-even or all-odd tickets.
- **Decade Breadth:** Ensuring the numbers are spread across the board.

---

## 📚 Appendix: Strategy Index

The engine supports a vast library of analytical and esoteric strategies. You can use these names with `--strategy <name>`.

### Statistical Tier (Nerd Mode)
- **`markov`**: First-order Markov chain transitions.
- **`bayesian`**: Recency-weighted Bayesian frequency.
- **`weighted`**: Balanced blend of frequency, gap, and position.
- **`hedge`**: Optimized for high-frequency lower-tier prize stability (Safe Play).
- **`vix_jitter`**: Correlates draw randomness with global financial volatility regimes.
- **`monte_carlo`**: Structural simulation and filtering.
- **`pattern`**: Empirical pattern matching.
- **`momentum`**: RSI-style frequency trend detection.
- **`spectral`**: FFT-based periodicity analysis.
- **`streak`**: Hot/Cold streak tracking.
- **`crowd_avoidance`**: Psychological bias evasion (EV focus).
- **`steiner_wheel`**: Combinatorial covering designs.
- **`void`**: Spatial void analysis for mean reversion.
- **`copairs`**: Co-occurrence and companion number analysis.
- **`cycle`**: Hit cycle and oscillation analysis.
- **`mutual_info`**: Information-theoretic dependency mapping.
- **`stability`**: Long-term hit rate variance tracking.
- **`harmonic`**: Convergence of physical grid and statistical lift.
- **`fisher`**: Information geometry and sensitivity peaks.
- **`primes`**: Prime density oscillator (Lunar-entrained).
- **`positional`**: Probability density of sorted draw slots.
- **`contagion`**: Physical grid neighbor 'spark' resonance.
- **`evt_extremes`**: Extreme Value Theory peaks.
- **`nash_equilibrium`**: Game-theoretic Nash equilibrium.
- **`stefan_mandel`**: 💼 Stefan Mandel Combinatorial Condensation — mathematical arbitrage formula targeting jackpots that exceed total combination costs with optimal coverage density.

### Esoteric & Chaos Tier (Absurdity Engine)
- **`numerology`**: Pythagorean date-based reduction.
- **`iching`**: Yarrow stalk hexagram casting.
- **`kabbalistic`**: Sephoric numerology and Triangle of Life.
- **`ley_lines`**: Astro-cartography and Earth grid resonance.
- **`noosphere`**: Global entropy jitter and collective unconscious.
- **`sefirot`**: Kabbalistic Tree of Life emanation paths.
- **`solar`**: NOAA K-index solar flare correlation.
- **`moon_phase`**: Lunar cycle and tidal drag frequency.
- **`weather`**: Atmospheric condition and refraction correlation.
- **`fibonacci`**: Golden ratio and market retracement levels.
- **`zodiac`**: Western astrological sign resonance.
- **`biorhythm`**: Personal biological cycle harmonics.
- **`lorentz`**: Strange attractor and Butterfly Effect simulation.
- **`sentiment`**: Social pulse and digital viral simulation.
- **`reincarnation`**: Past-life draw signature matching.
- **`entropy_global`**: Global chaos peak correlation.
- **`gematria`**: Linguistic vibration and name mapping.
- **`refraction`**: Atmospheric static potential mapping.
- **`seismic`**: Seismic activity resonance from USGS earthquake data.
- **`archetypes`**: Numerical archetypes and balanced narrative.
- **`kinetic`**: Pseudo-kinetic bouncing balls simulation.
- **`benford_illusion`**: Benford's Law anomaly analysis.
- **`retrocausality`**: Quantum retrocausality and future echoes.
- **`sacred_manifold`**: Spherical grid alignment with celestial transits.
- **`tda_topology`**: Topological data analysis and structural holes.

### Advanced & ML Tier
- **`synapse`**: The "Universal Conjunction" — convergence of Statistical, Deep, and Chaos tiers (The Peak Strategy).
- **`regime`**: Dynamic switching between models based on detected statistical "market regimes".
- **`voting`**: Weighted average ensemble of multiple independent strategies.
- **`logistic`**: Logistic regression classifier for probability estimation.
- **`knn`**: K-Nearest Neighbors sequence similarity clustering.
- **`quantum_anneal`**: Simulated quantum tunneling for cold-escape.
- **`survival`**: Alpha-pruning meta-ensemble (Auto-Backtest).
- **`transformer`**: Attention-based deep sequence modeling.
- **`lstm_gru`**: Recurrent memory cell sequence modeling.
- **`cnn_1d`**: Dilated 1D convolutional signal motifs.
- **`prob_weighted`**: Precision-weighted adaptive ensemble.
- **`hybrid`**: Two-stage statistical-structural filter.
- **`stacking`**: Meta-learner strategy blending.

---

*Disclaimer: This project is a mathematical and esoteric exploration. Use for entertainment only. Luck favor the bold.*
