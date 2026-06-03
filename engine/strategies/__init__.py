"""
engine.strategies
=================
Prediction strategies — each turns historical draw data into per-number scores
and generates ticket suggestions.

Architecture
------------
Every strategy:
  1. Implements  score(df, rules) → dict[int, float]   (number → 0–1 score)
  2. Inherits    suggest(...)     from BaseStrategy     (sampling + temperature)

Temperature-based sampling (from the deep-learning literature) controls
how deterministic vs. exploratory the ticket generation is:
  temperature = 0   → deterministic: always pick the top-N numbers
  temperature = 1   → sample proportional to scores
  temperature > 1   → more exploratory / random
  temperature < 1   → sharper, more confident picks

Ensemble is trivial: pass multiple strategy names separated by commas to the
CLI and a DynamicEnsemble averages their score dicts automatically.

Strategy tiers
--------------
  statistical/   pure stats, no extra deps  (markov, bayesian, monte_carlo, weighted, pattern)
  ml/            scikit-learn required       (logistic, random_forest, ensemble)
  deep/          torch required              (transformer, lstm_gru)
  fun/           entertainment / absurdity   (numerology, moon_phase, weather)
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

from engine.adapters import DrawRules

# --- Master Strategy Registry (Single Source of Truth) ---
# This map handles Lazy Loading, Help Descriptions, and Tier classification.
STRATEGY_REGISTRY = {
    # Statistical
    "markov": {"module": "engine.strategies.statistical.markov", "tier": "statistical", "description": "First-order Markov chain"},
    "markov_regime": {"module": "engine.strategies.statistical.markov_regime", "tier": "statistical", "description": "🔗📉 Markov Transition Drift — detects shifts in number-to-number relationships"},
    "bayesian": {"module": "engine.strategies.statistical.bayesian", "tier": "statistical", "description": "Bayesian frequency estimation"},
    "monte_carlo": {"module": "engine.strategies.statistical.monte_carlo", "tier": "statistical", "description": "Monte Carlo simulation"},
    "weighted": {"module": "engine.strategies.statistical.weighted", "tier": "statistical", "description": "Weighted signal blend"},
    "pattern": {"module": "engine.strategies.statistical.pattern", "tier": "statistical", "description": "Pattern matching"},
    "momentum": {"module": "engine.strategies.statistical.momentum", "tier": "statistical", "description": "Frequency momentum (RSI-style)"},
    "spectral": {"module": "engine.strategies.statistical.spectral", "tier": "statistical", "description": "FFT periodicity detection"},
    "streak": {"module": "engine.strategies.statistical.streak", "tier": "statistical", "description": "Hot/cold streak tracking"},
    "crowd_avoidance": {"module": "engine.strategies.statistical.crowd_avoidance", "tier": "statistical", "description": "Psychological bias avoidance"},
    "steiner_wheel": {"module": "engine.strategies.statistical.steiner_wheel", "tier": "statistical", "description": "Combinatorial Covering Design"},
    "survival": {"module": "engine.strategies.statistical.survival", "tier": "statistical", "description": "🧬 Survival of the Fittest"},
    "primes": {"module": "engine.strategies.statistical.primes", "tier": "statistical", "description": "🔢 Prime Oscillator"},
    "quantum_anneal": {"module": "engine.strategies.statistical.quantum", "tier": "statistical", "description": "⚛️ Quantum Annealing"},
    "void": {"module": "engine.strategies.statistical.void", "tier": "statistical", "description": "🕳️ Void Analysis"},
    "copairs": {"module": "engine.strategies.statistical.copairs", "tier": "statistical", "description": "🤝 Co-occurrence Pairs"},
    "cycle": {"module": "engine.strategies.statistical.cycle", "tier": "statistical", "description": "🚲 Cycle Analysis"},
    "mutual_info": {"module": "engine.strategies.statistical.mutual_info", "tier": "statistical", "description": "🧠 Mutual Information — dependency tracking"},
    "stability": {"module": "engine.strategies.statistical.stability", "tier": "statistical", "description": "⚖️ Stability — historical variance analysis"},
    "harmonic": {"module": "engine.strategies.statistical.harmonic", "tier": "statistical", "description": "💎 Harmonic Resonance"},
    "fisher": {"module": "engine.strategies.statistical.fisher", "tier": "statistical", "description": "🎣 Fisher Information"},
    "graph_influence": {"module": "engine.strategies.statistical.graph_influence", "tier": "statistical", "description": "🕸️ Network Influence (PageRank Centrality)"},
    "advanced": {"module": "engine.strategies.statistical.advanced", "tier": "statistical", "description": "Advanced statistical blend"},
    "positional": {"module": "engine.strategies.statistical.positional", "tier": "statistical", "description": "Ordered Vector Distribution"},
    "contagion": {"module": "engine.strategies.statistical.contagion", "tier": "statistical", "description": "Winning digit contagion"},
    "game_theory": {"module": "engine.strategies.statistical.game_theory", "tier": "statistical", "description": "♟️ Game Theory (EV Maximization via Crowd Antagonism)"},
    "expected_value": {"module": "engine.strategies.statistical.expected_value", "tier": "statistical", "description": "♟️ Game-Theoretic Expected Value Model (Advantage Principle)"},
    "spatial": {"module": "engine.strategies.statistical.spatial", "tier": "statistical", "description": "📐 Grid-aware analysis — models physical adjacency and clusters on the ticket"},
    "hedge": {"module": "engine.strategies.statistical.hedge", "tier": "statistical", "description": "Portfolio hedging"},
    "wonder_grid": {"module": "engine.strategies.statistical.wonder_grid", "tier": "statistical", "description": "🔮 Ion Saliu's Wonder Grid"},
    "structural": {"module": "engine.strategies.statistical.structural", "tier": "statistical", "description": "🏗️ Structural Focus — target Primes, Fibonacci, and Frame/Center balance"},
    "hurst_memory": {"module": "engine.strategies.statistical.hurst_memory", "tier": "statistical", "description": "📈 Hurst Exponent (Inertia & Memory)"},
    "kolmogorov_order": {"module": "engine.strategies.statistical.kolmogorov_order", "tier": "statistical", "description": "🧩 Kolmogorov Complexity (Emergent Order)"},
    "evt_extremes": {"module": "engine.strategies.statistical.evt_extremes", "tier": "statistical", "description": "🌋 Extreme Value Theory (EVT)"},
    "wavelet_signal": {"module": "engine.strategies.statistical.wavelet_signal", "tier": "statistical", "description": "🌊 Wavelet Decomposition (Multi-Scale Analysis)"},
    "fourier_forecast": {"module": "engine.strategies.statistical.fourier_forecast", "tier": "statistical", "description": "🌊 Fourier Spectral Projection"},
    "nash_equilibrium": {"module": "engine.strategies.statistical.nash_equilibrium", "tier": "statistical", "description": "♟️ Nash Equilibrium (Game Theory)"},
    "stefan_mandel": {"module": "engine.strategies.statistical.stefan_mandel", "tier": "statistical", "description": "💼 Stefan Mandel Arbitrage — targets jackpots exceeding combinatorial cost with optimal coverage"},
    
    # ML
    "logistic": {"module": "engine.strategies.ml.logistic", "tier": "ml", "description": "Logistic Regression"},
    "random_forest": {"module": "engine.strategies.ml.random_forest", "tier": "ml", "description": "Random Forest Classifier"},
    "gradient_boost": {"module": "engine.strategies.ml.gradient_boost", "tier": "ml", "description": "LightGBM Gradient Boosting"},
    "knn": {"module": "engine.strategies.ml.knn", "tier": "ml", "description": "K-Nearest Neighbors"},
    "synapse": {"module": "engine.strategies.ml.ensemble", "tier": "ml", "description": "Neural consensus (Synapse)"},
    "regime": {"module": "engine.strategies.ml.regime", "tier": "ml", "description": "📉 Regime-Switching — dynamic model selection based on statistical stability"},
    "voting": {"module": "engine.strategies.ml.ensemble", "tier": "ml", "description": "Weighted voting average"},
    "prob_weighted": {"module": "engine.strategies.ml.ensemble", "tier": "ml", "description": "Precision-weighted ensemble"},
    "hybrid": {"module": "engine.strategies.ml.ensemble", "tier": "ml", "description": "Two-stage hybrid ensemble"},
    "stacking": {"module": "engine.strategies.ml.ensemble", "tier": "ml", "description": "Meta-learner stacking ensemble"},
    "ml_regressor": {"module": "engine.strategies.ml.regressor_hub", "tier": "ml", "description": "🤖 Multi-Regressor ML Hub (XGB/LGBM/CAT Ensemble)"},
    
    # Deep
    "transformer": {"module": "engine.strategies.deep.transformer", "tier": "deep", "description": "Attention-based Transformer"},
    "lstm": {"module": "engine.strategies.deep.lstm_gru", "tier": "deep", "description": "Long Short-Term Memory Network"},
    "gru": {"module": "engine.strategies.deep.lstm_gru", "tier": "deep", "description": "Gated Recurrent Unit Network"},
    "lstm_crf": {"module": "engine.strategies.deep.lstm_crf", "tier": "deep", "description": "🧠 Sequence Logic Brain (LSTM-CRF) — models inter-number dependencies"},
    "cnn_1d": {"module": "engine.strategies.deep.cnn_1d", "tier": "deep", "description": "1D Convolutional Neural Network"},
    "deep_lstm": {"module": "engine.strategies.ml.deep_lstm", "tier": "ml", "description": "🧠 Deep LSTM — manual NumPy RNN"},
    "gnn": {"module": "engine.strategies.deep.gnn", "tier": "deep", "description": "🕸️ Graph Neural Network (GCN) — spatial propagation on grid"},
    
    # Fun / Chaos
    "numerology": {"module": "engine.strategies.fun.numerology", "tier": "fun", "description": "Pythagorean Gematria"},
    "archetypes": {"module": "engine.strategies.fun.archetypes", "tier": "fun", "description": "🎭 Numerical Archetypes (Balanced Narrative)"},
    "moon_phase": {"module": "engine.strategies.fun.moon_phase", "tier": "fun", "description": "Lunar Resonance"},

    "weather": {"module": "engine.strategies.fun.weather", "tier": "fun", "description": "Local Weather Resonance"},
    "bio_feedback": {"module": "engine.strategies.fun.bio_feedback", "tier": "fun", "description": "💓 Bio-Feedback Pulse — rhythmic resonance"},
    "biorhythm": {"module": "engine.strategies.fun.biorhythm", "tier": "fun", "description": "Personal Biorhythm Alignment"},
    "fibonacci": {"module": "engine.strategies.fun.fibonacci", "tier": "fun", "description": "Golden Ratio (Phi) intervals"},
    "zodiac": {"module": "engine.strategies.fun.zodiac", "tier": "fun", "description": "Astrological transit alignment"},
    "kabbalistic": {"module": "engine.strategies.fun.kabbalistic", "tier": "fun", "description": "Gematria & Kabbalistic Arcanos"},
    "esoteric_statistical": {"module": "engine.strategies.fun.esoteric_statistical", "tier": "fun", "description": "🔮 Esoteric Hashing × Statistical Core (Parity, StdDev, Cluster Gates)"},
    "reincarnation": {"module": "engine.strategies.fun.reincarnation", "tier": "fun", "description": "Past-draw reincarnation"},
    "lorentz": {"module": "engine.strategies.fun.lorentz", "tier": "fun", "description": "Chaotic Attractor Jitter"},
    "sentiment": {"module": "engine.strategies.fun.sentiment", "tier": "fun", "description": "Global Sentiment Flux"},
    "refraction": {"module": "engine.strategies.fun.refraction", "tier": "fun", "description": "Numerical Refraction"},
    "seismic": {"module": "engine.strategies.fun.seismic", "tier": "fun", "description": "Tectonic Plate Resonance"},
    "solar": {"module": "engine.strategies.fun.solar", "tier": "fun", "description": "Geomagnetic K-Index Flux"},
    "geomagnetic": {"module": "engine.strategies.fun.geomagnetic", "tier": "fun", "description": "☀️ Space Weather (Solar K-Index Volatility Modulation)"},
    "noosphere": {"module": "engine.strategies.fun.noosphere", "tier": "fun", "description": "Global Consciousness Jitter"},
    "iching": {"module": "engine.strategies.fun.iching", "tier": "fun", "description": "I Ching Resonance"},
    "sefirot": {"module": "engine.strategies.fun.sefirot", "tier": "fun", "description": "Sephoric Tree of Life"},
    "ley_lines": {"module": "engine.strategies.fun.ley_lines", "tier": "fun", "description": "Astro-Cartography & Ley Lines"},
    "kinetic": {"module": "engine.strategies.fun.kinetic", "tier": "fun", "description": "🎱 Pseudo-Kinetic Simulation — models balls bouncing in a 2D drum"},
    "entropy_global": {"module": "engine.strategies.fun.entropy_global", "tier": "fun", "description": "🌪️ Global Entropy — correlate numbers with simulated collective-unconscious jitter"},
    "gematria": {"module": "engine.strategies.fun.gematria", "tier": "fun", "description": "🔤 Gematria Resonance — linguistic mapping of number names to personal vibrations"},
    "vix_jitter": {"module": "engine.strategies.fun.vix_jitter", "tier": "fun", "description": "📉 Financial Volatility Resonance — correlate hits with global anxiety (VIX)"},
    "benford_illusion": {"module": "engine.strategies.fun.benford_illusion", "tier": "fun", "description": "🔢 Paradoxo da Lei de Benford"},
    "retrocausality": {"module": "engine.strategies.fun.retrocausality", "tier": "fun", "description": "⏳ Retrocausalidade Quântica (Ecos do Futuro)"},
    "deep_dream": {"module": "engine.strategies.ml.deep_dream", "tier": "ml", "description": "🌌 Deep Dream — generative VAE sampling"},
    "ensemble_pro": {"module": "engine.strategies.ml.ensemble_pro", "tier": "ml", "description": "🤖 Super-Stacking ML Ensemble"},
    "stacking_ai": {"module": "engine.strategies.ml.stacking_ai", "tier": "ml", "description": "🧠 Stacking AI (Meta-Learner)"},
    "lyapunov_chaos": {"module": "engine.strategies.fun.lyapunov_chaos", "tier": "fun", "description": "🦋 Windows of Order in Chaos (Lyapunov Exponent)"},
    "crowd_antagonism": {"module": "engine.strategies.fun.crowd_antagonism", "tier": "fun", "description": "🚫 Anti-Mass Filter (Avoids popular numbers)"},
    "geo_sync": {"module": "engine.strategies.fun.geo_sync", "tier": "fun", "description": "🌍 Geographic Synchronizer (Piracicaba)"},
    "cpu_entropy": {"module": "engine.strategies.fun.cpu_entropy", "tier": "fun", "description": "💻 Hardware Entropy (CPU White Noise)"},
    "sacred_grid": {"module": "engine.strategies.fun.sacred_grid", "tier": "fun", "description": "🌀 Sacred Geometry (Phi Spiral)"},
    "sacred_manifold": {"module": "engine.strategies.fun.sacred_manifold", "tier": "fun", "description": "🌀 Sacred Manifold Grid — aligns spherical ticket manifolds with celestial azimuth transits"},
    "ising_model": {"module": "engine.strategies.fun.ising_model", "tier": "fun", "description": "🌡️ Thermodynamic Phase Transition (Ising Model)"},
    "zeno_quantum": {"module": "engine.strategies.fun.zeno_quantum", "tier": "fun", "description": "👁️ Quantum Zeno Effect (Observation Freeze)"},
    "tda_topology": {"module": "engine.strategies.fun.tda_topology", "tier": "fun", "description": "🍩 Topological Data Analysis (Structural Holes)"},
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class SuggestionResult:
    """Returned by every strategy's suggest() method."""

    strategy_name: str
    tickets: list[list[int]]        # each ticket is a sorted list of numbers
    scores: dict[int, float]        # per-number score 0–1
    confidence: float = 0.0         # strategy's self-reported confidence
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"SuggestionResult(strategy={self.strategy_name!r}, "
            f"tickets={len(self.tickets)}, confidence={self.confidence:.3f})"
        )


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class BaseStrategy(ABC):
    """
    Abstract base for all prediction strategies.

    Subclasses implement score(); suggest() is provided for free.

    Class-level attributes
    ----------------------
    name                 : str   — short identifier used in the CLI, e.g. "markov".
    description          : str   — one-line description shown in ``lottery strategies``.
    requires_history     : int   — minimum number of draws needed before the strategy
                                   is meaningful (default: 30).
    tier                 : str   — one of "statistical" | "ml" | "deep" | "fun".
    recent_matches_count : int   — how many recent matched draws to include in the
                                   ``recent_matches`` metadata list returned by
                                   correlation strategies (moon_phase, weather).
                                   Override per strategy or pass ``--recent-matches``
                                   via the CLI (default: 5).
    top_numbers_count    : int   — how many top-scoring numbers to include in the
                                   ``top_numbers`` metadata list returned by
                                   correlation strategies.  Also drives the display
                                   in ``lottery suggest``.  Pass ``--top-numbers``
                                   via the CLI to override (default: 10).
    """

    name: str                        # short identifier used in CLI  e.g. "markov"
    description: str                 # one-line description for lottery list
    requires_history:     int = 30   # minimum draws needed before strategy is meaningful
    tier:                 str = "statistical"   # "statistical" | "ml" | "deep" | "fun"
    recent_matches_count: int = 5    # rows surfaced in metadata["recent_matches"]
    top_numbers_count:    int = 10   # rows surfaced in metadata["top_numbers"]

    # ------------------------------------------------------------------
    # Must override
    # ------------------------------------------------------------------

    @abstractmethod
    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        """
        Assign a score 0–1 to every number in the lottery pool.
        Higher score → the strategy thinks this number is more likely to appear.

        Parameters
        ----------
        df    : canonical draw DataFrame (sorted ascending by draw_id)
        rules : DrawRules for the target lottery

        Returns
        -------
        dict mapping every number in range(lo, hi+1) to a float in [0, 1].
        Scores need not sum to 1 — normalisation happens in suggest().
        """
        ...

    # ------------------------------------------------------------------
    # Provided
    # ------------------------------------------------------------------

    def is_harmonious(self, ticket: list[int], rules: DrawRules, filters: list[str] | None = None, k_of_n: int | None = None, **kwargs: Any) -> bool:
        """
        Structural Harmony Check with Meta-Logic (K-of-N Fault Tolerance).
        """
        from engine.modules import harmony
        
        active_list: list[str]
        if filters is None:
            active_list = ["sum_range", "parity", "breadth"]
        elif "balanced" in filters:
            expanded = [f for f in filters if f != "balanced"]
            expanded += ["sum_range", "parity", "breadth"]
            active_list = expanded
        elif "all" in filters:
            active_list = list(harmony.registry.list_available())
        else:
            active_list = filters
            
        return harmony.registry.validate(ticket, rules, active_list, k_of_n, **kwargs)

    def suggest(
        self,
        df: pd.DataFrame,
        rules: DrawRules,
        count: int = 1,
        temperature: float = 1.0,
        history_limit: int | None = None,
        seed: int | None = None,
        pick: int | None = None,
        pool: list[int] | None = None,
        key: list[int] | None = None,
        filters: list[str] | None = None,
        filters_k_of_n: int | None = None,
        chaos: bool = False,
        **kwargs: Any,
    ) -> SuggestionResult:
        """
        Generate `count` ticket suggestions using temperature-based sampling.

        Parameters
        ----------
        count          : number of distinct tickets to generate
        temperature    : sampling sharpness (0=deterministic, 1=proportional, >1=noisy)
        history_limit  : if set, only use the most recent N draws for scoring
        seed           : optional random seed for intentional/personalized synchronicity
        pick           : optional pick count override (for multiple bets)
        pool           : restrict possible numbers to this subset
        key            : mandatory numbers to include in every ticket
        filters        : list of structural filters to apply
        filters_k_of_n : pass if ticket satisfies at least K of the active filters
        chaos          : enable environmental jitter (Solar/Seismic)
        kwargs         : strategy-specific parameters
        """
        import numpy as np # Local import for performance
        # Default to standard pick count from rules if not overridden
        target_pick = pick if pick is not None else rules.pick_count

        # ── (v10.0) Environmental Chaos ──────────────────────────────────────
        env_metadata = {}
        active_temp = temperature
        if chaos:
            try:
                from engine.modules.environment import EnvironmentalService
                env_service = EnvironmentalService()
                env_jitter = env_service.get_jitter()
                active_temp += env_jitter["total_boost"]
                env_metadata["env_jitter"] = env_jitter
            except Exception:
                pass

        # 0. Adaptive Window Sweep (v8.0)
        final_history_limit = history_limit
        adaptive = getattr(self, "adaptive_window", False)
        if adaptive and not df.empty and len(df) > 50:
            best_limit = len(df)
            best_score = -1.0
            
            # Target: last 5 draws as validation
            val_df = df.tail(5)
            train_pool = df.iloc[:-5]
            
            # Test 3 regimes: Fast (20), Medium (50), Deep (All)
            for test_limit in [20, 50, len(train_pool)]:
                if len(train_pool) < test_limit: continue
                
                # Internal scoring check: how many of the validation numbers 
                # would have been in the top 30% of this strategy's scores?
                slice_df = train_pool.tail(test_limit)
                try:
                    # Avoid infinite recursion by calling score() directly
                    test_scores = self.score(slice_df, rules)
                    # Normalize and find threshold
                    vals = sorted(test_scores.values(), reverse=True)
                    threshold = vals[int(len(vals) * 0.3)]
                    
                    hits = 0
                    for row in val_df.itertuples():
                        hits += sum(1 for n in row.numbers if test_scores.get(n, 0) >= threshold)
                    
                    if hits >= best_score:
                        best_score = hits
                        best_limit = test_limit
                except Exception:
                    continue
            
            final_history_limit = best_limit

        # Apply recency bias limit if requested
        if final_history_limit is not None and final_history_limit > 0:
            df = df.tail(final_history_limit)

        if len(df) < self.requires_history:
            raise ValueError(
                f"{self.name} requires >= {self.requires_history} draws, "
                f"got {len(df)}."
            )
            
        # Warning if running close to the data floor
        if self.requires_history > 0 and len(df) < (self.requires_history * 1.2):
            import logging
            logging.warning(
                f"Strategy '{self.name}' is running near its minimum data floor "
                f"({len(df)}/{self.requires_history} draws). Results may be volatile."
            )

        # Only pass kwargs that belong to score
        score_kwargs = {k: v for k, v in kwargs.items() if k not in ["filters", "k_of_n", "density", "pool", "key"]}
        scores = self.score(df, rules, **score_kwargs)

        # Normalise to [0, 1]
        lo, hi = rules.number_range
        
        # --- (Howard Idea 2) Pool Constraint ---
        if pool:
            active_numbers = sorted(list(set(pool) & set(range(lo, hi + 1))))
            if not active_numbers:
                raise ValueError("Provided --pool has no valid numbers for this lottery.")
        else:
            active_numbers = list(range(lo, hi + 1))

        max_s = max(scores.values()) if scores else 1.0
        min_s = min(scores.values()) if scores else 0.0
        rng = max_s - min_s or 1.0
        
        # Only normalise numbers that are in our active pool
        normed = {n: (scores.get(n, 0.0) - min_s) / rng for n in active_numbers}

        # 4. Geometric Singularity (v7.0)
        # Identify top numbers and boost their 'Dodecahedron Neighbors'
        from engine.modules.geometry import get_dodecahedron_neighbors
        top_ns = sorted(normed.keys(), key=normed.get, reverse=True)[:3]
        for top_n in top_ns:
            neighbors = get_dodecahedron_neighbors(top_n, max_n=hi)
            for nb in neighbors:
                if nb in normed:
                    # Boost neighbors by 15% of the top number's score
                    normed[nb] = min(1.0, normed[nb] + (normed[top_n] * 0.15))

        # Initialize seeded random if provided
        import random
        local_rng = random.Random(seed) if seed is not None else random.Random()
        
        # --- (Howard Idea 3) Key Number Handling ---
        mandatory_keys = []
        if key:
            mandatory_keys = sorted(list(set(key) & set(active_numbers)))
            if len(mandatory_keys) > target_pick:
                raise ValueError(f"Too many mandatory keys ({len(mandatory_keys)}) for pick-{target_pick}")
        
        n_to_sample = target_pick - len(mandatory_keys)

        tickets: list[list[int]] = []
        # Max attempts to find harmonious tickets
        max_attempts = count * 20
        attempts = 0
        
        muon_strike_occurred = False

        while len(tickets) < count and attempts < max_attempts:
            attempts += 1
            
            # --- (Howard Idea 3) Key Number Injection ---
            remaining_normed = {n: v for n, v in normed.items() if n not in mandatory_keys}
            if n_to_sample > 0:
                sampled = _weighted_sample(list(remaining_normed.keys()), remaining_normed, n_to_sample, active_temp, rng=local_rng)
                ticket = sorted(list(sampled) + mandatory_keys)
            else:
                ticket = sorted(mandatory_keys)
            
            # (v10.0) Atmospheric Muon Flux: Simulate a Single-Event Upset (bit flip)
            from engine.modules.cosmic import simulate_muon_strike
            ticket, struck = simulate_muon_strike(ticket, rules, local_rng)
            if struck:
                muon_strike_occurred = True
            
            # If we already have this ticket, skip
            if ticket in tickets:
                continue
                
            last_draw = list(df.iloc[-1]["numbers"]) if not df.empty else []
            filters_active = bool(filters)
            if (target_pick != rules.pick_count
                    or not filters_active
                    or self.is_harmonious(ticket, rules, filters=filters, k_of_n=filters_k_of_n, last_draw=last_draw, df=df, **kwargs)
                    or attempts > (max_attempts * 0.8)):
                tickets.append(ticket)

        confidence = float(np.mean(list(normed.values())))

        # Dynamic parameter capture for transparency
        import inspect
        params = {}
        try:
            sig = inspect.signature(self.__class__.__init__)
            for p_name in sig.parameters:
                if p_name == "self":
                    continue
                if hasattr(self, p_name):
                    val = getattr(self, p_name)
                    params[p_name] = val.isoformat() if hasattr(val, "isoformat") else val
        except Exception:
            pass

        result = SuggestionResult(
            strategy_name=self.name,
            tickets=tickets,
            scores=normed,
            confidence=confidence,
            metadata={"parameters": params, **env_metadata}
        )
        
        if muon_strike_occurred:
            result.metadata["muon_strike"] = True
            
        return result


# ---------------------------------------------------------------------------
# Weighted sampling helper
# ---------------------------------------------------------------------------


def _weighted_sample(
    numbers: list[int],
    scores: dict[int, float],
    k: int,
    temperature: float = 1.0,
    rng: Any = None,
) -> list[int]:
    """
    Sample k numbers without replacement using temperature-scaled weights.

    temperature = 0   → top-k (deterministic)
    temperature = 1   → proportional to score
    temperature > 1   → flatter distribution (more random)
    temperature < 1   → sharper distribution (more confident)
    """
    import numpy as np # Local import for performance
    if temperature <= 0:
        return sorted(numbers, key=lambda n: scores.get(n, 0.0), reverse=True)[:k]

    raw = np.array([max(scores.get(n, 1e-9), 1e-9) for n in numbers], dtype=float)
    raw = raw ** (1.0 / temperature)
    probs = raw / raw.sum()

    if rng and hasattr(rng, 'random'):
        # Map python random instance to a local numpy generator for consistent seeding
        gen = np.random.default_rng(rng.getrandbits(32))
        chosen = gen.choice(numbers, size=k, replace=False, p=probs)
    else:
        chosen = np.random.choice(numbers, size=k, replace=False, p=probs)
        
    return chosen.tolist()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type[BaseStrategy]] = {}


def register(cls: type[BaseStrategy]) -> type[BaseStrategy]:
    """Class decorator — registers a strategy by its .name attribute."""
    _REGISTRY[cls.name] = cls
    return cls


# --- Registry Helpers ---

def bootstrap_registry():
    """No longer eagerly imports everything. Kept for backward compatibility."""
    pass

def _load_strategy(name: str):
    """Dynamically import a strategy module by name using the Registry."""
    if name in _REGISTRY:
        return
    
    config = STRATEGY_REGISTRY.get(name)
    if config and "module" in config:
        import importlib
        try:
            importlib.import_module(config["module"])
        except Exception as e:
            import logging
            logging.debug(f"Failed to lazy-load strategy {name} from {config['module']}: {e}")

# --- Strategy Presets 📂 ---

# Curated presets that mix tiers or select specific high-value subsets
CURATED_PRESETS = {
    "chaos": [
        "kabbalistic",
        "reincarnation",
        "lorentz",
        "sentiment",
        "refraction",
        "seismic",
        "benford_illusion",
        "retrocausality",
        "geo_sync",
        "cpu_entropy",
        "sacred_grid",
        "ising_model",
        "zeno_quantum",
        "tda_topology"
    ],
    "default": [
        "weighted",
        "markov",
        "bayesian",
        "momentum",
        "streak",
        "kabbalistic",
        "synapse",
        "copairs",
        "steiner_wheel"
    ],
    "fast": [
        "bayesian",
        "weighted",
        "monte_carlo",
        "copairs"
    ],
    "esoteric": [
        "moon_phase",
        "solar",
        "noosphere",
        "numerology",
        "fibonacci",
        "kabbalistic"
    ]
}

# Automatically generate tier-based presets from the registry
def _generate_presets():
    from collections import defaultdict
    presets = defaultdict(list)
    for name, config in STRATEGY_REGISTRY.items():
        presets[config["tier"]].append(name)
    
    # Merge with curated ones
    presets.update(CURATED_PRESETS)
    return dict(presets)

STRATEGY_PRESETS = _generate_presets()

def get_strategy(name: str, **kwargs: Any) -> BaseStrategy:
    """Instantiate a strategy by name with optional arguments. Raises KeyError if unknown."""
    # Support ensemble syntax: "voting:markov,weighted"
    members = None
    requested_base = name
    if ":" in name and name not in _REGISTRY:
        requested_base, members_str = name.split(":", 1)
        members = [m.strip() for m in members_str.split(",") if m.strip()]
        
    # Lazy load the requested strategy
    if requested_base not in _REGISTRY:
        _load_strategy(requested_base)

    if requested_base not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown strategy {name!r}. Available: {available}")
    
    cls = _REGISTRY[requested_base]
    # ... rest of get_strategy implementation ...
    
    # Handle classes with no custom __init__ (object.__init__ rejects arguments)
    if cls.__init__ is object.__init__:
        return cls()

    # Surgical instantiation: only pass kwargs that the strategy's __init__ accepts
    import inspect
    sig = inspect.signature(cls.__init__)
    
    # Merge members into kwargs if present
    if members is not None:
        kwargs["members"] = members

    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    
    if has_kwargs:
        return cls(**kwargs)
    
    filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return cls(**filtered)


def list_strategies() -> list[dict[str, str]]:
    """Return a list of {name, tier, description} dicts for all strategies in the registry."""
    results = []
    # Use registry for fast reporting without loading classes
    for name, config in STRATEGY_REGISTRY.items():
        results.append({
            "name": name,
            "tier": config["tier"],
            "description": config["description"]
        })
    
    # Also include any dynamically registered ones not in the hardcoded registry
    for name, cls in _REGISTRY.items():
        if name not in STRATEGY_REGISTRY:
            results.append({
                "name": name,
                "tier": cls.tier,
                "description": cls.description
            })
            
    return results
