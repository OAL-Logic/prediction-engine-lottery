# Overview

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ How to Quick to Pick Numbers](how-to-quick-picked-numbers.md) · [Printing Tickets on Paper ➡️](printing-tickets-to-paper.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Overview](#overview)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

## Overview



Lottery Studio can 
generate lottery tickets with three different categories of numbers: full 
generate number, smart (wheels) number, positon number and random numbers.

We recommend that if you are just learning to use Lottery Studio that 
you create your tickets using wheels numbers. The program does all the work for 
you, and all your tickets will contain numbers that have the best statistical 
chance of hitting.

Once you are more experienced interpreting the charts and graphs 
in the Lottery Studio, you 
may want to play your own Favorite numbers, or a combination of Smart (wheels) 
and Favorite numbers. 

We don't recommend that you play tickets generated with Random 
numbers. The option is included mainly so that you compare random results with 
results obtained from playing Smart (wheels) or Favorite numbers.

When you generate tickets using any of the three categories of 
numbers you have two choices as to how the tickets are generated; generate the 
tickets using the wheeling system of your choice, or generate the number of 
tickets that you specify. 

In most cases it is better to generate your tickets with one of 
the wheeling systems. When you play a wheeling system, you are guaranteed a 
prize if a portion of the numbers you play match the actual numbers picked. 
There is no such guarantee when create your tickets using the other method. Your 
overall winnings are normally larger when you play a wheeling system because you 
will have several tickets with winning matches. 

You normally choose a wheeling system based on how much you can 
afford to spend and the prize guarantee associated with the system. If you can 
only afford to play a small number of tickets, you can apply filters to your 
lottery tickets to eliminate tickets with unlikely number 
combinations.

When generated lines, you can use a lot of fiters to 
filtering line (supported 50 base filters, 18 advanced filters), remove all bad 
lines.

You also can edit your tickets, Lottery Studio 
support add, delete, save, export to file, import from file, print tickets to 
paper, add bouns and formate export.


---




Team All rights reserved.

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
> **Next Steps**: [⬅️ How to Quick to Pick Numbers](how-to-quick-picked-numbers.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Printing Tickets on Paper ➡️](printing-tickets-to-paper.md)
