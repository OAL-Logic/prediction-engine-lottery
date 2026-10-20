---
id: "108"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# Optimization/wheeling port to the Ticket Store, and real ticket printing

## Question

Two related fog items on the map:

1. **Optimization and wheeling port**: map the abbreviated-wheel / ticket-store reduction algorithms (F10-F12 in `docs/research/Lottery Studio-feature-map.md`'s WRG Combinatorial Layer) to the GUI's Ticket Store menu actions.
2. **Export & Print formatting (S40)**: `ProphetDashboard.print_tickets()` (`desktop/src/main.py`) was a pure stub — `QMessageBox.information(..., "Successfully queued N tickets to system spooler.")` with no printer ever touched.

## Resolution

**Reduction (F10-F12 → Ticket Store):** `engine/modules/wheels_wrg.py`'s `WheelingEngine.reduce_tickets()` (greedy t-if-m set-cover) already existed but had zero callers anywhere in the codebase — `WheelingTab` only ever used `WheelingEngine.get_gap_matrix()` for its heatmap. Added `TicketStoreReductionJob` (`desktop/src/telemetry/manager.py`), a thin QThread wrapper — no set-cover logic reimplemented — that:
- Parses the Ticket Store's current rows (same `" ".join(f"{n:02d}" ...)` / `int(x) for x in text.split()` convention `run_pruning()`/`handle_wheeling_tickets_shared()` already use).
- Remaps ticket numbers to the dense `1..pool_size` range `WheelingEngine` expects (same convention `WheelingWorker.run()` uses for `get_gap_matrix()`), since `reduce_tickets()` bit-shifts by the raw number value.
- **Guards the combinatorial universe**: `reduce_tickets()`'s inner loop is plain Python over `C(pool_size, m)` target subsets with no interruption support, so a large pool would hang the UI thread's *job* (not the UI itself, since it's already backgrounded, but with no progress and no way to cancel) for an impractical amount of time. Refuses upfront (clear error, no attempt) above `C(pool_size, m) = 50,000`.

Wired into `ProphetDashboard` as both a Ticket Store toolbar button ("🎯 REDUCE (WRG)") and a context-menu action ("🎯 Reduce (WRG Guarantee)..."), prompting for `m`/`t` via `QInputDialog` (defaulting to the active game's pick-count and pick-count-1), then replacing the table contents with the kept subset — same replace-in-place pattern `run_pruning()` already uses.

**Print (S40, print half):** Replaced the stub with a real `QPrinter` + `QPrintDialog` flow — renders the Ticket Store to an HTML table via `QTextDocument.setHtml()` / `.print_()`, standard PySide6 `QtPrintSupport` (confirmed importable in this project's venv). Export-to-TXT was already real (`export_tickets()`); custom export *formats* beyond `.txt` (the other half of S40) are untouched, still fog.

**Verified:** `test_ticket_store_reduction_job` builds the full C(5,3)=10-ticket wheel over a 5-number pool, reduces under a "2 if 3" guarantee, and checks by brute force that all 10 possible 3-number draws still have >=2 overlap with some kept ticket (10 → 2 tickets in practice). `test_ticket_store_reduction_job_rejects_oversized_universe` confirms the `C(30,15)` case fails fast with a clear message instead of hanging. Both added to `tests/test_desktop_logic.py`. Full `test_desktop_integrity.py` (instantiates `ProphetDashboard` itself, exercising the new imports/menu wiring) still passes (11/11).

## Not done here (separately tracked / still fog)

- **Custom export formats** (CSV, etc.) beyond the existing `.txt` export — the other half of S40.
- **Drawings Trend manual predictor (E5)** — untouched.
