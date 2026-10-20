# What is AC ?

> **Category:** Base & Advanced Filtering Pipeline (`06-filtering-system`)

﻿








  
  
    

## What is AC



AC value called Arithmetic Complexity value is a value which is 
calculated to determine the variation of differences among all numbers in one 
lottery combination.

(It) is an important parameter of assessing (a) type (of) 
lottery ticket number value. 

(Within) the lottery ticket, mean,( deduct of difference 
between?) any group all two positive number value(s) that total amount (of the?) 
number of figure(s) in the number in R/S (Lotto), 

among them R is counted for the bet number. 

For example: 

In lottery tickets of 7/35, it is 01, 05, 09, 13, 18, 26, 34 to 
elect the number, 

straight difference between these 7 numbers 

figures is: 4(=5-1=9-5=13-9); 5(=18-13); 
8=(9-1=13-5=26-18=34-26); 12(=13-1); 17(=18-1); 25(=26-1=34-9); 33(=34-1); 
13(=26-13=18-5); 9(=18-9); 21(=26-5=34-13); 29(=34-5); 17(=26-9); 16(=34-18). 


The above has 13 (instances) of difference, namely: 

4, 5, 8, 12, 17, 25, 33, 13, 9, 21, 29, 17, 16 in all, because 
of R =7, complicated value =13-(7-1) =7. 

It is 0 that AC is worth the minimum, the maximum :

It is 15 hour in 7 basic numbers, (not a clue on what the 
‘hour' issue might be)

6 basic numbers are 10 at (AC?), 5 basic numbers are 6 at 
(AC?).

The larger complicated value is, the more complicated the 
arithmetic series of the numbers. (Also), the worse the regularity is, and the 
(greater the) randomness. 

(If you consider) the number with too many arithmetic series, 
its complicated value is relatively low, (and the randomness becomes 
correspondingly greater). The risk of obtaining the winning number inside a bond 
can also be lower when that occurs. 

The number all formed by arithmetic series, complicated value 
can be 0.


Date....Drawings..AC.Value

1/02/2006 6 4 9 = 3
1/03/2006 9 4 3 = 3
1/04/2006 8 5 3 = 
3
1/05/2006 6 8 7 = 2
1/06/2006 6 0 7 = 3
1/07/2006 8 3 7 = 3


---




Team All rights reserved.

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
