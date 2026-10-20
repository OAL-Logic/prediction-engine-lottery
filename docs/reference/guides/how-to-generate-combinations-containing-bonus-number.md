# How to Generate Combinations Containing Bonus Number

We know that in some of the most popular lotteries around the world, there is a **Bonus**  
number, where all the numbers and bonus numbers are guessed to win the prize pool. In the Powerball lottery the Bonus is called red Powerball, In the Mega Millions the bonus called gold Mega Ball.

So If you want to win the jackpot, you must choose the correct bonus number.

## How to Select Bonus Numbers

[Lottery Studio](https://example.org/lottery-studio) lottery software supports adding Bonus ticket combinations. The animation below shows how to manually add Powerball lottery Bonus numbers

![[attachments/b6d39207ebd45a607a73fef27dbd0282_MD5.gif]]

Lottery Analysis Studio Picking Bonus Numbers

## How to Add Bonus to the Tickets Combinations

After selecting the bonus number, you have to select the combination of bonus **generation mode** l， **Lottery Studio** offers **3 models** **All, In turn, and Random**.

![[attachments/711c3f700a3cf19edcc2da5998edb9bc_MD5.jpg]]

3 Modes

#### Model 1: All

This model adds all bonus numbers for each combination from the bonus numbers we selected. If you choose a number that contains all the winning numbers, you are 100% guaranteed to win the Top Prize! The problem with this mode is that it will increase your bets exponentially!  
  
For example, the Powerball lottery **selects 6 numbers + 2 bonus numbers 08 11 15 20 23 56 + 03 15**.  
  
Generate only 6 lines of combinations that **do not contain two bonus** numbers  
  
ID Tickets  
1 08 11 15 20 23  
2 08 11 15 20 56  
3 08 11 15 23 56  
4 08 11 20 23 56  
5 08 15 20 23 56  
6 11 15 20 23 56

Generate 12 lines of combinations that **contain two bonus** numbers

ID Tickets  
1 08 11 15 20 23 03  
2 08 11 15 20 23 15  
3 08 11 15 20 56 03  
4 08 11 15 20 56 15  
5 08 11 15 23 56 03  
6 08 11 15 23 56 15  
7 08 11 20 23 56 03  
8 08 11 20 23 56 15  
9 08 15 20 23 56 03  
10 08 15 20 23 56 15  
11 11 15 20 23 56 03  
12 11 15 20 23 56 15

#### Model 2: In Turn

Use this model each bonus number is added to the combination **in order** from the bonus numbers we selected, without increasing the total number of combinations. If you choose a number that contains all the winning numbers, NOT guaranteed to win the Top Prize! The advantage of this model is that it **does not** increase the total betting amount.  
  
For example, the Powerball lottery **selects 6 numbers + 2 bonus numbers 08 11 15 20 23 56 + 03 15**.  
  
Generate 6 lines of combinations that **do not contain two bonus** numbers  
  
ID Tickets  
1 08 11 15 20 23  
2 08 11 15 20 56  
3 08 11 15 23 56  
4 08 11 20 23 56  
5 08 15 20 23 56  
6 11 15 20 23 56

Generate 6 lines of combinations that **contain two bonus** numbers

ID Tickets  
1 08 11 15 20 23 03  
2 08 11 15 20 23 15  
3 08 11 15 20 56 03  
4 08 11 15 20 56 15  
5 08 11 15 23 56 03  
6 08 11 15 23 56 15

#### Model 2: Random

Using this mode will randomly add bonus numbers from the bonus numbers we selected, without increasing the total number of combinations. If you choose a number that contains all the winning numbers, NOT guaranteed to win the Top Prize! The advantage of this model is that it **does not** increase the total betting amount.  
  
For example, the Powerball lottery **selects 6 numbers + 2 bonus numbers 08 11 15 20 23 56 + 03 15**.  
  
Generate 6 lines of combinations that **do not contain two bonus** numbers  
  
ID Tickets  
1 08 11 15 20 23  
2 08 11 15 20 56  
3 08 11 15 23 56  
4 08 11 20 23 56  
5 08 15 20 23 56  
6 11 15 20 23 56

Generate 6 lines of combinations that **contain two bonus** numbers

ID Tickets  
1 08 11 15 20 23 03  
2 08 11 15 20 23 15  
3 08 11 15 20 56 15  
4 08 11 15 20 56 03  
5 08 11 15 23 56 03  
6 08 11 15 23 56 15

#### Summary

If you are interested **Lottery Analysis Studio** you can [download](https://example.org/lottery-studio) and use the free version, you can use most of the features and the statistical analysis module is completely free!

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
