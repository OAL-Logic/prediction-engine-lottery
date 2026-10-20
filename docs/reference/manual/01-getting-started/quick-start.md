# Quick Start

> **Category:** Getting Started & Studio Overview (`01-getting-started`)

## Quick Start



Follow the instructions below to start using Lottery Studio 
right away. The steps should be performed in the order listed. Please refer to 
the other chapters in this help file for more detailed information.

**To open your lottery:** On the Toolbar, click the 
Lottery button open the select lottery form. Click on 
the name of the lottery you want to play. Click the Ok 
button.



**To update your lottery file with the latest 
drawings:** On the Toolbar, click the Drawings 
button open the Drawings Form. Click the Add button 
add numbers, click the Update button online update 
drawings data.



**To create your lottery tickets:** Lottery Studio 
support Standard, Wheel, Positoin and Random Mode create the tickets. Click Generate Tickets button add the tickets to the tickets 
form.


**To filtering 
tickets:** Checked your selected filters and set the filter conditoin 
then click Start Filtering button.

**To Edit 
tickets:** You can edit, add, delete, save, export, formate export, 
import and print tickets.


**To Check Winning tickets:** On the Toolbar, 
click the Check Win button show the check winning 
window.




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
