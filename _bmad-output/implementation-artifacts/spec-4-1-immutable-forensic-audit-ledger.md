---
title: 'Story 4.1: Immutable Forensic Audit Ledger'
type: 'feature'
created: '2026-11-09'
status: 'done'
baseline_revision: '7ecd52173e686fad0f0f75557f5b39bd2ec6d6da'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
warnings: []
deferred:
  - summary: >-
      Tail truncation or a fully re-sealed chain is not detectable by verify() alone, and nothing is wired to call capture() yet.
    evidence: |-
      The hash chain is unkeyed SHA-256 on a local DuckDB file; deleting the last rows leaves a valid chain. Documented in the module docstring and pinned by a test. Needs an external anchor of latest().entry_hash (or an HMAC key), and a Capture call site in ticket generation.
    location: >-
      engine/modules/ledger.py ForensicLedger.verify
    severity: medium (design limit)
---

<intent-contract>

## Intent

**Problem:** A generated ticket ("Justified Number") has no durable, tamper-evident record of the geodesic state, agent weights and QPU fidelity that justified it, so it cannot be defended or replayed later (FR12, FR18).

**Approach:** Add `engine/modules/ledger.py` with a `ForensicLedger` backed by its own DuckDB file. `capture()` appends one entry holding the full geodesic state-vector, agentic weights and QPU fidelity, sealed by a SHA-256 content hash chained to the previous entry. The API exposes no update/delete; `verify()` recomputes the chain and reports any mutation.

## Boundaries & Constraints

**Always:** Append-only API (`capture`, `get`, `entries`, `latest`, `verify`, `__len__`). Entry fields: `seq`, `captured_at` (UTC ISO), `ticket` (ints), `state_vector` (finite floats), `agent_weights` (name -> finite float), `qpu_fidelity` (float in [0,1]), `metadata` (JSON dict), `prev_hash`, `entry_hash`. `entry_hash = sha256(prev_hash + canonical JSON of the other fields)`; the first `prev_hash` is 64 zeros. Floats are stored losslessly (JSON text) so replay is bit-exact. Writes are serialized by a lock and the sequence number is assigned inside one transaction. Default DB path `data/forensic_ledger.duckdb`; path injectable. Invalid input raises `LedgerError` before anything is written. Telemetry pulse on capture must never abort the write.

**Never:** No update/delete/truncate methods, no writes to `lottery.db`, no changes to `JsonlLedger`/`HibernationMonitor`, the Go gateway, frontend or MANIFOLD_STATE protocol, no new dependencies, no replay logic (Story 4.2). No writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Capture | valid ticket, state vector, weights, fidelity 0.93 | entry with seq 1, hash chained to genesis | — |
| Round trip | capture then `get(seq)` | identical fields, floats bit-exact | Unknown seq returns None |
| Chain | two captures | entry 2 `prev_hash` == entry 1 `entry_hash` | — |
| Persistence | close, reopen same path | entries and chain intact, next seq continues | — |
| Tamper | row altered via raw SQL | `verify()` returns `ok=False` naming the first bad seq | — |
| Deleted row | middle row removed via raw SQL | `verify()` returns `ok=False` | — |
| Bad input | NaN/inf in state or weights, fidelity outside [0,1], empty ticket | `LedgerError`, ledger length unchanged | — |
| Concurrency | many threads capturing | unique contiguous seq, `verify()` ok | — |

</intent-contract>

## Code Map

- `engine/modules/storage.py` -- DuckDB usage pattern (`duckdb.connect`, lock); read-only reference.
- `engine/swarm/hibernation.py` -- `JsonlLedger` sink and lazy `_pulse` helper; style reference, untouched.
- `engine/modules/telemetry.py` -- `pulse(message, level)`.
- `engine/_paths.py` -- `PROJECT_ROOT` for the default `data/` path.
- `tests/test_swarm_hibernation.py` -- pytest style; use `.venv/bin/python -m pytest`.

## Tasks & Acceptance

**Execution:**
- `engine/modules/ledger.py` -- `LedgerError`, `LedgerEntry`, `VerifyResult`, `ForensicLedger` -- AC 4.1.1, 4.1.2
- `tests/test_forensic_ledger.py` -- cover every matrix row using `tmp_path` DB files

**Acceptance Criteria:**
- Given a generated ticket vector, when `capture` is called, then the entry stores the complete state-vector, agentic weights and QPU fidelity.
- Given a stored entry, when any persisted field is changed or a row removed outside the API, then `verify()` reports the ledger as not intact.

## Spec Change Log

## Review Triage Log

### 2026-11-09 — Review pass
- verdicts: 29 findings — high 0, medium 3, low 25, false 1, maybe-false 0 (intent-alignment layer is descriptive; its divergences restate rows below)
- findings:
  - `[medium]` `[patch]` Gap/Blind: verify() branches (captured_at, ticket, canonical, unreadable, prev_hash, sequence gap) untested — parametrized raw-SQL tamper tests added with reason and first_bad_seq asserted
  - `[medium]` `[patch]` Gap/Blind/Edge: capture validation branches (bool/float ticket, metadata, weights type) untested — cases added
  - `[medium]` `[patch]` Gap: rollback path and pulse untested — rollback and pulse tests added
  - `[low]` `[patch]` Edge/Blind: get/entries/latest/len/verify after close raise AttributeError — now LedgerError via `_conn()`; test added
  - `[low]` `[patch]` Edge: huge int state value raises OverflowError — mapped to LedgerError; test added
  - `[low]` `[defer]` Blind/Edge/Intent: tail truncation, unkeyed seal, no Capture call site — recorded in deferred
  - `[false]` `[reject]` Edge: metadata key collision makes verify flag a legit entry — mixed int/str keys fail sort_keys and raise LedgerError before write; test added
  - `[low]` `[reject]` Blind/Edge: multi-process or multi-instance writers, DuckDB lock errors, retry — single-process API by design
  - `[low]` `[reject]` Blind/Edge: captured_at not monotonic or injectable — wall clock under lock-free read is negligible
  - `[low]` `[reject]` Blind/Edge: RecursionError and non-sequence/generator inputs — caller-controlled
  - `[low]` `[reject]` Blind: no schema version in hash, weights not summing to 1, dimension checks — outside spec
  - `[low]` `[reject]` Blind: pulse swallows errors, entries() memory, no CHECKPOINT/export, file mode, int-to-float coercion — negligible or documented
  - `[low]` `[reject]` Blind/Edge: schema mismatch on existing table, rollback on KeyboardInterrupt, pathological JSON in verify — local trusted file

## Design Notes

DuckDB has no triggers or row-level permissions, so "mathematically immutable" is enforced as tamper-evidence: an exposed API with no mutators plus a hash chain that `verify()` can check at any time.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_forensic_ledger.py -q` -- expected: all pass

## Auto Run Result

Status: done

**Summary:** Added `ForensicLedger`, an append-only, SHA-256 hash-chained DuckDB ledger. `capture()` stores the ticket, full state-vector, agent weights, QPU fidelity and metadata; `verify()` detects mutation, row removal and reordering. No operator actions are owed.

**Files changed:**
- `engine/modules/ledger.py` — `ForensicLedger`, `LedgerEntry`, `VerifyResult`, `LedgerError`
- `tests/test_forensic_ledger.py` — 36 tests covering every matrix row plus tamper, validation, closed-ledger, rollback and pulse cases
- `_bmad-output/implementation-artifacts/spec-4-1-immutable-forensic-audit-ledger.md` — this spec

**Review:** patches applied 5 (3 medium, 2 low); deferred 1; rejected 22 (incl. 1 false), reasons in the triage log.

**Follow-up review recommended:** false (no high; 3 medium patched, all test additions plus small guards).

**Verification:** `.venv/bin/python -m pytest tests/test_forensic_ledger.py -q` — 36 passed.

**Residual risks:** immutability is tamper-evidence, not prevention; tail truncation needs an external anchor; nothing yet calls `capture()` from ticket generation.
