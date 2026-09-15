"""
Genetic Wheel CLI Tests 🎡
==========================
The genetic-wheel command previously used the bare, unseeded `random` module
throughout (population init, crossover, mutation) — every run was
non-reproducible. These tests verify the command is now registered, still
works unseeded (back-compat), and is fully reproducible when a seed is given.
"""

from __future__ import annotations

from typer.testing import CliRunner
from engine.cli.main import app

runner = CliRunner()
# Mega-Sena (pick 6) rather than Lotofácil (pick 15): --pool must be >= the
# game's pick_count, and a smaller pick makes the Monte Carlo fitness loop
# fast enough for a test.
GAME = "br/mega-sena"


def _ok(result):
    assert result.exit_code == 0, f"Exit {result.exit_code}:\n{result.output}"
    assert result.output.strip(), "Command produced no output"


def test_genetic_wheel_registered_and_runs_unseeded():
    """Command must be reachable from the top-level CLI (it previously was not wired up)."""
    result = runner.invoke(app, ["genetic-wheel", GAME, "--pool", "8", "--target", "3", "--tickets", "3", "--gens", "3"])
    _ok(result)
    assert "GENETIC WHEEL EVOLVED" in result.output


def test_genetic_wheel_seed_is_reproducible():
    """Same --seed -> byte-identical evolved wheel across independent runs."""
    args = ["genetic-wheel", GAME, "--pool", "8", "--target", "3", "--tickets", "3", "--gens", "5", "--seed", "42"]
    r1 = runner.invoke(app, args)
    r2 = runner.invoke(app, args)
    _ok(r1)
    _ok(r2)
    assert r1.output == r2.output


def test_genetic_wheel_different_seeds_can_differ():
    """Sanity check that --seed actually drives the RNG (not silently ignored)."""
    base = ["genetic-wheel", GAME, "--pool", "8", "--target", "3", "--tickets", "3", "--gens", "5"]
    r1 = runner.invoke(app, base + ["--seed", "1"])
    r2 = runner.invoke(app, base + ["--seed", "2"])
    _ok(r1)
    _ok(r2)
    # Not a strict guarantee for every possible pair, but overwhelmingly likely
    # for two different seeds over a stochastic multi-generation search.
    assert r1.output != r2.output


def test_genetic_wheel_weather_seed_smoke():
    """--weather-seed must not crash and must print the environmental seed panel."""
    result = runner.invoke(app, ["genetic-wheel", GAME, "--pool", "8", "--target", "3", "--tickets", "3", "--gens", "3", "--weather-seed"])
    _ok(result)
    assert "Environmental Seed" in result.output
