# How to Verify

> **Category:** Prediction Formulas, Trends & Verification (`07-prediction-and-trends`)

## How to Verify




  Verification is the program can now accurately record its own prediction history. This feature is very useful as it helps us to analyze the prediction accuracy of each prediction formula and algorithm.**





  1. To verify  prediction accuracy



  **On the Toolbar, click the 
  Prediction button then click Verification open the verify tab. Select one formula click Verification button to verify**.**.
 




  **2. To verify bonus Number**



 If the lottery game has the bonus number, the Verification Bonus button will display. click Verification Bonus button to verify bonus number**.3. To change verify past drawings ranges**



  After selecting the range of drawings, you need to re-click  Verification or Verification Bonus button to verify**.**







 

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
