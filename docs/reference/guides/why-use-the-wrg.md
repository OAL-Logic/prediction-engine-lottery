# Why use the WRG

## Why Use the WRG

WRG = **Wheel Reduction Guarantee**. The WRG is designed to enable a player to play more numbers. WRG can **quickly eliminate combinations** without changing the distribution of numbers in all combinations. Bet on few tickets and play more numbers.

## How to Use WRG

When we use the wheels and the filter after, there are still so many combinations, this time we can use WRG! You can change the combinations to 80% 50% 30% 20% 10% 5%.

What they mean:

80% – Eliminate about 20% of combinations.  
50% – Eliminate about 20% of combinations.  
30% – Eliminate about 70% of combinations.  
20% – Eliminate about 80% of combinations.  
10% – Eliminate about 90% of combinations.  
5% – Eliminate about 95% of combinations.

## For an Example of Mega Millions

Selected 26 numbers

Full generate 65780 combinations. Mega Millions one combination costs $2.00 per play, total of 65780 lines will cost $131,560.

This cost too much, we can’t afford it! So you need to use the wheeling formula.

After using the wheeling, total of 1558 lines, will cost $3,116. The amount of money invested is still too much, we continue to use the filtering function to filter out more lines.

We randomly selected 26 filters, total filtered out 784 bad lines. Finally, there are 774 lines, which will cost $1,548.

As shown below:

![](https://example.org/lottery-studio)

But I just want to spend $50-100 to go betting. How to do?

So we need to use the WRG function, we choose 5%, This will eliminate the 95% tickets, and finally 38 lines, will only cost $76.

![](https://example.org/lottery-studio)

## Summary

If you are interested **Lottery Studio & SamP3P4 lottery software** you can [download](https://example.org/lottery-studio) and use the free version, you can use most of the features and the statistical analysis module is completely free!

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
