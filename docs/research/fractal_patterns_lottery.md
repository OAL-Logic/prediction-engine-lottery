# 🌀 Fractal Patterns & the Absurdity Engine

> A deep-dive into how fractal geometry and chaos theory intersect with the lottery prediction engine you've already built — what's already there, what's missing, and what a dedicated `fractal` strategy would look like.

---

## 1. What Is a Fractal? (The Essential Math)

A **fractal** is a structure that exhibits **self-similarity across scales** — zoom in, and you see the same (or statistically similar) pattern repeating. Fractals arise from three distinct origins:

| Origin | Example | Engine Relevance |
|---|---|---|
| **Iterated Function Systems (IFS)** | Sierpiński triangle, Barnsley fern | Number scoring via geometric attractors |
| **Strange Attractors** | Lorenz attractor, Rössler system | ✅ Already in `lorentz` strategy |
| **Long-Range Dependence (LRD)** | Fractional Brownian motion | Hurst exponent on draw sequences |

The key mathematical idea is **fractal dimension** — a non-integer measure of how much "space" a pattern fills. A straight line is dimension 1.0; a plane is 2.0; the Lorenz attractor is ~2.06.

---

## 2. The Core Question: Are Lottery Draws Actually Fractal?

This is where it gets interesting. Here is the honest scientific answer:

> A **perfectly fair** lottery draw is i.i.d. uniform — every draw is independent. Pure white noise. Fractal dimension = maximum entropy. **No exploitable structure exists.**

BUT — here are the real-world caveats that make fractal analysis *useful* even if the game is fair:

### 2.1 Ball Machine Physics (Physical Chaos)
Real RNG machines are physical chaotic systems. Small perturbations in initial ball positions cascade — this is the **Butterfly Effect** you encoded in `lorentz.py`. Chaotic physical systems *do* produce trajectories with fractal structure. The ball machine is not a perfect uniform sampler; it is a strange attractor passing through a discrete sampling grid.

### 2.2 Draw Sequence as a Time Series
Even if individual draws are fair, the **sequence of which numbers appear over hundreds of draws** is a time series you can analyze. The question becomes:

- Is the autocorrelation in that time series consistent with **pure white noise**?  
- Or does it show **long-range dependence** (Hurst exponent H > 0.5)?

Your `spectral` strategy already probes this — FFT periodicity analysis is the frequency-domain cousin of fractal analysis.

### 2.3 The Number Grid Is a Spatial Structure
The physical board (1–25 for Lotofácil, 1–60 for Mega-Sena) is a **2D lattice**. Winning numbers form a **spatial pattern** on that grid each draw. Your `contagion` strategy already models this: neighboring numbers on the grid "spark" each other. Fractal geometry would ask — do winning patterns on the grid show **spatial self-similarity**?

---

## 3. Strategies That Already Embody Fractal Thinking

The engine already has several strategies that are, conceptually, fractal methods in disguise:

### 🌪️ `lorentz` — Strange Attractor (Direct Fractal)
```
Dimension: ~2.06 (Lorenz attractor)
What it does: Maps board numbers to 3D space → runs Euler integration 
of the ODE system → scores numbers by how often the chaotic trajectory 
"visits" their neighborhood.
```
**This IS a fractal strategy.** The Lorenz attractor is a fractal object. Your implementation maps the game's number space onto the attractor's natural scale. The weakness is that the mapping is arbitrary — the `% side` modulo wrapping is not physically grounded in the game.

---

### 🌊 `spectral` — FFT Periodicity (Frequency-Domain Fractal Analysis)
```
What it does: Builds a binary time series (number appeared / didn't) 
→ FFT → detects dominant period → scores by phase alignment.
```
**Connection to fractals:** The power spectrum of a fractal signal follows a power law:  
`S(f) ∝ f^(-β)` where `β = 2H - 1` and `H` is the **Hurst exponent**.

If the draw sequence has `β ≈ 0`, it's pure white noise (H=0.5).  
If `β > 0`, the sequence has **long-range memory** (H > 0.5) — each draw is subtly correlated with far-past draws.

Your spectral strategy looks for *single* dominant cycles. A fractal spectral strategy would instead fit the **power-law slope** of the entire spectrum to measure this memory.

---

### 🌀 `fibonacci` — Golden Ratio (Nature's Fractal Blueprint)
```
What it does: Scores numbers by proximity to Fibonacci numbers, 
φ-ratio pairs, digit roots, and frequency retracement levels.
```
**Connection to fractals:** The Fibonacci sequence is the backbone of the **golden spiral** — the most famous natural fractal. φ (phi) appears in the scaling ratio of self-similar structures: nautilus shells, galaxy arms, sunflower seed heads. The engine already blends φ-proximity with historical frequency retracements (Fibonacci retracement levels, borrowed from technical finance).

---

### 🔥 `contagion` — Spatial Neighbor Resonance (Grid Fractal)
```
What it does: Treats the physical number board as a 2D grid → 
models "contagion" where numbers that are spatial neighbors of recent 
winners get a propagation score.
```
**Connection to fractals:** This is a discrete approximation of **percolation theory** — a fractal process. In percolation, clusters form with fractal boundaries. Your contagion model is a 1-step, nearest-neighbor version. A full fractal contagion model would compute the **fractal dimension of the winning cluster** across multiple draws.

---

### 🔢 `cycle` + `primes` — Oscillation and Number Theory
The `cycle` strategy detects oscillation periods; `primes` uses a prime density oscillator. Both are looking for **recursive structure in number-theoretic sequences** — which are self-similar by definition (prime distribution follows the Riemann zeta function, itself deeply connected to fractal geometry).

---

## 4. What's Missing: A True `fractal` Strategy

Here are three mathematically grounded methods the engine doesn't yet have:

---

### 4.1 Hurst Exponent (Long-Range Dependence Detector)

The **Hurst exponent** H measures memory in a time series:

| H value | Interpretation |
|---|---|
| H = 0.5 | Pure random walk (white noise) — no exploitable pattern |
| H > 0.5 | **Persistent** — trends continue (mean-following) |
| H < 0.5 | **Anti-persistent** — mean-reverting (contrarian signal) |

**For each number**, build its binary appearance series and compute H using **R/S analysis** (Rescaled Range):

```python
def hurst_exponent(ts: np.ndarray) -> float:
    """Compute Hurst exponent via R/S analysis."""
    N = len(ts)
    if N < 20:
        return 0.5
    
    lags = range(2, N // 2)
    rs_values = []
    for lag in lags:
        # Split into chunks of size lag
        chunks = [ts[i:i+lag] for i in range(0, N - lag + 1, lag)]
        rs_list = []
        for chunk in chunks:
            mean = np.mean(chunk)
            dev = np.cumsum(chunk - mean)
            R = dev.max() - dev.min()  # Range
            S = np.std(chunk)          # Standard deviation
            if S > 0:
                rs_list.append(R / S)
        if rs_list:
            rs_values.append((lag, np.mean(rs_list)))
    
    if len(rs_values) < 3:
        return 0.5
    
    lags_log = np.log([r[0] for r in rs_values])
    rs_log   = np.log([r[1] for r in rs_values])
    H, _ = np.polyfit(lags_log, rs_log, 1)
    return float(np.clip(H, 0.0, 1.0))
```

**Scoring logic:**
- Numbers with H > 0.6 → **persistence signal** → boost score if they recently appeared
- Numbers with H < 0.4 → **anti-persistence** → boost score if they recently *missed* (mean reversion)
- Numbers with H ≈ 0.5 → pure noise → use frequency fallback

This directly connects to your existing `void` strategy (which exploits mean reversion) and `momentum` strategy (which exploits trends) — but grounds them in a single, well-defined fractal measure.

---

### 4.2 Multifractal Detrended Fluctuation Analysis (MF-DFA)

Standard Hurst analysis assumes a **monofractal** — one scaling exponent. Real complex systems (financial markets, biological signals, and arguably lottery machines) are **multifractal**: different parts of the signal have different local Hölder exponents.

MF-DFA computes a **spectrum of Hurst exponents** `h(q)` for different statistical moments `q`. The **width** of this spectrum measures the degree of multifractality:

```
Δh = h(q_min) - h(q_max)
```

- Narrow spectrum → nearly monofractal → simple structure
- Wide spectrum → strong multifractality → rich, heterogeneous dynamics

**Engine application:** Run MF-DFA on the full draw history. If Δh is wide, the series has rich structure that `spectral` and `markov` strategies might be missing. If Δh is near zero, the data is truly memoryless.

This is a **meta-diagnostic** — it tells you *whether* pattern-seeking strategies have any hope, complementing your `scan` command's GO/NO-GO verdict.

---

### 4.3 IFS (Iterated Function Systems) Number Scoring

An **Iterated Function System** generates a fractal by repeatedly applying a set of contractive transformations. For the lottery:

1. Take the number range as the seed space [1, N]
2. Define transformations based on the draw date or seed (similar to how `lorentz` uses the date)
3. Iterate 10,000 times to find the **attractor** — the set of numbers the IFS converges to
4. Score numbers by density in the attractor

```python
# Example: 3 contractive maps on [1, 60] for Mega-Sena
def ifs_attractor(n_range, seed, n_iterations=10_000):
    lo, hi = n_range
    rng = np.random.default_rng(seed)
    
    # Three affine maps with different contraction ratios
    maps = [
        lambda x: x * 0.5,                    # left half
        lambda x: x * 0.5 + (hi - lo) * 0.5, # right half  
        lambda x: x * 0.333 + (hi - lo) / 3, # middle third
    ]
    
    x = float(lo)
    visits = np.zeros(hi - lo + 1)
    
    for _ in range(n_iterations):
        f = rng.choice(maps)
        x = f(x)
        idx = int(round(x)) - lo
        if 0 <= idx < len(visits):
            visits[idx] += 1
    
    return visits / visits.max()
```

The **seed** can be derived from the draw date, creating a deterministic but complex scoring that shifts each draw — similar to how `lorentz` seeds its initial state from the date.

---

## 5. Fractal Dimension of the Number Grid

One of the most direct fractal analyses you can run on the game data is to measure the **fractal dimension of winning patterns** on the physical board.

### Box-Counting Dimension

For each draw, place winning numbers on the board grid. Compute box-counting dimension:

```
D_b = lim(ε→0) [ log N(ε) / log(1/ε) ]
```

where N(ε) is the number of grid cells of size ε that contain at least one winning number.

- If winning patterns are **clustered** (fractal, D_b < 2), the `contagion` strategy benefits
- If they are **uniform** (D_b ≈ 2), spatial strategies have no edge

**Practical implementation:**

```python
def box_count_dimension(numbers: list[int], grid_width: int = 5) -> float:
    """
    Measure fractal dimension of a winning pattern on a square number grid.
    Assumes numbers are laid out left-to-right, row by row.
    """
    positions = [(n - 1) % grid_width, (n - 1) // grid_width]
    grid = set(map(tuple, positions))
    
    counts = []
    scales = [1, 2, 4]  # box sizes
    for box_size in scales:
        boxes = set()
        for x, y in grid:
            boxes.add((x // box_size, y // box_size))
        counts.append(len(boxes))
    
    if len(set(counts)) == 1 or counts[0] == 0:
        return 2.0
    
    log_scales = np.log(scales)
    log_counts = np.log(counts)
    slope, _ = np.polyfit(log_scales, log_counts, 1)
    return abs(float(slope))
```

Over many draws, you build a **distribution of fractal dimensions**. Draws with low D_b (clustered patterns) become a signal for the `contagion` strategy to bet on neighbors.

---

## 6. Connecting to the Engine's Existing Architecture

### Where a `fractal` Strategy Lives
Following the existing tier structure, a `fractal` strategy would sit in the **Statistical Tier** (`engine/strategies/statistical/fractal.py`) — it's data-driven and mathematically grounded, not esoteric.

### How It Integrates with the Scan Pipeline
The Hurst exponent gives you a per-number, quantitative regime signal that could enhance the existing `scan` command:

```
Layer 7: Fractal Memory — Hurst H per number
  H > 0.6  → persistent signal → reinforces momentum strategies  [+2 pts]
  H < 0.4  → anti-persistent   → reinforces void/streak strategies [+2 pts]
  H ≈ 0.5  → white noise       → reduces confidence in all pattern strategies [0 pts]
```

### How It Enhances the Leaderboard
MF-DFA Δh (multifractal width) over the full history tells you whether this draw's data has enough structure for *any* pattern strategy to score > 0.5 on the leaderboard. It's a pre-filter.

### How It Informs `forecast`
The `forecast` command's strategy weighting (`stability × discrimination`) could incorporate H:
- High-H numbers → weight Momentum/Spectral higher
- Low-H numbers → weight Void/Streak higher
- H≈0.5 numbers → weight Statistical (Bayesian/Frequency) higher

---

## 7. Philosophical Frame: The Game as a Fractal System

The deepest connection between fractals and a lottery game is **not about predicting outcomes** — it's about understanding the *shape of randomness itself.*

> "The question is not whether the lottery is random. The question is: what *kind* of random?"

- **White noise** (H=0.5): All strategies are noise. Play for fun.
- **Colored noise** (H≠0.5): Some strategies capture real signal. Play with structure.
- **Chaotic determinism** (Lorenz regime): The outcome is deterministic but sensitive — the strange attractor *visits* certain regions of number-space more often.

The engine's dual-track architecture — **Nerd Mode (Statistical)** vs **Chaos Mode (Absurdity Engine)** — perfectly mirrors the dichotomy between:
- **Fractal statistics** (Hurst, MF-DFA, box-counting) → Nerd Mode
- **Strange attractors, IFS, chaos** (Lorentz, Fibonacci spirals) → Chaos Mode

They are two faces of the same mathematical object.

---

## 8. Proposed New Strategies Summary

| Strategy Name | Method | Tier | Connects To |
|---|---|---|---|
| `fractal` | Hurst exponent per number (R/S analysis) | statistical | `void`, `momentum`, `streak` |
| `multifractal` | MF-DFA spectrum width (Δh) | statistical | `scan`, `leaderboard`, `forecast` |
| `ifs` | Iterated Function System attractor scoring | fun | `lorentz`, `fibonacci` |
| `boxcount` | Box-counting fractal dimension of draw patterns | statistical | `contagion`, `heatmap` |

---

## 9. Quick Experiment You Can Run Now

Without writing any new strategy, you can get a rough fractal signal today using the existing `spectral` strategy in a slightly different way. The **slope of the log-log FFT power spectrum** is a proxy for the Hurst exponent:

```bash
# Run spectral analysis on a large history window
lottery suggest br/lotofacil --strategy spectral --limit 500

# Compare with shorter window  
lottery suggest br/lotofacil --strategy spectral --limit 50

# If results diverge significantly → the sequence has long-range memory
# (a fractal signal). If they converge → white noise.
lottery suggest br/lotofacil --strategy spectral --adaptive-window
```

The `--adaptive-window` flag already sweeps history limits to find the optimal signal — this is effectively a crude Hurst analysis. Numbers that score consistently high across many window sizes have **scale-invariant** signal — the definition of a fractal.

---

*"Chaos is not disorder — it is order at a scale we haven't found yet."*
