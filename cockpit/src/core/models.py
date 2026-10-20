"""
Core Domain Models & Schemas
============================
Formal schemas and dataclasses for the Next-Gen Lottery Engine Desktop Cockpit.
Provides domain representations for game definitions, dynamic filter nodes,
fault-tolerance rules, wheeling configurations, ticket receipts, perspectives,
and bidirectional profile bundles (Desktop JSON <-> Engine CLI YAML).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set


class PerspectiveType(str, Enum):
    """Cockpit top-level perspective classification."""
    EXPRESS = "Express"
    STUDIO = "Studio"
    ESOTERIC = "Esoteric"
    LAB = "Lab"
    PRINTER = "Printer"


class ToleranceMode(str, Enum):
    """Filter error allowance / logical combination mode."""
    AND = "AND"               # All active filters must match (100% strict)
    OR = "OR"                 # At least one active filter must match
    RANGE = "RANGE"           # Fault-tolerant: Pass if between min_pass and max_pass match
    GROUP = "GROUP"           # Tier/Group-level error tolerance


class WheelType(str, Enum):
    """Combinatorial wheeling classification."""
    FULL = "FULL"                         # Exhaustive C(n, k)
    ABBREVIATED = "ABBREVIATED"           # Minimal covering design (t-if-m of v)
    POSITIONAL = "POSITIONAL"             # Independent candidate lists per column
    KEY_BANKER = "KEY_BANKER"             # Core fixed numbers + wheeled remainder


@dataclass
class GameSchema:
    """Dynamic representation of a lottery game adapted from engine registry."""
    id: str                               # e.g., 'br/lotofacil', 'br/mega-sena', 'us/powerball'
    name: str                             # Display title
    pick_count: int                       # Numbers drawn (k)
    pool_size: int                        # Pool cardinality (M)
    number_range_min: int = 1             # 1-indexed (or 0 for Lotomania)
    bonus_count: int = 0                  # Extra balls (Powerball, Mega Millions)
    bonus_pool: Optional[int] = None      # Bonus number upper bound
    ticket_price: float = 0.0             # Base currency cost per line
    currency: str = "BRL"
    draw_days: List[str] = field(default_factory=list)
    board_cols: int = 10                  # Matrix layout width
    data_available: bool = True
    draw_file: Optional[str] = None

    @property
    def number_range_max(self) -> int:
        return self.number_range_min + self.pool_size - 1

    def format_number(self, n: int) -> str:
        """Formats numbers with appropriate zero-padding."""
        return f"{n:02d}"

    def validate_line(self, line: List[int]) -> Tuple[bool, Optional[str]]:
        """Validates if a line conforms to the game's pick rules."""
        if len(line) != self.pick_count:
            return False, f"Expected {self.pick_count} numbers, got {len(line)}"
        if len(set(line)) != len(line):
            return False, "Duplicate numbers detected in combination"
        for n in line:
            if n < self.number_range_min or n > self.number_range_max:
                return False, f"Number {n} outside range [{self.number_range_min}, {self.number_range_max}]"
        return True, None


@dataclass
class FilterNode:
    """Configurable node in the combinatorial filter graph."""
    id: str                               # Unique ID, e.g. 'structural_odd_count'
    name: str                             # Human-readable caption
    category: str                         # 'Structural', 'Positional', 'Algebraic', 'Advanced', etc.
    description: str = ""
    tags: List[str] = field(default_factory=list)
    enabled: bool = False
    min_val: float = 0.0
    max_val: float = 100.0
    default_min: float = 0.0
    default_max: float = 100.0
    step: float = 1.0
    positions: Optional[List[int]] = None # Restrict check to specific 1-indexed column indices
    weight: float = 1.0
    eliminated_count: int = 0             # Telemetry tracking during last run

    def matches(self, value: float) -> bool:
        """Checks if an evaluated scalar value falls within allowed bounds."""
        return self.min_val <= value <= self.max_val


@dataclass
class ToleranceRule:
    """
    Fault Tolerance Engine Configuration.
    Implements Lottery Studio's Error Allowance logic to prevent discarding jackpot
    lines due to small deviations or single filter edge-case misses.
    """
    mode: ToleranceMode = ToleranceMode.AND
    min_pass: int = 0                     # Minimum number of active filters that must evaluate True
    max_pass: int = 0                     # Maximum allowed matches (0 = unlimited / total active)
    group_rules: Dict[str, Tuple[int, int]] = field(default_factory=dict) # Group name -> (min, max)

    def compute_verdict(self, pass_count: int, total_active: int) -> bool:
        """Evaluates whether a candidate combination survives tolerance criteria."""
        if total_active == 0:
            return True
        if self.mode == ToleranceMode.AND:
            return pass_count == total_active
        elif self.mode == ToleranceMode.OR:
            return pass_count >= 1
        elif self.mode == ToleranceMode.RANGE:
            upper = self.max_pass if self.max_pass > 0 else total_active
            return self.min_pass <= pass_count <= upper
        return True


@dataclass
class WheelingConfig:
    """Combinatorial covering and wheeling specification."""
    wheel_type: WheelType = WheelType.ABBREVIATED
    pool_numbers: List[int] = field(default_factory=list)
    guarantee: int = 4                    # Match guarantee tier (t)
    condition_match: int = 5              # Numbers hitting pool required (m)
    pick_size: int = 6                    # Ticket line size (k)
    key_numbers: List[int] = field(default_factory=list) # Fixed Banker numbers
    pruning_enabled: bool = False         # Redundancy pruning via Hamming overlap
    pruning_distance_min: int = 2         # Minimum distinct balls between any two tickets
    max_ticket_cap: Optional[int] = None  # Budget constraint cap


@dataclass
class TicketReceipt:
    """Model representing an immutable candidate lottery ticket."""
    ticket_id: int
    numbers: List[int]
    bonus_numbers: List[int] = field(default_factory=list)
    confidence_score: float = 0.0
    filter_pass_count: int = 0
    strategy_source: str = "Ensemble"

    @property
    def formatted_main(self) -> str:
        return " ".join(f"{n:02d}" for n in sorted(self.numbers))

    @property
    def formatted_bonus(self) -> str:
        if not self.bonus_numbers:
            return ""
        return f"+ [{' '.join(f'{b:02d}' for b in sorted(self.bonus_numbers))}]"


@dataclass
class GenerationTelemetry:
    """Real-time performance metrics emitted by the streaming worker."""
    combinations_scanned: int = 0
    combinations_survived: int = 0
    reduction_rate_pct: float = 0.0
    scan_rate_per_sec: float = 0.0
    elapsed_seconds: float = 0.0
    is_complete: bool = False
    cancelled: bool = False


@dataclass
class ProfileBundle:
    """
    Complete state snapshot of the Desktop Cockpit.
    Can be serialized as a rich JSON desktop profile or exported as a clean
    headless CLI strategy preset (.yaml) matching `lottery suggest --profile`.
    """
    version: str = "2.0"
    active_game_id: str = "br/lotofacil"
    active_perspective: str = "Express"
    theme_name: str = "Trading Terminal (Default)"
    window_geometry: Optional[str] = None
    dock_layout_state: Optional[str] = None
    selected_pool: List[int] = field(default_factory=list)
    filters: List[FilterNode] = field(default_factory=list)
    tolerance: ToleranceRule = field(default_factory=ToleranceRule)
    wheeling: WheelingConfig = field(default_factory=WheelingConfig)
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        "frequency": 0.25,
        "skips": 0.25,
        "markov": 0.20,
        "delta_gaps": 0.15,
        "cosmic_ephemeris": 0.15,
    })

    def to_json(self) -> str:
        """Serializes complete UI & engine state into JSON."""
        def serialize_helper(obj):
            if isinstance(obj, Enum):
                return obj.value
            return obj
        raw = asdict(self)
        return json.dumps(raw, default=serialize_helper, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> ProfileBundle:
        """Loads desktop profile from JSON."""
        data = json.loads(json_str)
        filters = [FilterNode(**f) for f in data.get("filters", [])]
        
        tol_data = data.get("tolerance", {})
        if "mode" in tol_data and isinstance(tol_data["mode"], str):
            tol_data["mode"] = ToleranceMode(tol_data["mode"])
        tolerance = ToleranceRule(**tol_data)

        wheel_data = data.get("wheeling", {})
        if "wheel_type" in wheel_data and isinstance(wheel_data["wheel_type"], str):
            wheel_data["wheel_type"] = WheelType(wheel_data["wheel_type"])
        wheeling = WheelingConfig(**wheel_data)

        return cls(
            version=data.get("version", "2.0"),
            active_game_id=data.get("active_game_id", "br/lotofacil"),
            active_perspective=data.get("active_perspective", "Express"),
            theme_name=data.get("theme_name", "Trading Terminal (Default)"),
            window_geometry=data.get("window_geometry"),
            dock_layout_state=data.get("dock_layout_state"),
            selected_pool=data.get("selected_pool", []),
            filters=filters,
            tolerance=tolerance,
            wheeling=wheeling,
            strategy_weights=data.get("strategy_weights", {}),
        )

    def to_cli_yaml(self) -> str:
        """
        Converts the active filter bounds and strategy weights into a clean,
        headless YAML specification 100% compatible with existing CLI profiles
        (e.g., `lotofacil_optimized.yaml`).
        """
        import yaml
        cli_dict = {
            "game": self.active_game_id,
            "strategies": self.strategy_weights,
            "filters": {
                f.id: {"min": f.min_val, "max": f.max_val}
                for f in self.filters if f.enabled
            },
            "tolerance": {
                "mode": self.tolerance.mode.value,
                "min_pass": self.tolerance.min_pass,
                "max_pass": self.tolerance.max_pass,
            },
            "wheeling": {
                "guarantee": self.wheeling.guarantee,
                "condition_match": self.wheeling.condition_match,
                "pruning": self.wheeling.pruning_enabled,
            }
        }
        return yaml.dump(cli_dict, sort_keys=False, default_flow_style=False)
