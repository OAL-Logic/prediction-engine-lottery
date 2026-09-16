"""Pair Graph Export CLI Tests 🕸️"""

from __future__ import annotations

import pandas as pd
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.pair_graph_export import build_pair_counts, to_graphml, to_dot

runner = CliRunner()
GAME = "br/mega-sena"


def _df(rows):
    return pd.DataFrame([{"draw_id": i + 1, "numbers": nums} for i, nums in enumerate(rows)])


def test_build_pair_counts():
    df = _df([[1, 2, 3], [1, 2, 4]])
    counts = build_pair_counts(df)
    assert counts[(1, 2)] == 2
    assert counts[(1, 3)] == 1
    assert counts[(3, 4)] == 0  # never co-occurred


def test_to_graphml_structure():
    counts = {(1, 2): 5, (1, 3): 1}
    xml = to_graphml(counts, min_count=3)
    assert '<node id="n1"/>' in xml
    assert '<node id="n2"/>' in xml
    assert '<node id="n3"/>' not in xml  # filtered out by min_count
    assert 'source="n1" target="n2"' in xml
    assert xml.strip().endswith("</graphml>")


def test_to_dot_structure():
    counts = {(1, 2): 5}
    dot = to_dot(counts, min_count=1)
    assert dot.startswith("graph G {")
    assert "1 -- 2 [weight=5];" in dot
    assert dot.strip().endswith("}")


def test_pair_graph_export_registered_and_runs():
    result = runner.invoke(app, ["pair-graph-export", GAME, "--draws", "200", "--min-count", "2"])
    assert result.exit_code == 0, result.output
    assert "graph" in result.output.lower()


def test_pair_graph_export_dot_format(tmp_path):
    out = tmp_path / "graph.dot"
    result = runner.invoke(app, ["pair-graph-export", GAME, "--draws", "200", "--format", "dot", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.read_text().startswith("graph G {")


def test_pair_graph_export_rejects_bad_format():
    result = runner.invoke(app, ["pair-graph-export", GAME, "--format", "yaml"])
    assert result.exit_code != 0
