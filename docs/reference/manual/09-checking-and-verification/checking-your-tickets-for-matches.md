# Check Winning

> **Category:** Prize Tier & Winning Ticket Verification (`09-checking-and-verification`)

## Check Winning



Before you check winning, you should ensure that your drawing 
file is the latest. Lottery Studio will check the lottery tickets that in Tickets 
Stroe panel.

In the toolbar, click " Check Win" 
button open the check winning windo.

How to 
checking win tickets?

â‘? Choose a draw.

â‘? Choose matching =, >, <, 
>= or <=.

â‘? Choose matching amount of numbers.

â‘? 
Click "Check Now" button.

The correct tickets 
will be displayed in the matching tickets panel. 

**Check Bonus numbers**

If the current 
lottery supports bonus numbers, the Bonus checkbox will display. If checked, 
only combinations that match the bonus number will also be 
displayed.

To Save Matching 
Tickets:

Right-click pop-up 
menu

**Save To Html** - Save 
the correct tickets to htm file.
**Save To Txt** - Save the 
correct tickets to txt file.
**Save To 
Excel** - Save the correct tickets to xls file.
**Clear** - Clear the correct tickets.

---




reserved.

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
