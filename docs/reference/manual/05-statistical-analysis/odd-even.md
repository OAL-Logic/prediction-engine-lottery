# Odd-Even Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Multiple Analysis](multiple.md) · [Prior Drawing Analysis ➡️](prior-drawing.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Odd-Even Analysis](#odd-even-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

﻿








  
  
    

## Odd-Even Analysis



Click 
menu->Statistics->Odd-Even to open the Odd-Even 
analysis window.

**Odd Number**: List 
all Odd numbers.
**Even Number**: List all Even 
numbers.
**Odd Count**: Counting the number of Odd 
numbers.
**Even Count**: Counting the number of Even 
numbers.
**Odd Sum**: All Odd numbers added together. For 
example, 05, 11, 14, 15, 22, 39, Odd is 05 11 15 39, Odd sum is 5+11+15+39=106, 
so Odd Sum=70.
**Even Sum**: All Even numbers added together. 
For example, 05, 11, 14, 15, 22, 39, Even is 14 22, Even sum is 14+22=36, so 
Even Sum=36.
**Modality**: Show current number combination Odd 
number and Even number pattern. The Odd number is marked by 1 and the Even 
number is marked by 0.

For example, 02, 18, 19, 36, 41, Odd and Even 
pattern is Even-Even-Odd-Even-Odd, so modality=00101.



---






Team All rights reserved.

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
> **Next Steps**: [⬅️ Multiple Analysis](multiple.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Prior Drawing Analysis ➡️](prior-drawing.md)
