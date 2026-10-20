# Prior Drawing Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Odd-Even Analysis](odd-even.md) · [Range Analysis ➡️](range.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Previous Drawing Analysis](#previous-drawing-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Previous Drawing Analysis





  Click menu->Statistics->Previous Drawing to open the Prior Drawing
analysis window.

Count of the numbers repeats found in the previous draw winning combination.

**Previous 1 Draw:** Counts of the numbers repeats found in the previous 1 draw winning combination.

  **Previous 2 Draw**: Counts of the numbers repeats found in the previous 2 draw winning combination.

  **Previous 3 Draw**: Counts of the numbers repeats found in the previous 3 draw winning combination.

  **Previous 4 Draw**: Counts of the numbers repeats found in the previous 4 draw winning combination.

  **Previous 2 Draws**: Counts of the numbers repeats found in the previous 1 draw + previous 2 draw winning combinations.

  **Previous 3 Draws**: Counts of the numbers repeats found in all previous 3 draws winning combinations.

  **Previous 4 Draws**: Counts of the numbers repeats found in all previous 4 draws winning combinations.

  **Previous 5 Draws**: Counts of the numbers repeats found in all previous 5 draws winning combinations.









  

---

---

## Clean-Room Python Boilerplate

```python
def compute_actual_skips(draws: list[list[int]], number: int) -> dict[str, float | int | list[int]]:
    """Compute current skip (draws since last hit), average skip, and historical skip series."""
    skips: list[int] = []
    gap = 0
    for draw in draws:
        if number in draw:
            skips.append(gap)
            gap = 0
        else:
            gap += 1
    current_skip = gap
    avg_skip = sum(skips) / len(skips) if skips else float(len(draws))
    return {"current_skip": current_skip, "avg_skip": round(avg_skip, 2), "history": skips}
```

---
> **Next Steps**: [⬅️ Odd-Even Analysis](odd-even.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Range Analysis ➡️](range.md)
