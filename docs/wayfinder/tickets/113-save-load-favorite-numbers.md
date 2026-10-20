---
id: "113"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# Save and Load Your Own Favorite Number

## Question

`extracted_manual/lotto_chm/Creating and Edit Your Lottery Tickets/Save and Load Your Own Favorite Number.htm` names this as its own Lottery Studio capability: save the current number selection to a file, reload it later. Distinct from `DatabaseTab`'s Lottery Studio `.txt` import/export (#03/#102, which round-trips *drawing history*, not a manually-picked pool) and from the Ticket Store's CSV/TXT export (#110, which exports *generated tickets*, not the raw Pool Builder selection).

## Resolution

Two buttons in `ProphetDashboard`'s Pool Builder rail (`desktop/src/main.py`), next to the existing Quick Selections menu: "💾 SAVE FAVORITES" / "📂 LOAD FAVORITES". Format is a small JSON file (`{"lottery": ..., "numbers": [...]}`) rather than matching any Lottery Studio binary format — there's no interop requirement here the way there is for drawing history, since this is a new, this-app-only save file, not something read by real Lottery Studio installs.

Load path validates the file shape (rejects anything where `numbers` isn't a list), warns (with an override option) if the file was saved for a different game than the one currently active, and reuses `NumberGrid.select_numbers()` for applying the loaded set — which already clamps out-of-range numbers, so no separate bounds-checking needed here.

**Verified:** `test_save_and_load_favorite_numbers_round_trip` (`tests/test_desktop_integrity.py`) saves a real selection, clears the grid, reloads from the saved file, and asserts the restored selection is byte-for-byte the original. `test_load_favorite_numbers_rejects_malformed_file` checks the validation path. Full desktop suite (32 tests) passes.
