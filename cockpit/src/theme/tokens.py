"""
Design Tokens System (pyqt6-ui-designer)
========================================
Canonical design tokens enforcing strict enterprise guidelines:
- 4px base spatial grid (multiples of 4 only)
- Scaled border radii
- Monospace and UI typography standards
- Multi-theme color palettes (Light & Dark variants)
"""

from typing import Dict, Any

# =============================================================================
# 1. SPACING TOKENS (4px Base Grid — Multiples of 4 only)
# =============================================================================
SPACING_UNIT: int = 4
SPACING_XS: int = 4                    # Tight gaps, icon padding
SPACING_SM: int = 8                    # Button vertical padding, small gaps
SPACING_MD: int = 16                   # Card padding, button horizontal padding
SPACING_LG: int = 24                   # Section separators, panel boundaries
SPACING_XL: int = 32                   # Large hero headers, workspace margins
SPACING_CONTAINER_MARGIN: int = 24     # Main content area margin
SPACING_GUTTER: int = 16               # Multi-column grid gutters

# =============================================================================
# 2. BORDER RADIUS TOKENS
# =============================================================================
RADIUS_NONE: int = 0
RADIUS_SM: int = 4                     # Badges, small chips, micro buttons
RADIUS_DEFAULT: int = 6                # Standard buttons, text inputs, spinboxes
RADIUS_MD: int = 8                     # Cards, dropdown menus, dialog containers
RADIUS_LG: int = 12                    # Major perspectives, elevated panels
RADIUS_FULL: int = 9999                # Circular pills, status dots, lottery balls

# =============================================================================
# 3. TYPOGRAPHY TOKENS
# =============================================================================
FONT_HEADING: str = "Hanken Grotesk"
FONT_BODY: str = "Inter"
FONT_MONO: str = "JetBrains Mono"

TYPO_HEADLINE_LG = (24, 700, 32, -0.01) # Page titles, perspective headers
TYPO_HEADLINE_MD = (20, 600, 28, -0.01) # Section headers, card titles
TYPO_HEADLINE_SM = (16, 600, 24,  0.00) # Sub-section headers, dock titles
TYPO_BODY_LG     = (15, 400, 22,  0.00) # Lead emphasis body text
TYPO_BODY_MD     = (14, 400, 20,  0.00) # Standard body, menu items
TYPO_BODY_SM     = (13, 400, 18,  0.00) # Dense tables, secondary labels
TYPO_LABEL_MD    = (12, 600, 16, +0.05) # ALL-CAPS column headers, buttons
TYPO_LABEL_SM    = (11, 500, 14,  0.00) # Micro status chips, timestamps

# =============================================================================
# 4. PALETTE PRESETS (Light & Dark Variants)
# =============================================================================
THEME_PALETTES: Dict[str, Dict[str, str]] = {
    "Trading Terminal (Default)": {
        "is_dark": "true",
        "bg_root": "#0a0d14",          # Deep obsidian canvas
        "bg_surface": "#101522",       # Primary card panel surface
        "bg_card": "#151c2e",          # Elevated interactive card
        "bg_card_hover": "#1c263d",    # Hover card surface
        "bg_input": "#0c101a",         # Deep recessed inputs/tables
        "border": "#20293d",           # Refined card boundary
        "border_light": "#2d3a54",     # Highlight border
        "border_focus": "#00f0ff",     # Cyber Cyan focus ring
        "text_main": "#f1f5f9",        # Crisp high-contrast off-white
        "text_muted": "#8b9bb4",       # Accessible slate grey
        "text_dim": "#576782",         # Subdued label text
        "primary": "#00f0ff",          # Cyber Cyan brand primary
        "primary_hover": "#38f5ff",
        "primary_pressed": "#00cbd9",
        "matrix_green": "#10b981",     # Emerald green (GO, Pass, Live)
        "matrix_green_glow": "#00ff88",
        "warning_amber": "#f59e0b",    # Amber gold (Warning, Overdue)
        "signal_red": "#ef4444",       # Coral red (NO-GO, Eliminated)
        "accent_purple": "#a855f7",    # Esoteric purple
        "dock_title_bg": "#0e131f",
        "dock_title_active": "#161e30",
    },
    "Modern Enterprise Light": {
        "is_dark": "false",
        "bg_root": "#faf9ff",          # Soft light base canvas
        "bg_surface": "#f1f3ff",       # Surface low
        "bg_card": "#ffffff",          # Surface lowest (cards, white)
        "bg_card_hover": "#e9edff",    # Surface hover
        "bg_input": "#ffffff",         # Clean input background
        "border": "#c3c6d6",           # Subtle outline variant
        "border_light": "#e1e8ff",     # Light separator
        "border_focus": "#0052cc",     # Corporate Blue focus
        "text_main": "#051a3e",        # On-surface primary text
        "text_muted": "#434654",       # On-surface variant (muted)
        "text_dim": "#737685",         # Outline muted text
        "primary": "#0052cc",          # Corporate Blue brand
        "primary_hover": "#1e6fff",
        "primary_pressed": "#003d99",
        "matrix_green": "#00875a",     # Executive forest green
        "matrix_green_glow": "#00b074",
        "warning_amber": "#d97706",    # Warm gold
        "signal_red": "#de350b",       # Direct crimson red
        "accent_purple": "#6554c0",    # Deep indigo accent
        "dock_title_bg": "#e6eaf5",
        "dock_title_active": "#dbe2f5",
    },
    "Forensic Neon": {
        "is_dark": "true",
        "bg_root": "#050805",
        "bg_surface": "#0a120a",
        "bg_card": "#0f1c0f",
        "bg_card_hover": "#162816",
        "bg_input": "#060d06",
        "border": "#1a381a",
        "border_light": "#254d25",
        "border_focus": "#00ff66",
        "text_main": "#e6ffe6",
        "text_muted": "#7fa67f",
        "text_dim": "#486648",
        "primary": "#00ff66",
        "primary_hover": "#33ff85",
        "primary_pressed": "#00cc52",
        "matrix_green": "#00ff66",
        "matrix_green_glow": "#66ff99",
        "warning_amber": "#ffcc00",
        "signal_red": "#ff3333",
        "accent_purple": "#cc33ff",
        "dock_title_bg": "#091409",
        "dock_title_active": "#0e200e",
    },
    "Cyber Synthwave": {
        "is_dark": "true",
        "bg_root": "#0d0221",
        "bg_surface": "#19053b",
        "bg_card": "#260859",
        "bg_card_hover": "#360c7d",
        "bg_input": "#12032e",
        "border": "#4d1082",
        "border_light": "#6a1baf",
        "border_focus": "#ff007f",
        "text_main": "#fef6ff",
        "text_muted": "#b899d9",
        "text_dim": "#7d5d9e",
        "primary": "#ff007f",
        "primary_hover": "#ff3399",
        "primary_pressed": "#cc0066",
        "matrix_green": "#39ff14",
        "matrix_green_glow": "#66ff47",
        "warning_amber": "#ffff33",
        "signal_red": "#ff073a",
        "accent_purple": "#c084fc",
        "dock_title_bg": "#150c29",
        "dock_title_active": "#20123e",
    }
}

DEFAULT_THEME_NAME: str = "Trading Terminal (Default)"
