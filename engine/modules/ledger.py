"""
Immutable forensic audit ledger (Story 4.1).

Append-only DuckDB ledger of "Justified Numbers". Each ``capture`` stores the
full geodesic state-vector, agentic weights and QPU fidelity, sealed with a
SHA-256 hash chained to the previous entry. DuckDB has no triggers or row-level
permissions, so immutability is tamper-evidence: the API exposes no mutators and
``verify()`` recomputes the whole chain. (Truncating the *tail* of the chain
cannot be detected by the chain alone; anchor ``latest().entry_hash`` externally
if that matters.)
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from engine._paths import PROJECT_ROOT

DEFAULT_LEDGER_DB = PROJECT_ROOT / "data" / "forensic_ledger.duckdb"
GENESIS_HASH = "0" * 64

_COLUMNS = (
    "seq, captured_at, ticket, state_vector, agent_weights, "
    "qpu_fidelity, metadata, prev_hash, entry_hash"
)


class LedgerError(ValueError):
    """Invalid ledger input or unusable ledger."""


@dataclass(frozen=True)
class LedgerEntry:
    seq: int
    captured_at: str
    ticket: List[int]
    state_vector: List[float]
    agent_weights: Dict[str, float]
    qpu_fidelity: float
    metadata: Dict[str, Any]
    prev_hash: str
    entry_hash: str


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    checked: int
    first_bad_seq: Optional[int] = None
    reason: str = ""


def _dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _seal(prev_hash: str, fields: Dict[str, Any]) -> str:
    return hashlib.sha256((prev_hash + _dumps(fields)).encode("utf-8")).hexdigest()


def _finite(x: Any, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise LedgerError(f"{what} must be a finite number, got {x!r}")
    try:
        f = float(x)
    except OverflowError as exc:
        raise LedgerError(f"{what} out of float range") from exc
    if not math.isfinite(f):
        raise LedgerError(f"{what} must be finite, got {x!r}")
    return f


def _pulse(message: str, level: str = "INFO") -> None:
    try:
        from engine.modules.telemetry import pulse

        pulse(message, level)
    except Exception:
        pass


class ForensicLedger:
    """Append-only, hash-chained forensic ledger on its own DuckDB file."""

    def __init__(self, path: Optional[Any] = None):
        try:
            import duckdb
        except ImportError as exc:  # pragma: no cover
            raise LedgerError("duckdb is required for the forensic ledger") from exc
        self.path = Path(path) if path is not None else DEFAULT_LEDGER_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._con = duckdb.connect(str(self.path))
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS ledger ("
            "seq BIGINT PRIMARY KEY, captured_at VARCHAR NOT NULL, "
            "ticket VARCHAR NOT NULL, state_vector VARCHAR NOT NULL, "
            "agent_weights VARCHAR NOT NULL, qpu_fidelity VARCHAR NOT NULL, "
            "metadata VARCHAR NOT NULL, prev_hash VARCHAR NOT NULL, "
            "entry_hash VARCHAR NOT NULL)"
        )

    # -- lifecycle -------------------------------------------------------
    def close(self) -> None:
        with self._lock:
            if self._con is not None:
                self._con.close()
                self._con = None

    def __enter__(self) -> "ForensicLedger":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- helpers ---------------------------------------------------------
    def _conn(self):
        """Return the live connection (caller holds the lock) or raise."""
        if self._con is None:
            raise LedgerError("ledger is closed")
        return self._con

    @staticmethod
    def _row_to_entry(row: Sequence[Any]) -> LedgerEntry:
        return LedgerEntry(
            seq=int(row[0]),
            captured_at=row[1],
            ticket=json.loads(row[2]),
            state_vector=json.loads(row[3]),
            agent_weights=json.loads(row[4]),
            qpu_fidelity=json.loads(row[5]),
            metadata=json.loads(row[6]),
            prev_hash=row[7],
            entry_hash=row[8],
        )

    @staticmethod
    def _hash_fields(captured_at: str, ticket, state, weights, fidelity, metadata, seq: int):
        return {
            "seq": seq,
            "captured_at": captured_at,
            "ticket": ticket,
            "state_vector": state,
            "agent_weights": weights,
            "qpu_fidelity": fidelity,
            "metadata": metadata,
        }

    # -- API -------------------------------------------------------------
    def capture(
        self,
        ticket: Sequence[int],
        state_vector: Sequence[float],
        agent_weights: Dict[str, float],
        qpu_fidelity: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LedgerEntry:
        # Validate everything before touching the database.
        if ticket is None or len(ticket) == 0:
            raise LedgerError("ticket must be a non-empty sequence of ints")
        if any(isinstance(n, bool) or not isinstance(n, int) for n in ticket):
            raise LedgerError("ticket must contain only ints")
        if state_vector is None or len(state_vector) == 0:
            raise LedgerError("state_vector must be non-empty")
        state = [_finite(x, "state_vector element") for x in state_vector]
        if not isinstance(agent_weights, dict):
            raise LedgerError("agent_weights must be a dict of name -> float")
        weights: Dict[str, float] = {}
        for name, w in agent_weights.items():
            if not isinstance(name, str):
                raise LedgerError("agent_weights keys must be strings")
            weights[name] = _finite(w, f"agent weight {name!r}")
        fid = _finite(qpu_fidelity, "qpu_fidelity")
        if not 0.0 <= fid <= 1.0:
            raise LedgerError(f"qpu_fidelity must be in [0, 1], got {fid!r}")
        meta = {} if metadata is None else metadata
        if not isinstance(meta, dict):
            raise LedgerError("metadata must be a dict")
        try:
            meta_text = _dumps(meta)
        except (TypeError, ValueError) as exc:
            raise LedgerError(f"metadata is not JSON-serializable: {exc}") from exc
        meta = json.loads(meta_text)
        tkt = [int(n) for n in ticket]
        captured_at = datetime.now(timezone.utc).isoformat()

        with self._lock:
            if self._con is None:
                raise LedgerError("ledger is closed")
            self._con.execute("BEGIN TRANSACTION")
            try:
                row = self._con.execute(
                    "SELECT seq, entry_hash FROM ledger ORDER BY seq DESC LIMIT 1"
                ).fetchone()
                seq, prev_hash = (row[0] + 1, row[1]) if row else (1, GENESIS_HASH)
                entry_hash = _seal(
                    prev_hash,
                    self._hash_fields(captured_at, tkt, state, weights, fid, meta, seq),
                )
                self._con.execute(
                    "INSERT INTO ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        seq, captured_at, _dumps(tkt), _dumps(state), _dumps(weights),
                        _dumps(fid), meta_text, prev_hash, entry_hash,
                    ],
                )
                self._con.execute("COMMIT")
            except BaseException:
                try:
                    self._con.execute("ROLLBACK")
                except Exception:
                    pass
                raise
        entry = LedgerEntry(seq, captured_at, tkt, state, weights, fid, meta, prev_hash, entry_hash)
        _pulse(f"forensic ledger capture seq={seq} hash={entry_hash[:12]}")
        return entry

    def get(self, seq: int) -> Optional[LedgerEntry]:
        with self._lock:
            row = self._conn().execute(
                f"SELECT {_COLUMNS} FROM ledger WHERE seq = ?", [seq]
            ).fetchone()
        return self._row_to_entry(row) if row else None

    def entries(self) -> List[LedgerEntry]:
        with self._lock:
            rows = self._conn().execute(f"SELECT {_COLUMNS} FROM ledger ORDER BY seq").fetchall()
        return [self._row_to_entry(r) for r in rows]

    def latest(self) -> Optional[LedgerEntry]:
        with self._lock:
            row = self._conn().execute(
                f"SELECT {_COLUMNS} FROM ledger ORDER BY seq DESC LIMIT 1"
            ).fetchone()
        return self._row_to_entry(row) if row else None

    def __len__(self) -> int:
        with self._lock:
            return int(self._conn().execute("SELECT count(*) FROM ledger").fetchone()[0])

    def verify(self) -> VerifyResult:
        """Recompute the whole chain; report the first bad seq, if any."""
        with self._lock:
            rows = self._conn().execute(f"SELECT {_COLUMNS} FROM ledger ORDER BY seq").fetchall()
        prev = GENESIS_HASH
        expected_seq = 1
        for n, row in enumerate(rows):
            seq = int(row[0])
            if seq != expected_seq:
                return VerifyResult(False, n, expected_seq, f"sequence gap: expected {expected_seq}, found {seq}")
            if row[7] != prev:
                return VerifyResult(False, n, seq, "prev_hash does not match preceding entry")
            try:
                parsed = [json.loads(row[i]) for i in (2, 3, 4, 5, 6)]
                # Stored text must be exactly the canonical form.
                if any(_dumps(p) != row[i] for p, i in zip(parsed, (2, 3, 4, 5, 6))):
                    return VerifyResult(False, n, seq, "stored field is not canonical")
                ticket, state, weights, fid, meta = parsed
                recomputed = _seal(
                    prev, self._hash_fields(row[1], ticket, state, weights, fid, meta, seq)
                )
            except (ValueError, TypeError):
                return VerifyResult(False, n, seq, "unreadable stored field")
            if recomputed != row[8]:
                return VerifyResult(False, n, seq, "entry_hash mismatch")
            prev = row[8]
            expected_seq += 1
        return VerifyResult(True, len(rows))
