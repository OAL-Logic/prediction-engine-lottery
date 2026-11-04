"""
Tests for Synthetic Multiverse Benchmark Engine (Track F).
"""

from pathlib import Path
import pytest
import numpy as np

from engine.adapters import DrawRules
from engine.modules.synthetic_multiverse import (
    SyntheticUniverseGenerator,
    evaluate_synthetic_universe,
    run_synthetic_multiverse_benchmark,
    render_ascii_roc_curve,
    export_synthetic_benchmark_report,
)
from engine.cli.commands.synthetic_bench import synthetic_bench


@pytest.fixture
def mega_rules():
    return DrawRules("Mega-Sena", 6, (1, 60))


def test_synthetic_universe_noise_generation(mega_rules):
    gen = SyntheticUniverseGenerator(rules=mega_rules, seed=42)
    df = gen.generate_pure_noise_draws(n_draws=25)
    assert len(df) == 25
    assert set(df.columns) == {"draw_id", "date", "numbers"}
    for nums in df["numbers"]:
        assert len(nums) == 6
        assert len(set(nums)) == 6
        assert all(1 <= n <= 60 for n in nums)


def test_synthetic_universe_anomaly_generators(mega_rules):
    gen = SyntheticUniverseGenerator(rules=mega_rules, seed=123)

    # Ising anomaly
    df_ising, mask_ising = gen.generate_ising_anomaly_draws(n_draws=20, signal_strength=0.4)
    assert len(df_ising) == 20
    assert len(mask_ising) == 60
    assert mask_ising.sum() > 0

    # Lorenz anomaly
    df_lorenz, mask_lorenz = gen.generate_lorenz_anomaly_draws(n_draws=20, signal_strength=0.3)
    assert len(df_lorenz) == 20
    assert len(mask_lorenz) == 60
    assert mask_lorenz.sum() > 0

    # Zeno anomaly
    df_zeno, mask_zeno = gen.generate_zeno_anomaly_draws(n_draws=20, signal_strength=0.5)
    assert len(df_zeno) == 20
    assert len(mask_zeno) == 60
    assert mask_zeno.sum() > 0


def test_evaluate_synthetic_universe_roc(mega_rules):
    gen = SyntheticUniverseGenerator(rules=mega_rules, seed=42)
    df, mask = gen.generate_ising_anomaly_draws(n_draws=30, signal_strength=0.35)

    res = evaluate_synthetic_universe(
        strategy_name="ising_model",
        anomaly_type="ising",
        universe_df=df,
        true_signal_mask=mask,
        rules=mega_rules,
        signal_strength=0.35,
    )
    assert res.strategy_name == "ising_model"
    assert res.anomaly_type == "ising"
    assert 0.0 <= res.auc_score <= 1.0
    assert len(res.fpr_curve) > 0
    assert len(res.tpr_curve) > 0
    assert 0.0 <= res.power_at_5pct_fpr <= 1.0


def test_render_ascii_roc_curve():
    fpr = [0.0, 0.1, 0.5, 1.0]
    tpr = [0.0, 0.6, 0.9, 1.0]
    ascii_art = render_ascii_roc_curve(fpr, tpr, width=20, height=8)
    assert "┌" in ascii_art
    assert "└" in ascii_art
    assert "█" in ascii_art
    assert "·" in ascii_art


def test_run_synthetic_multiverse_benchmark_mini(mega_rules):
    results = run_synthetic_multiverse_benchmark(
        rules=mega_rules,
        signals=[0.0, 0.3],
        n_draws=25,
        seed=42,
    )
    assert len(results) == 6  # 3 models * 2 signal levels
    for b in results:
        assert 0.0 <= b.auc_score <= 1.0
        assert b.strategy_name in ["ising_model", "lorentz", "zeno_quantum"]


def test_export_report_and_cli(mega_rules, tmp_path):
    report_file = tmp_path / "synth_report.md"
    synthetic_bench(
        lottery="br/mega-sena",
        draws=20,
        seed=42,
        export_md=str(report_file),
        quiet=True,
    )
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Estudo de Sensibilidade em Multiversos Sintéticos" in content
    assert "Curvas ROC" in content
    assert "Zero-PII Auditado" in content
