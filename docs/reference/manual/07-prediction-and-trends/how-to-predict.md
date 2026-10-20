# How to Predict

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ What is AC ?](../06-filtering-system/what-is-ac.md) · [How to Use Drawings Trend ➡️](how-to-use-drawings-trend.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [How to Predict](#how-to-predict)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Prediction Formulas, Trends & Verification (`07-prediction-and-trends`)

## How to Predict



**1. To predict  lottery:** On the Toolbar, click the 
  Prediction button then click Predictor open the predictor tab. Select a formula click Predict Now button to predict next drawing numbers now.
 












**2. To add the prediction numbers to picking numbers panel: ** click the button pop-up dialog box, and then click the Yes button.







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

---
> **Next Steps**: [⬅️ What is AC ?](../06-filtering-system/what-is-ac.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [How to Use Drawings Trend ➡️](how-to-use-drawings-trend.md)
