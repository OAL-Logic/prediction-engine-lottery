# Locked Number Analysis

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

﻿








  
  
    

## Locked Number Analysis



Click 
menu->Statistics->Locked Number to open the 
Locked Number analysis window.

Count each number and 
other numbers in the combination of wining numbers hits of same 
time.

**Same The Time Appear Count = 
0**: Counts the numbers that appear 0 times at the same time as the 
current number.
**Same The Time Appear Count = 1**: Counts the 
numbers that appear 1 time at the same time as the current 
number.
**Same The Time Appear Count = 2**: Counts the numbers 
that appear 2 times at the same time as the current number.
**Same The 
Time Appear Count = 3**: Counts the numbers that appear 3 times at the 
same time as the current number.
**Same The Time Appear Count >= 
4**: Counts the numbers that appear 4 times at the same time as the 
current number.



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
