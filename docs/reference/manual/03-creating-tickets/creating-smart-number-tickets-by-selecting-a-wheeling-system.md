# Creating Smart Number Tickets by Selecting a Wheeling System

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Creating Full Generate Number Tickets](creating-full-generate-number-tickets.md) · [Editing  Tickets ➡️](editing-tickets.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Creating Smart Number Tickets by Selecting a Wheeling System](#creating-smart-number-tickets-by-selecting-a-wheeling-system)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Ticket Generation & Line Editing (`03-creating-tickets`)

﻿








  
  
    

## Creating Smart Number Tickets by Selecting a Wheeling System






To Creating Smart Number Tickets by Selecting a Wheeling 
System:

①.On the numbers panel, selecting your like numbers, If the 
number is selected will become a Red button. If you want to cancel selection, please 
use the mouse to click the specified number.

②. In the radio box, select Wheels Generator, In the drop-down list, select a 
formula.

③. Click Generate Tickets button. 




Then 
the all tickes will be saved in the tickets panel. 





 

---

---

## Clean-Room Python Boilerplate

```python
from itertools import combinations

def apply_wheel_template(pool: list[int], index_template: list[list[int]]) -> list[list[int]]:
    """Map a 1-based combinatorial wheel template onto a sorted candidate pool."""
    ordered_pool = sorted(pool)
    return [sorted(ordered_pool[idx - 1] for idx in row) for row in index_template]

def verify_wheel_guarantee(
    tickets: list[list[int]],
    pool: list[int],
    draw_hit_count: int,
    guarantee_tier: int,
) -> dict[str, int | float]:
    """Verify m-if-t covering guarantee across all C(v, t) possible draw subsets of the pool."""
    ticket_sets = [set(t) for t in tickets]
    scenarios = list(combinations(pool, draw_hit_count))
    covered = sum(
        1 for s in scenarios if any(len(t & set(s)) >= guarantee_tier for t in ticket_sets)
    )
    return {
        "total_scenarios": len(scenarios),
        "covered_scenarios": covered,
        "coverage_pct": round(100.0 * covered / max(1, len(scenarios)), 2),
    }
```

---
> **Next Steps**: [⬅️ Creating Full Generate Number Tickets](creating-full-generate-number-tickets.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Editing  Tickets ➡️](editing-tickets.md)
