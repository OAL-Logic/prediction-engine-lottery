# Deleting a Drawing

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Adding a New Lottery](adding-a-new-lottery.md) · [Exporting and Importing Drawings.htm ➡️](exporting-and-importing-drawings.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Deleting a Draw](#deleting-a-draw)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Drawing History & Game File Management (`02-drawing-files`)

## Deleting a Draw



At times it may be necessary to 
delete a drawing that was previously entered in a drawing file.



To Delete a drawing:

1.On the Toolbar, click the Drawings 
button open the edit drawings form.

2. Click on the drawing that you want to delete in the drawing 
list. 

3. Click on the Delete button. 

4. Click the Yes button when you are 
asked to confirm the deletion. 

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
> **Next Steps**: [⬅️ Adding a New Lottery](adding-a-new-lottery.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Exporting and Importing Drawings.htm ➡️](exporting-and-importing-drawings.md)
