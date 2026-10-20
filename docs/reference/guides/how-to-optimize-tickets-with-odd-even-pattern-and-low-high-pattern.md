# How to Optimize Tickets with Odd-Even Pattern and Low-High Pattern

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ How to Generate Pick 3 Pick 4 Lottery Combinations](how-to-generate-pick-3-pick-4-lottery-combinations.md) · [How to Set Filter Fault Tolerance to Avoid Losing the Big Prize ➡️](how-to-set-filter-fault-tolerance-to-avoid-losing-the-big-prize.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

  - [What is Odd-Even Pattern and Low-High Pattern？](#what-is-odd-even-pattern-and-low-high-pattern)
  - [Statistics and Analysis Past Drawings Odd-Even Pattern and Low-High Pattern](#statistics-and-analysis-past-drawings-odd-even-pattern-and-low-high-pattern)
  - [How to Optimize Tickets](#how-to-optimize-tickets)
  - [Summary](#summary)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

### What is Odd-Even Pattern and Low-High Pattern？

In a ticket, the odd number is marked by the first letter O of Odd and the even number is marked by the first letter E of Odd, and then identify the even-odd pattern using the EOE or EEO pattern, etc. In addition, the High and low would also read in this way such as HHH or LLL, etc.

As an example, here are the tickets and their corresponding Odd-Even Pattern and Low-High Pattern

| **Drawings** | **Odd-Even Patterns** | **Low-High Patterns** |
| --- | --- | --- |
| 3 9 2 | OOE | LHL |
| 4 8 1 | EEO | LHL |
| 7 6 3 | OEO | HHL |
| 0 1 9 | EOO | LLH |

Odd-Even Pattern and Low-High Pattern

In the Pick 3 lottery, all Odd-Even Pattern and Low-High Pattern are as below:

| **All Odd-Even Patterns** | **All Low-High Patterns** |
| --- | --- |
| EEE | LLL |
| EEO | LLH |
| EOE | LHL |
| EOO | LHH |
| OEE | HLL |
| OEO | HLH |
| OOE | HHL |
| OOO | HHH |

**Odd-Even** **Low-High Patterns**

### Statistics and Analysis Past Drawings Odd-Even Pattern and Low-High Pattern

SamP3P4 supports statistics and analysis of past drawings Odd-Even Patterns and Low-High Patterns. The following two screenshots show the statistics and analysis of Odd-Even Pattern and Low-High Pattern for the past 20 drawings.  
  
According to the statistics, EOO has appeared 5 times in the last 20 drawings, and OEO has not appeared in 11 drawings. Let’s analyze Low-High Pattern, HHH and HLL both appeared 5 times, HLH HLH has not appeared for 18 drawings. With this data, we can find more patterns so that we can set optimization parameters more accurately.

![[attachments/6365be278fcfe701ac2a08ab3ec24886_MD5.jpg]]

Odd-Even Pattern

![[attachments/e3fb024e39ef5ae34a3b3795a6cb1275_MD5.jpg]]

Low-High Pattern

### How to Optimize Tickets

The following animation demonstrates that EEE, EOO, OOO, HHL, HLL are unchecked. These Patterns’ tickets will be deleted.

![[attachments/94d581759bb30f39475783a9c05cf6d2_MD5.gif]]

### Summary

If you have any suggestions or tips for picking lottery numbers share your ideas

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
> **Next Steps**: [⬅️ How to Generate Pick 3 Pick 4 Lottery Combinations](how-to-generate-pick-3-pick-4-lottery-combinations.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [How to Set Filter Fault Tolerance to Avoid Losing the Big Prize ➡️](how-to-set-filter-fault-tolerance-to-avoid-losing-the-big-prize.md)
