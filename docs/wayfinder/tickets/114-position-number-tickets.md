---
id: "114"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# Creating a Position Number Tickets

## Question

Lottery Studio's Build Tickets screen has three tabs — Standard, Position, Smart (`extracted_manual/.../Creating a Positon Number Tickets.htm`, screenshot `Pic/position.jpg`). "Standard"/"Smart" map to WheelingTab's existing pool-based generation (Full/Key wheels, Abbreviated ≈ Smart). "Position" — independently specify candidate numbers for each ticket position, then generate every valid combination — had no equivalent anywhere.

## Resolution

New `desktop/src/widgets/position_tickets_dialog.py`, launched from a new button in `WheelingTab` rather than folded into its existing pool-grid UI, since the input shape is fundamentally different (K independent candidate lists, one per position, vs. one shared pool + optional keys):

- `PositionTicketsDialog` — one row per ticket position (`rules.pick_count` rows), each a free-text comma-separated candidate list.
- `PositionTicketsJob` — Cartesian product of the K lists, keeping only combinations where all K picks are distinct, sorted into the final ticket (position order is a *selection*-time organizing device here, matching the manual's own screenshot — Position 6's candidates were smaller numbers than Position 1's — not a constraint on the stored, always-sorted ticket), deduplicated (different position-assignments can land on the same final set). Guarded by a `MAX_POSITION_COMBINATIONS = 200,000` safety cap on the raw (pre-filter) product size, the same defensive pattern #108's `TicketStoreReductionJob` uses for its own combinatorial universe.

`WheelingTab.launch_position_tickets_dialog()` re-emits the dialog's results through `WheelingTab`'s own existing `tickets_generated` signal rather than wiring a second path into `ProphetDashboard` — `main.py` already connects that signal to the Ticket Store and Verification Desk, so no `main.py` changes were needed at all.

**Verified:** `test_position_tickets_job_combinatorics` hand-computes the expected output for a tiny 3-position case ({1,2}×{2,3}×{3,4} → 8 raw entries → 4 after dropping repeated-number entries and deduplicating) and asserts the job matches exactly — not just "produced some tickets." `test_position_tickets_job_safety_cap`, `test_position_tickets_dialog_matches_pick_count` (row count tracks the active game's real `pick_count`, e.g. 15 for Lotofácil), and `test_wheeling_tab_position_tickets_reemits_own_signal` (confirms the re-emit wiring specifically, with `PositionTicketsDialog.exec()` stubbed so the test doesn't block on a real modal loop) round it out. Full desktop suite (36 tests) passes.
