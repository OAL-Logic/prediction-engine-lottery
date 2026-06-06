---
title: First Lottery Systems, Gambling Systems on Skips, Software
sources:
  - https://forums.saliu.com/lottery-gambling-skips-systems.html
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
handles:
published:
created: 2026-05-06T14:24:46-03:00
modified: 2026-05-06T14:24:46-03:00
description: These are the first lottery systems, gambling systems, roulette strategies, football, horse racing based on SKIPS, gaps, hits with special software programs.
tags:
  - libraries/clippings
  - libraries/sources/forums.saliu.com
activities:
---
[Get software  
![[attachments/4dd53758f7b5e2c00e99f042d401ece3_MD5.gif]]](https://saliu.com/membership.html)  

## Theory of Skips Gambling, Lottery, Software, Strategies, Systems Based on Skips

## By Ion Saliu, ★ Founder of Gambling Science, ★ Founder of Lottery Mathematics

*Reposted from the now-closed lottery and gambling forums* —

Axiomatic one, the **skip** represents the amount, or length, or span of drawings or roulette spins, etc. that a number misses between two hits or wins. For example, a lotto number came out (hit) 24 drawings ago, then it just hit again the last draw; therefore the *skip = 23* (that particular number “waited” 23 lottery drawings to come out again). That's how the skip is calculated in my lottery and horse racing software. It was calculated the same way in skip system software prior to version 3. Now, the skip as exemplified above is equal to 24. We say now *the number hit again in 24 draws*. Please read the notes that come later on this page.

I presented as early as 1990s a strategy (collection of systems) derived from **skips**. I wrote about it in my forums and also at the main website:

- [***Skip Systems Software***](https://saliu.com/skip-strategy.html) ***for Lotto, Lottery, Powerball, Mega Millions, Euromillions, Horse Racing, Roulette***.

*Crocodil Apache* — a very active member of one of my online communities — made two serious contributions regarding strategies based on skips. He wrote in a forum about the *bookie lottery*. In a different forum, he also presented his roulette system based on *3 consecutive skips* (that system is not reliable). *Crocodile Apache* deserves credit for his discoveries and his original posts can be read here:

- [***Crocodile Apache: Roulette Systems, Strategies Based on Skips***](https://forums.saliu.com/apache-roulette-systems.html).

I significantly upgraded my previous software that generated skip systems:

**SkipSystem** version 3.0, October 2006.

I offer an early release especially for the members of this message board. You go to the FTP site and download the program, even if it does not show *version 3.0*. I will make the necessary updates in a few.

This version also adds two new games: 4-number lotto games (different from pick or daily 4) and NFL (American) football. The *football* function requires two additional files. You can download *TEAMS.NFL* from my software site. You can create the other file — *NFL.ODS* — by copying and pasting the point-spread results I published in the sports betting forum. Make sure there are exactly 15 results (i.e. teams) per line (including *open* in some weeks). Get the NFL results from the best facility, with every team, every game, every week on one page:

- [***National Football League (NFL): Schedule, Results of All Games and Every NFL Team in Current Season***](https://saliu.com/NFL-Schedule.html).

There are three fundamental elements when generating gambling/lottery systems derived from skips:

- **the degree of certainty DC**;
- **the *skip* corresponding to the degree of certainty**;
- **the *cycle of fruition* for the system to hit**.

I set the ***degree of certainty*** to be close to **1/e (37% or approximately 1/3)** as to be correlated to ***Ion Saliu's Paradox of N Trials***. The new degree of certainty DC in version 3.0 corresponds to shorter skips. In turn, shorter skips lead to shorter cycles of fruition.

The *cycle of fruition* is a tricky parameter. I haven't found a formula to quantify it (in relation to DC or skip). But we can “visualize” it this way. The skip is 5, for example. If we play a system *under the skip of 5*, the system requires from 1 up to 5 draws (trials, spins, etc.) to complete. The ideal situation is *skip = 1*. The cycle of fruition is 1: The number either hits in the next draw, or it turns into a loser.

The problem with playing *ABOVE a skip corresponding to the **1/e** degree of certainty* is the… uncertainty of the end. The skip could end after a big number of trials. Take the case of roulette, for example. There are roulette numbers that hit again AFTER 200 spins, even more sometimes!

The *cycle of fruition*, as I see it, requires that the system numbers be played for the next several drawings. Some of the numbers will no longer meet the skip restrictions after a few draws; therefore, they must be discarded; new numbers become eligible for the system, based on their new current skip. Perhaps there are better (EASIER!) ways, but I haven't discovered them yet.

I'll present next a few recent examples or samples of my playing with **Skip System**: American football and roulette. The program generates 5 systems automatically. The reports show also the file names. For example, in the case of football, the automatic systems are named FFG-1F.SYS to FFG-5F.SYS. You can still create your own system based on the last two skips; you choose the file name for your system.

The program treats the gambling systems based on:

- ***two* consecutive skips**;
- ***three* consecutive skips**.

Each category in turn is founded on two parameters:

- ***UNDER/EQUAL TO* a skip corresponding to the **1/e** degree of certainty**;
- ***ABOVE* a skip corresponding to the **1/e** degree of certainty**.

At the end, the report shows total number of hits for each system. Actually, the *number of hits* counts the number of occurrences for each system in the range of past drawings (horse races, spins, weeks) analyzed.

The program does NOT count the 1st skip in the string and the last skip (i.e. for each number analyzed). The method is a lot more accurate than before. The 1st skip is not complete yet; it is still running and we don't know when it will end. The last skip is not certain: We don't know if the program had sufficient data to establish the last skip.

The counting of a system occurrences starts at the skip in front of the last one and goes to the beginning of the string named *Any Position*.

```
Football Skip Chart and System Hits
File: NFL.ODS; Date: 10-25-2006
Weeks Analyzed: 100

Team: BEARS
Any Position -> 2 1 2 1 2 1 2 1 1 2 1 1 1 4 1 5 3 1 1 5
 1 4 2 1 1 2 1 1 2 7 5 1 7 2 1 1 1 3 1 2 1 1 2 2 2 2 2 1 2

* System #1 ~ File FFG-1F.SYS:
~ First 2 skips SUM-UP TO 2 -> 9 times in 49 hits (18%)

* System #2 ~ File FFG-2F.SYS:
~ 2 skips UNDER/EQUAL TO 1 -> 9 times in 49 hits (18%)

* System #3 ~ File FFG-3F.SYS:
~ 2 skips ABOVE 1 -> 9 times in 49 hits (18%)

* System #4 ~ File FFG-4F.SYS:
~ 3 skips UNDER/EQUAL TO 1 -> 2 times in 49 hits (4%)

* System #5 ~ File FFG-5F.SYS:
~ 3 skips ABOVE 1 -> 4 times in 49 hits (8%)

* Your System Hits <= 1 1 -> 9 times in 49 hits (18%)

Sorted Skips: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
 1 1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 3 3 4 4 5 5 5 7 7
*Median Skip Any: 1

#1: Total hits 2 skips SUM-UP TO 2 -> 252 hits in 100 (252%)
#2: Total hits 2 skips UNDER/EQUAL 1 -> 252 hits in 100 (252%)
#3: Total hits 2 skips ABOVE 1 -> 403 hits in 100 (403%)
#4: Total hits 3 skips UNDER/EQUAL 1 -> 101 hits in 100 (101%)
#5: Total hits 3 skips ABOVE 1 -> 211 hits in 100 (211%)
#6: Total hits Your System <= 1 1 -> 252 hits in 100 (252%)
```

The system #3 ('2 skips ABOVE 1') predicted 10 teams to bet on the next week:

49ERS BILLS BRONCOS CHIEFS FALCONS JAGUARS PACKERS RAVENS TEXANS VIKINGS

The 49ERS and the RAVENS were idle, so we eliminate them from the list. JAGUARS and TEXANS played in the same game, so they canceled each other. We eliminate them from the list. The remaining qualifying teams are:

BILLS BRONCOS CHIEFS FALCONS PACKERS VIKINGS = 6.

The system predicted 5 winners: BRONCOS CHIEFS FALCONS PACKERS VIKINGS.

The system #5 ('3 skips ABOVE 1') predicted 3 teams to be bet on: BRONCOS CHIEFS PACKERS All three were winners!

The **1/e** based skip for roulette is much higher: 15. The fruition cycle is also much higher than in American football betting. It appears that the systems based on skips ABOVE **1/e** degree of certainty perform more poorly than the systems based on skips UNDER/EQUAL TO **1/e** degree of certainty.

```
0-Roulette Skip Chart and System Hits
File: HAMB0106.DAT Date: 10-25-2006
Spins Analyzed: 1000

Roulette Number: 4
Any Position -> 16 2 42 52 21 19 19 1 35 3 2 12 4 8 13 51 70 5 16
 41 88 38 65 34 1 20 18 38 27 17 12 31 35 4 11 71 56 2

* System #1 ~ File FFG-1R.SYS:
~ First 2 skips SUM-UP TO 30 -> 10 times in 38 hits (26%)

* System #2 ~ File FFG-2R.SYS:
~ 2 skips UNDER/EQUAL TO 15 -> 6 times in 38 hits (16%)

* System #3 ~ File FFG-3R.SYS:
~ 2 skips ABOVE 15 -> 16 times in 38 hits (42%)

* System #4 ~ File FFG-4R.SYS:
~ 3 skips UNDER/EQUAL TO 15 -> 4 times in 38 hits (11%)

* System #5 ~ File FFG-5R.SYS:
~ 3 skips ABOVE 15 -> 10 times in 38 hits (26%)

* Your System Hits <= 15 15 -> 6 times in 38 hits (16%)

Sorted Skips: 1 1 2 2 2 3 4 4 5 8 11 12 12 13 16 16 17 18 19 19 20
 21 27 31 34 35 35 38 38 41 42 51 52 56 65 70 71 88
* Median Skip Any: 19

 FFG-1: 2 skips SUM-UP TO 52   =  2823  hits in  7000 (40%) = 16 numbers
 FFG-2: 2 skips UNDER/EQUAL 26 =  1806  hits in  7000 (26%) = 12 numbers
 FFG-3: 2 skips ABOVE 26       =  1681  hits in  7000 (24%) = 11 numbers
 FFG-4: 3 skips UNDER/EQUAL 26 =   927  hits in  7000 (13%)  = 7 numbers
 FFG-5: 3 skips ABOVE 26       =   859  hits in  7000 (12%)  = 8 numbers
 FFG-6: MEDIAN & SUM <= 52     =  2309  hits in  7000 (33%) = 11 numbers
 FFG-7: 1st Skip <= 26         =  3505  hits in  7000 (50%) = 17 numbers
 FFG-8: 1st Skip  > 26         =  3384  hits in  7000 (48%) = 20 numbers
 SYS-:  Your System <= 20 20   =  1244  hits in  7000 (18%)  = 7 numbers
```

I deleted the top 12 spins from the Hamburg casino results file: HAMB0106.WH1. I saved to the new working file HAMB0106.BAK. I checked the roulette numbers generated by the systems against the 12 “future” spins.

The system #1 predicted 10 numbers with 5 hits. Total to play: 12 \* 10 = 120; total winnings: 5 \* 36 = 180; profit = 60 betting units.

The system #2 predicted 4 numbers with 2 hits. Total cost: 12 \* 4 = 48; total winnings: 2 \* 36 = 72; profit = 24 bet units.

The system #3 predicted 15 numbers with 4 hits. Total to play: 12 \* 15 = 180; total winnings: 4 \* 36 = 144; loss = 36 betting units.

The system #4 predicted 1 number with 0 hits.

The system #5 predicted 11 numbers with 1 hit.

The systems *UNDER/EQUAL TO* possibly perform better because of shorter *cycles of fruition*.

The lottery offers a mixed bag. The pick-3 and pick-4 games have short *skips* and *cycles of fruition*. All systems predicted, in general, 1 or 2 digits to play. The systems hit 1 of 1 or 1 of 2 in the next drawing. I did not check for multiple draws.

But this is the most serious problem: the **house edge**. Compared to roulette, the **house edge** in lottery games is 10 times worse.

- The skip systems are ideal for roulette or other casino games where the skips can be tracked. In turn, these games have their own drawback: The players are not allowed to use computers inside casinos. The skip gambling systems for roulette or craps can be plotted manually, on paper only. For example, play only the numbers (outcomes) that show 2 (or even 3) consecutive skips *under median*.
- As for online casinos, they are a definite NO-NO — they cheat big time. Their offers seem totally insane, with bonuses of 200%, even 300%. You start with a bankroll of $1000 and they add $2000 to it — but you must gamble, not cash out immediately? Why all that extra money? Because the [***online casinos cheat***](https://saliu.com/bbs/messages/850.html) like you ain't seen nothing quite like it — that's why!

The lotto games do not hit well in the very next drawing. That's so because their skips and cycles of fruition are longer. I saw lotto situations with 0 winners of 16, or 0 in 10, or 2 in 17 numbers. But those situations create an advantage for ***lottery strategy in reverse*** playing (***LIE elimination***). Chances are the skip strategies will not hit immediately in a lotto game. We can eliminate those numbers altogether, or eliminate groups of 2, 3 numbers, etc.

We can *reverse* the strategy. Since the fruition cycles of lottery skips are longer, I know the systems do not hit immediately. Let's take the example of 6/49 lotto games; the median is calculated by FFG as 6 (see [***Winning Lotto Software, Lottery Software, Strategies, Systems, Lotto Wheels***](https://saliu.com/LottoWin.htm)). Instead of starting play at the most recent lottery drawing, let's go back 6 or 12 draws.

That is, delete the last 6 or 12 drawings. Plot the skip systems at that point in the data file. Check (with ***Super Utilities***, 1st menu of **Bright**) the combinations generated against the original lotto results file to make sure the system didn't hit a significant winner. If it did, start the plotting of the skip systems at draw #11, or draw #10, etc. The reason is *the hits do not repeat very soon*.

The median figures and everything else calculated by the ***Fundamental Formula of Gambling (FFG)*** are confirmed by reality (i.e. statistical analyses of real-life lottery drawings). Here is an illustration for the *6 49 lotto* in Pennsylvania:

```
Median of Skip Medians Any (Regardless of Position):  6 
Sorted Skip Medians Any: 
4  4  4  4  4  4  5  5  5  5  5  5  5  5  5  5  5  5  5  6  6  6  6
6  6  6  6  6  6  6  6  6  6  6  6  6  6  6  6
6  6  7  7  7  7  7  7  8  9
```
Here is a report of the skips of each of the 6 numbers in a lottery drawing — draw by draw. **Add 1** to each value for compatibility with **Skip System** version 3 and later (see note after the screenshot). The report is created by **SkipDecaFreq** (function *D = Skips, Decades, Frequency*, 2nd menu in **Bright6**).

![[attachments/43870af0031e5d79a15b5b74c1ea912c_MD5.gif]]

In draw #5, 5 of the 6 lotto 6/49 numbers repeated after 4 drawings or fewer (i.e. skips under 4). In draws #16 and #17, 5 of the 6 numbers repeated after 5 drawings or fewer (i.e. skips under 5). Also in draws #16 and #17, all 6 lotto numbers had skips of 8 or under. There are situations when the skips of all numbers in a drawing are *under or equal to median*: [***Filters in Lottery, Lotto Jackpot, FFG Probability Median***](https://saliu.com/bbs/messages/923.html).

We can apply the skips to the ***LIE elimination*** feature present only in Ion Saliu's lottery software. We can see that no string of lotto skips repeats in many, many drawings. It is guaranteed that the string *0 1 4 11 6 7* will not repeat the next lottery drawing. We enter those values as filters, minimum values, in **Skip Decades Frequency**, function *L = Lexicographic Combinations* (generate). The program generates about 400,000 lotto *combosnations* (a favorite term of my lottery-speak!) to be eliminated by the ***LIE*** function. It is guaranteed to work virtually every time. No 6 winning numbers from those 400K will come out the next drawing! In my testing, I came across situations when NO 5 winning numbers were drawn the very next lottery drawing!

This ***LIE elimination*** feature works best only with the last 10 skip strings. Yes, sometimes it works with the last 50 skip strings! This eliminating function can't be tracked for many situations because the same skip string generates very different lotto combinations depending on the point in the data file (lottery results).

- Another important factor to improve the efficiency of the skip system: The skips of a lottery drawing are **never equal** to one another across the line. It must be extremely rare to see all 6 skips being the same in a 6-number lotto game. Look at the real-life report above. You won't find situations with all 6 skips equal to 0(1); or equal to 1(2); or equal to 2(3); etc. We can run **Skip Decades Frequency** to generate combinations based on **skips**. As filter values, type per each run, 0 for all 6 skips (named *Any*); 1 next run for *Any1* to *Any6*; 2 next run; etc. Concatenate all output files in one big LIE file; e.g. *Skips123L6.LIE*. LIE-eliminate all those combosnations from the lotto combinations generated by the skip systems.
- It means all skip systems generated by this ultimate lottery software contain ***unnecessary*** lotto combinations. We can get rid of them via ***Purge*** and ***LIE elimination***.

The **bookie lotteries** are also ideal for playing skip systems. The players can bet on one lotto number. The **house edge** is far better than in state-run lotto games. Very importantly, the *cheat factor* is eliminated in the online **bookie lotteries**. The bookmakers do not run their own software to generate jackpot lotto draws. Instead, the bookies use the lottery results of various national lotteries. Such results are verifiable and honest, for all intents and purposes.

Further testing can be done only manually at this time. I don't have [***lottery software to test automatically***](https://saliu.com/bbs/messages/9.html) — in the manner of **Grid Check**, for example. If you have the patience, you can test by going back 100 draws or so in your lotto, lottery games, or football results file, or roulette spins file. Then generate the systems for one drawing at a time. You go up from draw #101 to draw #100, then to draw #99, then to draw #98, etc.

### SkipSystem reached version 10.0 in 2017.

I verified quite a few situations and found the program to yield the correct results. But, again, I do not claim I tested the program extensively. I encourage you to trust but verify. Axiomatic one, do some testing before deciding to play.

The presentation of the latest software version is always here:

- [***Skip Systems Software***](https://saliu.com/skip-strategy.html) ***for Lotto, Lottery, Powerball, Mega Millions, Euromillions, Horse Racing, Roulette***.

![[attachments/403f8f8dce11d1f7b5621e4a25bb08d8_MD5.gif]]

- Please read these very important notes.
- **Skip System** employed several methods of creating systems relative to a **skip value**. It all started with the **skip value equal to the median**: The value in the **middle** of a string of skips. That value coincides with what I call **FFG median**: **Number of trials N corresponding to a degree of certainty DC equal to 50%**. For example, that value is 25 (or 26) in roulette.
- Starting with version 3 of **SkipSystem**, the systems are created for a **DC = 1/e**, inspired by ***Ion Saliu's Paradox of N Trials***. For example, that value is 15 in roulette. This method makes **tighter** the systems based on **skips under than or equal to** the foundation value; the systems **above** the foundation value are **looser** (they consist of more numbers and have higher frequency).
- **Skip System** **version 10 2017** comes back to establishing the s ystems based on the *degree of certainty* **DC = 50%**. I analyzed a large number of trials (including 7000 roulette spins) and I concluded that **DC = 50%** offers mathematically the best systems with the best hit frequencies.
- As you can see in the roulette report above, the ***under median*** systems offer more hits, while resulting in fewer roulette numbers to play. It is a two-edge sword against the odds. Furthermore, the 3-skip systems can be totally replaced by *Your System* with the last 2 skips set to *less than or equal to 20* (median -25%, or minus approximately one *FFG deviation*).
- And remember to always keep track of the hits and misses of every system.
- The skips themselves are calculated differently beginning with software version 3: It only counts the drawings between hits, including the last hit. Thus, if a number hit 4 drawings back, the skip is 4; that is, 4, 3, 2, 1. Up to version 3, **Skips Systems** calculated the skips consistently with my lottery software. The skip was the amount of draws that the number **skipped absolutely**. In the example, the skip was 3: 4, 3, 2; we don't count the last lotto draw when the number hit. I and a few roulette players discovered a few quirks in the roulette software reports.
- Besides, the ***Fundamental Formula of Gambling (FFG)*** calculates the number of trials corresponding to a degree of certainty **without** deducting 1. The rest of my software is totally correct in establishing the filter values (e.g. deducting 1 in the case of the minimum levels of the filters).
- You can still create skip systems based on the traditional median. **SkipSystem** still creates the skip reports and establishes the median skips for each number. Then, it calculates the median skip relative to all numbers. That median of skip medians is equal to the value calculated by ***FFG*** for **DC = 50%**. You need to run the program for a large number of drawings or roulette spins (I did it for 2000 real casino spins). You'll see this entry at the end of the roulette report: *\* Median of Skip Medians: 25*.
- You can also create systems based on the individual median skip for each number, as in the *Crocodil Apache* systems. I prefer the **median of skip medians**, as it is a **constant** with a solid mathematical foundation.
- You'll end up with numbers that satisfy your parameter (e.g. individual median skip of each lottery number). Type those numbers on one line in a text file (I highly recommend the free **Notepad++** editor). Save the file with a mnemonic name. **Skips Systems** will easily create your skip strategies from such files. It applies to lottery and horse racing only, as roulette and football do not have outcomes with multiple positions. The roulette and football skip systems are already created: The numbers or teams your will enter in the respective text file.
- In case you get an error message, it might be caused by an old *INI* file. Exit the program and delete that *INI* file (e.g. *Pick3.INI* for pick 3 lottery). Restart the software.
- You will find the skip strategy all over the Internet. But you will not find mentions of the true author of the theory of skips, or what software people are using to create strategies based on skips. As a matter of fact, *Ion Saliu* is largely *taboo* on the Internet. That's the character of the world we live in. *O tempora! O mores!* (The famous adagio was created by Cicero, the Roman orator who was impaired by stuttering early in life.)