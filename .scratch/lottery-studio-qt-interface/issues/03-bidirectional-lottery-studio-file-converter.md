# 03 — Bidirectional SamLotto Flat File Converter

**What to build:** File conversion routines and database header buttons ("📥 IMPORT SAMLOTTO .TXT" and "📤 EXPORT SAMLOTTO .TXT") that open file selection dialogs and convert drawing data bidirectionally in-process between SamLotto's flat space-delimited format and DuckDB.

**Blocked by:** 02 — DuckDB Editable Model & CRUD Drawings UI

**Status:** ready-for-agent

- [ ] A new utility module is created under `desktop/src/utils/converter.py` containing `parse_samlotto_txt` and `export_duckdb_to_samlotto`.
- [ ] `parse_samlotto_txt` correctly parses SamLotto space-delimited files, mapping line numbers to implicit draw IDs and converting `M/D/YYYY` date styles.
- [ ] `export_duckdb_to_samlotto` queries DuckDB draws, formats date fields to `M/D/YYYY`, zero-pads numbers to 2-digit strings, and writes the output with CRLF endings.
- [ ] "📥 IMPORT SAMLOTTO .TXT" and "📤 EXPORT SAMLOTTO .TXT" buttons are added to the header control panel of `DatabaseTab` with icons.
- [ ] The Import button launches `QFileDialog` for `.txt` files, runs the parser, updates DuckDB draws, triggers a model reload, and pops up a QMessageBox showing the count of records loaded.
- [ ] The Export button launches `QFileDialog` to select a save location, calls `export_duckdb_to_samlotto`, and pops up a confirmation alert upon completion.
