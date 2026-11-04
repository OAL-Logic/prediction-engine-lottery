# ADR-005: Fringe Speculative Theories, Dual-Layer Pipeline & Popperian Falsification Protocol

## Status
**ACCEPTED** (2026-11-04)

---

## Context & Problem Statement

The Lottery Prediction Engine contains a suite of non-traditional, speculative modules inspired by theoretical physics, non-linear dynamics, and fringe science (e.g., Benford's Law, Quantum Retrocausality, Quantum Zeno Effect, Ising Spin Models, Topological Data Analysis, Lorenz Strange Attractors, Sacred Geometry, and Global Consciousness entropy). Historically, these concepts were documented informally in `docs/CRAZY_LOTTERY_THEORIES.md` as esoteric curiosities with disconnected numbering, missing strategies (such as Everett Many-Worlds), and without an empirical falsification methodology.

Furthermore, a critical epistemological tension exists between:
1. **Orthodox Combinatorial Filters**: Documented in canonical guides ([Mega-Sena Guide](../reference/guides/win-brazil-mega-sena-lottery-ultimate-guide.md) and [Quina Guide](../reference/guides/how-to-win-brazil-quina.md)), enforcing strict historical density boundaries (Sum range, Odd/Even parity, AC complexity, decile distribution); and
2. **Marginal Speculative Theories**: Algorithms that attempt to model hypothetical non-linear or physical correlations in the draw mechanism.

Without a formal architectural boundary and scientific falsification protocol, these speculative modules risked either contaminating production ensemble pipelines or remaining untested and unverifiable.

---

## Decision Drivers

1. **Popperian Falsifiability**: Every non-standard predictive theory must formulate an explicit Null Hypothesis ($H_0$) and a quantitative falsification metric testable against real historical draws.
2. **Strict Tier Isolation (Governance Gatekeeper)**: Non-mainstream strategies must reside in tier `"fun"`, isolated from production ensembles (`--strategy auto`) unless empirical significance ($p < 0.01$ with Bonferroni correction) is formally demonstrated.
3. **Dual-Layer Pipeline (Scoring vs. Pruning)**: Speculative models must operate solely as *Scorers* (generating candidate weight distributions), while generated tickets must pass through canonical *Orthodox Combinatorial Filters* to prevent pathological bets.
4. **Universal Game Agnosticism**: All theoretical formulations and modules must operate dynamically through abstract contracts (`DrawRules`), supporting Mega-Sena (6/60), Quina (5/80), Lotofácil (15/25), and any global lottery without hardcoded numbers.
5. **No External Network Dependencies**: Quantum and chaotic simulations must execute 100% locally and offline, leveraging native OS hardware entropy (`/dev/urandom` via `secrets`) rather than unstable external APIs.

---

## Architectural Decision

We formalized the complete design tree through an adversarial interviewing protocol (**Grilling**), establishing four core architectural pillars:

```mermaid
flowchart TD
    subgraph Layer1["Camada 1: Heurística / Scorer Marginal (Tier 'fun')"]
        direction TB
        Q1["Quantum Multiverse (Everett /dev/urandom)"]
        Q2["Ising Model (Spin Lattice Energy)"]
        Q3["Quantum Zeno (Observation Freeze)"]
        Q4["TDA (Persistent Homology / Betti-1)"]
        Q5["Lorenz & Lyapunov (Strange Attractors)"]
        Q6["Retrocausality & Reverse Markov"]
    end

    subgraph Layer2["Camada 2: Poda Combinatória Ortodoxa (Guias Canônicos)"]
        direction TB
        F1["Filtro de Soma Ideal (Mega 121-296 | Quina 122-330)"]
        F2["Equilíbrio Par/Ímpar (3:3, 2:4 | 3:2, 2:3)"]
        F3["Complexidade Aritmética AC ≥ 6"]
        F4["Dispersão por Faixas / Quadrantes"]
        F5["Exclusão de Sequências Triviais e Repetições"]
    end

    subgraph Output["Emissão & Backtest"]
        Tickets["Bilhetes Válidos de Alta Cobertura"]
        Audit["Estudo Empírico & Testes de Hipótese (reports/br/studies/)"]
    end

    Layer1 -->|Vetor de Pesos P(n)| Layer2
    Layer2 --> Output
```

### 1. Specification of the 9 Synchronized Fringe Theories

Each theory in `docs/CRAZY_LOTTERY_THEORIES.md` conforms to a standardized 4-part technical specification:
1. **Benford's Paradox (`benford_illusion`)**: Scale-invariant logarithmic gaps $P(d) = \log_{10}(1 + 1/d)$ vs. uniform $H_0: P(d)=1/9$.
2. **Quantum Retrocausality (`retrocausality`)**: Time-reversed stochastic transition matrices conditioned on future harmonic attractors vs. $H_0: I(X_{t+1}; X_t) = 0$.
3. **Quantum Multiverse & Immortality (`quantum_multiverse`)**: Vectorized simulation of $M=1,000$ Everett branches using OS entropy (`/dev/urandom`) and anthropic constructive interference vs. $H_0: \mathbb{E}[P(n)] = 1/N$.
4. **Ising Spin Model (`ising_model`)**: 2D lattice thermodynamic phase transition and Hamiltonian minimization vs. $H_0: \text{Moran's } I = 0$.
5. **Quantum Zeno Effect (`zeno_quantum`)**: Wavefunction freeze under hyper-frequent observation vs. $H_0: \text{Poisson independence}$.
6. **Topological Data Analysis (`tda_topology`)**: Persistent homology and 1-dimensional Betti cycles ($\beta_1$) in co-occurrence simplicial complexes vs. $H_0: \text{Erdős-Rényi } G(n, p)$.
7. **Sacred Geometry & Phi Spiral (`sacred_grid` / `sacred_manifold`)**: Euclidean ticket projection to Golden Ratio ($\phi$) vortex nodes vs. $H_0: \text{Uniform spatial Euclidean distance}$.
8. **Deterministic Chaos (`lorentz` / `lyapunov_chaos`)**: Runge-Kutta 4 integration of Rayleigh-Bénard convection equations mapped to toroidal phase space vs. $H_0: \lambda \le 0$.
9. **Noosphere & Global Consciousness (`noosphere` / `entropy_global`)**: Collective unconscious variance modulation vs. $H_0: \text{Levene variance homogeneity } Var_1 = Var_0$.

### 2. Triple Baseline Benchmark Standard

All empirical audits must compare strategy candidates against three distinct references:
* **Reference A (Theoretical Expected Value)**: Exact closed-form hypergeometric mean $\mathbb{E}[X] = \frac{n K}{N}$.
* **Reference B (Uniform Random Monte Carlo)**: Pure unconstrained independent sampling.
* **Reference C (Orthodox Filtered Baseline)**: Combinations satisfying all canonical guide filters simultaneously.

---

## Empirical Benchmark Results (Mega-Sena & Quina)

Conducted across 100 historical blind out-of-sample draws for both Mega-Sena (draws 2981–3080) and Quina (draws 7059–7158):

### Summary Table

| Game ($N, k$) | Metric / Baseline | Theoretical $\mathbb{E}[X]$ | Fringe Performance Range | Best Fringe Strategy ($p$-val) | Orthodox Baseline ($p$-val) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Mega-Sena** (6/60) | Mean Hits ($\mu$) | **0.6000** | $0.5700$ – $0.6400$ | `zeno_quantum`: 0.6400 ($p = 0.5787$) | 0.4100 ($p = 0.0029$) | **$H_0$ Retained** (No edge) |
| **Quina** (5/80) | Mean Hits ($\mu$) | **0.3125** | $0.2100$ – $0.3400$ | `ising_model`: 0.3400 ($p = 0.6320$) | 0.2400 ($p = 0.0944$) | **$H_0$ Retained** (No edge) |

### Key Epistemological Insights
1. **Falsification of Marginal Advantage**: With $p$-values between $0.40$ and $0.96$, no fringe strategy demonstrated statistically significant predictive edge over uniform chance. They represent exploratory heuristics, not lottery breakers.
2. **The "Orthodox Over-Constraint" Trap**: Enforcing all classical guide filters simultaneously on a single bet reduced mean hits below theoretical expectation in small samples ($0.4100$ vs. $0.6000$ in Mega-Sena, $p = 0.0029$), because single draws with atypical clusters are eliminated. Combinatorial filters are effective for large-scale wheel coverage pruning, but detrimental when over-applied to isolated single bets.

---

## Consequences

### Positive
* **Epistemological Integrity**: The repository clearly distinguishes between peer-reviewed statistical models (`tier="ml"` / `tier="statistical"`) and speculative/recreational models (`tier="fun"`).
* **Code & Spec Alignment**: All 9 fringe theories cataloged in documentation now correspond to concrete, tested Python classes.
* **Universal Game Compatibility**: All modules work transparently across 6/60, 5/80, 15/25, and future global lotteries.
* **Zero PII & Automated Guardrails**: Fully compliant with repository privacy guidelines and automated commit hooks.

### Negative / Trade-Offs
* Running multi-branch quantum simulations ($M=1,000$ branches) requires slightly more CPU cycles than simple frequency counters (mitigated via vectorized NumPy array broadcasting).
* Clear empirical evidence that fringe theories do not beat the house, dispelling speculative claims while maintaining full mathematical transparency.
