# Creating Full Generate Number Tickets

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Creating a Random Number Tickets](creating-a-random-number-tickets.md) · [Creating Smart Number Tickets by Selecting a Wheeling System ➡️](creating-smart-number-tickets-by-selecting-a-wheeling-system.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Creating Full Generate Number Tickets](#creating-full-generate-number-tickets)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

## Creating Full Generate Number Tickets





To Creating Full Generate Number Tickets:

Setup 1: In the numbers panel, selecting your like numbers, If 
the number is selected will become  Red. If you want to cancel selection, 
please use the mouse to click the specified number.

Setup 2: In the radio box, selected Full 
Generator.

Setup 3: Click Generate Tickets 
button.

Click OK, the all tickes will be 
saved in the tickets panel.



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
> **Next Steps**: [⬅️ Creating a Random Number Tickets](creating-a-random-number-tickets.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Creating Smart Number Tickets by Selecting a Wheeling System ➡️](creating-smart-number-tickets-by-selecting-a-wheeling-system.md)
