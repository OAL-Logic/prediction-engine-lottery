# Product

<!-- impeccable:product-schema 1 -->

## Platform

web (closest fit for Impeccable's platform enum — actual runtime is PySide6/Qt Widgets, a cross-platform native desktop app; there is no iOS/Android build and `adaptive` would wrongly imply one, so generic non-native guidance applies over Qt Widgets/QSS instead of HTML/CSS)

## Users

Primary: the developer/operator, running the engine themselves to generate and verify their own lottery tickets (BR games: Lotofácil, Mega-Sena, Quina, Dupla Sena, Dia de Sorte, Lotomania, Mais Milionária; US/EU games: Powerball, Mega Millions, EuroMillions). Built for personal use today, with confirmed intent to eventually be usable by a broader audience of players — no other audience or use case confirmed yet.

## Product Purpose

A lottery prediction and analysis engine that ingests historical draw data, runs 80+ statistical/ML/deep-learning strategies (plus optional esoteric ones) through a 5-tier filtering and wheeling pipeline, and produces verified, backtested ticket recommendations. Success means tickets the operator can trust because they're grounded in out-of-sample-tested strategies, not novelty.

## Positioning

Most "lucky number" tools are single-strategy generators with no verification loop. This engine's differentiator is the closed loop: fetch → statistical scan → multi-strategy ensemble/consensus → wheeling (covering designs) → backtest/verify against real draw history → forecast, auditable end-to-end from the Desktop Cockpit's Verification tab (Ticket Auditor + Formula Leaderboard). No neighboring tool combines this many rigorous strategy families (Statistical, ML, Deep, Foundation-model zero-shot) with walk-forward backtesting in one workflow.

## Operating Context

- Design focus for this track: the PySide6 Desktop Cockpit (`desktop/`) — 8 tabs: Database, Analysis, Filters, Wheeling, Predict, Verification, EV, Telemetry.
- Backed by `engine/` (per-lottery adapters + strategies) and local storage (`data/lottery.db`, `data/draw_log.jsonl`) plus cached weather/solar/seismic data some strategies consume.
- The product also has an Expo React Native app (`app/`, mobile+web, 3D visualization) and a Go API gateway (`gateway/`) + FastAPI sidecar. These are out of scope for this design track by explicit choice and may get their own surface brief later.
- Operational rituals the UI supports: `lottery fetch`, `lottery daily`, `lottery session`, `lottery tune`, `lottery forecast --explain` — the CLI is the operational backbone; the desktop app is the analytical/visual layer over the same engine.

## Capabilities and Constraints

- 80+ prediction strategies across Statistical (38), ML (14), Deep (5), Foundation zero-shot (2), and Fun/Chaos-esoteric (27+) tiers.
- 10 registered lottery games (BR + US + EU) via a pluggable adapter registry (`engine/adapters/registry.py`).
- Backtesting/verification is a first-class capability (walk-forward backtest, formula leaderboard) — not just prediction.
- Desktop app ships 5 built-in themes (Forensic Neon, Cyber Synthwave, Astro Emerald, Classic Dark, Sleek Dark Mode) via `ThemeManager`; theming is data-driven (a Python dict of tokens per theme), not hardcoded per-widget.
- Constraint: some strategies (esoteric/personalization ones) read private user data from git-ignored `*.local.yaml` files — never treat this as fixture/sample content in design work.
- Constraint: `lotomania`'s 00–99, 50-pick mechanic doesn't fit the standard `pick_count` model used elsewhere — numeric displays must handle zero-indexed ranges correctly.

## Brand Commitments

- Name: "Lottery Engine" in packaging; internal names "Prophet Dashboard" (desktop cockpit) and "Absurdity Engine" / "Universal Synapse" also appear in docs. No single confirmed public-facing brand name yet.
- Tone (confirmed this session): serious, rigorous analytics is the visual/tonal focus going forward. The incumbent neon/occult theme names (Forensic Neon, Cyber Synthwave, `sacred_manifold`, etc.) are existing implementation, not a brand mandate — new design work is not obligated to lean into the chaos-magic angle, even though esoteric strategies remain functionally present.

## Evidence on Hand

- Real historical draw data for all registered games in `data/lottery.db` and `data/draw_log.jsonl` — genuine draw history, not sample/fixture data.
- Backtest results and inspection reports under `data/inspections/`, `reports/`, `backtest_results.md`.
- No testimonials, pricing, or external customer evidence exist — this is a personal-use tool with no confirmed external users yet; future work must not fabricate any of these.

## Product Principles

1. Every recommendation must be traceable to a backtested/verifiable strategy — no unverified black-box outputs.
2. Serious analytics leads the tone; esoteric strategies are a feature, not the brand.
3. The desktop Cockpit is the primary analytical surface for now; the mobile/web app and gateway exist but are out of scope until named.
4. Personal/private user data (`*.local.yaml`) is real and sensitive — never fabricate or expose it as sample content in mockups or copy.
5. Built for one operator today, with the door open to more users later — don't over-invest in features that only make sense at scale (accounts, sharing) until that's confirmed.

## Accessibility & Inclusion

No product-specific accessibility requirement established yet.
