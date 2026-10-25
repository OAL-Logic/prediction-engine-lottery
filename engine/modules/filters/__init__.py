"""
Consolidated Vectorized Harmony Gate 🛡️
=======================================
High-performance lottery filter implementation utilizing NumPy vectorization.
Supports lazy loading of 100+ analytical vectors.
"""

from __future__ import annotations
import sys
import importlib.util
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import numpy as np

if TYPE_CHECKING:
    from engine.adapters import DrawRules

# --- Constants ---
PRIMES = np.array([
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
])

# Bit-count lookup table for uint16 (65536 entries)
BIT_COUNT_TABLE = np.array([bin(i).count('1') for i in range(65536)], dtype=np.uint8)

def count_bits_64(arr: np.ndarray) -> np.ndarray:
    """Vectorized set-bit count for uint64 arrays using lookup table."""
    return (BIT_COUNT_TABLE[(arr & 0xFFFF).astype(np.uint16)].astype(int) + 
            BIT_COUNT_TABLE[((arr >> 16) & 0xFFFF).astype(np.uint16)].astype(int) + 
            BIT_COUNT_TABLE[((arr >> 32) & 0xFFFF).astype(np.uint16)].astype(int) + 
            BIT_COUNT_TABLE[((arr >> 48) & 0xFFFF).astype(np.uint16)].astype(int))

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

def format_gauge(val: float | int, min_val: float | int, max_val: float | int, passed: bool, width: int = 18) -> str:
    """Renders a dynamic visual ASCII bracket gauge showing where val lies relative to min_val..max_val."""
    try:
        val_f = float(val)
        min_f = float(min_val)
        max_f = float(max_val)
        span = max(max_f - min_f, 1.0)
        low_bound = min_f - 0.25 * span
        high_bound = max_f + 0.25 * span
        total_range = max(high_bound - low_bound, 1.0)

        pos = int(((val_f - low_bound) / total_range) * width)
        pos = max(0, min(width - 1, pos))

        bracket_start = int(((min_f - low_bound) / total_range) * width)
        bracket_end = int(((max_f - low_bound) / total_range) * width)
        bracket_start = max(0, min(width - 1, bracket_start))
        bracket_end = max(bracket_start, min(width - 1, bracket_end))

        chars = ["-"] * width
        for i in range(bracket_start, bracket_end + 1):
            chars[i] = "="
        chars[pos] = "●"
        status_sym = "✓ PASS" if passed else "✗ FAIL"
        return f"[{''.join(chars)}] {status_sym} (value: {val}, target: [{min_val}..{max_val}])"
    except Exception:
        return "[✓ PASS]" if passed else "[✗ FAIL]"

@dataclass
class FilterExplanation:
    filter_id: str
    filter_name: str
    tier: int
    category: str
    passed: bool
    actual_value: Any
    allowed_range: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    formula: str = ""
    diagram: str = ""
    mermaid: str = ""
    gauge: str = ""

    def render_text(self) -> str:
        status_label = "PASS ✓" if self.passed else "FAIL ✗"
        lines = [
            f"=== [{self.tier}] {self.filter_name} ({self.filter_id}) ===",
            f"Category : {self.category}",
            f"Verdict  : {status_label}",
            f"Value    : {self.actual_value} | Target: {self.allowed_range}",
            f"Gauge    : {self.gauge}",
            f"Summary  : {self.summary}",
        ]
        if self.formula:
            lines.append(f"Formula  : {self.formula}")
        if self.diagram:
            lines.append("Diagram  :\n" + self.diagram)
        return "\n".join(lines)

# --- Core Protocol ---

class VectorizedFilter(ABC):
    unique_id: str
    display_name: str
    tier: int
    description: str = ""
    category: str = "General"
    formula: str = ""
    diagram: str = ""
    mermaid: str = ""

    @abstractmethod
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        pass

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        """Dynamically evaluate a combination and return structured explanation with metrics & visual gauge."""
        comb_arr = np.asarray(combination, dtype=int)
        if comb_arr.ndim == 1:
            arr_2d = comb_arr.reshape(1, -1)
        else:
            arr_2d = comb_arr

        if rules is None:
            from engine.adapters import DrawRules
            max_v = int(np.max(arr_2d)) if arr_2d.size else 60
            rules = DrawRules(name="Standard Pool", pick_count=arr_2d.shape[1], number_range=(1, max(max_v, 60)))

        passed = bool(self.apply(arr_2d, rules)[0])
        summary = f"{'Passed' if passed else 'Failed'} criteria for {self.display_name}."
        gauge = "[✓ PASS]" if passed else "[✗ FAIL]"
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=getattr(self, "category", "General"),
            passed=passed,
            actual_value=passed,
            allowed_range="Configured predicate",
            summary=summary,
            details={"numbers": list(comb_arr.ravel()), "passed": passed},
            formula=getattr(self, "formula", ""),
            diagram=getattr(self, "diagram", ""),
            mermaid=getattr(self, "mermaid", ""),
            gauge=gauge,
        )

    def generate_documentation(self, rules: Optional[DrawRules] = None, sample: Optional[Sequence[int]] = None) -> str:
        """Returns a formatted Markdown documentation card with formulas, diagrams, and dynamic evaluation."""
        sample_nums = sample if sample is not None else [4, 11, 23, 35, 48, 59][:rules.pick_count if rules else 6]
        exp = self.explain(sample_nums, rules)

        md = [
            f"### `{self.unique_id}` — {self.display_name}",
            f"- **Tier**: Tier {self.tier} ({self.category})",
            f"- **Description**: {self.description}",
        ]
        if self.formula:
            md.append(f"- **Mathematical Formulation**: `{self.formula}`")
        if self.diagram:
            md.append(f"\n```text\n{self.diagram}\n```")
        if self.mermaid:
            md.append(f"\n```mermaid\n{self.mermaid}\n```")

        md.append(f"\n**Dynamic Evaluation Example** (Ticket: `{list(sample_nums)}`):")
        md.append(f"- **Verdict**: `{'PASS' if exp.passed else 'FAIL'}`")
        md.append(f"- **Metric Value**: `{exp.actual_value}` (Allowed Range: `{exp.allowed_range}`)")
        md.append(f"- **Gauge**: `{exp.gauge}`")
        md.append(f"- **Summary**: {exp.summary}")
        return "\n".join(md)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.unique_id}' tier={self.tier}>"

ALIAS_MAP: Dict[str, str] = {
    "sum_range": "historical_sum_range",
    "parity": "structural_odd_count",
    "odd_count": "structural_odd_count",
    "even_count": "structural_even_count",
    "prime": "structural_prime_count",
    "primes": "structural_prime_count",
    "ac_value": "structural_ac_value",
    "ac_range": "historical_ac_range",
    "high_low": "historical_hl_pattern",
    "consecutive": "historical_consecutive_pattern",
    "decade": "historical_decade_pattern",
    "unit": "historical_unit_pattern",
    "median": "historical_median_range",
    "std_dev": "historical_std_dev_range",
    "spread": "historical_spread_range",
    "common_pair": "historical_common_pair",
    "common_triplet": "historical_common_triplet",
    "digit_sum": "historical_digit_sum_pattern",
    "breadth": "structural_breadth",
    "unit_different": "structural_distinct_units",
    "average_value": "structural_average_value",
    "quadrant_balance": "positional_quadrant_balance",
    "birthday_bias": "structural_birthday_bias",
    "magic_square": "algebraic_magic_square",
    "digit_space_123": "algebraic_digit_space_123",
    "mixed_parity_digits": "algebraic_mixed_parity_digits",
    "max_skips": "historical_max_skips",
    "trevo_resonance": "custom_trevo_resonance",
}

class VectorRegistry:
    def __init__(self):
        self._instances: Dict[str, VectorizedFilter] = {}
        self._module_map: Dict[str, str] = {} # id -> module_path
        self._discovered = False

    def _discover(self):
        if self._discovered: return
        base_dir = Path(__file__).parent
        for p in base_dir.glob("tier*.py"):
            # Load the module temporarily to find filter classes
            spec = importlib.util.spec_from_file_location(f"engine.modules.filters.{p.stem}", p)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                for attr_name in dir(mod):
                    cls = getattr(mod, attr_name)
                    if (isinstance(cls, type) and issubclass(cls, VectorizedFilter) 
                        and cls != VectorizedFilter):
                        uid = getattr(cls, 'unique_id', None)
                        if uid:
                            self._module_map[uid] = f"engine.modules.filters.{p.stem}"
        self._discovered = True

    def register(self, filter_obj: VectorizedFilter):
        """Manual registration (for testing or dynamic filters)."""
        self._instances[filter_obj.unique_id] = filter_obj

    def get(self, unique_id: str) -> Optional[VectorizedFilter]:
        if unique_id in ALIAS_MAP:
            unique_id = ALIAS_MAP[unique_id]

        if unique_id in self._instances:
            return self._instances[unique_id]
        
        self._discover()
        if unique_id not in self._module_map:
            # Handle special cases like div_by_N which are factories
            if unique_id.startswith("algebraic_div_by_"):
                try:
                    n = int(unique_id.split("_")[-1])
                    from engine.modules.filters.tier3_algebraic import DividedByNFilter
                    f = DividedByNFilter(n)
                    self._instances[unique_id] = f
                    return f
                except Exception: return None
            return None
        
        # Lazy load the module
        mod_name = self._module_map[unique_id]
        mod = importlib.import_module(mod_name)
        
        # Find the class that matches this unique_id
        for attr_name in dir(mod):
            cls = getattr(mod, attr_name)
            if (isinstance(cls, type) and issubclass(cls, VectorizedFilter) 
                and cls != VectorizedFilter and getattr(cls, 'unique_id', None) == unique_id):
                inst = cls()
                self._instances[unique_id] = inst
                return inst
        return None

    def list_by_tier(self, tier: int) -> List[VectorizedFilter]:
        self._discover()
        # This requires loading everything in that tier
        results = []
        for uid, mod in self._module_map.items():
            f = self.get(uid)
            if f and f.tier == tier:
                results.append(f)
        return results

    def validate_batch(self, combinations: np.ndarray, rules: DrawRules, active_ids: List[str], k_of_n: int = 0) -> np.ndarray:
        if not active_ids: return np.ones(combinations.shape[0], dtype=bool)
        results = np.zeros((combinations.shape[0], len(active_ids)), dtype=bool)
        for i, uid in enumerate(active_ids):
            f = self.get(uid)
            results[:, i] = f.apply(combinations, rules) if f else True
        return np.sum(results, axis=1) >= k_of_n if k_of_n > 0 else np.all(results, axis=1)

    def explain(self, unique_id: str, combination: Sequence[int], rules: Optional[DrawRules] = None) -> Optional[FilterExplanation]:
        f = self.get(unique_id)
        if f is None:
            return None
        return f.explain(combination, rules)

    def explain_all(
        self,
        combination: Sequence[int],
        rules: Optional[DrawRules] = None,
        filter_ids: Optional[List[str]] = None,
    ) -> List[FilterExplanation]:
        self._discover()
        ids = filter_ids if filter_ids is not None else sorted(self._module_map.keys())
        explanations = []
        for uid in ids:
            f = self.get(uid)
            if f:
                explanations.append(f.explain(combination, rules))
        return explanations

    def get_documentation(
        self,
        unique_id: str,
        rules: Optional[DrawRules] = None,
        sample: Optional[Sequence[int]] = None,
    ) -> Optional[str]:
        f = self.get(unique_id)
        if f is None:
            return None
        return f.generate_documentation(rules, sample)

    def catalog_summary(self, tier: Optional[int] = None) -> Dict[int, List[Dict[str, Any]]]:
        self._discover()
        tiers_to_check = [tier] if tier else [1, 2, 3, 4, 5]
        summary: Dict[int, List[Dict[str, Any]]] = {}
        for t in tiers_to_check:
            items = []
            for f in sorted(self.list_by_tier(t), key=lambda x: x.unique_id):
                items.append({
                    "unique_id": f.unique_id,
                    "display_name": f.display_name,
                    "tier": f.tier,
                    "category": getattr(f, "category", "General"),
                    "description": getattr(f, "description", ""),
                    "formula": getattr(f, "formula", ""),
                })
            summary[t] = items
        return summary

# Global singleton
registry = VectorRegistry()

# ── Legacy Helpers (Backward Compatibility) ───────────────────────────────────

def get_odd_count(nums: List[int]) -> int:
    return sum(1 for n in nums if n % 2 != 0)

def get_even_count(nums: List[int]) -> int:
    return sum(1 for n in nums if n % 2 == 0)

def get_high_low_counts(nums: List[int], pool_size: int) -> Dict[str, int]:
    mid = pool_size // 2
    lows = sum(1 for n in nums if n <= mid)
    highs = len(nums) - lows
    return {"low": lows, "high": highs}

def get_decade_metrics(nums: List[int]) -> Dict[str, int]:
    from collections import Counter
    decades = [n // 10 for n in nums]
    counts = Counter(decades)
    sorted_decades = sorted(list(set(decades)))
    groups = 0
    if sorted_decades:
        groups = 1
        for i in range(1, len(sorted_decades)):
            if sorted_decades[i] != sorted_decades[i-1] + 1:
                groups += 1
    return {"different": len(counts), "groups": groups}

def get_ac_value(nums: List[int]) -> int:
    """Calculates Arithmetic Complexity (legacy version)."""
    if len(nums) < 2: return 0
    diffs = set()
    sorted_nums = sorted(nums)
    for i in range(len(sorted_nums)):
        for j in range(i + 1, len(sorted_nums)):
            diffs.add(sorted_nums[j] - sorted_nums[i])
    return len(diffs) - (len(nums) - 1)

def get_prime_count(nums: List[int]) -> int:
    return sum(1 for n in nums if n in PRIMES)

def get_composite_count(nums: List[int]) -> int:
    return sum(1 for n in nums if n > 1 and n not in PRIMES)

def get_average_value(nums: List[int]) -> float:
    return sum(nums) / len(nums) if nums else 0.0

def get_unit_metrics(nums: List[int]) -> Dict[str, Any]:
    units = [n % 10 for n in nums]
    return {"sum": sum(units), "different": len(set(units)), "units": units}

def get_successive_metrics(nums: List[int]) -> Dict[str, int]:
    sorted_nums = sorted(nums)
    empty = {"max_successive": 0, "groups": 0, "groups_of_2": 0, "groups_of_3": 0, "groups_of_4": 0}
    if not sorted_nums: return empty
    groups, current = 0, 1
    max_s = 1
    run_lengths = []
    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i-1] + 1:
            current += 1
        else:
            if current > 1:
                groups += 1
                run_lengths.append(current)
            max_s = max(max_s, current)
            current = 1
    if current > 1:
        groups += 1
        run_lengths.append(current)
    max_s = max(max_s, current)
    return {
        "max_successive": max_s if max_s > 1 else 0,
        "groups": groups,
        "groups_of_2": sum(1 for r in run_lengths if r == 2),
        "groups_of_3": sum(1 for r in run_lengths if r == 3),
        "groups_of_4": sum(1 for r in run_lengths if r >= 4),  # filter_successive_4 blocks any 4-or-longer streak
    }

def get_root_sum(nums: List[int]) -> int:
    s = sum(nums)
    return 1 + (s - 1) % 9 if s > 0 else 0

def get_distance_metrics(nums: List[int]) -> Dict[str, Any]:
    sorted_nums = sorted(nums)
    if not sorted_nums: return {"spread": 0, "max": 0, "min": 0, "avg": 0.0, "different": 0}
    diffs = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
    return {
        "spread": sorted_nums[-1] - sorted_nums[0], 
        "max": max(diffs) if diffs else 0, 
        "min": min(diffs) if diffs else 0,
        "avg": sum(diffs) / len(diffs) if diffs else 0.0,
        "different": len(set(diffs))
    }

def get_advanced_sums(nums: List[int], pool_size: int) -> Dict[str, int]:
    mid = pool_size // 2
    low_sum = sum(n for n in nums if n <= mid)
    high_sum = sum(n for n in nums if n > mid)
    return {"low": low_sum, "high": high_sum}

def get_exact_successive_counts(nums: List[int]) -> Dict[int, int]:
    from collections import defaultdict
    sorted_nums = sorted(nums)
    res = defaultdict(int)
    if not sorted_nums:
        return res
    
    current_run = 1
    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i-1] + 1:
            current_run += 1
        else:
            if current_run > 1:
                res[current_run] += 1
            current_run = 1
    if current_run > 1:
        res[current_run] += 1
    return res

def get_modulo_distribution(nums: List[int], base: int) -> Dict[int, int]:
    from collections import defaultdict
    res = defaultdict(int)
    for n in nums:
        res[n % base] += 1
    return res

def get_multiples_count(nums: List[int], divisor: int) -> int:
    return sum(1 for n in nums if n % divisor == 0)

def get_successive_end_units(nums: List[int]) -> int:
    units = sorted(list(set(n % 10 for n in nums)))
    if not units: return 0
    max_run = 1
    current_run = 1
    for i in range(1, len(units)):
        if units[i] == units[i-1] + 1:
            current_run += 1
        else:
            max_run = max(max_run, current_run)
            current_run = 1
    max_run = max(max_run, current_run)
    return max_run if max_run > 1 else 0

def get_digit_parity_pairs(nums: List[int]) -> Dict[str, int]:
    res = {"mixed": 0, "even_only": 0, "odd_only": 0}
    for n in nums:
        digits = [int(d) for d in str(n)]
        has_even = any(d % 2 == 0 for d in digits)
        has_odd = any(d % 2 != 0 for d in digits)
        if has_even and has_odd:
            res["mixed"] += 1
        elif has_even:
            res["even_only"] += 1
        else:
            res["odd_only"] += 1
    return res

def get_restricted_digit_space_count(nums: List[int], allowed_digits: set[int]) -> int:
    count = 0
    for n in nums:
        s = f"{n:02d}"
        if all(int(d) in allowed_digits for d in s):
            count += 1
    return count

# ── Lazy Access Pattern ───────────────────────────────────────────────────────

def __getattr__(name: str):
    """Allows lazy access to registry tiers or instances."""
    if name == "filters":
        return registry
    raise AttributeError(f"module {__name__} has no attribute {name}")

