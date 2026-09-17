---
name: Lottery Engine — Desktop Cockpit
description: A trading-terminal-grade instrument panel for backtested lottery strategy generation and verification.
colors:
  obsidian-black: "#000000"
  matrix-green: "#00ff41"
  matrix-green-hover: "#00e63a"
  matrix-green-pressed: "#00cc33"
  neon-green-dim: "#009c11"
  lead-grey: "#333333"
  panel-black: "#0a0a0a"
  tab-charcoal: "#1a1a1a"
  astro-violet: "#8a2be2"
  signal-red: "#ff3131"
  warning-amber: "#ffea00"
  cyber-cyan: "#00f0ff"
  ball-void: "#1a1a1e"
  ball-void-border: "#222226"
  neon-magenta-red: "#ff3366"
  neon-magenta-red-hover: "#ff5588"
  pure-white: "#ffffff"
typography:
  body:
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
    fontWeight: 400
  label:
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
    fontWeight: 700
  data:
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
    fontSize: "11px"
    fontWeight: 400
  numeric-ball:
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
    fontSize: "10pt"
    fontWeight: 700
rounded:
  xs: "2px"
  sm: "4px"
  pill: "18px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
components:
  button-primary:
    backgroundColor: "{colors.panel-black}"
    textColor: "{colors.matrix-green}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.matrix-green}"
    textColor: "{colors.obsidian-black}"
  button-primary-pressed:
    backgroundColor: "{colors.matrix-green-pressed}"
    textColor: "{colors.obsidian-black}"
  input:
    backgroundColor: "{colors.panel-black}"
    textColor: "{colors.matrix-green}"
    rounded: "{rounded.xs}"
    padding: "4px"
  number-ball:
    backgroundColor: "{colors.ball-void}"
    textColor: "{colors.cyber-cyan}"
    rounded: "{rounded.pill}"
    size: "36px"
    typography: "{typography.numeric-ball}"
  number-ball-selected:
    backgroundColor: "{colors.neon-magenta-red}"
    textColor: "{colors.pure-white}"
    rounded: "{rounded.pill}"
    size: "36px"
    typography: "{typography.numeric-ball}"
---

# Design System: Lottery Engine — Desktop Cockpit

## Overview

**Creative North Star: "The Trading Terminal"**

The Cockpit is an instrument panel for a professional operator making a real decision, not a consumer dashboard. Every surface is flat, dense, and monospaced — Bloomberg-terminal energy applied to lottery draw data: statistical regimes, filter passes, wheeling coverage, and backtested win rates rendered as high-contrast data on obsidian black. Nothing here is decorative; a color or a glow exists to carry a specific piece of state (primary action, dim/inactive, success, warning, error), never to soften the tool into something friendlier than it is.

The canonical theme, **Forensic Neon**, is Matrix Green text and primary actions on true black, with Astro Violet held in reserve as the system's one deliberate second voice. The Cockpit ships four sibling themes (Cyber Synthwave, Astro Emerald, Classic Dark, Sleek Dark Mode) that recolor the same structural tokens — see **Theme Variants** below — but Forensic Neon is the source of truth for this document's values.

This is explicitly not a generic admin/CRUD dashboard. There is no card-grid-with-shadows softness, no rounded-pill nav, no pastel status chips. Density and monospace type are load-bearing to the identity, not an unstyled default.

**Key Characteristics:**
- Flat, bordered panels on true black — zero shadows, zero gradients.
- One typeface everywhere (JetBrains Mono stack); hierarchy comes from weight, size, and case.
- Matrix Green carries both body text and primary actions; Astro Violet is the only other accent, reserved for section titles.
- Outlined ("ghost") controls at rest that invert to a solid fill on hover — restrained by default, precise and legible before interaction.
- A circular number-ball grid (the signature component) as the one place the interface gets tactile.

## Colors

A near-monochrome system: one dominant signal color doing double duty as text and primary action, one reserved second voice, and a standard success/warning/error triad for state.

### Primary
- **Matrix Green** (`#00ff41`): the dominant channel — primary buttons, active tab underline, and default body text all read in this one green. Hover (`#00e63a`) and pressed (`#00cc33`) are the same hue, stepped darker.

### Secondary
- **Astro Violet** (`#8a2be2`): reserved exclusively for `QGroupBox` section titles. The system's only deliberate second color — its rarity is the point.

### Tertiary
- **Neon Green Dim** (`#009c11`): secondary/inactive text — unselected tab labels, muted status lines. Bumped from `#008f11` (4.09:1 on Tab Charcoal) to meet the 4.5:1 body-text contrast floor.

### Neutral
- **Obsidian Black** (`#000000`): the base window/app background.
- **Panel Black** (`#0a0a0a`): the surface color for tab panes, inputs, dropdowns, dialogs — one tonal step above Obsidian Black.
- **Tab Charcoal** (`#1a1a1a`): the next step up — tab bar background, table headers, menu bars.
- **Lead Grey** (`#333333`): the universal 1px border color separating every panel, input, and table cell.

### State
- **Signal Red** (`#ff3131`): error state.
- **Warning Amber** (`#ffea00`): warning state.
- Success reuses Matrix Green — there is no separate success color in Forensic Neon.

### Signature-component colors (see Do's and Don'ts)
- **Cyber Cyan** (`#00f0ff`) on **Ball Void** (`#1a1a1e`, border `#222226`): the number-ball grid's unselected state.
- **Neon Magenta-Red** (`#ff3366`, hover `#ff5588`) on white text: the number-ball grid's selected state.

These four are fixed in code independent of the active theme — see the Ball-Grid Exception under Do's and Don'ts.

### Named Rules
**The Single-Channel Rule.** Matrix Green carries both running text and primary actions — the interface reads as one continuous signal. Astro Violet is switched on only for section/group titles; introducing it anywhere else dilutes the one contrast it's meant to provide.

## Typography

**Body/Label/Data Font:** JetBrains Mono (fallback: Fira Code, Courier New, monospace)

**Character:** One monospaced face for every role in the system — running text, section titles, button labels, table data, and the number-ball grid. Hierarchy is built entirely from weight, size, and case, never from a second typeface.

### Hierarchy
- **Label** (bold, uppercase): button text, tab names, `QGroupBox` titles. Uppercase + bold is the system's primary hierarchy device.
- **Body** (regular): default widget/label text, inherits the platform's base point size — no explicit override in the stylesheet.
- **Data** (regular, 11px): tabular and statistical readouts — analysis summaries, stats tables, verification output.
- **Numeric Ball** (bold, 10pt): the digits inside the number-ball grid.

### Named Rules
**The All-Monospace Rule.** Every text role uses the JetBrains Mono stack. A second typeface anywhere in the Cockpit is a defect, not a variation.

## Layout

Tab-based single-window layout (`QTabWidget`) with one primary tab per workflow stage (Database, Analysis, Filters, Wheeling, Predict, Verification, EV, Telemetry). Within a tab, content is organized into bordered `QGroupBox` sections rather than free-floating cards. Density is high and intentional: 4–8px control padding, 6px grid spacing in the number-ball grid, 12px group-box top margin. No responsive/breakpoint behavior — this is a fixed-DPI-aware desktop window, not a fluid layout.

## Elevation & Depth

Flat by design — no shadows, no gradients, no blur, anywhere in the stylesheet or codebase. Depth is conveyed entirely through a tonal ladder (Obsidian Black → Panel Black → Tab Charcoal) plus a single 1px Lead Grey border between adjacent surfaces.

### Named Rules
**The No-Shadow Rule.** Depth is never simulated with `box-shadow` or glow blur. A panel separates from its background with a 1px border and a tonal step, full stop.

## Shapes

Two radius scales cover the whole system: a tight `2px`–`4px` radius on rectangular controls (buttons, inputs, group boxes, checkboxes, progress bars) that keeps the terminal's hard edge, and a full `18px` (50% of a 36px button) radius exclusively on the number-ball grid, making the balls the one genuinely circular, tactile element in an otherwise rectilinear system.

## Components

### Buttons
- **Shape:** 4px radius, 1px border.
- **Primary (at rest):** Panel Black background, Matrix Green border and text, uppercase bold label, 8px 16px padding.
- **Hover:** inverts to a solid Matrix Green fill with Obsidian Black text — the only fill transition in the system, restrained until it happens.
- **Pressed:** darkens to Matrix Green Pressed (`#00cc33`).
- **Icon convention:** actions that fetch, mutate, or destroy data — and a few high-emphasis generators — lead their uppercase label with a single Unicode emoji glyph (⚡ fetch/run, 📥/📤 import/export, 💾 save, ❌ delete, 🎯/🎡 generate or reduce, 🛡️ send-to-verification, ⚙ auto-calculate). Established on Database, Wheeling, Verification, and the pool-builder toolbar in `main.py`. It is not universal: simple toggles (`HOT`/`COLD`/`CLEAR`/`ALL`), list navigation (`Select All`, `Search`, `Look up`), and some primary CTAs (`GENERATE JUSTIFIED ASSET`, `RETRAIN SWARM`) stay plain uppercase text. One glyph max, no icon font or SVG substitute.

### Inputs / Fields
- **Style:** Panel Black background, Lead Grey 1px border, 2px radius, Matrix Green text, 4px padding.
- Applies uniformly to `QLineEdit`, `QTextEdit`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QDateEdit`.

### Tabs
- **Style:** Tab Charcoal background, Lead Grey border, Neon Green Dim label when inactive.
- **Selected:** Panel Black background, Matrix Green label, 2px Matrix Green bottom border.

### Group Boxes (section containers)
- **Corner:** 4px radius, Lead Grey 1px border, 12px top margin.
- **Title:** Astro Violet, uppercase, bold — the system's one reserved second-color usage.

### Tables
- **Style:** Lead Grey gridlines and border, Tab Charcoal headers, Panel Black body with Tab Charcoal alternating rows.

### Number-Ball Grid (signature component)
36×36px circular (`18px` radius) buttons, JetBrains Mono Bold 10pt digit, zero-padded (`01`, `02`, …). Two states only:
- **Unselected:** Ball Void background (`#1a1a1e`), Cyber Cyan border and text.
- **Selected:** Neon Magenta-Red fill and border, white text.
These colors are fixed in code and do not change with the active theme (see Do's and Don'ts).

## Theme Variants

The same token structure (background / primary / primary-hover / primary-pressed / text / text-dim / border / panel / tab-bg / accent / success / warning / error) is recolored wholesale by `ThemeManager` into four sibling themes. Forensic Neon above is canonical; the others swap the palette without changing any layout, radius, spacing, or component structure:

- **Cyber Synthwave:** Deep Void Indigo background, Neon Hot Pink primary, Cyber Cyan text, Neon Amber accent.
- **Astro Emerald:** Astral Deep Teal background, Aurora Turquoise primary, Cosmic Lime text, Solar Flare Magenta accent.
- **Classic Dark:** conventional Material-style dark theme — `#121212` background, blue primary (`#1976D2`), light grey text. The most conservative variant.
- **Sleek Dark Mode:** near-black background, Cyber Cyan primary, magenta accent (`#FF3366`) — the app's current default at first launch.

## Do's and Don'ts

### Do:
- **Do** keep every surface flat — no `box-shadow`, no gradients. Separate panels with a 1px Lead Grey border and a tonal step (Obsidian Black → Panel Black → Tab Charcoal), never elevation.
- **Do** use uppercase, bold labels for every interactive control (buttons, tab names, group-box titles) — it is the system's primary hierarchy device beyond size.
- **Do** route new or refactored component colors through `ThemeManager`'s token dict (`self.themes[...]`) so components repaint correctly across all 5 themes.
- **Do** reserve Astro Violet for group/section titles only — it is the one deliberate second color against the dominant Matrix Green.

### Don't:
- **Don't** add drop shadows, glow-as-blur, or soft elevation of any kind — this system has none, anywhere, by design.
- **Don't** introduce a second typeface. Every text role uses the JetBrains Mono stack.
- **Don't** hardcode component colors independent of the active theme. **Ball-Grid Exception (flagged, not endorsed):** `NumberGrid.get_ball_style()` and several stat/status labels (`ev.py`, `telemetry.py`, `database.py`, `predict.py`) currently hardcode Forensic-Neon-era hex values (`#00ff41`, `#00F0FF`, `#FF3366`) instead of reading from `ThemeManager`, so they stay visually static across all 5 themes. The same drift has since produced one-off near-duplicates that aren't registered in `ThemeManager` at all — `#ffb300` (`database.py` export button), `#ff3b30` (`database.py` delete-button text, within a point of `signal-red` `#ff3131`), `#b15dff` (`wheeling.py` key-number hover, an unregistered lighter step of Astro Violet), and `filters.py`'s `#1A1A1C`/`#333338` pair (near-duplicates of Panel Black/Lead Grey at slightly shifted values). None of this is a pattern to extend — new work should read from theme tokens, and these call sites should be consolidated onto the registered tokens when touched.
- **Don't** style this as a generic Bootstrap/Material admin dashboard. Density, monospace type, and flat bordered panels are load-bearing to the Trading Terminal identity, not an unstyled default.
