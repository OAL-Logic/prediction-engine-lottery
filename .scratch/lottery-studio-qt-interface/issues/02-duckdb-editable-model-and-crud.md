# 02 — DuckDB Editable Model & CRUD Drawings UI

**What to build:** An inline editable drawings table grid in the Draws Database tab that binds `QTableView` directly to DuckDB draws, enabling direct spreadsheet-like cell editing and CRUD buttons (Insert, Update, Delete) that update DuckDB and notify other tabs of changes via signals.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob)

**Status:** ready-for-agent

- [ ] The custom `DuckDBDrawsTableModel` (derived from `QAbstractTableModel`) is implemented with CRUD helper methods (`load_data`, `insert_draw`, `remove_draw`).
- [ ] `flags()` is overridden to mark Date, Main Numbers, and Bonus Numbers columns as editable inline, while keeping Draw ID as read-only.
- [ ] `setData()` is overridden to parse, validate dates and list formats, upsert modifications to DuckDB via `storage.save_draws()`, and emit both `dataChanged` and `data_mutated` signals.
- [ ] The manual draw entry form fields (ID, Date, Balls, Bonus) are bound to the new table model, populated with valid default range checks.
- [ ] The "SAVE / UPDATE DRAW" button triggers `insert_draw` / `setData` on the model with a success status message.
- [ ] The "DELETE SELECTED DRAW" button triggers `remove_draw` on the model with a warning confirmation dialog.
