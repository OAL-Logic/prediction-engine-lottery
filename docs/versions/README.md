# Feature Batch Documentation

These files (`feature-batch-1.md` through `feature-batch-7.md`) document the
feature additions that landed in the Apr-26 / Apr-27 Gemini-CLI sessions.

## Naming history

They were originally named `v4.0.md` through `v10.0.md`, framing them as
released versions. They are not. The package version in `pyproject.toml` is
still `0.1.0`. The v4–v10 numbering reflected *design rounds* — each round
shipped 2–3 new features into the engine and was documented as if it were
a release.

On 2026-04-28 we renamed these files to `feature-batch-N.md` to match
reality. The original `v*.md` filenames are kept as one-line redirect stubs.

## Index

| Batch | Theme | Headline features |
|-------|-------|-------------------|
| 1 | Celestial & Gematria | Lunar tides, Universal Gematria, Prime Oscillator |
| 2 | Balanced Wheel + Chaos Governor | Sum/parity/decade resampling, temperature blending, color sigils |
| 3 | Intentional Seeding + Seismic | SHA-256 seeded RNG, USGS earthquake correlation, ensemble pruning |
| 4 | Dodecahedron + Convergence | 20-vertex graph, 500-iter Monte Carlo, atmospheric refraction |
| 5 | Noosphere + Adaptive Window | Sephoric Tree, GCP-style entropy, auto-`--limit` sweep |
| 6 | Quantum + I Ching + Muon | Tunneling sim, yarrow-stalk hexagrams, atmospheric muon flux |
| 7 | Ley Lines + Fibonacci | Becker-Hagens grid, technical-analysis retracement levels |
| 8 | Continuous Improvement | Automated Insights, Standardized API, Dashboard V3 |
| 9 | Positional & Contagion | PDF slot distribution, Lagged Adjacency Resonance |
| 10 | CLI Modularization | ADR: modular subcommand architecture, strategy hardening |

## When new feature batches are added

Add the next file as `feature-batch-N+1-<theme>.md` and update the table above.
