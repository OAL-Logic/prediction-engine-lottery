import threading

import duckdb
import pytest

from engine.modules.ledger import GENESIS_HASH, ForensicLedger, LedgerError

STATE = [0.1, -2.5e-17, 1 / 3, 4.0]
WEIGHTS = {"a": 0.25, "b": 0.75}


def cap(led, **kw):
    args = dict(ticket=[1, 2, 3], state_vector=STATE, agent_weights=WEIGHTS, qpu_fidelity=0.93)
    args.update(kw)
    return led.capture(**args)


@pytest.fixture
def path(tmp_path):
    return tmp_path / "l.duckdb"


def test_capture_and_roundtrip(path):
    with ForensicLedger(path) as led:
        e = cap(led, metadata={"k": [1, 2]})
        assert e.seq == 1 and e.prev_hash == GENESIS_HASH
        g = led.get(1)
        assert g == e
        assert g.state_vector == STATE and g.qpu_fidelity == 0.93
        assert g.agent_weights == WEIGHTS and g.metadata == {"k": [1, 2]}
        assert led.get(99) is None
        assert led.latest() == e and len(led) == 1


def test_chain(path):
    with ForensicLedger(path) as led:
        a, b = cap(led), cap(led)
        assert b.prev_hash == a.entry_hash and b.seq == 2
        assert led.verify().ok


def test_persistence(path):
    with ForensicLedger(path) as led:
        a = cap(led)
    with ForensicLedger(path) as led:
        assert led.get(1) == a and led.verify().ok
        assert cap(led).seq == 2 and led.verify().ok


def _raw(path, sql):
    con = duckdb.connect(str(path))
    con.execute(sql)
    con.close()


def test_tamper(path):
    with ForensicLedger(path) as led:
        cap(led), cap(led), cap(led)
    _raw(path, "UPDATE ledger SET qpu_fidelity='0.99' WHERE seq=2")
    with ForensicLedger(path) as led:
        r = led.verify()
        assert not r.ok and r.first_bad_seq == 2


def test_deleted_row(path):
    with ForensicLedger(path) as led:
        cap(led), cap(led), cap(led)
    _raw(path, "DELETE FROM ledger WHERE seq=2")
    with ForensicLedger(path) as led:
        assert not led.verify().ok


@pytest.mark.parametrize(
    "kw",
    [
        {"state_vector": [1.0, float("nan")]},
        {"state_vector": [float("inf")]},
        {"agent_weights": {"a": float("nan")}},
        {"qpu_fidelity": 1.5},
        {"qpu_fidelity": -0.1},
        {"qpu_fidelity": float("nan")},
        {"ticket": []},
    ],
)
def test_bad_input(path, kw):
    with ForensicLedger(path) as led:
        with pytest.raises(LedgerError):
            cap(led, **kw)
        assert len(led) == 0


def test_concurrency(path):
    with ForensicLedger(path) as led:
        ts = [threading.Thread(target=cap, args=(led,)) for _ in range(20)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        assert [e.seq for e in led.entries()] == list(range(1, 21))
        assert led.verify().ok


@pytest.mark.parametrize(
    "sql,reason",
    [
        ("UPDATE ledger SET captured_at = '2000-01-01' WHERE seq = 2", "entry_hash mismatch"),
        ("UPDATE ledger SET ticket = '[9,9,9]' WHERE seq = 2", "entry_hash mismatch"),
        ("UPDATE ledger SET state_vector = '[1.0]' WHERE seq = 2", "entry_hash mismatch"),
        ("UPDATE ledger SET agent_weights = '{\"a\":1.0}' WHERE seq = 2", "entry_hash mismatch"),
        ("UPDATE ledger SET metadata = '{\"x\":1}' WHERE seq = 2", "entry_hash mismatch"),
        ("UPDATE ledger SET qpu_fidelity = '0.930' WHERE seq = 2", "not canonical"),
        ("UPDATE ledger SET ticket = '[1,' WHERE seq = 2", "unreadable"),
        ("UPDATE ledger SET prev_hash = 'x' WHERE seq = 2", "prev_hash"),
        ("UPDATE ledger SET entry_hash = 'x' WHERE seq = 2", "entry_hash mismatch"),
    ],
)
def test_tamper_columns(path, sql, reason):
    with ForensicLedger(path) as led:
        cap(led), cap(led), cap(led)
    _raw(path, sql)
    with ForensicLedger(path) as led:
        r = led.verify()
    assert not r.ok and r.first_bad_seq == 2 and reason in r.reason


def test_deleted_row_reason(path):
    with ForensicLedger(path) as led:
        cap(led), cap(led), cap(led)
    _raw(path, "DELETE FROM ledger WHERE seq = 2")
    with ForensicLedger(path) as led:
        r = led.verify()
    assert not r.ok and r.first_bad_seq == 2 and "sequence gap" in r.reason


def test_tail_truncation_is_documented_limitation(path):
    with ForensicLedger(path) as led:
        cap(led), cap(led)
    _raw(path, "DELETE FROM ledger WHERE seq = 2")
    with ForensicLedger(path) as led:
        assert led.verify().ok  # needs an external anchor of latest().entry_hash


@pytest.mark.parametrize(
    "kw",
    [
        dict(ticket=[True, 2]),
        dict(ticket=[1.5]),
        dict(state_vector=[10**400]),
        dict(agent_weights=[1.0]),
        dict(agent_weights={1: 1.0}),
        dict(metadata=[1]),
        dict(metadata={"x": float("nan")}),
        dict(metadata={"x": object()}),
        dict(metadata={1: 1, "a": 2}),
    ],
)
def test_bad_input_more(path, kw):
    with ForensicLedger(path) as led:
        with pytest.raises(LedgerError):
            cap(led, **kw)
        assert len(led) == 0 and led.verify().ok


def test_closed_ledger(path):
    led = ForensicLedger(path)
    led.close()
    led.close()
    for call in (lambda: cap(led), lambda: led.get(1), led.entries, led.latest, led.verify, lambda: len(led)):
        with pytest.raises(LedgerError):
            call()


def test_failed_insert_rolls_back(path, monkeypatch):
    import engine.modules.ledger as mod

    with ForensicLedger(path) as led:
        a = cap(led)
        real = mod._seal
        monkeypatch.setattr(mod, "_seal", lambda *x: (_ for _ in ()).throw(RuntimeError("boom")))
        with pytest.raises(RuntimeError):
            cap(led)
        monkeypatch.setattr(mod, "_seal", real)
        b = cap(led)
        assert b.seq == 2 and b.prev_hash == a.entry_hash and led.verify().ok


def test_capture_pulses_and_survives_pulse_failure(path, monkeypatch):
    import engine.modules.telemetry as tel

    seen = []
    monkeypatch.setattr(tel, "pulse", lambda m, level="INFO": seen.append(m))
    with ForensicLedger(path) as led:
        cap(led)
        assert len(seen) == 1 and "seq=1" in seen[0]
        monkeypatch.setattr(tel, "pulse", lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
        cap(led)
        assert len(led) == 2
