# 15 — Complete `reference.local/` Distillation & Hybrid Synthesis Matrix

> **Purpose**: Guarantee that **100% of every file, mathematical formula, physical/astronomical constant, statistical operator, esoteric/numerological parameter, machine-learning curve, covering wheel specification, and binary disassembly routine** inside the git-ignored `reference.local/` directory is permanently captured, documented, and implemented inside tracked repository files (`engine/`, `docs/`, `data/`, `tests/`), while elevating those intrinsic mechanics into new, grounded hybrid algorithms.

---

## 1. Master Traceability Matrix (`reference.local/` $\to$ Tracked Repository)

| Source Path in `reference.local/` | Category | Intrinsic Models, Constants & Mechanics | Tracked Documentation | Tracked Code / Data Implementation |
| :--- | :--- | :--- | :--- | :--- |
| `old/Modules/astronomy_engine.py` | Astronomical / Physical | Synodic lunar month $L_{\text{syn}} = 29.530588853\text{ days}$; J2000 New Moon epoch `2000-01-06 18:14:00 UTC`; 8-octant lunar phase classification; phase-dependent odd/even/prime/central-range boost $[1.0, 1.30]$. | §2.1 below | [`SynodicAstronomyModel`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/modules/esoteric.py`](../../../../engine/modules/esoteric.py) |
| `old/Modules/bayesian_inference.py` | Statistical / Bayesian | Symmetric Beta-Binomial Laplace smoothing $P(i \mid \mathcal{H}) = \frac{c_i + \alpha}{T + 2\alpha}$ ($\alpha = 1.0$); elevated with exponential forgetting factor $\gamma \in (0, 1]$. | §2.2 below | [`LaplaceBayesianTracker`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/strategies/bayesian.py`](../../../../engine/strategies/bayesian.py) |
| `old/Modules/markov_predictor.py` | Stochastic / Markov | All-pairs cross-draw bipartite transition matrix $M[u][v] = \sum_{t} \mathbb{I}(u \in D_t \land v \in D_{t+1})$ ($1 \le u,v \le N$); elevated to 2nd-order lag-2 blend $S(v) = (1-\lambda)S_1(v) + \lambda S_2(v)$. | §2.3 below | [`BipartiteMarkovChain`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/strategies/markov.py`](../../../../engine/strategies/markov.py) |
| `old/Modules/numerology_analyzer.py` | Esoteric / Numerology | Master-preserving digital root (`11, 22, 33` preserved); Modulo-9 congruence (`i % 9 == lp % 9` $\to +0.25$) + digit-substring inclusion (`str(lp) in str(i)` $\to +0.15$). | §2.4 below | [`MasterNumerologyResonator`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/modules/numerology.py`](../../../../engine/modules/numerology.py) |
| `old/Modules/weather_engine.py` | Meteorological / Physical | Date-seeded deterministic micro-climate (`MD5(YYYY-MM-DD)[:8]`); temperature $T \in [15, 35]^\circ\text{C}$, humidity $H \in [30, 90]\%$, pressure $P \in [1000, 1025]\text{ hPa}$; thermal/barometric number weighting. | §2.5 below | [`DeterministicWeatherCorrelator`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/modules/weather.py`](../../../../engine/modules/weather.py) |
| `old/Modules/correlation_analyzer.py` | Statistical Correlation | Pearson correlation $r_{X,Y}$ between `temperature`/`humidity` and draw `sum`, `mean`, and `even_count`. | §2.5 below | [`DeterministicWeatherCorrelator.analyze_historical_correlations`](../../../../engine/modules/hybrid_synthesis.py) |
| `old/Modules/statistics_analyzer.py` | Board Geometry & Number Theory | 5×5 Frame/Border (`MOLDURA` = 16 cells) vs Center (`MIOLO` = 9 cells), Primes (`PRIMOS`), Fibonacci (`FIBONACCI`), pairwise frequency (`Counter(combinations(sorted(draw), 2))`), Gap/Atraso (`T - last_seen[i]`). | §2.6 below | [`BoardGeometryAndBoundaryBalancer`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/core/analytics.py`](../../../../engine/core/analytics.py) |
| `old/Modules/weighted_ensemble.py` | Multi-Model Ensemble | Tri-Modal convex combination: $W_{\text{total}}(i) = 0.40 \cdot \widetilde{W}_{\text{Markov}}(i) + 0.40 \cdot \widetilde{W}_{\text{Bayes}}(i) + 0.20 \cdot \widetilde{W}_{\text{Astro+Num}}(i)$. | §2.7 below | [`TriModalWeightedEnsemble`](../../../../engine/modules/hybrid_synthesis.py) & [`engine/strategies/ensemble.py`](../../../../engine/strategies/ensemble.py) |
| `old/Modules/main_engine.py` & `main.ipynb` | Combinatorial Boundary-Swap Equilibrium | Post-sampling **Boundary-Swap Sum Equilibrium Operator**: if $\sum T < \Sigma_{\min}$, swap $\min(T)$ with $\max(P \setminus T)$; if $\sum T > \Sigma_{\max}$, swap $\max(T)$ with $\min(P \setminus T)$. | §2.6 & §2.7 below | [`BoardGeometryAndBoundaryBalancer.boundary_swap_sum_balance`](../../../../engine/modules/hybrid_synthesis.py) |
| `catboost_info/catboost_training.json` | Gradient Boosted Decision Trees | 100-iteration CatBoost RMSE convergence curve (`0.4648447607` $\to$ `0.2364516368`) on tabular lag features. | §3 below & [`03-ml-and-deep-learning-models.md`](../../wiki/02-theoretical-foundations/03-ml-and-deep-learning-models.md) | [`engine/strategies/ml_boost.py`](../../../../engine/strategies/ml_boost.py) |
| `SamLotto Free Edition/Drawings/*.txt` (308 files) | Historical Draw Corpus | 308 international & national lottery draw history files (`Pick3`, `Pick4`, `PowerBall`, `MegaMillions`, `EuroMillions`, `UK Lotto`, etc.). | [`02-Binary-Data-Formats-and-File-Structures.md`](02-Binary-Data-Formats-and-File-Structures.md) | `data/drawings/` (all **308/308** files tracked) |
| `SamLotto Free Edition/Formula/*.Wheels` (2,360 files) | Combinatorial Covering Designs | 2,360 abbreviated & full wheel files (`W{k}{v}{t}{m}_{lines}.Wheels`), 8-byte binary block stride, reduction ratios up to $99.9\%$. | §4 below & [`03-Abbreviated-Wheeling-Engine-and-Covering-Designs.md`](03-Abbreviated-Wheeling-Engine-and-Covering-Designs.md) | [`docs/reference/architecture/wheels-catalog.csv`](wheels-catalog.csv) & [`CoveringWheelCatalogAndSynthesizer`](../../../../engine/modules/hybrid_synthesis.py) |
| `SamLotto Free Edition/disassembly_*.txt` (27 files) | Binary Reverse Engineering | 91-entry jump table `jump_table_58613d[0x5b]`, 24-byte ticket stride (`0x18`), $10^6$ ticket cap (`0xf4240`), `u"||$[[][][]]"` filter grammar, intrusive Red-Black BST (`+0x04..+0x14`) for $O(\log N)$ hit counting. | §5 below & [`14-Static-Binary-Analysis-and-Reverse-Engineering.md`](14-Static-Binary-Analysis-and-Reverse-Engineering.md) | [`engine/filters/`](../../../../engine/filters/) & [`engine/modules/hybrid_synthesis.py`](../../../../engine/modules/hybrid_synthesis.py) |
| `SamLotto Free Edition/Documentation/_wayfinder/` | Reverse Engineering Wayfinder | 7-ticket reverse-engineering specification (`MAP.md`, `T1..T7`) & `.trae` desktop feature breakdown. | [`docs/research/samlotto/wayfinder/MAP.md`](../../research/samlotto/wayfinder/MAP.md) | [`docs/research/samlotto/reverse-engineer-desktop-app-features.md`](../../research/samlotto/reverse-engineer-desktop-app-features.md) |
| `extracted_manual/*.htm` (61 files) | Reference Manual | All 61 HTML topics + 225 diagrams from `Manual.chm`. | [`docs/reference/manual/`](../manual/index.md) | [`docs/reference/dynamic-portal.html`](../dynamic-portal.html) |

---

## 2. Mathematical, Physical & Esoteric Formulations (`old/Modules/*.py`)

### 2.1 Synodic Lunar Phase & Harmonic Resonance (`astronomy_engine.py`)

In `reference.local/old/Modules/astronomy_engine.py`, the astronomical state for draw date $t$ is anchored to the astronomical **J2000 first New Moon epoch**:
$$t_0 = \text{2000-01-06 18:14:00 UTC}, \qquad L_{\text{syn}} = 29.530588853\text{ days}$$

The continuous synodic phase $\phi(t) \in [0, 1)$ and 8-octant lunar index $k \in \{0,\dots,7\}$ are:
$$\phi(t) = \frac{(t - t_0)_{\text{days}} \bmod L_{\text{syn}}}{L_{\text{syn}}}, \qquad k = \lfloor \phi(t) \times 8 \rfloor \bmod 8$$

#### Step vs. Continuous Harmonic Weighting
1. **Discrete Step Modifiers (Original `astronomy_engine.py`)**:
   - **New Moon ($k = 0$)**: Boosts odd numbers ($+20\%$) and lower half $i \le \lfloor N/2 \rfloor$ ($+15\%$).
   - **Full Moon ($k = 4$)**: Boosts even numbers ($+25\%$) and upper half $i > \lfloor N/2 \rfloor$ ($+20\%$).
   - **First / Third Quarter ($k \in \{2, 6\}$)**: Boosts prime numbers ($+30\%$).
   - **Crescent / Gibbous ($k \in \{1, 3, 5, 7\}$)**: Boosts the central band $[0.32N, 0.68N]$ ($+15\%$).
2. **Continuous Gaussian Harmonic Kernel (Elevated in `SynodicAstronomyModel`)**:
   Instead of discontinuous jumps at octant boundaries, each ball $i \in \{1,\dots,N\}$ is mapped to its normalized angular coordinate $\theta_i = \frac{i - 1}{N - 1} \in [0, 1]$ and weighted by a smooth circular resonance kernel centered at $\mu(\phi) = \frac{1 - \cos(2\pi \phi)}{2}$:
   $$W_{\text{harmonic}}(i, \phi) = 1 + 0.25 \exp\!\left(-\frac{((\theta_i - \mu(\phi) + 0.5) \bmod 1 - 0.5)^2}{2\sigma^2}\right)$$

---

### 2.2 Laplace-Smoothed Beta-Binomial Bayesian Updating (`bayesian_inference.py`)

In `reference.local/old/Modules/bayesian_inference.py`, each ball $i \in \{1,\dots,N\}$ is modeled as a Bernoulli trial across $T$ historical draws with uniform Beta$(1,1)$ prior ($\alpha = 1$):
$$P_{\text{Laplace}}(i \mid \mathcal{H}_T) = \frac{c_i + \alpha}{T + 2\alpha}, \qquad c_i = \sum_{t=1}^{T} \mathbb{I}(i \in D_t)$$

**Elevated Exponential Forgetting Factor (`LaplaceBayesianTracker`)**:
To capture non-stationary mechanical or RNG regime shifts, historical draws can be weighted with decay factor $\gamma \in (0, 1]$:
$$\tilde{c}_i = \sum_{t=1}^{T} \gamma^{T - t} \mathbb{I}(i \in D_t), \qquad \tilde{T} = \sum_{t=1}^{T} \gamma^{T - t}, \qquad P_{\gamma}(i \mid \mathcal{H}_T) = \frac{\tilde{c}_i + \alpha}{\tilde{T} + 2\alpha}$$

---

### 2.3 Bipartite Cross-Draw Markov Transition Tensor (`markov_predictor.py`)

In `reference.local/old/Modules/markov_predictor.py`, transitions are tracked between every pair of balls $(u, v) \in D_t \times D_{t+1}$:
$$C_{u \to v}^{(1)} = \sum_{t=1}^{T-1} \mathbb{I}(u \in D_t \land v \in D_{t+1}), \qquad P^{(1)}(v \mid u) = \frac{C_{u \to v}^{(1)}}{\sum_{w=1}^{N} C_{u \to w}^{(1)}}$$

Given the most recent draw $D_T$, the 1st-order score for candidate ball $v$ is the marginal sum over all balls $u \in D_T$:
$$S_1(v \mid D_T) = \sum_{u \in D_T} P^{(1)}(v \mid u)$$

**Elevated 2nd-Order Lag-2 Tensor (`BipartiteMarkovChain`)**:
Incorporates lag-2 transitions $C_{u \to v}^{(2)}$ from $D_{T-1} \to D_{T+1}$ via convex blending parameter $\lambda \in [0, 1]$:
$$S(v \mid D_T, D_{T-1}) = (1 - \lambda) S_1(v \mid D_T) + \lambda S_2(v \mid D_{T-1})$$

---

### 2.4 Master-Number Digital Root & Modulo-9 Congruence (`numerology_analyzer.py`)

In `reference.local/old/Modules/numerology_analyzer.py`, a target date `YYYY-MM-DD` is reduced by iterative digit summation while halting if the intermediate sum hits a Master Number $M \in \{11, 22, 33\}$:
$$\operatorname{DR}_{\text{master}}(n) = \begin{cases} n & \text{if } n < 10 \text{ or } n \in \{11, 22, 33\} \\ \operatorname{DR}_{\text{master}}\!\left(\sum_{d \in \text{digits}(n)} d\right) & \text{otherwise} \end{cases}$$

Each candidate ball $i \in \{1,\dots,N\}$ receives two resonance boosts relative to $L = \operatorname{DR}_{\text{master}}(\text{YYYYMMDD})$:
1. **Modulo-9 Harmonic Congruence**: $+0.25$ if $i \equiv L \pmod 9$.
2. **Glyph Substring Inclusion**: $+0.15$ if $\text{str}(L)$ is a substring of $\text{str}(i)$ or $\operatorname{DR}_{\text{master}}(i) = L$.

---

### 2.5 Meteorological Micro-Climate & Pearson Correlation (`weather_engine.py`, `correlation_analyzer.py`)

1. **Deterministic Seeded Micro-Climate**:
   Using $s = \operatorname{int}(\operatorname{MD5}(\text{YYYY-MM-DD})_{0..7}, 16)$, temperature $T \in [15, 35]^\circ\text{C}$, humidity $H \in [30, 90]\%$, and pressure $P \in [1000, 1025]\text{ hPa}$ are deterministically synthesized.
2. **Thermal/Barometric Ball Modifiers**:
   - High temperature ($T > 28^\circ\text{C}$) boosts the upper third of the pool ($i > \lfloor 2N/3 \rfloor$) by $+20\%$.
   - High humidity ($H > 70\%$) boosts Modulo-3 multiples ($i \equiv 0 \pmod 3$) by $+15\%$.
   - Low pressure ($P < 1010\text{ hPa}$) boosts the lower third ($i \le \lfloor N/3 \rfloor$) by $+15\%$.
3. **Historical Pearson Correlation (`correlation_analyzer.py`)**:
   Computes the exact sample Pearson correlation coefficient $r_{X,Y}$ between `[temperature, humidity, pressure]` and draw metrics `[sum, mean, even_count]`.

---

### 2.6 Board Geometry (Frame/Center) & Boundary-Swap Sum Equilibrium (`statistics_analyzer.py`, `main_engine.py`)

For a 25-ball $5 \times 5$ board (and generalized to arbitrary $R \times C$ matrices in `BoardGeometryAndBoundaryBalancer`):
- **Frame / Border (`MOLDURA`, 16 cells)**: $\{1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25\}$
- **Center / Core (`MIOLO`, 9 cells)**: $\{7,8,9,12,13,14,17,18,19\}$
- **Primes (`PRIMOS`, 9 cells)**: $\{2,3,5,7,11,13,17,19,23\}$
- **Fibonacci (`FIBONACCI`, 7 cells)**: $\{1,2,3,5,8,13,21\}$

#### Boundary-Swap Sum Equilibrium Operator (`main_engine.py` lines 334–357)
When weighted sampling produces a $k$-ball ticket $T$ whose sum $\Sigma(T) = \sum_{x \in T} x$ falls outside the target equilibrium band $[\Sigma_{\min}, \Sigma_{\max}]$ (e.g., $[180, 210]$ for $15/25$, or generalized to $\mu_{\Sigma} \pm 0.65\sigma_{\Sigma}$ for any $k/N$ game):
- **Undershoot ($\Sigma(T) < \Sigma_{\min}$)**: Remove $x_{\min} = \min(T)$ and insert the highest-weighted available ball $y \in \{1,\dots,N\} \setminus T$ that brings $\Sigma(T')$ into $[\Sigma_{\min}, \Sigma_{\max}]$ (fallback: $\max(\{1,\dots,N\} \setminus T)$).
- **Overshoot ($\Sigma(T) > \Sigma_{\max}$)**: Remove $x_{\max} = \max(T)$ and insert the highest-weighted available ball $y \in \{1,\dots,N\} \setminus T$ that brings $\Sigma(T')$ into $[\Sigma_{\min}, \Sigma_{\max}]$ (fallback: $\min(\{1,\dots,N\} \setminus T)$).

---

### 2.7 Tri-Modal Weighted Ensemble (`weighted_ensemble.py`)

Normalizes each sub-model vector to unit sum $\widetilde{W}_m(i) = \frac{W_m(i)}{\sum_{j=1}^{N} W_m(j)}$ and fuses them via:
$$W_{\text{ensemble}}(i) = 0.40 \cdot \widetilde{W}_{\text{Markov}}(i) + 0.40 \cdot \widetilde{W}_{\text{Bayes}}(i) + 0.20 \cdot \widetilde{W}_{\text{Env}}(i)$$
where $\widetilde{W}_{\text{Env}}(i)$ combines the Synodic Astronomy, Master Numerology, and Micro-Climate resonance vectors.

---

## 3. CatBoost Gradient Boosting Learning Curve (`catboost_info/catboost_training.json`)

The file `reference.local/catboost_info/catboost_training.json` records a 100-iteration gradient boosting training run (`iteration_count: 100`) optimizing `RMSE`:
- **Iteration 0**: $\text{RMSE}_0 = 0.4648447607$
- **Iteration 25**: $\text{RMSE}_{25} = 0.3693221567$
- **Iteration 50**: $\text{RMSE}_{50} = 0.3055359985$
- **Iteration 75**: $\text{RMSE}_{75} = 0.2649844743$
- **Iteration 99**: $\text{RMSE}_{99} = 0.2364516368$ (a **$49.13\%$ error reduction** over 100 trees).

This exact 100-tree architecture is implemented in [`engine/strategies/ml_boost.py`](../../../../engine/strategies/ml_boost.py) and documented in [`03-ml-and-deep-learning-models.md`](../../wiki/02-theoretical-foundations/03-ml-and-deep-learning-models.md).

---

## 4. Exhaustive 2,360 Abbreviated Wheel Catalog (`Formula/*.Wheels`)

Every single `.Wheels` binary file in `reference.local/SamLotto Free Edition/Formula/` (2,360 files) follows the canonical naming and binary layout:
- **Filename Pattern**: `W{k}{v:02d}{t}{m}_{lines}.Wheels`
  - $k \in \{3, 4, 5, 6, 7\}$: Ticket pick size (`pick_k`)
  - $v \in [4, 55]$: Pool size (`pool_v`)
  - $t \in [2, 7]$: Minimum prize guarantee (`guarantee_t`)
  - $m \in [2, 7]$: Match condition in drawn balls (`condition_m`)
  - `lines`: Total tickets $b$ in the covering design (`tickets_count`)
- **Binary Layout**: Each line occupies exactly **8 bytes** on disk (`binary_bytes = 8 * tickets_count`), expanded in memory by `sub_4937e0` (`disassembly_wheel_io.txt`) into **24-byte (`0x18`)** 6-int32 stride records.
- **Complete Catalog**: Saved to [`docs/reference/architecture/wheels-catalog.csv`](wheels-catalog.csv) (all 2,360 rows with exact `reduction_ratio`) and queryable/synthesizable at runtime via [`CoveringWheelCatalogAndSynthesizer`](../../../../engine/modules/hybrid_synthesis.py).

---

## 5. Binary Disassembly Constants & Engine Internals (`disassembly_*.txt`)

All 27 disassembly dumps in `reference.local/SamLotto Free Edition/disassembly_*.txt` have been mapped to clean-room Python equivalents:

1. **91-Entry Filter & Scoring Dispatch Table (`disassembly_sub_585f7c.txt`)**:
   - `sub_585f7c` iterates over a ticket pool using a **24-byte stride** (`esi += 0x18`, holding up to $6 \times \text{int32}$ balls per ticket) and dispatches on `jump_table_58613d[0x5b]` (91 cases, `0x00..0x5a`), accumulating ball indicators into a 90-ball (`0x5a`) byte buffer `memset(&var_78, 0, 0x5a)`.
2. **Hard Ticket Generation Ceiling (`disassembly_generator.txt`)**:
   - `sub_4cce34` enforces a hard cap of `0xf4240` ($1,000,000$) generated tickets per pass (`if (ebx > 0xf4240) ebx = 0xf4240`).
3. **Serialized Filter Expression Grammar (`disassembly_filters_2.txt`)**:
   - `sub_581188` parses wide-character filter group expressions delimited by `u"||$[[][][]]"` (`|` = boolean OR, `$` = parameter separator, `[[...]]` = nested filter groups).
4. **Intrusive Red-Black / Binary Search Tree for $O(\log N)$ Pattern Frequency Counting (`disassembly_filters_2.txt`)**:
   - `sub_589934` and `sub_589a44` maintain an intrusive 24-byte BST node:
     - `+0x04`: `parent` pointer
     - `+0x08`: `left` child pointer
     - `+0x0c`: `right` child pointer
     - `+0x10`: `key` (32-bit pattern/tuple signature)
     - `+0x14`: `hit_count` (`*(eax_24 + 0x14) += 1`)
5. **INI & Auxiliary Binary State Files (`Current_Set.ini`, `Lottery_Set.ini`, `search_list.sl`, `Num_Dis_Next.nxt`)**:
   - `Current_Set.ini` & `Lottery_Set.ini`: Track active `[Current Lottery]` (`Name`, `File_Name`) and `[Custom]` pool dimensions (`Bonus_Enable`, `Bonus_Same`, `Total`, `Selected`).
   - `search_list.sl`: UTF-16LE (`ff fe`) serialized search filter state.
   - `Num_Dis_Next.nxt`: Fixed-width ASCII matrix storing empirical follower frequencies (`Follower Distribution Next-Draw Table`).
