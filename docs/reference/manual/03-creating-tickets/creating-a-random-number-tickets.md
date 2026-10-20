# Creating a Random Number Tickets

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Creating Positons Number Tickets](creating-a-positon-number-tickets.md) · [Creating Full Generate Number Tickets ➡️](creating-full-generate-number-tickets.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Creating Random Number Tickets or Smart Tickets](#creating-random-number-tickets-or-smart-tickets)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

## Creating Random Number Tickets or Smart Tickets








How to Creating a Random  or Smart Tickets List

①. In the Analysis Depth drop-down list, if you want to generate random tickets select "**Random Numbers**". If you want to generate smart tickets please select past drawings analysis depht.

②.  In the Generate drop-down list, select how many lines to generate.



③. Click Start...  button. 

④. Click Add to Tickets>>  button.







  Click OK, the all tickes will be saved in the tickets panel.



  

 

　

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
> **Next Steps**: [⬅️ Creating Positons Number Tickets](creating-a-positon-number-tickets.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Creating Full Generate Number Tickets ➡️](creating-full-generate-number-tickets.md)
