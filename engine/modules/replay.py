"""
Forensic replay (Story 4.2).

Read-only: loads a ledger entry by ``seq``, re-verifies the whole hash chain and
returns a JSON-able payload for the 3D "geodesic ghost" view. No payload is
produced unless the chain verifies.
"""

from __future__ import annotations

from typing import Any, Dict

from engine.modules.ledger import ForensicLedger, LedgerError


class ReplayError(ValueError):
    """Replay refused: unknown seq, tampered chain or unusable ledger."""


def build_replay(ledger: ForensicLedger, seq: int) -> Dict[str, Any]:
    if isinstance(seq, bool) or not isinstance(seq, int):
        raise ReplayError(f"seq must be an int, got {seq!r}")
    try:
        result = ledger.verify()
        if not result.ok:
            raise ReplayError(
                f"ledger verification failed at seq {result.first_bad_seq}: {result.reason}"
            )
        entry = ledger.get(seq)
    except LedgerError as exc:
        raise ReplayError(str(exc)) from exc
    if entry is None:
        raise ReplayError(f"unknown ledger seq {seq}")
    return {
        "seq": entry.seq,
        "ticket": list(entry.ticket),
        "state_vector": list(entry.state_vector),
        "agent_weights": dict(entry.agent_weights),
        "qpu_fidelity": entry.qpu_fidelity,
        "entry_hash": entry.entry_hash,
        "captured_at": entry.captured_at,
    }
