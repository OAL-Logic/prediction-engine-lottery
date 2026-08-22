# 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**What to build:** Renders the application in the Sleek Dark theme (using custom QSS with neon accents) and restructures the main screen with a `QSplitter` dividing the **Pool Builder** (interactive `NumberGrid` where clicking numbers toggles active/red state) and the **Ticket Store** table.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob)

**Status:** ready-for-agent

- [ ] A centralized QSS stylesheet is designed and integrated into `desktop/src/theme/manager.py` with style tokens (dark `#121214` background, active red `#FF3366`, accent cyan `#00F0FF`, success green `#39FF14`).
- [ ] Custom stylesheet definitions are written for QTableWidget, QTabWidget, QScrollBar, QPushButton, and QCheckBox.
- [ ] The main window `ProphetDashboard` is refactored to use a `QSplitter` dividing the Left Rail and Right Rail.
- [ ] The Left Rail is configured with the Pool Builder (NumberGrid widget, generator selection radios, quick-pick menu button).
- [ ] The `NumberGrid` dynamically draws buttons from 1 to the active game's pool size. Clicking toggles the number in/out of the active pool, coloring the button neon red.
- [ ] The Right Rail displays the Ticket Store grid with right-click menu actions (sort, dedupe, print, export).
- [ ] The Setup Dock (bottom of the window) holds tabs for Base Filters and Advanced Filters.
