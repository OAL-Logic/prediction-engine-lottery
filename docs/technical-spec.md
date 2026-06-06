# Absurdity Engine: Technical Specification 🧠

## 1. The Chaos Temperature Governor
Sampling "Temperature" ($T$) is no longer static. It is calculated as:
$$T_{active} = T_{base} + \delta_{seismic} + \delta_{solar} + \delta_{lunar} + \delta_{arcano} + \delta_{noosphere}$$

- **Seismic Jitter ($\delta_{seismic}$):** $\min(0.5, MaxMag \times 0.1)$ within 1000km.
- **Solar Storm ($\delta_{solar}$):** $+0.3$ if Planetary K-index ($Kp$) $\ge 5.0$.
- **Tidal Drag ($\delta_{lunar}$):** $+0.2$ if Tidal Intensity $> 0.8$ (Syzygy + Perigee).
- **Windfall ($\delta_{arcano}$):** $+0.5$ if Arcano 78 is active in the user's cycle.
- **Noosphere Entropy ($\delta_{noosphere}$):** $+0.2$ if Global Jitter (high-frequency hash drift) is Volatile ($>0.7$).

## 2. Atmospheric Physics Layer
Calculates real-world variables acting on the pneumatic lottery balls:

### Air Density ($\rho$)
$$\rho = \frac{P}{R_{specific} \times T}$$
*Where $P$ is surface pressure (Pa), $T$ is temperature (K), and $R_{specific}$ is 287.058 J/(kg·K).*

### Refractive Index ($N$)
$$N = 77.6 \times \frac{P}{T}$$
*Used as a proxy for static charge potential. High $N$ (dense/moist air) correlates with lower static electricity buildup.*

## 3. The Non-Euclidean Geometry (Dodecahedron)
Numbers $N \in [1, 60]$ are mapped to a 20-vertex Dodecahedron graph $G(V, E)$:
- **Mapping:** $v = (N-1) \mod 20$.
- **Adjacency:** If number $A$ has a high score, its 3 immediate vertices and their modular aliases (e.g., $v+20$, $v+40$) receive a $15\%$ cross-pollination boost.
- **Theory:** This recognizes "Higher-Dimensional Adjacency" where numbers are physically neighboring in esoteric geometric space.

## 4. Survival & Ensemble Pruning
The `survival` meta-strategy implements **Recursive Alpha Pruning**:
1. **Precision Check:** Evaluates the last 10 draws for every registered strategy.
2. **Pruning:** Discards the bottom $25\%$ of strategies.
3. **Weighting:**
   - Rank 1: $2 \times Precision$
   - Rank $n$: $Precision / n$
4. **Convergence:** Runs 500 parallel Monte Carlo samplings on the weighted ensemble to identify **Convergence Zones** (numbers that emerge in $>15\%$ of simulated futures).

## 5. Quantum Annealing Simulation (v9.0)
To escape classical probability traps, `quantum_anneal` employs simulated quantum tunneling:
$$P_{tunnel} = \frac{1}{2} e^{-C_{score} / \beta}$$
*Where $C_{score}$ is the classical frequency score and $\beta$ is the cooling schedule parameter ($0.8$). If pseudo-random collapse value $V_c < P_{tunnel}$, the number "tunnels" through the energy barrier, inverting its score to become highly probable.*

## 6. I Ching Resonance (v9.0)
Maps the number pool to the 64 Hexagrams of the *Book of Changes*.
- **Casting:** Deterministic Yarrow Stalk simulation using the `intent_seed`.
  - Probabilities: Old Yin (1/16), Young Yang (5/16), Young Yin (7/16), Old Yang (3/16).
- **Transformation:** Identifies Primary Hexagram and Transformed Hexagram (based on changing lines: 6 and 9). The active hexagram numbers are normalized to the lottery pool and receive a significant probability boost.

## 7. Intentional Synchronicity (Hashing)
To ensure the observer affects the observed, the sampling `seed` is generated via:
$$Seed = \text{SHA256}(\text{Name} + \text{BirthDate} + \text{Topic} + \text{Arcano}) \pmod{2^{32}}$$
This seed governs the `numpy.random.default_rng`, making the prediction a deterministic mathematical fingerprint of the user's input.

## 8. Gematria & Sephoric Logic
- **Mapping:** Chaldean (1-8).
- **Reduction:** Recursive digit summing until $\le 9$. Master numbers (11, 22) are preserved in Core Profiles but reduced in Triangle paths.
- **Negative Sequences:** Detected when $\ge 3$ identical digits appear adjacent in the primary name sequence, indicating vibrational stagnation.
- **Sephoric Tree (v8.0):** Numbers are mapped to the 10 Sephiroth, 22 Paths, and external harmonics. The Active Sephirah is identified via $(Day + Month - 1) \pmod{10} + 1$, directing the energetic probability distribution.

## 9. Adaptive History Sweep (v8.0)
To avoid recency-bias stagnation, `BaseStrategy` implements a localized grid-sweep during suggestions when `--adaptive-window` is flagged. It evaluates precision over multiple temporal windows (e.g., 20, 50, all) to dynamically adjust the sample size of the input DataFrame to the optimal signal-to-noise ratio.

## 10. Atmospheric Muon Flux Simulation (v9.0)
To inject true non-deterministic physical chaos into the final ticket generation, the `BaseStrategy` simulates a high-energy particle strike (Single-Event Upset).
- **Probability:** Simulated 0.5% per-ticket strike chance.
- **Mutation:** If a muon strikes, an active number is randomly targeted and mutated via a bitwise XOR flip `mutated = number ^ (1 << rand(0,5))`. The number is then modularly mapped back into the valid lottery pool.

## 11. Fibonacci Market Retracement (v10.0)
Historical frequencies are analyzed using technical analysis (TA) principles. The engine calculates the All-Time High ($H$) and Low ($L$) frequencies.
$$Range = H - L$$
Support levels are established at:
- $L_{23.6} = H - (Range \times 0.236)$
- $L_{38.2} = H - (Range \times 0.382)$
- $L_{61.8} = H - (Range \times 0.618)$
Numbers with current frequencies $\approx L_i$ receive a probability boost, assuming a "bounce" back into the draw pool.

## 12. Astro-Cartography & Ley Lines (v10.0)
The physical draw location ($Lat_1, Lon_1$) is mapped against a subset of the Becker-Hagens planetary grid nodes ($Lat_2, Lon_2$).
- **Haversine Distance ($d$):** Calculates the great-circle distance between the draw and the nearest node.
- **Geomantic Resonance:** If $d < 500\text{km}$, the draw is considered "Active".
- **Sacred Geometry Boost:** During active resonance, numbers whose digit roots equal 3, 6, or 9 (Tesla's sacred sequence) receive an extreme $+0.3$ probability boost, reflecting the amplified environmental energy.

## 13. Advanced Ensembles & Meta-Learning
- **Stacking Ensemble:** A meta-learner that trains a secondary model to weight member strategy predictions based on their historical performance and precision.
- **Mutual Information ($I(X;Y)$):** Uses Shannon Entropy to identify numbers with the highest probabilistic dependency on the most recent winning draws, highlighting non-linear correlations.
- **Voting Ensemble (`voting`):** A simplified ensemble that calculates the weighted average of multiple member strategies.
- **Regime Switching (`regime`):** Dynamically selects between models based on a Chi-squared ($ \chi^2 $) test for statistical stability in recent draws.
- **Universal Synapse (`synapse`):** The engine's peak convergent strategy. It runs three independent "cylinders" (Statistical, Deep, Chaos) and calculates their **Universal Conjunction** — numbers that appear in the top-10 of all three cylinders receive a $1.5 \times$ Conjunction Boost.

## 14. ML Classifiers (Scikit-Learn)
- **Logistic Regression (`logistic`):** Treats each number as a binary classification target (hit/no-hit) and uses logistic regression to estimate probabilities based on lag features.
- **K-Nearest Neighbors (`knn`):** Uses sequence vectorization to find the $K$ historical draws most similar to the current state and aggregates their successor frequencies.

## 14. Void & Cycle Analysis
- **Void Analysis:** Creates spatial heatmaps to identify "Cold Sectors" (quadrants or rows on the betslip) that have been empty for $\ge 5$ draws, applying Mean-Reversion probability boosts to assume a sector "pop".
- **Cycle Analysis:** Identifies the mean hit interval for each number via spectral/frequency properties and scores them based on their proximity to their individual cycle completion.


## 15. Reincarnation & Global Entropy
- **Reincarnation:** Hashes the current date's vibrational signature and searches the historical database for the "Past Life" draw with the closest match. Numbers from that past draw receive a harmonic resonance boost.
- **Global Entropy:** Correlates the draw timeline with simulated or external global chaos peaks (based on collective unconscious theories) to modulate the sampling temperature accordingly.


## 18. Advanced Structural Metrics (Power Pack)
The `advanced` strategy scores numbers based on their contribution to historical "Structural Harmony" zones. It identifies the 10th-90th percentile "Sweet Spot" for the following metrics:
- **Arithmetic Complexity (AC):** Measures the diversity of differences between numbers in a ticket.
- **Digital Root Sum:** Recursive sum of digits until a single digit remains.
- **Unit Sum:** Sum of the last digits (remainders modulo 10).
- **Successive Groups:** Count of adjacent pairs or triplets.
- **Spread:** Absolute distance between the lowest and highest number.

Tickets falling within the "Sweet Spot" for all metrics receive a high harmony score, which is then used to weight individual number candidates via participation frequency.

## 19. CLI Lazy-Loading Standards
To maintain sub-second CLI startup times despite supporting 85+ commands and 50+ strategy modules, `engine/cli/main.py` adheres to a strict **Lazy Loading** pattern:
- **Eager Imports Forbidden**: No top-level imports of heavy numerical libraries (`pandas`, `numpy`, `scipy`) or command implementation modules.
- **Wrapper Pattern**: Every command is registered via a lightweight wrapper function.
- **Internal Import**: The actual implementation and its dependencies are imported *inside* the wrapper function scope, ensuring they are only loaded into memory when that specific command is called.

## 20. The Tuning Algorithm (`lottery tune`)
The `tune` command implements an automated **Out-of-Sample Hyperparameter Optimizer**:
1. **Target Selection**: Selects the last $N$ draws as evaluation targets.
2. **Temporal Isolation**: For each target draw $d$, the training window is strictly limited to draws $d_{i} < d$ to prevent look-ahead bias.
3. **Grid Sweep**: Iterates through a Cartesian product of:
   - **Strategies**: (e.g., `bayesian`, `weighted`, `spectral`)
   - **Parameters**: (e.g., `alpha0`, `decay`, `minimum_magnitude`)
   - **Structural Filters**: (e.g., `[]`, `['sum_range']`, `['sum_range', 'parity']`)
4. **Scoring**: Computes real-world hit rates, lift (vs. random baseline), and top-N capture rates.
5. **Serialization**: Exports the winning $K$ configurations to a YAML schema compatible with `backtest --config` and `forecast --config`.

## 21. Private Context Injection
The engine supports a "Bring Your Own Data" (BYOD) security model for personalized strategies:
- **Detection**: On execution, the CLI searches for `*.local.yaml` files in the root directory (standard: `personal.local.yaml`).
- **Merging**: Values from these files (e.g., `full_name`, `birth_date`) are merged into a `personal_data` dictionary.
- **Kwarg Propagation**: This dictionary is passed as `**kwargs` to every strategy instantiation. Strategies that do not define these parameters in their `__init__` safely ignore them via surgical argument filtering in `BaseStrategy`.

---

## 📚 Appendix: Strategy Registry & Concept Mapping

| Strategy Name         | Core Technical Concept            | Reference Section   |
| :-------------------- | :-------------------------------- | :------------------ |
| **`markov`**          | First-order transition matrix     | Section 14          |
| **`bayesian`**        | Dirichlet-Multinomial posterior   | Section 13          |
| **`weighted`**        | Multi-signal harmonic blend       | Section 17 (Legacy) |
| **`hedge`**           | Lower-tier prize optimization     | Section 18 (Stability) |
| **`vix_jitter`**      | Market volatility correlation     | Section 19 (Economics) |
| **`monte_carlo`**     | Resampling & structural filtering | Section 4           |
| **`pattern`**         | Empirical pattern vectorization   | Section 14          |
| **`momentum`**        | RSI/Relative Strength Index       | Section 11          |
| **`spectral`**        | Fast Fourier Transform (FFT)      | Section 14          |
| **`streak`**          | Poisson-window appearance count   | Section 14          |
| **`crowd_avoidance`** | Psychological anti-clustering     | Section 13          |
| **`steiner_wheel`**   | Combinatorial Covering Design     | Section 15          |
| **`void`**            | Spatial quadrant entropy          | Section 14          |
| **`copairs`**         | Lift-based co-occurrence          | Section 14          |
| **`cycle`**           | Mean hit interval oscillation     | Section 14          |
| **`mutual_info`**     | Shannon Mutual Information        | Section 13          |
| **`stability`**       | Variance of hit-rate blocks       | Section 14          |
| **`harmonic`**        | Adjacency × Co-occurrence         | Section 17          |
| **`fisher`**          | Fisher information matrix sensitivity | Section 13          |
| **`primes`**          | Prime density × Lunar harmonics   | Section 1           |
| **`positional`**      | Slot frequency PDF                | Section 14          |
| **`contagion`**       | Grid neighbor resonance           | Section 14          |
| **`numerology`**      | Pythagorean date-based reduction  | Section 8           |



| **`iching`**          | Yarrow stalk hexagram casting     | Section 6           |
| **`kabbalistic`**     | Gematria × Arcanos                | Section 8           |
| **`ley_lines`**       | Haversine distance × Earth Grid   | Section 12          |
| **`noosphere`**       | Global entropy jitter             | Section 1, 15       |
| **`sefirot`**         | Sephoric path mapping             | Section 8           |
| **`solar`**           | NOAA K-index correlation          | Section 1           |
| **`moon_phase`**      | Synodic cycle frequency           | Section 1           |
| **`weather`**         | Air density & Refractive index    | Section 2           |
| **`fibonacci`**       | Market support level retracement  | Section 11          |
| **`zodiac`**          | Astrological elemental mapping    | Section 1           |
| **`biorhythm`**       | Sinusoidal biological cycles      | Section 1           |
| **`lorentz`**         | Strange attractor simulation      | Section 1           |
| **`sentiment`**       | Viral pulse simulation            | Section 15          |
| **`reincarnation`**   | Hashed signature matching         | Section 15          |
| **`entropy_global`**  | Collective high-noise correlation | Section 15          |
| **`gematria`**        | Linguistic root vibration         | Section 8           |
| **`refraction`**      | Static potential mapping          | Section 2           |
| **`advanced`**        | Structural Health (AC, Root/Unit Sum) | Section 18 |
| **`quantum_anneal`**  | Simulated quantum tunneling | Section 5 |
| **`synapse`**         | Universal Conjunction             | Section 13          |
| **`regime`**          | Statistical Regime Switching      | Section 13          |
| **`voting`**          | Weighted average ensemble         | Section 13          |
| **`logistic`**        | Logistic Regression (Lag bits)    | Section 14          |
| **`knn`**             | K-Nearest Neighbors similarity    | Section 14          |



| **`survival`**        | Recursive Alpha Pruning           | Section 4           |
| **`transformer`**     | Attention-based deep sequence     | Section 13          |
| **`lstm_gru`**        | Recurrent memory state            | Section 13          |
| **`cnn_1d`**          | 1D Dilated convolutions           | Section 13          |
| **`prob_weighted`**   | Precision-weighted ensemble       | Section 13          |
| **`hybrid`**          | Two-stage filtered sampling       | Section 13          |
| **`stacking`**        | Meta-learner stacking             | Section 13          |
| **`pattern`**         | Structural distribution analysis  | Section 14          |
| **`momentum`**        | Regime-based trend tracking       | Section 11          |
| **`refraction`**      | Atmospheric physics               | Section 2           |

