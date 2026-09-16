"""
Registry <-> adapter consistency 🔗
====================================
Guards against the exact gap this test was written to catch: a lottery
marked `data_available: true` in data/registry.yaml whose `adapter:` name
has no matching (or no) entry, so the CLI can't actually reach it.

Found or, `dupla_sena` / `dia_de_sorte` / `lotomania` all had complete,
working adapter classes and were already wired into `get_adapter()`'s
adapter_map (engine/cli/utils.py), but had never been added to
registry.yaml — so `lottery fetch br/dupla-sena` failed with "not
available" despite the adapter code existing and working.
"""

from __future__ import annotations

import pytest

from engine.adapters.registry import registry
from engine.cli.utils import ADAPTER_MAP, get_adapter

_AVAILABLE_GAMES = registry.list_games(only_available=True)


@pytest.mark.parametrize("game", _AVAILABLE_GAMES, ids=lambda g: g.id)
def test_available_game_has_resolvable_adapter(game):
    """Every `data_available: true` game must set `adapter:` and resolve to a real class."""
    assert game.adapter, f"{game.id} is data_available but has no `adapter:` set in registry.yaml"

    adapter = get_adapter(game.id)
    assert adapter is not None

    assert adapter.rules.pick_count == game.pick_count, (
        f"{game.id}: registry pick_count={game.pick_count} != "
        f"adapter.rules.pick_count={adapter.rules.pick_count}"
    )

    # Range width should match pool_size regardless of where the range starts
    # (Lotomania is 0-99: width 100, number_range_min 0 — see GameDefinition.to_rules()).
    lo, hi = adapter.rules.number_range
    assert hi - lo + 1 == game.pool_size, (
        f"{game.id}: registry pool_size={game.pool_size} != "
        f"adapter number_range width={hi - lo + 1}"
    )


def test_at_least_the_known_games_are_available():
    ids = {g.id for g in _AVAILABLE_GAMES}
    expected = {
        "br/mega-sena", "br/lotofacil", "br/quina", "br/mais-milionaria",
        "br/dupla-sena", "br/dia-de-sorte", "br/lotomania",
        "us/powerball", "us/mega-millions", "eu/euro-millions",
    }
    missing = expected - ids
    assert not missing, f"Expected available games missing from registry.yaml: {missing}"


@pytest.mark.parametrize("adapter_short_name", sorted(ADAPTER_MAP), ids=sorted(ADAPTER_MAP))
def test_every_adapter_map_entry_is_reachable_from_the_registry(adapter_short_name):
    """
    The inverse of test_available_game_has_resolvable_adapter: a fully-coded,
    ADAPTER_MAP-wired adapter is still dead code if no registry.yaml row
    points `adapter:` at it with `data_available: true` — exactly the state
    dupla_sena/dia_de_sorte/lotomania were found in. Prevents that from
    silently recurring for any future adapter.
    """
    referencing_games = [g for g in _AVAILABLE_GAMES if g.adapter == adapter_short_name]
    assert referencing_games, (
        f"ADAPTER_MAP['{adapter_short_name}'] has no data_available:true registry.yaml "
        f"entry pointing `adapter: {adapter_short_name}` at it — the adapter is unreachable "
        f"from the CLI. Add a registry.yaml entry or remove the orphaned ADAPTER_MAP entry."
    )


def test_lotomania_uses_zero_indexed_pool():
    """The one game so far whose pool doesn't start at 1 — regression guard for
    GameDefinition.number_range_min (see engine/adapters/registry.py)."""
    game = registry.get_game("br/lotomania")
    assert game is not None
    rules = game.to_rules()
    assert rules.number_range == (0, 99)
