---
title: How to Set Filter Fault Tolerance to Avoid Losing the Big Prize
sources:
  - https://www.samlotto.com/how-to-set-filter-fault-tolerance-to-avoid-losing-the-big-prize/
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
handles:
published: 2021-02-04T11:19:25-03:00
created: 2026-04-28T22:36:03-03:00
modified: 2026-04-28T22:36:03-03:00
description: How to remedy this mistake? When we use many filters at the same time, If there is a conditional parameters set error, we will lose the big prize.
tags:
  - libraries/clippings
activities:
---
When we use many filters at the same time, If there is a conditional parameter set error, we will lose the big prize.

**How to remedy this mistake?**

**We need to set the Filter Fault Tolerance.**

On the left side of the “Star Filtering” button, have a Logical Condition Combox, before filtering, you can set the fault tolerance here. There are only two options by default, “AND” or “OR”.

![[attachments/8bd22165a523dbaf35047912be440673_MD5.jpg]]

The default parameter of the Logical Condition is “AND”, which means that the combination does match the all selected filters conditions that will be included. If you select “OR” which means that the combination does match the one, or more selected filters conditions will be included.

The following example will step by step how to use Filter Fault Tolerance.

We use the lottery data of Mega Millions 10/29/2019.

First, randomly select some numbers and generate combinations, these numbers must contain Mega Millions 10/29/2019 winning numbers: 04 09 17 27 39

Then automatically generate Mega Millions 10/29/2019 winning numbers base conditions (Menu->Generate Current Drawings Conditions (10/29/2019))

Randomly selected 10 filters:

```
Even Count=1
High Count=1
Prime Count=1
Number Sum=96
Average Value=19
Unit Number Different Count=3
Minimum Number=4
Max Distance=12
AC=6
Lowest 4 Units Count=4
```

Then start filtering, because the set filter conditions are all correct, so the winning condition will be included.

![[attachments/f63dab6ce735ae57e1011682e511dad0_MD5.jpg]]

Next, to test, we set an error filter parameter, modify High Count to 2, and then filtering.

What happens?

All the lines were filtered out. We lose the big prize.

![[attachments/66b8257e72998a0beab332cfe6a02fb4_MD5.jpg]]

**How can we avoid this?**

We need to use the Filtering **Fault Tolerance**, set Logical Condition to 9-10, which means that the combination does match 9-10 selected filter conditions will be included.

![[attachments/ed74cfd3fe8ddb2f63f04596d333d077_MD5.gif]]

After setting up the filter Fault Tolerance, we rerun the filters and even though there is a filter we set wrong, the big prize is still included.

![[attachments/36671c48d58127d8f3a98f8ed04d2e8d_MD5.jpg]]

