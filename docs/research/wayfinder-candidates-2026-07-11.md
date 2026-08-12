# Wayfinder Candidate Destinations

*Captured 2026-07-11 during an open-ended project scan. These are large, decision-rich efforts worth charting when focus is available.*

---

## 1. Integrate TimesFM + TabFM Foundation Models as New Strategies

**Source:** Untracked `TODO.md` at repo root (Mega-Sena Cycle & Quantitative Prediction Report).

**Rough destination:** A production-ready `timesfm` and/or `tabfm` strategy in the engine that feeds zero-shot probabilistic scores into the existing ensemble and structural-filter pipeline.

**Why it needs wayfinding:**
- Data shape for foundation-model input is not settled (binary hit indicators vs. tabular feature rows vs. multivariate series).
- Dependency and packaging impact is large (`timesfm`, GPU/CPU inference, model weights, context windows).
- Integration point with existing strategies/ensembles is undefined.
- Runtime cost and offline/air-gapped use cases need decisions.
- Chi²-gate and calibration story must be preserved.

**Open questions (fog):**
- Do we vendor a frozen TimesFM checkpoint or download on first use?
- How does a per-number time-series model interact with ticket-level structural filters?
- Is this one strategy or a family (`timesfm_point`, `timesfm_quantile`, `tabfm_classifier`)?
- What is the inference latency target for CLI `suggest`?
- How do we backtest a zero-shot model fairly on limited historical data?

---

## 2. Sprint 5 — Content + Deploy

**Source:** `SPRINT_PLAN.md` status board marks Sprint 5 as ⏳ pending.

**Rough destination:** Published content (blog posts, docs, possibly video/scripts) plus a deployment story for the engine, all framed around the chi²-gate integrity narrative.

**Why it needs wayfinding:**
- Content calendar and audience are not defined.
- Deployment target is not chosen (PyPI package, Docker image, hosted API, desktop installer, all of the above?).
- The "absurdity" content from Absurdity Engine v4–v10 needs to be shaped into publishable, honest writing.
- The quant narrative ("what a quant would do") needs to be grounded in the optimizer/backtest output.

**Open questions (fog):**
- Is the primary deliverable a blog series, a documentation site, or a launch campaign?
- Do we ship a public demo API or keep everything local-only?
- What is the release/branching cadence tied to content?
- How do we maintain the "OSS Smart Luck parity" positioning without overclaiming?

---

## 3. Strategy Pruning and Meta-Selection System

**Source:** Observation that the engine now has 80+ strategies but no automated mechanism to retire, weight, or dynamically select them per game/regime.

**Rough destination:** A decision layer that maintains a live subset of strategies per game based on empirical calibration and regime signals, with clear rules for promotion, demotion, and retirement.

**Why it needs wayfinding:**
- Selection criteria are not agreed (capture@N, lift, ROI, stability, runtime cost?).
- Relationship to existing `calibrate` and `rank-numbers` commands is unclear.
- Runtime overhead of running many strategies needs a policy.
- Retirement/deletion vs. soft-disable is a product decision.
- How the meta-selector interacts with ensembles and the forecast command is undefined.

**Open questions (fog):**
- Is this a new command (`lottery prune-live`, `lottery meta-select`) or a background daemon update?
- What is the minimum history length required before a strategy can be promoted/demoted?
- Should selection be global per game or regime-aware?
- How do we present the selected subset to the user transparently?
- What happens to esoteric strategies that cannot beat random but are user favorites?

---

## 4. Desktop / Mobile App Convergence

**Source:** Architecture diagrams and `docs/architecture/app.md`, `docs/user_guides/PROPHET_DESKTOP.md`.

**Rough destination:** A shipped desktop MVP or a defined mobile feature-parity map that exposes the engine's commands through the existing Go gateway / FastAPI sidecar.

**Why it needs wayfinding:**
- Recent sprints have heavily favored CLI features; client surfaces are lagging.
- Scope choice is wide: desktop first, mobile first, or a shared design system?
- Communication protocol and offline capability are not decided.
- Which commands are MVP vs. v2 is undefined.

**Open questions (fog):**
- Which client (PySide6 desktop or Expo mobile/web) is the higher-value first ship?
- Does the desktop client bundle the Python engine or talk to a local sidecar?
- What is the auth/access model for the gateway in a client context?
- How do we keep the "terminal cockpit" aesthetic across platforms?

---

## Notes

- Candidate **#3** was selected as the active wayfinder destination for the 2026-07-11 session.
- File should be revisited after any candidate is completed or scoped out.
