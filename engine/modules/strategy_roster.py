"""
Strategy Roster & Meta-Selection 🗳️
===================================
Turns empirical strategy performance into a persisted, per-game "active
roster" — the set of strategies `lottery forecast --strategies roster` /
`lottery rank-numbers --strategies roster` will actually use.

This is the implementation half of the wayfinder effort at
docs/wayfinder/strategy-pruning-meta-selection-map.md. Policy is documented
in full at docs/wayfinder/decisions/003-policy-thresholds-decision.md
(MDR-003); the persisted schema is documented at
docs/wayfinder/decisions/001-roster-data-model-decision.md (MDR-001).

Policy summary
--------------
- Primary signal: `data/calibration_cache.json` lift, written by
  `lottery calibrate`. That cache uses a **1.0-baseline** scale (1.0 = same
  as random, >1.0 = better — see calibrate.py's `_save_cache`/"Lift > 1.0 =
  above random").
- A strategy with no calibration entry is evaluated live via
  `engine.modules.pruning.run_pruning_audit()`, whose `lift_over_random` is
  **0-baseline** (0.0 = same as random). It is converted to the same
  1.0-baseline scale (`1.0 + lift_over_random`) before comparison, so every
  entry in the roster sits on one consistent axis.
- A strategy that fails to even instantiate (missing optional dependency —
  e.g. a `deep` tier strategy without torch installed) is excluded
  immediately, before any lift computation, with a "failed to load" reason.
- Active iff lift >= min_lift (default 1.0 — must beat random). No fixed
  roster size: every strategy clearing the bar is included.
- `--pin` / `--exclude` are explicit user overrides and always win; on a
  pin/exclude conflict for the same name, exclude wins (a stronger, more
  deliberate signal). Overrides are recorded with a plain-language reason so
  the roster file stays self-documenting.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent.parent / "data"
ROSTER_PATH = DATA_DIR / "strategy_roster.json"
CALIBRATION_CACHE_PATH = DATA_DIR / "calibration_cache.json"

POLICY_ID = "calibration-lift-threshold-v1"

DEFAULT_MIN_LIFT = 1.0
DEFAULT_MIN_DRAWS = 20  # sample-size floor; matches esoteric_significance()'s convention


@dataclass
class RosterEntry:
    name: str
    tier: str
    lift: float | None      # None only for "unevaluated"/pin-without-prior-data entries
    source: str              # "calibration" | "pruning" | "pinned" | "unevaluated"
    n_draws: int | None      # only meaningful for source == "pruning"
    active: bool
    reason: str = ""         # only meaningful when not active


@dataclass
class RosterResult:
    game_id: str
    entries: list[RosterEntry]
    policy_id: str = POLICY_ID

    @property
    def active_strategies(self) -> list[str]:
        return [e.name for e in self.entries if e.active]

    @property
    def exclusions(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for e in self.entries:
            if e.active:
                continue
            metrics: dict[str, float] = {}
            if e.lift is not None:
                metrics["lift"] = round(e.lift, 4)
            if e.n_draws is not None:
                metrics["n_draws"] = e.n_draws
            out[e.name] = {"reason": e.reason, "metrics": metrics}
        return out


def _load_calibration(lottery_id: str) -> dict[str, float]:
    """name -> lift, 1.0-baseline scale. {} if no cache or no entry for this game."""
    if not CALIBRATION_CACHE_PATH.exists():
        return {}
    try:
        cache = json.loads(CALIBRATION_CACHE_PATH.read_text())
        return dict(cache.get(lottery_id, {}).get("strategies", {}))
    except Exception:
        return {}


def compute_roster(
    adapter: Any,
    lottery_id: str,
    candidate_names: list[str],
    *,
    min_lift: float = DEFAULT_MIN_LIFT,
    window: int = DEFAULT_MIN_DRAWS,
    pin: list[str] | None = None,
    exclude: list[str] | None = None,
) -> RosterResult:
    """
    Score every candidate strategy and classify it active/excluded.

    `adapter` is only used if a live pruning-audit fallback is needed (i.e.
    at least one candidate has no calibration-cache entry); it is not
    fetched otherwise.
    """
    from engine.strategies import STRATEGY_REGISTRY, get_strategy
    from engine.modules.pruning import run_pruning_audit

    pin_set = {n.strip() for n in (pin or []) if n.strip()}
    exclude_set = {n.strip() for n in (exclude or []) if n.strip()}

    calibrated = _load_calibration(lottery_id)
    entries: dict[str, RosterEntry] = {}
    needs_live_audit: list[str] = []

    for name in candidate_names:
        tier = STRATEGY_REGISTRY.get(name, {}).get("tier", "unknown")

        # Dependency/load guard first: a strategy that can't be instantiated
        # can't be scored, calibrated, or later run by forecast/rank-numbers.
        try:
            get_strategy(name)
        except Exception as exc:
            entries[name] = RosterEntry(
                name=name, tier=tier, lift=None, source="unevaluated",
                n_draws=None, active=False,
                reason=f"failed to load ({exc.__class__.__name__}: {exc})",
            )
            continue

        if name in calibrated:
            lift = float(calibrated[name])
            active = lift >= min_lift
            entries[name] = RosterEntry(
                name=name, tier=tier, lift=lift, source="calibration",
                n_draws=None, active=active,
                reason="" if active else f"calibration lift {lift:.3f} < min {min_lift:.3f}",
            )
        else:
            needs_live_audit.append(name)

    if needs_live_audit:
        # Mirror run_pruning_audit()'s own history guard so a real "not enough
        # draws yet" can be told apart from a strategy that simply threw
        # (e.g. a `deep`/`ml` tier strategy whose optional dependency isn't
        # installed — get_strategy() above only proves the class *loads*,
        # not that its deferred torch/sklearn import will succeed at
        # `.suggest()` time).
        has_enough_history = len(adapter.fetch()) >= window + 10
        try:
            audit_results = run_pruning_audit(adapter, needs_live_audit, window=window, threshold=0.0)
        except Exception:
            audit_results = []
        audited = {m.strategy_name: m for m in audit_results}
        for name in needs_live_audit:
            tier = STRATEGY_REGISTRY.get(name, {}).get("tier", "unknown")
            m = audited.get(name)
            if m is None:
                if has_enough_history:
                    reason = (
                        "live audit failed to run (likely a missing optional dependency for the "
                        f"'{tier}' tier, or a transient error) — run "
                        f"'lottery prune {lottery_id} --strategies {name}' directly to see the "
                        "underlying error"
                    )
                else:
                    reason = f"insufficient history to evaluate (need more than {window} draws)"
                entries[name] = RosterEntry(
                    name=name, tier=tier, lift=None, source="unevaluated",
                    n_draws=None, active=False, reason=reason,
                )
                continue
            lift = 1.0 + m.lift_over_random  # normalize to calibrate.py's 1.0-baseline scale
            active = lift >= min_lift
            entries[name] = RosterEntry(
                name=name, tier=tier, lift=lift, source="pruning",
                n_draws=window, active=active,
                reason="" if active else
                       f"live audit lift {lift:.3f} < min {min_lift:.3f} "
                       f"(no calibration cache — ran live over last {window} draws)",
            )

    # ── User overrides: pin, then exclude. Exclude always wins on conflict. ──
    for name in pin_set:
        if name in entries:
            entries[name].active = True
            entries[name].reason = ""
        else:
            tier = STRATEGY_REGISTRY.get(name, {}).get("tier", "unknown")
            entries[name] = RosterEntry(name=name, tier=tier, lift=None,
                                         source="pinned", n_draws=None, active=True)

    for name in exclude_set:
        prior = entries.get(name)
        tier = prior.tier if prior else STRATEGY_REGISTRY.get(name, {}).get("tier", "unknown")
        entries[name] = RosterEntry(
            name=name, tier=tier,
            lift=prior.lift if prior else None,
            source=prior.source if prior else "excluded",
            n_draws=prior.n_draws if prior else None,
            active=False, reason="excluded by user (--exclude)",
        )

    ordered = [entries[n] for n in candidate_names if n in entries]
    extra_names = [n for n in list(pin_set | exclude_set) if n not in candidate_names]
    ordered += [entries[n] for n in extra_names]

    return RosterResult(game_id=lottery_id, entries=ordered)


def load_roster(lottery_id: str) -> dict[str, Any] | None:
    """Raw persisted roster entry for one game, or None if absent/unreadable."""
    if not ROSTER_PATH.exists():
        return None
    try:
        data = json.loads(ROSTER_PATH.read_text())
    except Exception:
        return None
    return data.get(lottery_id)


def save_roster(result: RosterResult) -> None:
    """Persist (or update) this game's entry in data/strategy_roster.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {}
    if ROSTER_PATH.exists():
        try:
            existing = json.loads(ROSTER_PATH.read_text())
        except Exception:
            existing = {}

    prior_regime_overrides = existing.get(result.game_id, {}).get("regime_overrides", {})
    existing[result.game_id] = {
        "game_id": result.game_id,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "policy_id": result.policy_id,
        "active_strategies": result.active_strategies,
        "exclusions": result.exclusions,
        # Future-proof hook for regime-aware sub-rosters (MDR-001 §3); this
        # MVP never writes to it, so any value a later tool sets is preserved.
        "regime_overrides": prior_regime_overrides,
    }
    ROSTER_PATH.write_text(json.dumps(existing, indent=2))
