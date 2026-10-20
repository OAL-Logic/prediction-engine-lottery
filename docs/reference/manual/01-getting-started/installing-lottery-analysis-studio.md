# Installing Lottery Studio

> **Category:** Getting Started & Studio Overview (`01-getting-started`)

﻿








  
  
    

## Installing Lottery Studio



1. Be sure that your system meets all of the system requirements 
for running Lottery Studio. 

2. Be sure that all other open program are closed. 

3. If you have enough available space on your C or other 
drives, recommend that you install it in the default 
location.

**Lottery Studio Software System 
Requirement**

Lottery Studio software program supports all 32 bit or 64 bit Windows 
computer systems including Windows XP, Vista, Windows 7, Windows 8, and Windows 
10. You can install it on your PC, laptop, or surface.



　

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
