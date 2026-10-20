# Sum Analysis

> **Category:** Historical Combination & Pattern Search (`08-optimization-and-search`)

﻿








  
  
    

## How to Use Search Past Drawings




Click 
Toolbar->Search to open the Search Past Drawings.


The following animation demonstrates how to use Search Past Drawings.



After the search is completed, the program will count the number of appears and skips of the number combinations. And a detailed list of which drawings show these number combinations.





As shown below animation, first we select the search for the past 360 drawings data, and then a search list of all two number combinations is automatically generated. Finally, click the 'Search' button.





After the search is completed we can sort the search results, as shown below we put the combination of the two numbers with the most occurrences at the front, click the mouse, the right column will list all the Drawings with the current number combination.









---






Team All rights reserved.

---

## Clean-Room Python Boilerplate

```python
from itertools import combinations

def optimize_ticket_set(tickets: list[list[int]], target_match: int = 3) -> list[list[int]]:
    """
    Greedy sub-combination coverage reduction (Ticket Optimizer / WRG reducer):
    Eliminates redundant tickets whose C(k, target_match) tuples are already covered.
    """
    seen_tuples: set[tuple[int, ...]] = set()
    kept: list[list[int]] = []
    for t in tickets:
        t_sorted = sorted(t)
        tuples = set(combinations(t_sorted, target_match))
        if not tuples.issubset(seen_tuples):
            kept.append(t_sorted)
            seen_tuples.update(tuples)
    return kept
```
