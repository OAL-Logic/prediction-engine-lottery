"""
Betslip Models & Brazilian Caixa Calibration Presets
=====================================================
Defines precise millimeter-space dimensional templates for physical lottery
slips, specifically prioritizing Brazilian Caixa Econômica Federal formats:
- Lotofácil (25 numbers, 3 panels)
- Mega-Sena (60 numbers, 3 panels)
- Quina (80 numbers, 3 panels)
- Lotomania (100 numbers, 1 panel)
- Dupla Sena (50 numbers, 2 panels)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple


@dataclass
class BetslipTemplate:
    """
    Millimeter-precision specification of a physical lottery betslip.
    Coordinates are defined in millimeters from the physical paper edges:
    - Top-left corner of paper is (0.0, 0.0) mm.
    - X increases to the right.
    - Y increases downwards.
    """
    name: str = "Caixa Lotofácil"
    game_slug: str = "br/lotofacil"
    
    # Paper outer dimensions (Standard Caixa thermal/pre-printed paper)
    slip_width_mm: float = 82.0
    slip_height_mm: float = 155.0
    
    # Multi-panel game layout (e.g. Jogo 1, Jogo 2, Jogo 3)
    panels_per_slip: int = 3
    panel_gap_y_mm: float = 34.0   # Vertical pitch between consecutive panel origins
    
    # Primary grid origin for Panel 1 (center or top-left of first number)
    origin_x_mm: float = 9.5
    origin_y_mm: float = 33.5
    
    # Grid matrix geometry
    rows: int = 5
    cols: int = 5
    pitch_x_mm: float = 4.8        # Center-to-center horizontal distance between numbers
    pitch_y_mm: float = 4.2        # Center-to-center vertical distance between numbers
    
    # Physical optical mark properties
    mark_width_mm: float = 3.6     # Standard optical black dash width
    mark_height_mm: float = 1.8    # Standard optical black dash height
    mark_style: str = "rectangle"  # rectangle, dash, cross, oval
    
    # Number indexing
    number_offset: int = 1         # 1-indexed (1..25) or 0-indexed (00..99 for Lotomania)
    number_order: str = "row_major" # row_major: 1 2 3 across rows; col_major: 1 2 3 down columns
    
    # Fine-tuning printer hardware calibration offsets
    hardware_offset_x_mm: float = 0.0
    hardware_offset_y_mm: float = 0.0
    scale_x: float = 1.0           # Stepper feed stretch compensation (X axis)
    scale_y: float = 1.0           # Stepper feed stretch compensation (Y axis)

    def calculate_mark_position_mm(self, panel_idx: int, number: int) -> Optional[Tuple[float, float]]:
        """
        Calculates the center (x_mm, y_mm) coordinates of a given number in a given panel.
        Returns None if number is outside the valid range.
        """
        if panel_idx < 0 or panel_idx >= self.panels_per_slip:
            return None
        
        norm_num = number - self.number_offset
        total_cells = self.rows * self.cols
        if norm_num < 0 or norm_num >= total_cells:
            return None
        
        if self.number_order == "row_major":
            row = norm_num // self.cols
            col = norm_num % self.cols
        else: # col_major
            row = norm_num % self.rows
            col = norm_num // self.rows
        
        # Base panel origin
        panel_y_origin = self.origin_y_mm + (panel_idx * self.panel_gap_y_mm)
        
        # Calculate raw millimeter position
        raw_x = self.origin_x_mm + (col * self.pitch_x_mm)
        raw_y = panel_y_origin + (row * self.pitch_y_mm)
        
        # Apply hardware compensation and stretch factors
        calibrated_x = (raw_x * self.scale_x) + self.hardware_offset_x_mm
        calibrated_y = (raw_y * self.scale_y) + self.hardware_offset_y_mm
        
        return (calibrated_x, calibrated_y)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> BetslipTemplate:
        data = json.loads(json_str)
        return cls(**data)


# Standard Brazilian Caixa Econômica Federal Presets
CAIXA_PRESETS: Dict[str, BetslipTemplate] = {
    "Caixa Lotofácil": BetslipTemplate(
        name="Caixa Lotofácil",
        game_slug="br/lotofacil",
        slip_width_mm=82.0,
        slip_height_mm=155.0,
        panels_per_slip=3,
        panel_gap_y_mm=34.5,
        origin_x_mm=9.5,
        origin_y_mm=33.5,
        rows=5,
        cols=5,
        pitch_x_mm=4.8,
        pitch_y_mm=4.2,
        mark_width_mm=3.6,
        mark_height_mm=1.8,
        mark_style="rectangle",
        number_offset=1,
    ),
    "Caixa Mega-Sena": BetslipTemplate(
        name="Caixa Mega-Sena",
        game_slug="br/mega-sena",
        slip_width_mm=82.0,
        slip_height_mm=155.0,
        panels_per_slip=3,
        panel_gap_y_mm=33.0,
        origin_x_mm=8.0,
        origin_y_mm=31.0,
        rows=6,
        cols=10,
        pitch_x_mm=4.5,
        pitch_y_mm=3.6,
        mark_width_mm=3.2,
        mark_height_mm=1.6,
        mark_style="rectangle",
        number_offset=1,
    ),
    "Caixa Quina": BetslipTemplate(
        name="Caixa Quina",
        game_slug="br/quina",
        slip_width_mm=82.0,
        slip_height_mm=155.0,
        panels_per_slip=3,
        panel_gap_y_mm=34.0,
        origin_x_mm=7.5,
        origin_y_mm=29.0,
        rows=8,
        cols=10,
        pitch_x_mm=4.4,
        pitch_y_mm=3.1,
        mark_width_mm=3.0,
        mark_height_mm=1.4,
        mark_style="rectangle",
        number_offset=1,
    ),
    "Caixa Lotomania": BetslipTemplate(
        name="Caixa Lotomania",
        game_slug="br/lotomania",
        slip_width_mm=82.0,
        slip_height_mm=155.0,
        panels_per_slip=1,
        panel_gap_y_mm=0.0,
        origin_x_mm=7.0,
        origin_y_mm=30.0,
        rows=10,
        cols=10,
        pitch_x_mm=4.3,
        pitch_y_mm=3.5,
        mark_width_mm=3.0,
        mark_height_mm=1.5,
        mark_style="rectangle",
        number_offset=0, # 00 to 99
    ),
    "Caixa Dupla Sena": BetslipTemplate(
        name="Caixa Dupla Sena",
        game_slug="br/dupla-sena",
        slip_width_mm=82.0,
        slip_height_mm=155.0,
        panels_per_slip=2,
        panel_gap_y_mm=42.0,
        origin_x_mm=8.0,
        origin_y_mm=32.0,
        rows=5,
        cols=10,
        pitch_x_mm=4.5,
        pitch_y_mm=3.8,
        mark_width_mm=3.2,
        mark_height_mm=1.6,
        mark_style="rectangle",
        number_offset=1,
    ),
}
