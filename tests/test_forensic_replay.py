import json

import duckdb
import pytest

from engine.modules.ledger import ForensicLedger
from engine.modules.replay import ReplayError, build_replay

STATE = [0.1, -2.5e-17, 1 / 3, 4.0]
WEIGHTS = {"a": 0.25, "b": 0.75}


def cap(led):
    return led.capture(ticket=[1, 2, 3], state_vector=STATE, agent_weights=WEIGHTS, qpu_fidelity=0.93)


def test_replay_matches_entry(tmp_path):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        e = cap(led)
        p = build_replay(led, 2)
        assert p == {
            "seq": 2, "ticket": [1, 2, 3], "state_vector": STATE, "agent_weights": WEIGHTS,
            "qpu_fidelity": 0.93, "entry_hash": e.entry_hash, "captured_at": e.captured_at,
        }
        assert all(a == b for a, b in zip(p["state_vector"], STATE))
        assert json.loads(json.dumps(p)) == p
        assert len(led) == 2


def test_unknown_seq(tmp_path):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        with pytest.raises(ReplayError):
            build_replay(led, 99)


def test_tampered_chain(tmp_path):
    path = tmp_path / "l.duckdb"
    with ForensicLedger(path) as led:
        cap(led)
        cap(led)
    con = duckdb.connect(str(path))
    con.execute("UPDATE ledger SET qpu_fidelity = '0.5' WHERE seq = 2")
    con.close()
    with ForensicLedger(path) as led:
        with pytest.raises(ReplayError, match="seq 2"):
            build_replay(led, 1)
        with pytest.raises(ReplayError, match="seq 2"):
            build_replay(led, 2)
