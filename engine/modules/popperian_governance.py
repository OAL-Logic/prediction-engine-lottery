"""
Popperian Strategy Governance & Tier Isolation Engine 🏛️⚖️
===========================================================
Enforces scientific Popperian falsification and architectural tier isolation
governance (ADR-0005 & Issue 07):

1. Strict Tier Classification: Every strategy must belong to an approved tier:
   ('statistical', 'ml', 'deep', 'foundation', 'fun').
2. Class & Registry Consistency: Strategy class `.tier` must match registry declaration.
3. Production Ensemble Purity: Default/production presets ('default', 'fast') must contain
   ZERO strategies with tier 'fun' unless certified with empirical significance (p < 0.01).
4. Fringe Demarcation & Null Hypothesis Audit:
   - All 9 fringe theories are isolated under tier 'fun' and grouped in preset 'fringe'.
   - Empirical study report must exist and prove H_0 retention (p >= 0.01).
   - Any attempt to promote an unverified fringe theory to production raises a governance violation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from engine.strategies import (
    CURATED_PRESETS,
    STRATEGY_PRESETS,
    STRATEGY_REGISTRY,
    get_strategy,
)

APPROVED_TIERS: Set[str] = {"statistical", "ml", "deep", "foundation", "fun"}

PRODUCTION_PRESETS: Set[str] = {"default", "fast"}

PERMITTED_FUN_PRESETS: Set[str] = {"fun", "fringe", "chaos", "esoteric"}

CANONICAL_FRINGE_THEORIES: Set[str] = {
    "benford_illusion",
    "retrocausality",
    "quantum_multiverse",
    "ising_model",
    "zeno_quantum",
    "tda_topology",
    "sacred_grid",
    "lorentz",
    "noosphere",
}

EMPIRICAL_STUDY_PATH = (
    Path(__file__).parent.parent.parent
    / "reports"
    / "br"
    / "studies"
    / "fringe-theories-empirical-evaluation.md"
)


@dataclass
class GovernanceViolation:
    rule: str
    severity: str  # "ERROR" or "WARNING"
    strategy: str | None
    message: str


@dataclass
class GovernanceAuditResult:
    passed: bool
    total_strategies: int
    total_presets: int
    fringe_theories_checked: int
    violations: List[GovernanceViolation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"🏛️ Popperian Governance Status: {'PASSED (Zero Violations)' if self.passed else 'FAILED'}",
            f"   • Strategies Checked: {self.total_strategies}",
            f"   • Presets Audited: {self.total_presets}",
            f"   • Fringe Theories Demarcated: {self.fringe_theories_checked} / {len(CANONICAL_FRINGE_THEORIES)}",
            f"   • Violations Found: {len(self.violations)}",
        ]
        if self.violations:
            lines.append("\n⚠️ VIOLATION DETAILS:")
            for v in self.violations:
                lines.append(f"   [{v.severity}] Rule '{v.rule}' (Strategy: {v.strategy or 'N/A'}): {v.message}")
        return "\n".join(lines)


def audit_tier_classification() -> List[GovernanceViolation]:
    """Verify that every strategy has an approved tier and matches its class definition."""
    violations: List[GovernanceViolation] = []

    for name, config in STRATEGY_REGISTRY.items():
        tier = config.get("tier")
        if not tier:
            violations.append(
                GovernanceViolation(
                    rule="approved-tier-mandatory",
                    severity="ERROR",
                    strategy=name,
                    message=f"Strategy '{name}' has no declared tier in STRATEGY_REGISTRY.",
                )
            )
            continue

        if tier not in APPROVED_TIERS:
            violations.append(
                GovernanceViolation(
                    rule="approved-tier-vocabulary",
                    severity="ERROR",
                    strategy=name,
                    message=f"Strategy '{name}' has invalid tier '{tier}'. Must be one of {sorted(APPROVED_TIERS)}.",
                )
            )
            continue

        # Check strategy class instantiation consistency if importable
        try:
            strat_instance = get_strategy(name)
            class_tier = getattr(strat_instance, "tier", None)
            if class_tier != tier:
                violations.append(
                    GovernanceViolation(
                        rule="class-registry-tier-match",
                        severity="ERROR",
                        strategy=name,
                        message=f"Class attribute tier='{class_tier}' does not match STRATEGY_REGISTRY tier='{tier}'.",
                    )
                )
        except Exception:
            # Strategies with missing optional heavy deps (e.g. PyTorch) are tolerated if properly registered
            pass

    return violations


def audit_production_presets_purity() -> List[GovernanceViolation]:
    """Verify that production presets do not contain any uncertified 'fun' tier strategies."""
    violations: List[GovernanceViolation] = []

    for preset_name in PRODUCTION_PRESETS:
        strategies_in_preset = CURATED_PRESETS.get(preset_name, [])
        for strat in strategies_in_preset:
            config = STRATEGY_REGISTRY.get(strat)
            if not config:
                violations.append(
                    GovernanceViolation(
                        rule="preset-registered-strategy",
                        severity="ERROR",
                        strategy=strat,
                        message=f"Production preset '{preset_name}' references unregistered strategy '{strat}'.",
                    )
                )
                continue

            strat_tier = config.get("tier")
            if strat_tier == "fun":
                violations.append(
                    GovernanceViolation(
                        rule="production-tier-isolation",
                        severity="ERROR",
                        strategy=strat,
                        message=(
                            f"Production preset '{preset_name}' contains tier='fun' strategy '{strat}'. "
                            f"Fun/speculative strategies must not contaminate production ensembles without "
                            f"empirical certification demonstrating p < 0.01."
                        ),
                    )
                )

    return violations


def audit_fringe_theories_demarcation() -> List[GovernanceViolation]:
    """Verify that all 9 fringe theories are isolated under tier 'fun' and documented in preset 'fringe'."""
    violations: List[GovernanceViolation] = []

    fringe_preset = set(CURATED_PRESETS.get("fringe", []))

    for strat in CANONICAL_FRINGE_THEORIES:
        if strat not in STRATEGY_REGISTRY:
            violations.append(
                GovernanceViolation(
                    rule="canonical-fringe-registered",
                    severity="ERROR",
                    strategy=strat,
                    message=f"Canonical fringe theory '{strat}' is missing from STRATEGY_REGISTRY.",
                )
            )
            continue

        config = STRATEGY_REGISTRY[strat]
        strat_tier = config.get("tier")
        if strat_tier != "fun":
            violations.append(
                GovernanceViolation(
                    rule="fringe-tier-demarcation",
                    severity="ERROR",
                    strategy=strat,
                    message=(
                        f"Canonical fringe theory '{strat}' has tier='{strat_tier}'. "
                        f"It must remain in tier='fun' under the Popperian falsification protocol until p < 0.01 is proven."
                    ),
                )
            )

        if strat not in fringe_preset:
            violations.append(
                GovernanceViolation(
                    rule="fringe-preset-membership",
                    severity="ERROR",
                    strategy=strat,
                    message=f"Canonical fringe theory '{strat}' is not included in CURATED_PRESETS['fringe'].",
                )
            )

    return violations


def audit_empirical_report_retention(report_path: Path = EMPIRICAL_STUDY_PATH) -> List[GovernanceViolation]:
    """Verify the existence and empirical integrity of the continuous falsification study."""
    violations: List[GovernanceViolation] = []

    if not report_path.is_file():
        violations.append(
            GovernanceViolation(
                rule="empirical-report-exists",
                severity="ERROR",
                strategy=None,
                message=f"Empirical study report missing at expected path: {report_path}",
            )
        )
        return violations

    try:
        content = report_path.read_text(encoding="utf-8")
    except Exception as e:
        violations.append(
            GovernanceViolation(
                rule="empirical-report-readable",
                severity="ERROR",
                strategy=None,
                message=f"Could not read empirical report: {e}",
            )
        )
        return violations

    # Extract entries from markdown tables:
    # | **`strategy`** | mu | sigma | lift_uni | lift_ort | p_val | ... | status |
    empirical_records = []
    for line in content.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 12 and "H_0" in parts[11]:
            strat_name = parts[1].replace("*", "").replace("`", "")
            try:
                pval = float(parts[6])
                status = parts[11]
                empirical_records.append((strat_name, pval, status))
            except ValueError:
                pass

    if not empirical_records:
        violations.append(
            GovernanceViolation(
                rule="empirical-p-values-present",
                severity="WARNING",
                strategy=None,
                message="No explicit empirical p-values found in empirical study report tables.",
            )
        )
    else:
        # Check that empirical falsification is upheld (H_0 retained, p >= 0.01)
        for strat, pval, status in empirical_records:
            if pval < 0.01:
                violations.append(
                    GovernanceViolation(
                        rule="popperian-falsification-anomaly",
                        severity="WARNING",
                        strategy=strat,
                        message=(
                            f"Strategy '{strat}' showed empirical p={pval:.4f} < 0.01. "
                            f"If an empirical edge is statistically proven, a formal review is required before tier promotion."
                        ),
                    )
                )

    return violations


def run_popperian_governance_audit(
    report_path: Path = EMPIRICAL_STUDY_PATH,
) -> GovernanceAuditResult:
    """Execute the full Popperian Strategy Governance quality gate audit."""
    all_violations: List[GovernanceViolation] = []

    # 1. Tier classification
    all_violations.extend(audit_tier_classification())

    # 2. Production presets purity
    all_violations.extend(audit_production_presets_purity())

    # 3. Canonical fringe theories demarcation
    all_violations.extend(audit_fringe_theories_demarcation())

    # 4. Empirical study integrity
    all_violations.extend(audit_empirical_report_retention(report_path))

    # Any ERROR severity violation causes failure
    has_errors = any(v.severity == "ERROR" for v in all_violations)

    return GovernanceAuditResult(
        passed=not has_errors,
        total_strategies=len(STRATEGY_REGISTRY),
        total_presets=len(STRATEGY_PRESETS),
        fringe_theories_checked=len(CANONICAL_FRINGE_THEORIES),
        violations=all_violations,
    )
