# Range Analysis

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Range Analysis





  Click menu->Statistics->Range to open the Range 
analysis.



The program automatically splits all numbers into multiple number groups, then counts the number of hits of each range.









Use the Powerball as an example, as in the following screenshot, the 1-69 numbers automatically split into 5 groups of numbers.



**Group 01-13**: Counting the winning number of hits in the number group 01-13.

**Group 14-26**: Counting the winning number of hits in the number group 14-26.

**Group 27-39**: Counting the winning number of hits in the number group 27-39.

**Group 40-52**: Counting the winning number of hits in the number group 40-52.

**Group 53-69**: Counting the winning number of hits in the number group 53-69.











---

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
