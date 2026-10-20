# Successive Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Range Analysis](range.md) · [Sum Analysis ➡️](sum.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Successive Analysis](#successive-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

﻿








  
  
    

## Successive Analysis



Click 
menu->Statistics->Successive to open the 
Successive analysis.

**What is the successive 
number?**

The successive number is the adjacent number in a 
combination. For example 04 05 26 27 28 43, 04 05 and 26 27 28 are all 
successive numbers.l numbers into multiple number groups, then counts the number 
of hits of each range.

**Successive**: Count all adjacent numbers in a 
combination and find the group with the highest amount of adjacent numbers. For 
example 03 04 25 26 27 43, 03 04 and 25 26 27 are all the successive numbers, 03 
04 adjacent amount is 2, and 25 26 27 adjacent amount is 3, so 
Successive=3.

**Successive 
Groups**: Count all adjacent numbers in a combination and find the group 
amount of adjacent numbers. For example 03 04 25 26 27 43, 03 04 and 25 26 27 
are all the successive numbers, 03 04 is a group and 25 26 27 is a group, so 
Successive Groups=2.

**Odd 
Successive**: Count all odd adjacent numbers in a combination and find 
the group with the highest amount of odd adjacent numbers. For example 03 13 25 
26 27 43, 03 13 25 and 27 43 are all the odd numbers, 03 13 25 adjacent amount 
is 3, and 27 43 adjacent amount is 2, so Odd Successive=3..

**Even Successive**: Count all even adjacent numbers 
in a combination and find the group with the highest amount of odd adjacent 
numbers. For example 04 12 22 25 33 43, 04 12 22 are all the even numbers, the 
adjacent amount is 3, so Even Successive=3.



---






Team All rights reserved.

---

## Clean-Room Python Boilerplate

```python
def compute_successive_metrics(ticket_in_draw_order: list[int]) -> dict[str, int]:
    """
    Consecutive run metrics with the 'run >= 2 else 0' rule.
    """
    def _longest_and_groups(pred_fn) -> tuple[int, int]:
        longest = 0
        groups = 0
        run = 1
        for a, b in zip(ticket_in_draw_order, ticket_in_draw_order[1:]):
            if pred_fn(a, b):
                run += 1
            else:
                if run >= 2:
                    longest = max(longest, run)
                    groups += 1
                run = 1
        if run >= 2:
            longest = max(longest, run)
            groups += 1
        return (longest if longest >= 2 else 0), groups

    succ_len, succ_groups = _longest_and_groups(lambda a, b: abs(b - a) == 1)
    odd_len, _ = _longest_and_groups(lambda a, b: a % 2 == 1 and b % 2 == 1)
    even_len, _ = _longest_and_groups(lambda a, b: a % 2 == 0 and b % 2 == 0)
    return {
        "successive": succ_len,
        "successive_groups": succ_groups,
        "odd_successive": odd_len,
        "even_successive": even_len,
    }
```

---
> **Next Steps**: [⬅️ Range Analysis](range.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Sum Analysis ➡️](sum.md)
