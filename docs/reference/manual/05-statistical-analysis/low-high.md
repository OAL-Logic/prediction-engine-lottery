# Low-High Analysis

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Low-High Analysis



Click 
menu->Statistics->Low-High to open the Low-High 
analysis window.

**What is 
Low number and High number?

**All numbers are divided into two 
groups, For example, Mega Millions (1 to 70 numbers), from 1 â€?35 are low 
numbers and from 36 â€?70 are high numbers.

**Low Number:** 
List all Low numbers.
**High Number**: List all high 
numbers.
**Low Count:** Counting the number of Low 
numbers.
**High Count**: Counting the number of High 
numbers.
**Low Sum**: All Low numbers added together. For 
example, Mega Millions, 08, 22, 30, 41, 50, 61, Low number is 08 22 30, Low sum 
is 8+22+30=60, so Low Sum=60.
**High Sum**: All High numbers 
added together.

**

---


Home 
Page: https://example.org/lottery-studio
** Support:support@example.org 

Copyright: Â© Lottery Analysis Studio All rights 
reserved.**

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
