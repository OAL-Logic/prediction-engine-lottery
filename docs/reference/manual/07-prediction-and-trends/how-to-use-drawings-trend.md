# How to Use Drawings Trend

> **Category:** Prediction Formulas, Trends & Verification (`07-prediction-and-trends`)

## How to Use Drawings Trend



Observation number charts, you will find there are certain rules, according to the number of movements manual predict next drawings.**











  1. To manual predict next drawings:** In the bottom of the table you can see Next Drawings,  The left mouse button click on the "==" area show/hide numbers.











**To picking manual predict next drawings numbers:**  click  button picking the all Next Drawings numbers.



 






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
