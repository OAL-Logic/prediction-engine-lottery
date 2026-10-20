# Sum Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Successive Analysis](successive.md) · [Units Number Analysis ➡️](units-number.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Sum Analysis](#sum-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

﻿








  
  
    

## Sum Analysis



Click 
menu->Statistics->Sum to open the Sum 
analysis.

**Sum**: The value of the sum 
of all numbers in the combination, For example, 05, 11, 14, 15, 22, 39, the sum 
is 5+11+14+15+22+39=106, so Number Sum=106.
**High Sum**: The 
value of the sum of all High numbers in the combination.
**Low 
Sum:** The value of the sum of all Low numbers in the 
combination.
**Odd Sum**: The value of the sum of all Odd 
numbers in the combination.
**Even Sum**: The value of the sum 
of all Even numbers in the combination.
**Prime Sum**: The value 
of the sum of all Prime numbers in the combination.

**The Unit 
Number Sum**: The value of the sum of Second Unit numbers in the 
combination. For example, 01 08 14 29 31 42, Sum of second units is 
1+8+4+9+1+2=25, so The Unit Number Sum value is 25.

**Root 
Sum**: Add the numbers in the combination to each other, then split the 
sum value and add all the digits together again. For example, 08 13 14 33 35 40, 
the sum of this combination is 143 and the Root Sum is 1+4+3=8, so the Root Sum 
value is 8.

**First and Second Unit Sum**: The value of the 
sum of First and Second Unit numbers in the combination. For example, 01 08 14 
29 31 42, Sum of first units is 0+0+1+2+3+4=10, and Sum of second units is 
1+8+4+9+1+2=25. Sum of first units + Sum of second units equals 10 + 25, so 
First and Second Unit Sum value is 35.



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
> **Next Steps**: [⬅️ Successive Analysis](successive.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Units Number Analysis ➡️](units-number.md)
