# Distance Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Base Analysis](base.md) · [Divided Analysis ➡️](divided.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Distance Analysis](#distance-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

﻿








  
  
    

## Distance Analysis



Click 
menu->Statistics->Distance to open theDistance 
analysis windows.

Distance is the value of the 
difference between the last number and first number.

**First-Last Distance**: The 
value of the difference between the last number and the first number. For 
example 11 15 17 30 41 51, the last number is 51, the first number is 11, so the 
First-Last Distance value is 51-11=40.

**Max Distance**: The values of 
the difference between the all adjacent two numbers. the largest value is Max 
Distance. For example 02, 05, 17, 19, 27, 31, the distance list : 3 (05-02=3), 
12 (17-05=12), 2 (19-17), 8 (27-19), 4 (31-27=4), so the max distance is 
12.

**Average Distance**: The 
values of the difference between the all adjacent two numbers, all values are 
added together and finally divide by the numbers amount. For example, 02, 05, 
17, 19, 27, 31, the distance is 3 (05-02=3), 12 (17-05=12), 2 (19-17=2), 8 
(27-19=8), 4 (31-27=4). (3+12+2+8+4)/5=5, so the distance average value is 
5.

**Different Distance**: The 
values of the difference between all adjacent two numbers, remove duplicate 
values, and count the amount. For example: 02, 05, 08, 19, 27, 31, the distance 
is: 3 (05-02=3), 3 (08-05=3), 11 (19-08=11), 8 (27-19=8), 4 (31-27=4), remove 
duplicates value 3, so the different distance is 4.



---






Team All rights reserved.

---

## Clean-Room Python Boilerplate

```python
def compute_drawn_order_distances(ticket_in_draw_order: list[int]) -> dict[str, int]:
    """
    Adjacent distances evaluated in drawn order (plus sort-invariant First-Last spread).
    """
    k = len(ticket_in_draw_order)
    adj_diffs = [abs(ticket_in_draw_order[i + 1] - ticket_in_draw_order[i]) for i in range(k - 1)]
    return {
        "first_last_distance": max(ticket_in_draw_order) - min(ticket_in_draw_order),
        "max_distance": max(adj_diffs) if adj_diffs else 0,
        "average_distance": sum(adj_diffs) // len(adj_diffs) if adj_diffs else 0,
        "different_distance": len(set(adj_diffs)),
    }
```

---
> **Next Steps**: [⬅️ Base Analysis](base.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Divided Analysis ➡️](divided.md)
