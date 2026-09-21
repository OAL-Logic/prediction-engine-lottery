# 1. Use TypeSafe AI (Jev) for Dynamic Strategy Routing

Date: 2026-09-21

## Status

Accepted

## Context

The lottery prediction engine currently has dozens of statistical, machine learning, and esoteric prediction strategies. To optimize performance, we need a way to dynamically route or combine these strategies into an ensemble depending on the current conditions (e.g., statistical stability, clustering, esoteric anomalies like solar activity or seismic resonance).

Traditional LLMs are capable of this reasoning but suffer from hallucinations (type errors), latency (seconds of delay), and require expensive string generation (prompting). Since the strategy options are static, we need a solution that maps the game's diagnostic metrics to a strict probability distribution of prediction strategies.

## Decision

We will integrate **Jev** (a System One Model by TypeSafe AI) as the core dynamic strategy router.

Jev is chosen because it:
1. Replaces autoregressive string generation with **parallel sampling**, resulting in response times under 500ms.
2. Uses **structured program state** (JSON) as input instead of natural language, eliminating the need to cast numerical diagnostic metrics into text.
3. Outputs **strict, typed probabilistic decisions** with mathematically calibrated confidence scores (thanks to RLCD - Reinforcement Learning for Calibrated Decisions).
4. Guarantees **zero type errors**, meaning it will never hallucinate a strategy name that does not exist in our enum.

## Architecture

We defined a strict schema bridging the output of the `lottery scan` diagnostic engine to Jev's input format:

**Input State Schema (`DiagnosticState`)**:
Contains real-time metrics including `fairness_p`, `stability`, `js_divergence`, `regime` (STABLE/DRIFT/SHIFT), `solar_kp`, etc.

**Output Decision Enum (`PredictionStrategy`)**:
A strict enum containing all core strategies: `markov`, `bayesian`, `gradient_boost`, `vix_jitter`, etc.

**Execution Flow**:
1. The `scan` command runs the 6-layer diagnostic and compiles the `DiagnosticState` payload.
2. The payload is sent to Jev alongside the `PredictionStrategy` enum and routing instructions (e.g., favoring ML models in STABLE regimes, esoteric models in SHIFT regimes).
3. Jev returns a type-safe probability distribution over the options.
4. The engine uses this distribution to configure a weighted ensemble (e.g., 65% Gradient Boost, 20% Bayesian, 15% Vix Jitter) to generate the final ticket.

A standalone script demonstrating the integration schema and mocked API response has been added to `scripts/test_jev_routing.py`.

## Consequences

**Positive:**
- Strategy selection becomes fully autonomous and mathematically calibrated without the risk of breaking downstream code due to LLM hallucinations.
- Execution speed is preserved (no hanging API requests blocking the game loop).

**Negative:**
- Introduces a dependency on TypeSafe AI's infrastructure.
