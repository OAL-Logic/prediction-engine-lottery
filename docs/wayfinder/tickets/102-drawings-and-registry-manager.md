---
id: "102"
type: research
status: closed
assignee: antigravity
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-08-11
---

# Drawings and registry manager

## Question

How should the PySide6 Drawings Manager interface with the core DuckDB database to load, insert, modify, and delete draws, and how do we implement robust import/export routines for SamLotto flat `.txt` drawing files?

## Context

- In the original SamLotto Free Edition, drawings are managed via `S12 TDrawingsForm` (supporting Add, Insert, Modify, Delete, Import, Export, and weekday Splitting).
- The Python engine stores draw histories in [lottery.db](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/data/lottery.db) (DuckDB) in a `draws` table containing `lottery_id`, `draw_id`, `draw_date`, and arrays of `numbers` and `bonus`.
- The GUI must provide a high-fidelity editor that binds directly to this database while also supporting flat `.txt` drawings (which use space/tab delimited columns, e.g., `YYYY-MM-DD Num1 Num2 Num3...`) for interoperability.

## What to research

1. **Database Bindings and Grid Model**:
   - Design a PySide6 data model (subclassing `QAbstractTableModel`) that queries DuckDB efficiently, handles pagination/sorting, and displays results in a high-density table.
2. **CRUD Dialogs Design**:
   - Specify the layout and validation rules for the Add/Insert/Modify drawing dialogs (ensuring correct count, ranges, dates, and handling of bonus numbers).
3. **Import/Export Format Specification**:
   - Define the exact regex or parser needed to read SamLotto `.txt` drawings.
   - Address issues like date format variations (e.g. `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`) and draw order parsing.
4. **Weekday Splitter Logic**:
   - Replicate SamLotto's "Split Drawings" feature, allowing the user to select specific weekdays and filter the active drawing history inside the engine, either dynamically or by exporting a subset.

## Acceptance criteria

- [x] A PySide6 table model design for DuckDB draws is specified.
- [x] Text format specifications for importing and exporting SamLotto `.txt` drawings are documented.
- [x] Validation and layout designs for the Add/Insert/Modify dialogs are outlined.
- [x] Output is a markdown design spec linked from this ticket.

## Resolution

Resolved on 2026-08-11. See [MDR-102: Drawings and Registry Manager Design](../decisions/102-drawings-and-registry-manager-decision.md) for full design and details.

### Key Decisions
- **Model Bindings**: Designed `DuckDBDrawsTableModel` subclassing `QAbstractTableModel` for inline CRUD and direct binding to DuckDB records.
- **Interoperability**: Documented flat file parser specifications for SamLotto's space-delimited text drawing format (handling US date style and sorted integers).
- **CRUD Operations**: Mapped out dialog layouts and validators for CRUD operations on table cells.
- **Weekday Splitting**: Integrated weekday split selection queries.
