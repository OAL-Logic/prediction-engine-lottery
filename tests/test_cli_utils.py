"""engine/cli/utils.py tests: resolve_strategies() seam and load_local_config()."""

from __future__ import annotations

import json

import engine.cli.utils as cli_utils
from engine.cli.utils import load_local_config, resolve_strategies

_GROUPS = {"default": ["weighted", "markov"], "fast": ["bayesian"]}


# ── resolve_strategies() ──────────────────────────────────────────────────────

def test_resolve_strategies_explicit_list_bypasses_roster_and_groups():
    names, source = resolve_strategies("a,b,c", "br/lotofacil", _GROUPS)
    assert names == ["a", "b", "c"]
    assert source == "explicit"


def test_resolve_strategies_known_preset():
    names, source = resolve_strategies("fast", "br/lotofacil", _GROUPS)
    assert names == ["bayesian"]
    assert source == "preset:fast"


def test_resolve_strategies_roster_reads_active_list(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_utils, "DATA_DIR", tmp_path)
    (tmp_path / "strategy_roster.json").write_text(json.dumps({
        "br/lotofacil": {"active_strategies": ["monte_carlo", "copairs"]}
    }))
    names, source = resolve_strategies("roster", "br/lotofacil", _GROUPS)
    assert names == ["monte_carlo", "copairs"]
    assert source == "roster"


def test_resolve_strategies_roster_missing_file_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_utils, "DATA_DIR", tmp_path)  # empty dir, no roster file at all
    names, source = resolve_strategies("roster", "br/lotofacil", _GROUPS)
    assert names == _GROUPS["default"]
    assert source == "preset:default"


def test_resolve_strategies_roster_missing_game_entry_falls_back(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_utils, "DATA_DIR", tmp_path)
    (tmp_path / "strategy_roster.json").write_text(json.dumps({"br/mega-sena": {"active_strategies": ["weighted"]}}))
    names, source = resolve_strategies("roster", "br/lotofacil", _GROUPS)
    assert names == _GROUPS["default"]
    assert source == "preset:default"


def test_resolve_strategies_roster_empty_active_list_falls_back(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_utils, "DATA_DIR", tmp_path)
    (tmp_path / "strategy_roster.json").write_text(json.dumps({"br/lotofacil": {"active_strategies": []}}))
    names, source = resolve_strategies("roster", "br/lotofacil", _GROUPS)
    assert names == _GROUPS["default"]


def test_resolve_strategies_roster_corrupt_file_falls_back(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_utils, "DATA_DIR", tmp_path)
    (tmp_path / "strategy_roster.json").write_text("{not valid json")
    names, source = resolve_strategies("roster", "br/lotofacil", _GROUPS)
    assert names == _GROUPS["default"]


# ── load_local_config() regression: only full_name/birth_date are extracted ─

def test_load_local_config_extracts_only_documented_keys(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "personal.local.yaml").write_text("full_name: Jane Doe\nbirth_date: '1990-05-01'\nextra: ignored\n")
    config = load_local_config()
    assert config == {"full_name": "Jane Doe", "birth_date": "1990-05-01"}


def test_load_local_config_ignores_unrelated_dict_shaped_local_yaml(tmp_path, monkeypatch):
    """
    Regression test: a *.local.yaml file that isn't personal data at all (e.g.
    a `report`-pipeline template with its own top-level `name`/`steps` keys)
    must never leak those keys into the merged config. Before this fix, a
    `name` key here collided with get_strategy()'s own `name` parameter and
    raised `TypeError: get_strategy() got multiple values for argument 'name'`
    for every strategy in `forecast`/`suggest`/`tune`, silently swallowed by
    their broad `except Exception` guards around strategy execution.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "some_report.local.yaml").write_text(
        "name: My Report Pipeline\nsteps:\n  - type: fetch\n    lottery: br/lotofacil\n"
    )
    config = load_local_config()
    assert config == {}
    assert "name" not in config
    assert "steps" not in config


def test_load_local_config_merges_across_multiple_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.local.yaml").write_text("full_name: Jane Doe\n")
    (tmp_path / "b.local.yaml").write_text("birth_date: '1990-05-01'\n")
    config = load_local_config()
    assert config == {"full_name": "Jane Doe", "birth_date": "1990-05-01"}


def test_load_local_config_no_files_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_local_config() == {}
