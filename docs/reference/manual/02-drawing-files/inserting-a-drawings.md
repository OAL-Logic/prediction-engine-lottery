# Inserting a Drawings

> **Category:** Drawing History & Game File Management (`02-drawing-files`)

﻿








  
  
    

## Inserting a Draw



At times it may be necessary to 
insert a drawing that was previously entered in a drawing file.

　



To insert a drawing:

1.On the Toolbar, click the Drawings 
button open the edit drawings window.

2. Click on the drawing that you want to insert in the drawing 
list. 

3. Click the Insert button open the 
Insert Drawings window:

Selecting a date and enter your 
numbers in the edit box then click the Ok button.

4. Click on the Yes button when you 
are asked to confirm. 

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
