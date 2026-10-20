# How to Count Each Number Hit Times of Occurrence in Bets Tickets

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ How to Choose Lottery Numbers](how-to-choose-lottery-numbers.md) · [How to Generate All Possible Combinations by Positions ➡️](how-to-generate-all-possible-combinations-by-positions.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Why Count Each Number Hit Times of Occurrence in Bets Tickets](#why-count-each-number-hit-times-of-occurrence-in-bets-tickets)
- [Generate Full Combinations Without Using the Wheeling Formula and Filters](#generate-full-combinations-without-using-the-wheeling-formula-and-filters)
- [Filter Combinations Using Filters](#filter-combinations-using-filters)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

you can **count** the number of times each number appears in betting combinations.

## Why Count Each Number Hit Times of Occurrence in Bets Tickets

We know that if combinations are generated using the full combination generator (without using the wheeling formula and filters). The hit times of occurrences of each number in the combination are the same. If you use wheeling or filter, the hit times that each number appears in the combination are different.

## Generate Full Combinations Without Using the Wheeling Formula and Filters

In the following screenshot, we have selected 21 numbers and used the Full generator to generate the **complete combinations**, and clicked on the “ **Menu -> Numbers Hit** ” button in the Tickets Store area to count the number of times all the numbers appear in the combinations.

Through the screenshot below we find that all numbers appearing times are the same.

![[attachments/016962a67a29c5270b2c90e7db97c667_MD5.jpg]]

## Filter Combinations Using Filters

These numbers and combinations were filtered using filter that removed almost 50% of the combinations. Re-hits numbers, as in the screenshot below, the number hits sorting has changed.

![[attachments/a56e1d0ced854c64c7ec40191c4513d0_MD5.jpg]]

**35, 43, 52, 61, 26, 20, 47** These numbers **appeared more than 3000 times**, so we should focus on these numbers

---

## Clean-Room Python Boilerplate

```python
def compute_ac_value(ticket: list[int]) -> int:
    """
    Arithmetic Complexity (AC):
    AC = #{distinct positive pairwise differences} - (k - 1)
    """
    k = len(ticket)
    diffs = {abs(a - b) for i, a in enumerate(ticket) for b in ticket[i + 1 :]}
    return len(diffs) - (k - 1)
```

---
> **Next Steps**: [⬅️ How to Choose Lottery Numbers](how-to-choose-lottery-numbers.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [How to Generate All Possible Combinations by Positions ➡️](how-to-generate-all-possible-combinations-by-positions.md)
