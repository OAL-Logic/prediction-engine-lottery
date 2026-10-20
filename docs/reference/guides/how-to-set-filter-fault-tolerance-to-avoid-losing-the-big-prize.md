# How to Set Filter Fault Tolerance to Avoid Losing the Big Prize

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ How to Optimize Tickets with Odd-Even Pattern and Low-High Pattern](how-to-optimize-tickets-with-odd-even-pattern-and-low-high-pattern.md) · [How to Use Lottery Analysis Studio Filters to Eliminate Bad Tickets ➡️](how-to-use-lottery-analysis-studio-filters-to-eliminate-bad-tickets.md)

When we use many filters at the same time, If there is a conditional parameter set error, we will lose the big prize.

**How to remedy this mistake?**

**We need to set the Filter Fault Tolerance.**

On the left side of the “Star Filtering” button, have a Logical Condition Combox, before filtering, you can set the fault tolerance here. There are only two options by default, “AND” or “OR”.

![[attachments/8bd22165a523dbaf35047912be440673_MD5.jpg]]

The default parameter of the Logical Condition is “AND”, which means that the combination does match the all selected filters conditions that will be included. If you select “OR” which means that the combination does match the one, or more selected filters conditions will be included.

The following example will step by step how to use Filter Fault Tolerance.

We use the lottery data of Mega Millions 10/29/2019.

First, randomly select some numbers and generate combinations, these numbers must contain Mega Millions 10/29/2019 winning numbers: 04 09 17 27 39

Then automatically generate Mega Millions 10/29/2019 winning numbers base conditions (Menu->Generate Current Drawings Conditions (10/29/2019))

Randomly selected 10 filters:

```
Even Count=1
High Count=1
Prime Count=1
Number Sum=96
Average Value=19
Unit Number Different Count=3
Minimum Number=4
Max Distance=12
AC=6
Lowest 4 Units Count=4
```

Then start filtering, because the set filter conditions are all correct, so the winning condition will be included.

![[attachments/f63dab6ce735ae57e1011682e511dad0_MD5.jpg]]

Next, to test, we set an error filter parameter, modify High Count to 2, and then filtering.

What happens?

All the lines were filtered out. We lose the big prize.

![[attachments/66b8257e72998a0beab332cfe6a02fb4_MD5.jpg]]

**How can we avoid this?**

We need to use the Filtering **Fault Tolerance**, set Logical Condition to 9-10, which means that the combination does match 9-10 selected filter conditions will be included.

![[attachments/ed74cfd3fe8ddb2f63f04596d333d077_MD5.gif]]

After setting up the filter Fault Tolerance, we rerun the filters and even though there is a filter we set wrong, the big prize is still included.

![[attachments/36671c48d58127d8f3a98f8ed04d2e8d_MD5.jpg]]

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
> **Next Steps**: [⬅️ How to Optimize Tickets with Odd-Even Pattern and Low-High Pattern](how-to-optimize-tickets-with-odd-even-pattern-and-low-high-pattern.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [How to Use Lottery Analysis Studio Filters to Eliminate Bad Tickets ➡️](how-to-use-lottery-analysis-studio-filters-to-eliminate-bad-tickets.md)
