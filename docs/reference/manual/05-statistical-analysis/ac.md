# AC Analysis

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
