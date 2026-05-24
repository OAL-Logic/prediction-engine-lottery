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

# --- Core Protocol ---

class VectorizedFilter(ABC):
    unique_id: str
    display_name: str
    tier: int
    description: str = ""

    @abstractmethod
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.unique_id}' tier={self.tier}>"

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
    if not sorted_nums: return {"max_successive": 0, "groups": 0}
    groups, current = 0, 1
    max_s = 1
    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i-1] + 1:
            current += 1
        else:
            if current > 1: groups += 1
            max_s = max(max_s, current)
            current = 1
    if current > 1: groups += 1
    max_s = max(max_s, current)
    return {"max_successive": max_s if max_s > 1 else 0, "groups": groups}

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

