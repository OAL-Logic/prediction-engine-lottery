# Save and Load Your Own Favorite Number

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

## Save and Load Your Own Favorite Number






To Save and Load Your Own Favorite Number:

①. Click Menu button pop-up menu, click Save Selected open save as window:







②. Enter file name click Save button.



To Load Your  Favorite Number:

①. Click Menu button pop-up menu, click Load Selected open open window:







  ②. Select file  click Open button.

　

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
