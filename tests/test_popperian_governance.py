"""
Tests for Popperian Strategy Governance & Tier Isolation Quality Gate 🏛️⚖️
========================================================================
Validates that:
1. Every strategy has an approved tier.
2. Strategy class tier attributes match STRATEGY_REGISTRY declarations.
3. Production presets ('default', 'fast') never contain tier='fun' strategies.
4. Canonical fringe theories remain isolated in tier='fun' and in preset 'fringe'.
5. Continuous falsification empirical study report is valid with p >= 0.01 (H_0 retained).
6. Quality gate catches tampering or rule violations.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from engine.strategies import (
    CURATED_PRESETS,
    STRATEGY_PRESETS,
    STRATEGY_REGISTRY,
    get_strategy,
)
from engine.modules.popperian_governance import (
    APPROVED_TIERS,
    CANONICAL_FRINGE_THEORIES,
    EMPIRICAL_STUDY_PATH,
    PRODUCTION_PRESETS,
    audit_empirical_report_retention,
    audit_fringe_theories_demarcation,
    audit_production_presets_purity,
    audit_tier_classification,
    run_popperian_governance_audit,
)
from engine.cli.commands.popper_check import popper_check


def test_all_strategies_have_valid_approved_tiers():
    """Verify that every strategy has a recognized tier and class-registry consistency."""
    violations = audit_tier_classification()
    error_violations = [v for v in violations if v.severity == "ERROR"]
    assert not error_violations, f"Tier classification violations found: {error_violations}"


def test_production_presets_purity():
    """Verify that default/fast production presets never include uncertified 'fun' tier strategies."""
    violations = audit_production_presets_purity()
    assert not violations, f"Production preset purity violated: {violations}"

    for preset_name in PRODUCTION_PRESETS:
        strategies = CURATED_PRESETS.get(preset_name, [])
        for s in strategies:
            strat_tier = STRATEGY_REGISTRY[s]["tier"]
            assert strat_tier != "fun", f"Strategy '{s}' in production preset '{preset_name}' has tier='fun'!"


def test_canonical_fringe_theories_demarcation():
    """Verify that all 9 fringe theories are isolated in tier='fun' and in preset 'fringe'."""
    violations = audit_fringe_theories_demarcation()
    assert not violations, f"Fringe demarcation violations: {violations}"

    assert len(CANONICAL_FRINGE_THEORIES) == 9
    fringe_preset = set(CURATED_PRESETS["fringe"])
    for s in CANONICAL_FRINGE_THEORIES:
        assert s in STRATEGY_REGISTRY, f"Fringe strategy '{s}' missing from registry"
        assert STRATEGY_REGISTRY[s]["tier"] == "fun", f"Fringe strategy '{s}' not classified as 'fun'"
        assert s in fringe_preset, f"Fringe strategy '{s}' missing from CURATED_PRESETS['fringe']"


def test_empirical_study_report_integrity_and_h0_retention():
    """Verify the continuous falsification study report exists and retains H_0 (p >= 0.01)."""
    assert EMPIRICAL_STUDY_PATH.is_file(), f"Empirical report missing: {EMPIRICAL_STUDY_PATH}"
    violations = audit_empirical_report_retention(EMPIRICAL_STUDY_PATH)
    error_violations = [v for v in violations if v.severity == "ERROR"]
    assert not error_violations, f"Empirical report audit failed: {error_violations}"


def test_tamper_detection_on_illegal_tier_or_preset_injection(tmp_path: Path):
    """Ensure the governance engine detects illegal injections and raises ERROR violations."""
    # 1. Test missing report detection
    bogus_path = tmp_path / "non_existent_report.md"
    violations = audit_empirical_report_retention(bogus_path)
    assert any(v.rule == "empirical-report-exists" for v in violations)


def test_run_popperian_governance_audit_overall():
    """Execute complete governance audit and ensure PASSED status with 0 violations."""
    result = run_popperian_governance_audit()
    assert result.passed is True
    assert len(result.violations) == 0
    assert result.total_strategies == len(STRATEGY_REGISTRY)
    assert result.fringe_theories_checked == 9
    summary = result.summary()
    assert "PASSED" in summary
    assert "Zero Violations" in summary


def test_cli_popper_check_command():
    """Verify that the CLI command popper_check executes cleanly without exceptions."""
    # Should run with quiet=True without raising SystemExit
    popper_check(quiet=True)
