# Set the Number of the Specified Positions to Participate in the Calculation

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ Pick 3 Tic-Tac-Toe Generator  Free Lottery Software](pick-3-tic-tac-toe-generator-free-lottery-software.md) · [US Powerball Lottery Win Strategies and Tips Ultimate Guide(2022 Updated) ➡️](us-powerball-lottery-win-strategies-and-tips-ultimate-guide-2022-updated.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Set the Positions to Contain When Filtering](#set-the-positions-to-contain-when-filtering)
- [Set the Positions of the Filter Assistant Contain](#set-the-positions-of-the-filter-assistant-contain)
- [Set the Positions of the Statistical Analysis Contain](#set-the-positions-of-the-statistical-analysis-contain)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

Sometimes we just want the number combinations or drawings results in a given **position** to be **filtered**, counted, or analyzed. **[Lottery Studio](https://example.org/lottery-studio)** and **[SamP3P4](https://example.org/lottery-studio)** are All support this feature.

## Set the Positions to Contain When Filtering

Default program includes numbers for all positions (**Bonus** numbers are **not included** if the lottery has Bonus numbers).

For example, in the screenshot below, I select position 1, position 2, position 3, position 4, and position 5 to participate in the filter, Position 6 is not selected (in the Powerball lottery position 6 is the Bonus number).

![[attachments/41b54c8dc541d0b20eb9f6f70e7a787b_MD5.jpg]]

Base Filter Selected Positions

![[attachments/08a68b8d44fb493b277b8878518d57c2_MD5.jpg]]

Advanced Filter Selected Positions

## Set the Positions of the Filter Assistant Contain

Filters assistant contain positions and filtering contain positions should be selected in the same position when used, otherwise the bad combination cannot be filtered correctly.

![[attachments/231b9d4dfb82eb1ddbd82db4768886f6_MD5.jpg]]

Set Filter Assistant Participation Calculation Positions

## Set the Positions of the Statistical Analysis Contain

In the statistical analysis of historical drawings results, you can freely choose which positions to analyze only and ignore the positions that are not selected.

For example, in the screenshot below, I select position 1, position 2, position 3, position 4, and position 5 to analyze and statistics, Position 6 is not selected. So the program only counts the numbers in the first 5 positions.

![[attachments/3729731ea95a59c1204a5278589a0bc2_MD5.jpg]]

Set Which Position is Participating in the Statistics and Calculations

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
> **Next Steps**: [⬅️ Pick 3 Tic-Tac-Toe Generator  Free Lottery Software](pick-3-tic-tac-toe-generator-free-lottery-software.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [US Powerball Lottery Win Strategies and Tips Ultimate Guide(2022 Updated) ➡️](us-powerball-lottery-win-strategies-and-tips-ultimate-guide-2022-updated.md)
