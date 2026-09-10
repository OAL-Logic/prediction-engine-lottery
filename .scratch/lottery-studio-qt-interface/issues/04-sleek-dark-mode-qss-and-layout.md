# 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**What to build:** Renders the application in the Sleek Dark theme (using custom QSS with neon accents) and restructures the main screen with a `QSplitter` dividing the **Pool Builder** (interactive `NumberGrid` where clicking numbers toggles active/red state) and the **Ticket Store** table.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob)

**Status:** resolved

- [x] A centralized QSS stylesheet is designed and integrated into `desktop/src/theme/manager.py` with style tokens (dark `#121214` background, active red `#FF3366`, accent cyan `#00F0FF`, success green `#39FF14`).
- [x] Custom stylesheet definitions are written for QTableWidget, QTabWidget, QScrollBar, QPushButton, and QCheckBox.
- [x] The main window `ProphetDashboard` is refactored to use a `QSplitter` dividing the Left Rail and Right Rail.
- [x] The Left Rail is configured with the Pool Builder (NumberGrid widget, generator selection radios, quick-pick menu button).
- [x] The `NumberGrid` dynamically draws buttons from 1 to the active game's pool size. Clicking toggles the number in/out of the active pool, coloring the button neon red.
- [x] The Right Rail displays the Ticket Store grid with right-click menu actions (sort, dedupe, print, export).
- [x] The Setup Dock (bottom of the window) holds tabs for Base Filters and Advanced Filters.

## Comments

### Refactoring Summary
1. **Centralized QSS Customizations**: Updated [`desktop/src/theme/manager.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/theme/manager.py) to style scrollbars (`QScrollBar`), checkboxes (`QCheckBox`), and tables (`QTableWidget` / `QTableView`) matching the visual tokens of the user's selected "Sleek Dark Mode" theme (cyber cyan `#00F0FF`, active red `#FF3366`, radioactive green `#39FF14`, background `#121214`).
2. **Consolidated Cockpit Layout**: Refactored `ProphetDashboard` in [`desktop/src/main.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/main.py) to use a vertical `QSplitter` holding the horizontal `QSplitter` workspace (Pool Builder on the left, Ticket Store on the right) and the Harmony Gate Setup Dock at the bottom.
3. **Interactive NumberGrid Widget**: Created a responsive [`desktop/src/widgets/number_grid.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/widgets/number_grid.py) that renders number buttons based on the selected game rules, mapping active numbers to selected/active neon red states.
4. **Ticket Store Toolbar & Context Actions**: Added quick selections (HOT/COLD/ODD/EVEN/PRIMES) to the Left Rail, connected suggestion results directly to the Ticket Store table on the Right Rail, and integrated a right-click context menu (Sort, Deduplicate, Export, Print) on the table.
5. **Modeless View Dialogs**: Added a "View" menu to the menu bar allowing the user to view the draws database, statistics cockpit, telemetry logs, and expected value panel in independent, modeless floating windows, preserving all existing Qt slot communication and background thread updates.
6. **Integrity Tests Calibration**: Updated the headless layout assertions in `tests/test_desktop_integrity.py` to target the new layout architecture splitters and setup tabs.

