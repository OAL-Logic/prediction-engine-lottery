import re

import duckdb
import pytest

from engine.modules.ledger import ForensicLedger
from engine.modules.obsidian_export import ObsidianExportError, build_evidence_link, export_to_obsidian

STATE = [0.1, -2.5e-17, 1 / 3, 4.0, 1e16]
WEIGHTS = {"a": 0.25, "b": 0.75}


def cap(led):
    return led.capture(ticket=[1, 2, 3], state_vector=STATE, agent_weights=WEIGHTS, qpu_fidelity=0.93)


def test_happy_path_and_link_roundtrip(tmp_path):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        e = cap(led)
        p = export_to_obsidian(led, 2, "The swarm converged.", tmp_path / "out")
    assert p.name == f"evidence-2-{e.entry_hash[:12]}.md"
    text = p.read_text(encoding="utf-8")
    assert "The swarm converged." in text and e.entry_hash in text and "1, 2, 3" in text
    for key in ("source-strategy", "confidence-rating", "#lottery/analysis", "ledger-seq: 2", "entry-hash", "evidence-link"):
        assert key in text
    m = re.search(r"^evidence-link: \"(lottery://evidence/(\d+)\?hash=(\w+)&coords=([^\"]+))\"", text, re.M)
    assert m and int(m.group(2)) == 2 and m.group(3) == e.entry_hash
    coords = [float(c) for c in m.group(4).split(",")]
    assert coords == STATE


def test_unknown_seq(tmp_path):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        with pytest.raises(ObsidianExportError):
            export_to_obsidian(led, 9, "x", tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("bad", ["", "   \n"])
def test_blank_narrative(tmp_path, bad):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        with pytest.raises(ObsidianExportError):
            export_to_obsidian(led, 1, bad, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_tampered_chain(tmp_path):
    path = tmp_path / "l.duckdb"
    with ForensicLedger(path) as led:
        cap(led)
        cap(led)
    con = duckdb.connect(str(path))
    con.execute("UPDATE ledger SET qpu_fidelity = '0.5' WHERE seq = 2")
    con.close()
    with ForensicLedger(path) as led:
        with pytest.raises(ObsidianExportError):
            export_to_obsidian(led, 1, "x", tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_reexport_overwrites(tmp_path):
    with ForensicLedger(tmp_path / "l.duckdb") as led:
        cap(led)
        a = export_to_obsidian(led, 1, "first", tmp_path / "out")
        b = export_to_obsidian(led, 1, "second", tmp_path / "out")
    assert a == b and "second" in b.read_text(encoding="utf-8") and "first" not in b.read_text(encoding="utf-8")
    assert len(list((tmp_path / "out").iterdir())) == 1


def test_build_evidence_link_matches_ts_literal():
    h = "aa19bd9bd8e386517bbcbb6e660ea8ef6c68e67152e9d8fd3badf3e18be8bf1b"
    link = build_evidence_link({"seq": 1, "entry_hash": h, "state_vector": [0.1, -2.5e-17, 1 / 3, 1e16]})
    assert link == f"lottery://evidence/1?hash={h}&coords=0.1,-2.5e-17,0.3333333333333333,1e+16"
