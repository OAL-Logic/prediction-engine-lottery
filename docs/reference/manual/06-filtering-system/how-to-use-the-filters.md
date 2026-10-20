# How to use the filter

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ How to Use Average Distance](how-to-use-lottery-software-filters-to-filtered-out-bad-combinations.md) · [What is AC ? ➡️](what-is-ac.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Filters Overview](#filters-overview)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** Base & Advanced Filtering Pipeline (`06-filtering-system`)

﻿








  
  
    

## Filters Overview



Sometimes, we need use filters to remove some of the 
low probability of the tickets.
Lottery Studio supported more than 50 base filters 
and 18 advanced filters to filtering tickets.


Questions:

  
  
    
    
    
  
    
    
    
  
    
    

| 1. Base Filters. | 2. Advanced Filters. | 3. What is the "Logical Condition" ? |
| --- | --- | --- |
| 4. How to set the base filters condition ? | 5. How to set the advanced filters condition ? | 6. How to use the filters assistant ? |
| 7. What is "Filtering Contain Position" ? | 8. What is "Generate Default Condition" ? | 9. What is "Filtering Report" ? |



**1. Base Filters

**In the Setup Two 
Panel click "Base Filters" sheet dispaly the base filters 
panel:

Supports 50+ filters. if you want get about base filters 
explain click here.

2. Advanced Filters.

In the 
Setup Two Panel click "Advanced Filters" sheet dispaly the advanced filters 
panel:

Supports 20+ advanced filters, if you want get about advanced 
filters explain click here.

**3. What 
is the "Logical Condition"?**

In filter panel you can set logical condition,  if logical 
condition = "AND" when you start filtering all selected filters conditions must 
correct, if logical condition = "OR" only need one filter condition 
correct.

you can set logical condition yourself, for example: if we 
selected 5 filters, we can set the logical condition = "3-5", this is a 
Fault-tolerant function.

**4. How to set the base 
filters condition?

**In base filters panel clickwill dispaly 
the base filters window:

Click 
"Assistant" button you can see the current filter statistic and chart, input your condition value, click 
"Ok" button to save condition.

**5. How to set the 
advanced filters condition?

**In filters panel cickdisplay the advanced filter window:

Click "Assistant" button see 
current filter statistic and chart, input your condition value, click "Ok" button save condition.

**6. How to use the filters 
assistant?

**

Click 
"Assistant" button you can see the current filter 
chart:

We 
can use the chart set the filters conditions, for example: we can see Odd 
filter: value 1 appear  5 times, value 2 appear 5 times, value 3 appear 4 
times, value 4 appear 2 times, value 5 appear 2 time, in this way we can set the 
Odd conditions: 1-5.

**7. What is "Filtering Contain 
Position"?**

If we 
selected the position: 1,2,3,4,5, when filtering it's only filter the lines 
position: 1,2,3,4,5. 

8. What is "Generate Default 
Condition"?



System automation statistic the 
history drawings (default statistic the last 20 drawings), automation enter 
filters conditions. "Generate Default Condition" only 
support the base filter!
Now support last 20, 2, 3, 5, 10, 30 and 50 
drawings.



9. What is "Filtering Report"?



Click "Filtering Report" will dispaly the last filters report 
window:



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
> **Next Steps**: [⬅️ How to Use Average Distance](how-to-use-lottery-software-filters-to-filtered-out-bad-combinations.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [What is AC ? ➡️](what-is-ac.md)
