# 03 — Bidirectional Lottery Studio Flat File Converter

**What to build:** File conversion routines and database header buttons ("📥 IMPORT Lottery Studio .TXT" and "📤 EXPORT Lottery Studio .TXT") that open file selection dialogs and convert drawing data bidirectionally in-process between Lottery Studio's flat space-delimited format and DuckDB.

**Blocked by:** 02 — DuckDB Editable Model & CRUD Drawings UI

**Status:** resolved

- [x] A new utility module is created under `desktop/src/utils/converter.py` containing `parse_studio_txt` and `export_duckdb_to_studio`.
- [x] `parse_studio_txt` correctly parses Lottery Studio space-delimited files, mapping line numbers to implicit draw IDs and converting `M/D/YYYY` date styles.
- [x] `export_duckdb_to_studio` queries DuckDB draws, formats date fields to `M/D/YYYY`, zero-pads numbers to 2-digit strings, and writes the output with CRLF endings.
- [x] "📥 IMPORT Lottery Studio .TXT" and "📤 EXPORT Lottery Studio .TXT" buttons are added to the header control panel of `DatabaseTab` with icons.
- [x] The Import button launches `QFileDialog` for `.txt` files, runs the parser, updates DuckDB draws, triggers a model reload, and pops up a QMessageBox showing the count of records loaded.
- [x] The Export button launches `QFileDialog` to select a save location, calls `export_duckdb_to_studio`, and pops up a confirmation alert upon completion.

## Comments

### Resolution Summary
1. **Converter Module**: Created [`desktop/src/utils/converter.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/utils/converter.py) with `parse_studio_txt` and `export_duckdb_to_studio`.
2. **Space-Delimited Conversions**: Implemented `parse_studio_txt` to map file line numbers to implicit 1-based `draw_id` keys, parse `M/D/YYYY` date styles, and split numbers into main/bonus categories. Implemented `export_duckdb_to_studio` to zero-pad numbers, use `M/D/YYYY` formatting, and output with CRLF endings.
3. **Database Tab Integration**: Added action buttons "📥 IMPORT Lottery Studio .TXT" and "📤 EXPORT Lottery Studio .TXT" to the header control panel of the draws database tab, connecting them to `QFileDialog` file selection windows and the new conversion backend.
4. **Validation Test**: Added comprehensive unit test `test_Lottery Studio_bidirectional_converter` to `tests/test_desktop_logic.py`, validating both directions under isolated SQLite/DuckDB test configurations.

