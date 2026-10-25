"""
Tests for filter documentation, diagrams, and dynamic explanation capabilities.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.filters import registry, format_gauge, FilterExplanation

runner = CliRunner()


def test_format_gauge_rendering():
    gauge_pass = format_gauge(15, 10, 20, True)
    assert "✓ PASS" in gauge_pass
    assert "●" in gauge_pass
    assert "target: [10..20]" in gauge_pass

    gauge_fail = format_gauge(5, 10, 20, False)
    assert "✗ FAIL" in gauge_fail
    assert "●" in gauge_fail


def test_tier1_explain_odd_count():
    f = registry.get("structural_odd_count")
    assert f is not None
    assert f.category == "Parity & Balance"
    assert len(f.formula) > 0
    assert len(f.diagram) > 0
    assert "graph LR" in f.mermaid

    # Test combination with 3 odds (balanced) -> PASS
    exp_pass = f.explain([5, 12, 23, 34, 45, 56])
    assert exp_pass.passed is True
    assert exp_pass.actual_value == 3
    assert "PASS" in exp_pass.gauge

    # Test combination with 0 odds (all even) -> FAIL
    exp_fail = f.explain([2, 4, 6, 8, 10, 12])
    assert exp_fail.passed is False
    assert exp_fail.actual_value == 0
    assert "FAIL" in exp_fail.gauge


def test_tier2_explain_positional():
    f = registry.get("positional_first_last_distance")
    assert f is not None
    assert f.category == "Span & Spread"
    assert len(f.diagram) > 0

    exp = f.explain([5, 10, 15, 20, 25, 50])
    assert exp.passed is True
    assert exp.actual_value == 45
    assert "≥ 25" in exp.allowed_range


def test_tier3_explain_algebraic():
    f = registry.get("algebraic_number_sum")
    assert f is not None
    assert f.category == "Summation"

    exp = f.explain([10, 20, 30, 40, 50, 60])
    assert exp.actual_value == 210
    assert len(exp.summary) > 0


def test_tier4_explain_historical():
    f = registry.get("historical_sum_range")
    assert f is not None
    assert f.category == "Empirical Distribution"

    exp = f.explain([10, 20, 30, 40, 50, 55])
    assert exp.actual_value == 205
    assert exp.passed is True


def test_tier5_explain_custom():
    f = registry.get("custom_inner_core")
    assert f is not None
    assert f.category == "Central Shell"

    # [25, 30, 35] in [20..40] -> count 3 >= 2 -> PASS
    exp = f.explain([5, 10, 25, 30, 35, 55])
    assert exp.passed is True
    assert exp.actual_value == 3


def test_registry_get_documentation():
    doc = registry.get_documentation("structural_odd_count")
    assert doc is not None
    assert "### `structural_odd_count`" in doc
    assert "Mathematical Formulation" in doc
    assert "```mermaid" in doc
    assert "Dynamic Evaluation Example" in doc


def test_cli_docs_filter_command():
    result = runner.invoke(app, ["docs", "--filter", "structural_odd_count", "--ticket", "5,12,23,34,45,56"])
    assert result.exit_code == 0, result.output
    assert "ODD NUMBER COUNT" in result.output
    assert "Parity & Balance" in result.output
    assert "ASCII Circuit Diagram" in result.output
    assert "Dynamic Evaluation Walkthrough" in result.output
    assert "PASS ✓" in result.output


def test_cli_docs_filters_catalog():
    result = runner.invoke(app, ["docs", "filters", "--tier", "1"])
    assert result.exit_code == 0, result.output
    assert "LOTTERY ENGINE FILTER CATALOG" in result.output
    assert "structural_odd_count" in result.output
    assert "structural_ac_value" in result.output


def test_cli_filter_funnel_info():
    result = runner.invoke(app, ["filter-funnel", "br/mega-sena", "--info", "structural_odd_count"])
    assert result.exit_code == 0, result.output
    assert "FILTER INFO: ODD NUMBER COUNT" in result.output
    assert "Formula" in result.output
