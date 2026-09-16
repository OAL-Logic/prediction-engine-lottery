"""Number Clique CLI Tests 🔗🕸️"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.number_clique import find_cliques

runner = CliRunner()
GAME = "br/mega-sena"


def test_find_cliques_detects_mutual_triangle():
    # 1-2, 1-3, 2-3 all >= 5: a genuine triangle/clique.
    # 1-4 exists but 2-4/3-4 don't: 4 must NOT form a clique with 1,2,3.
    pair_counts = {
        (1, 2): 6, (1, 3): 5, (2, 3): 7,
        (1, 4): 9,
    }
    cliques = find_cliques(pair_counts, k=3, min_pair_count=5)
    assert (1, 2, 3) in [c for c, _ in cliques]
    assert all(4 not in c for c, _ in cliques)


def test_find_cliques_respects_min_pair_count():
    pair_counts = {(1, 2): 2, (1, 3): 2, (2, 3): 2}
    cliques = find_cliques(pair_counts, k=3, min_pair_count=5)
    assert cliques == []


def test_find_cliques_raises_over_safety_cap():
    import pytest
    # 50 fully-connected nodes -> way over the 40-node cap.
    pair_counts = {}
    nodes = list(range(1, 51))
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            pair_counts[(a, b)] = 10
    with pytest.raises(ValueError):
        find_cliques(pair_counts, k=3, min_pair_count=5)


def test_number_clique_registered_and_runs():
    # High min-pair-count keeps the candidate set well under the safety cap
    # regardless of how real cached history happens to distribute.
    result = runner.invoke(app, ["number-clique", GAME, "--min-pair-count", "20", "--draws", "300"])
    assert result.exit_code == 0, result.output
    assert "NUMBER CLIQUE" in result.output


def test_number_clique_low_threshold_hits_safety_cap_gracefully():
    # An unrealistically low threshold over full history will legitimately
    # exceed the safety cap -- it must fail cleanly (typer.Exit), not crash.
    result = runner.invoke(app, ["number-clique", GAME, "--min-pair-count", "1"])
    assert result.exit_code != 0
    assert "safety cap" in result.output


def test_number_clique_rejects_k_below_2():
    result = runner.invoke(app, ["number-clique", GAME, "--k", "1"])
    assert result.exit_code != 0
