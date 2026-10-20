---
id: "110"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# Custom export formats (S40, export half)

## Question

Last item on the map's fog list: `export_tickets()` (`desktop/src/main.py`) only ever wrote `.txt`. S40 (export/print formatting) wanted "custom export formatting options" beyond the Lottery Studio-compatible flat file.

## Resolution

Extended `export_tickets()`'s save dialog with a second filter, "CSV Files (*.csv)". CSV path writes `Index,Numbers,Score` via the stdlib `csv` module (no hand-rolled escaping) instead of the bare combination string the `.txt` path writes — same Ticket Store rows, machine-readable with a header for spreadsheet import. Branches on the chosen file's extension (falling back to the dialog's selected filter name), defaulting to the pre-existing `.txt` behavior unchanged.

**Verified:** `test_export_tickets_txt` / `test_export_tickets_csv` (`tests/test_desktop_logic.py`) monkeypatch `QFileDialog.getSaveFileName` and `QMessageBox.information` (both modal — would otherwise hang a headless run) and assert exact file contents for both formats.

## Map status

This was the last open item on `lottery-studio-qt-interface-map.md`'s "Not yet specified" list. The map has no remaining fog as of this ticket.
