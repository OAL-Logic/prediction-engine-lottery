# AC Analysis

> **Category:** 18 Statistical Analysis Methods (`05-statistical-analysis`)

## Introduction to the Statistical Analysis Interface



Lottery Studio and SamP3P4 lottery software offer 
over 10 methods of lottery historical data analysis. The professional analysis 
function is very useful for setting lottery filter condition parameters. You can 
customize the range of analyzed drawings data, Customized analysis statistics of 
drawings numbers at specified positions, and analyze the skips of each 
value.



- **1. **Customize the range of historical data statistics 
  analysis. 

- **2. **Mouse click on a column will automatically analyze and 
  count the information of the current column value. 

- **3. **Displays the current column Actual Skip information 
  for each value. 

- **4. **Set the statistical analysis is to calculate which 
  position of the drawings numbers.


.



---






Software Team All rights reserved.

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
