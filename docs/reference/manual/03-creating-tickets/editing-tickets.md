# Editing  Tickets

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Creating Smart Number Tickets by Selecting a Wheeling System](creating-smart-number-tickets-by-selecting-a-wheeling-system.md) · [How to Quick to Pick Numbers ➡️](how-to-quick-picked-numbers.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Editing Tickets](#editing-tickets)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

## Editing Tickets



Lottery Studio software supports analysis, statistics and editing of your betting tickets. Some times you need edit your tickets lines, Lottery Studio support add, delete, save, export to file, import from file, print tickets to paper, add bouns and formate export.



Click Menu button or Right-click Pop-up  edit tickets menu:









  **Save Tickets File **- Save tickets list to the tickets file.



  **Load   Tickets File** - Load tickets list from the tickets file.



  **Load   Drawings** - Load previous drawings results. suppors load previous 10 drawings, past 20 drawings, past 30 drawings, past 50 drawings, past 100 drawings, past 200 drawings, past 500 drawings and All drawings.



  **Save To Txt File** - Save   tickets list to Txt file.



  **Load From Txt File** - Load tickets list from   Txt file.



  **Formate Export** - Formate export tickets to txt file.



  **Add Ticket** - Add a ticket.



  **Delete Ticket** - Delete   a line.



  **Sort: Low to High ** - For each line, the numbers are re-ordered from smallest to largest



  **Copy Selected** - Copy the selected area.



  **Add Bonus   Number **- In the last position of each line, add the bonus number.



  **Numbers Hits - **Statistic every number appear times in all tickets and sort all number that appears.


  
  **Delete 'x' Tag Tickets **-    Delete Tag = "X" in lines.



  **Delete ' ' Tag Tickets **-  Delete Tag   = " " in lines.



  **Clear All Tickets** - Clear the all   lines.



  **Print Tickets** - Print tickets lines to paper.



  **Filters Report** - Display the most recent filter report.

　

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
> **Next Steps**: [⬅️ Creating Smart Number Tickets by Selecting a Wheeling System](creating-smart-number-tickets-by-selecting-a-wheeling-system.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [How to Quick to Pick Numbers ➡️](how-to-quick-picked-numbers.md)
