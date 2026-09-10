---
id: "103"
type: prototype
status: closed
assignee: antigravity
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-08-11
---

# Sleek dark theme and layout

## Question

What are the QSS style rules, layout configurations, and custom widget structures required to implement the Sleek Dark Mode theme and build the main workspace layout (Pool Builder left, Ticket Store right, Setup Dock bottom)?

## Context

- The user selected the "Sleek Dark Mode" theme aesthetic (custom QSS, neon accents, semi-transparent overlays, and modern typography).
- The core workspace layout consists of:
  - **Left Rail**: Pool Builder (high-contrast interactive `NumberGrid` where clicking numbers toggles them into the active pool and colors them red; generator selection controls; quick-pick menus).
  - **Right Rail**: Ticket Store (active grid of lines, row counts, and context menus for sorting, duplicates, exporting, and printing).
  - **Bottom Dock**: Setup panel containing tabs for base and advanced filters, logical conditions, and the execute button.
- The existing [theme manager](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/theme/manager.py) and tabs need to be updated or refactored to support this design system.

## What to decide

1. **QSS Style Guide**:
   - Establish the primary, secondary, background, border, and text colors (using Hex/RGB) for the sleek dark mode (e.g. background `#121214`, active red `#FF3366`, accent cyan `#00F0FF`, success green `#39FF14`).
   - Define custom styling for QTableWidget, QTabWidget, QScrollBar, QPushButton, and QCheckBox.
2. **Core Layout Architecture**:
   - Define the split layout using `QSplitter` to allow users to resize the Pool Builder and Ticket Store panels.
   - Design the responsive grid behavior of the `NumberGrid` so buttons wrap nicely as the window resizes.
3. **NumberGrid Interactive States**:
   - Specify styles and behaviors for grid states: default (unselected), hover (subtle glow), active (neon red), and disabled (out-of-range for games like Lotofácil vs. Powerball).
4. **Draft layout mock**:
   - Recreate the main workspace using PySide6 code stubs or layouts that display the styled split view.

## Acceptance criteria

- [x] A design stylesheet (QSS) with color tokens is documented.
- [x] A layout hierarchy (widgets and layouts) is specified.
- [x] Responsive resizing behavior is outlined.
- [x] Output is a markdown design/style record linked from this ticket.

## Resolution

Resolved on 2026-08-22. See [MDR-103: Sleek Dark Theme and Layout Design](../decisions/103-sleek-dark-theme-and-layout-decision.md) for full design and details.

### Key Decisions
- **Sleek Dark Mode theme**: Configured colors (background `#121214`, active red `#FF3366`, accent cyan `#00F0FF`, success green `#39FF14`) in `ThemeManager` (`desktop/src/theme/manager.py`).
- **Nested Split-Pane Layout**: Standardized on an outer vertical `QSplitter` dividing the upper workspace and the bottom Setup Dock, with an inner horizontal `QSplitter` partitioning the `PoolBuilder` (left) and `TicketStore` (right).
- **Interactive NumberGrid States**: Standardized on cyan border-only for unselected balls and active neon red (`#FF3366`) solid fill for selected pool numbers.
- **Runnable Prototype**: Created a standalone prototype at `desktop/src/prototype_layout.py` mapping out all controls, layouts, responsive grids, and stylesheets.
