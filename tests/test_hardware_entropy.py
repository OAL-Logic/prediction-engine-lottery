"""
Tests for Hardware Entropy & Quantum RNG (QRNG) Bridge Engine ⚛️🔌
================================================================
Validates:
1. Multi-source harvesting (PRNG, CSPRNG, HWRNG, QUANTUM_CACHE).
2. Uniform floats and integer sampling.
3. NIST SP 800-22 randomness tests (Monobit, Runs, Shannon entropy).
4. Failure detection on non-random data.
5. Lottery vs Quantum indistinguishability audit.
6. Quantum Multiverse strategy integration.
7. CLI command execution and report generation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from engine.adapters import DrawRules
from engine.modules.hardware_entropy import (
    EntropySource,
    HardwareEntropyBridge,
    compute_shannon_entropy,
    evaluate_entropy_source,
    nist_monobit_test,
    nist_runs_test,
    serial_autocorrelation,
    audit_lottery_vs_quantum,
)
from engine.strategies.fun.quantum_multiverse import QuantumMultiverseStrategy
from engine.cli.commands.entropy_bench import entropy_bench


def test_entropy_sources_harvest_bytes():
    """Verify that all entropy sources deliver the exact byte length requested."""
    bridge = HardwareEntropyBridge(quantum_seed_override=42)
    for src in EntropySource:
        raw = bridge.harvest_bytes(128, source=src)
        assert isinstance(raw, bytes)
        assert len(raw) == 128


def test_harvest_uniform_floats_and_integers():
    """Verify bounds for uniform float and discrete integer harvesting."""
    bridge = HardwareEntropyBridge()
    floats = bridge.harvest_uniform_floats(100, source=EntropySource.CSPRNG)
    assert len(floats) == 100
    assert np.all((floats >= 0.0) & (floats < 1.0))

    ints = bridge.harvest_uniform_integers(200, lo=1, hi=60, source=EntropySource.QUANTUM_CACHE)
    assert len(ints) == 200
    assert np.all((ints >= 1) & (ints <= 60))
    assert np.any(ints > 1) and np.any(ints < 60)


def test_nist_randomness_tests_on_good_and_bad_data():
    """Verify NIST tests pass on random data and fail on zeroed/biased data."""
    bridge = HardwareEntropyBridge()
    good_bytes = bridge.harvest_bytes(2048, source=EntropySource.CSPRNG)

    # Shannon entropy of good data should be close to 8.0 bits/byte
    entropy_good = compute_shannon_entropy(good_bytes)
    assert entropy_good > 7.8

    monobit_good = nist_monobit_test(good_bytes)
    assert monobit_good.p_value >= 0.001

    runs_good = nist_runs_test(good_bytes)
    assert runs_good.p_value >= 0.001

    # Bad data: all zeroes
    bad_bytes = b"\x00" * 2048
    assert compute_shannon_entropy(bad_bytes) == 0.0
    monobit_bad = nist_monobit_test(bad_bytes)
    assert monobit_bad.passed is False
    assert monobit_bad.p_value == 0.0


def test_evaluate_entropy_sources():
    """Run full evaluation across all 4 entropy sources."""
    bridge = HardwareEntropyBridge()
    for src in EntropySource:
        eval_res = evaluate_entropy_source(src, bridge, n_bytes=2048)
        assert eval_res.shannon_entropy_bits > 7.8
        assert eval_res.monobit_p_val >= 0.001
        assert eval_res.runs_p_val >= 0.001


def test_audit_lottery_vs_quantum_execution():
    """Test the complete Popperian audit pipeline against mock lottery draw data."""
    rules = DrawRules(name="Mock Lottery", number_range=(1, 60), pick_count=6)
    rng = np.random.default_rng(123)

    # Generate 50 mock draws
    draws = []
    for d in range(1, 51):
        draws.append({
            "draw_id": d,
            "numbers": sorted(rng.choice(np.arange(1, 61), size=6, replace=False).tolist()),
        })
    df = pd.DataFrame(draws)

    audit = audit_lottery_vs_quantum(
        df=df,
        rules=rules,
        lottery_name="mock/mega",
        n_benchmark_bytes=1024,
    )
    assert audit.total_draws_evaluated == 50
    assert 0.0 <= audit.ks_p_value <= 1.0
    assert 0.0 <= audit.chi2_p_value <= 1.0
    assert "H_0" in audit.verdict
    assert len(audit.source_evaluations) == 4


def test_quantum_multiverse_with_entropy_sources():
    """Verify QuantumMultiverseStrategy executes cleanly with custom entropy source."""
    rules = DrawRules(name="Mega Mock", number_range=(1, 60), pick_count=6)
    df = pd.DataFrame({
        "draw_id": [1, 2, 3, 4, 5],
        "numbers": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12], [13, 14, 15, 16, 17, 18], [19, 20, 21, 22, 23, 24], [25, 26, 27, 28, 29, 30]],
    })

    strat = QuantumMultiverseStrategy(branches=100, entropy_source="quantum_cache")
    scores = strat.score(df, rules)
    assert len(scores) == 60
    assert all(0.0 <= s <= 1.0 for s in scores.values())


def test_cli_entropy_bench_command_and_export(tmp_path: Path):
    """Test CLI command execution and report export to disk."""
    report_file = tmp_path / "quantum_entropy_report.md"
    entropy_bench(
        lottery="br/mega-sena",
        bytes_bench=1024,
        export_md=str(report_file),
        quiet=True,
    )
    assert report_file.is_file()
    content = report_file.read_text(encoding="utf-8")
    assert "Hardware Entropy & Quantum RNG" in content
    assert "NIST SP 800-22" in content
    assert "QUANTUM_CACHE" in content
