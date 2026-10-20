# Hot-Cold Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Drawings Analysis](drawings.md) · [AC Analysis ➡️](introduction-to-the-statistical-analysis-interface.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Hot-Cold Analysis](#hot-cold-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Hot-Cold Analysis





  Click menu->Statistics->Hot-Cold  to open the Hot-Cold
analysis window.



**Hot Number**: Counts the drawings before the current draw. The number of times each number has appeared, the number with the most hits is the hot number.



  **Cold Number**: Counts the drawings before the current draw. The number of times each number has appeared, the number with the less often hits is the cold number.



  **Warm Number**: Numbers other than hot and cold numbers.



  **Hot Same Count**: Count of the hot numbers repeats found in the previous 1 draw winning combination.



  **Cold Same Count**: Count of the cold numbers repeats found in the previous 1 draw winning combination.



  **Warm Same Count**: Count of the warm numbers repeats found in the previous 1 draw winning combination. Numbers other than hot and cold numbers are all warm numbers.











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
> **Next Steps**: [⬅️ Drawings Analysis](drawings.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [AC Analysis ➡️](introduction-to-the-statistical-analysis-interface.md)
