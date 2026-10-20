# AC Analysis

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ Why Use Wheeling Systems](../04-wheeling-systems/why-use-wheeling-systems.md) · [Actual Skip ➡️](actual-skip.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [AC Analysis](#ac-analysis)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## AC Analysis





  Click menu->Statistics->AC to open the AC
analysis window.



Calculate the AC value of the current number combination.











---

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
> **Next Steps**: [⬅️ Why Use Wheeling Systems](../04-wheeling-systems/why-use-wheeling-systems.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 02. Functional Studio Manual](../INDEX.md) · [Actual Skip ➡️](actual-skip.md)
