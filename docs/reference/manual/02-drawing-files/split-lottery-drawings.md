# Choose a Lottery

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Choose a Lottery](opening-a-lottery.md) · [Creating Positons Number Tickets ➡️](../03-creating-tickets/creating-a-positon-number-tickets.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Split Lottery Drawings](#split-lottery-drawings)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Drawing History & Game File Management (`02-drawing-files`)

## Split Lottery Drawings



**To Split  your lottery drawings**



On the Toolbar, click the Drawings button open edit drawings window.

2. Click  the Split  button open the split drawings window.

For example, the following screenshot, The current lottery draws 5 times a week, if you only want to keep Thursday's draw data. Select Thursday, then click Ok and the data for the other dates will be deleted.



  

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
> **Next Steps**: [⬅️ Choose a Lottery](opening-a-lottery.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Creating Positons Number Tickets ➡️](../03-creating-tickets/creating-a-positon-number-tickets.md)
