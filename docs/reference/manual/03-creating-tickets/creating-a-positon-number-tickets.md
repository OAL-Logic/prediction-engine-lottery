# Creating Positons Number Tickets

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

﻿








  
  
    

## Creating Positons Number Tickets



Use this feature you can specify the numbers of each position.








How to Creating a Positon Number Tickets:

①. Click each "Pick" button open the 
pick numbers form.



Selected your numbers, then click Ok 
button. If want add the bouns number, please checked the Bouns chekbox.



②. Click Generate Tickets button. 


Then the all tickes will be saved in the tickets panel. 





 

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
