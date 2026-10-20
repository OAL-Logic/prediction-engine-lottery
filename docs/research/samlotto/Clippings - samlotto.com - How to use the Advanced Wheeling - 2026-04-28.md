---
title: How to use the Advanced Wheeling
sources:
  - https://www.samlotto.com/how-to-use-the-advanced-wheeling/
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
handles:
published: 2021-02-24T09:39:12-03:00
created: 2026-04-28T22:34:59-03:00
modified: 2026-04-28T22:34:59-03:00
description:
tags:
  - libraries/clippings
activities:
---
## Rearrange the Selected Numbers Position

When we use the wheeling formula to generate number combinations, The default is to generate combinations in the order from smallest to largest. We know that when we use the wheeling formula. The number in front of the position appears more often in all combinations. Different number positions will generate different combination results.

For example, we chose 13 numbers, the number order is 08 11 20 23 36 44 47 49 52 62 65 68 69.  
Use 5 out of 4 wheeling formula a total of 56 combinations were generated.

```
ID   Tickets
1 08 11 20 36 52
2 08 11 20 44 47
3 08 11 20 49 69
4 08 11 23 44 62
5 08 11 23 47 68
6 08 11 36 62 68
7 08 11 44 49 65
8 08 11 44 65 69
9 08 11 52 65 68
10 08 20 23 47 52
11 08 20 23 62 65
12 08 20 36 47 49
13 08 20 52 62 65
14 08 20 65 68 69
15 08 23 36 44 68
16 08 23 36 52 69
17 08 23 44 47 69
18 08 23 49 52 68
19 08 36 44 65 69
20 08 36 47 49 65
21 08 44 47 52 69
22 08 44 47 62 68
23 08 44 49 52 69
24 08 47 49 62 69
25 11 20 23 36 49
26 11 20 23 52 69
27 11 20 44 52 68
28 11 20 47 62 65
29 11 23 36 52 65
30 11 23 44 49 69
31 11 23 62 68 69
32 11 36 44 47 69
33 11 36 47 68 69
34 11 36 62 65 69
35 11 44 49 65 68
36 11 47 49 52 62
37 11 52 62 65 69
38 20 23 36 44 65
39 20 23 36 65 68
40 20 23 44 49 62
41 20 23 47 68 69
42 20 36 44 62 69
43 20 36 47 52 62
44 20 44 47 49 68
45 20 49 52 65 69
46 20 49 62 65 68
47 23 36 47 49 62
48 23 44 47 52 65
49 23 47 49 62 65
50 23 47 49 65 69
51 23 52 62 68 69
52 36 44 47 65 69
53 36 44 49 52 62
54 36 47 52 65 68
55 36 49 52 68 69
56 44 62 65 68 69
```
```
Number Hits
08: 24
69: 24
65: 23
11: 22
23: 22
44: 22
47: 22
20: 21
36: 21
49: 20
52: 20
62: 20
68: 19
```

As shown above, the back numbers **68** and **62** appear only **19** and **20** times.

**SamLotto** lottery software supports **custom number positions,** you can specify the position of each number so that the generated wheeling combination will generate **different combinations.**

Select **Advanced** -> Click the “ **Arrange** ” button to modify the position of each number, as shown below

![[attachments/e991f9c353e4779e2105d5c4fa1dcbbc_MD5.jpg]]

As shown above, we have rearranged these 13 numbers 62 36 11 44 52 20 23 68 49 08 69 65 47. Use the same wheeling formula to regenerate the combination.

```
ID   Tickets
1 11 36 49 52 62
2 11 20 23 36 62
3 11 36 47 62 68
4 08 20 36 44 62
5 23 36 44 62 65
6 08 36 52 62 65
7 20 36 62 68 69
8 20 36 47 62 69
9 36 49 62 65 69
10 11 23 44 49 62
11 08 11 44 62 69
12 11 23 52 62 68
13 08 11 49 62 69
14 11 47 62 65 69
15 20 44 52 62 65
16 44 47 49 52 62
17 20 23 44 47 62
18 44 49 62 65 68
19 20 47 52 62 69
20 23 52 62 68 69
21 20 23 47 49 62
22 08 20 23 62 65
23 20 47 49 62 68
24 08 23 47 62 68
25 11 36 44 52 68
26 11 36 44 47 49
27 11 20 36 49 65
28 08 11 23 36 69
29 36 44 49 52 69
30 20 36 44 47 68
31 08 36 44 47 65
32 20 23 36 47 52
33 23 36 47 52 65
34 08 36 47 52 69
35 20 36 65 68 69
36 08 23 36 49 68
37 08 36 47 49 69
38 11 20 44 52 69
39 11 44 52 65 69
40 08 11 20 44 68
41 11 23 44 47 65
42 08 11 20 47 52
43 08 11 23 49 52
44 11 20 23 65 68
45 11 47 49 68 69
46 08 11 65 68 69
47 08 23 44 52 68
48 20 23 44 49 69
49 08 23 44 68 69
50 23 44 47 68 69
51 08 44 47 49 65
52 20 23 47 52 69
53 08 20 49 52 68
54 23 49 52 65 69
55 47 49 52 65 68
56 08 20 47 65 69
```
```
Number Hits
47: 24
62: 24
69: 23
20: 22
23: 22
36: 22
44: 22
11: 21
52: 21
08: 20
49: 20
68: 20
65: 19
```

**Comparing** these two generated combinations, the results are **completely different**. We can apply this method to our combination strategy by putting numbers with a high probability of appearing in the next draw in front.

## Use Custom Wheeling

Checking “Custom Wheel” will import and use the custom wheel.

![[attachments/bc3b3e44d3926cd646842b69cd43af06_MD5.jpg]]

Custom wheel files can be text files, the format is as follow.

```
01 03 04 07 22
01 03 11 20 22
01 03 14 18 22
01 03 16 18 22
01 04 11 14 18
01 04 16 18 20
01 07 11 14 16
01 07 14 18 20
03 04 07 11 20
03 04 07 14 16
03 04 11 14 20
03 04 18 20 22
03 07 14 16 18
03 11 16 18 20
04 07 11 18 22
04 11 14 16 22
07 14 16 20 22
```

