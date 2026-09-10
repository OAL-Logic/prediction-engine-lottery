# 02 — DuckDB Editable Model & CRUD Drawings UI

**What to build:** An inline editable drawings table grid in the Draws Database tab that binds `QTableView` directly to DuckDB draws, enabling direct spreadsheet-like cell editing and CRUD buttons (Insert, Update, Delete) that update DuckDB and notify other tabs of changes via signals.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob)

**Status:** resolved

- [x] The custom `DuckDBDrawsTableModel` (derived from `QAbstractTableModel`) is implemented with CRUD helper methods (`load_data`, `insert_draw`, `remove_draw`).
- [x] `flags()` is overridden to mark Date, Main Numbers, and Bonus Numbers columns as editable inline, while keeping Draw ID as read-only.
- [x] `setData()` is overridden to parse, validate dates and list formats, upsert modifications to DuckDB via `storage.save_draws()`, and emit both `dataChanged` and `data_mutated` signals.
- [x] The manual draw entry form fields (ID, Date, Balls, Bonus) are bound to the new table model, populated with valid default range checks.
- [x] The "SAVE / UPDATE DRAW" button triggers `insert_draw` / `setData` on the model with a success status message.
- [x] The "DELETE SELECTED DRAW" button triggers `remove_draw` on the model with a warning confirmation dialog.

## Comments

### Implementation Details
1. **DuckDB Draws Table Model**: Created the custom `DuckDBDrawsTableModel` supporting inline updates via `setData()` and spreadsheet-like cell editing. The model handles background writes to DuckDB using `storage.save_draws()`.
2. **Inline Edit Validations**: Added validation inside `setData()` to enforce correct date strings, and list format/boundaries based on the active lottery's `DrawRules` (e.g. enforcing exactly 15 balls in 1-25 range for Lotofácil).
3. **Spreadsheet CRUD Actions**: Hooked the manual forms up to `model.insert_draw()` and `model.remove_draw()`, keeping the view fully synchronized.
4. **Data Sync Signals**: Connected the model's `data_mutated` signal to the database tab's `database_changed` broadcaster, instantly refreshing the analysis and verification tabs on any CRUD/inline changes.
5. **Unit Testing**: Added isolated unit tests `test_duckdb_draws_table_model_crud` in `tests/test_desktop_logic.py` that mock the DB cache files using a temporary sqlite database file to ensure test isolation.

