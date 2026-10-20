# Divided Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Distance Analysis](distance.md) · [Drawings Distributing ➡️](drawings-distributing.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Divided Analysis](#divided-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Divided Analysis





  Click menu->Statistics->Divided to open the Divided
analysis window.



Divide all the numbers by 3-10 and the remainder of 0, 1, 2, 3, 4, 5, 6, 7, 8, and 9 as the number group. then counts the number of hits of each number group.









**How to calculate divided by 3 reminder of 0, 1, 2 numbers?**



From **1 to 69**, **divided by 3 reminder of 0 numbers** 03 06 09 12 15 18 21 24 27 30 33 36 39 42 45 48 51 54 57 60 63 66 69.

**Divided by 3 reminder of 1 numbers** 01 04 07 10 13 16 19 22 25 28 31 34 37 40 43 46 49 52 55 58 61 64 67.

**Divided by 3 reminder of 2 numbers** 02 05 08 11 14 17 20 23 26 29 32 35 38 41 44 47 50 53 56 59 62 65 68.



**Remainder 0 Count: **Counting the winning number of hits in the divided by 3 reminder of 0 numbers.

**Remainder 1 Count: **Counting the winning number of hits in the divided by 3 reminder of 1 numbers.

**Remainder 2 Count: **Counting the winning number of hits in the divided by 3 reminder of 2 numbers.

**Modality: **Show current number combination divided by 3 reminder of 0, 1, and 2 numbers pattern. For example, Remainder 0 Count=3, Remainder 1 Count=1, Remainder 2 Count=1, so modality=311.







**Change the Divisor**: Click Divided by ComboBox to change the divisor. Supports divide by 3 to divide by 10.






---

---

## Clean-Room Python Boilerplate

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class RangeFilter:
    tag: int
    name: str
    metric_fn: Callable[[list[int]], int]
    min_val: int
    max_val: int

    def evaluate(self, ticket: list[int]) -> bool:
        val = self.metric_fn(ticket)
        return self.min_val <= val <= self.max_val

def evaluate_filter_suite(
    ticket: list[int],
    filters: list[RangeFilter],
    mode: str = "AND",
    n_of_m: tuple[int, int] | None = None,
) -> bool:
    passed = sum(1 for f in filters if f.evaluate(ticket))
    if mode == "AND":
        return passed == len(filters)
    if mode == "OR":
        return passed >= 1
    if n_of_m is not None:
        lo, hi = n_of_m
        return lo <= passed <= hi
    return True
```

---
> **Next Steps**: [⬅️ Distance Analysis](distance.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Drawings Distributing ➡️](drawings-distributing.md)
