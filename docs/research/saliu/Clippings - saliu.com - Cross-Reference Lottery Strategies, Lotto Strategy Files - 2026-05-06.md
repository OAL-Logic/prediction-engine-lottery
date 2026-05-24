---
title: Cross-Reference Lottery Strategies, Lotto Strategy Files
sources:
  - https://saliu.com/cross-lines.html
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
handles:
published:
created: 2026-05-06T14:32:19-03:00
modified: 2026-05-06T14:32:19-03:00
description: Cross-reference, combine lottery strategy files created by many types of lotto software to increase probability, winning chances by orders of magnitude.
tags:
  - libraries/clippings
  - libraries/sources/saliu.com
activities:
---
[Get software  
![[attachments/3864e048bbf170f787647c722d9a0ad7_MD5.gif]]](https://saliu.com/membership.html)  

## Cross-Reference, Combine Lottery Strategy Files Created by Various Types of Lottery Software ★ ★ ★ ★ ★

## By Ion Saliu, Founder of Lottery Strategizing Science

Last updated: November 2025.

• FileLines version VI.O, December 2018 – Scientific software to combine lottery strategy files  
• SortFilterReports version 3.0 ~ May 2016 – Lotto, lottery software to sort reports by column  
• Sorting version XIX.O ~ December 2018 – Scientific software to sort and format data files.

## 1\. The necessity of combining lotto, lottery strategy files

- **FileLines** is a component of the **Bright / Ultimate** software packages, menu #2, function *T = Cross-Checking Strategies*.
- The program writes to disk the lines of specified indexes in a file, usually a lottery strategy file created by the strategy checking functions. This represents one situation when working with **LotWon software** and also **MDIEditor Lotto WE**.
- For example: You created the *WS* files in the ***Command Prompt LotWon*** lottery software, such as **Bright / Ultimate** software packages. You also generated the statistical reports in **MDIEditor Lotto**. You then created the lottery strategy file for the stats in **MDIEditor And Lotto** (***Windows*** lottery and lotto software).
- You can't have one strategy file across the two platforms. You want to see the same line numbers in the filter report files for a more comprehensive lottery strategy. That's when **FileLines** steps in. The main (original) function is: *R = Common Lines from W\* Reports*.

![[attachments/9e5c1fbc293cf483409cf4851d026439_MD5.gif]]

However, the strategy checking is done by type of application. There are situations when you want to see the lines (lottery drawings) that various strategies have in common. In other words, we want to know when different strategies would hit simultaneously. For that task, we need a function to create a new file consisting of the common numbers in various *HIT* files created by various **Strategy\*.exe** programs. New function introduced in December 2018: *H = Common Lines from **.HIT** Files*.

![[attachments/3b50c3c4690aeeadfb0c2b8c34077766_MD5.gif]]

The numbers in a *HIT* file actually show the lottery draw numbers when a particular strategy hit (won). Normally, a single-app strategy also creates a *skip report*. But this feature becomes impossible when we combine or cross-reference multiple strategies as it is the purpose of this incredible application: **File Lines**. And that's when this module steps in: Create a skips report based on the combined *HIT* file we created from multiple lottery strategies. The output (report) will show the unordered skips, the skips in ascending order, and the all-important *median skip*.

And that's the goal of the December 2018 function *F = Format, Sort HIT Files & Calculate Skips* as seen in this screenshot:

![[attachments/9b96476353a14d0be7b0100dd7c1d835_MD5.gif]]

The program cross-references strategy files, data files, any text files, for that matter. The user can decide what lines to cross-reference. It could be a *prompt input* (typing), or a *file input*. The *file input* is the most convenient method. The input file consists of a series of numbers representing what lines to cross-reference in the *source files*. The source files can be the *W\** or *MD\** *lotto filter files*, and/or *lottery data files* (drawings history).

Creating the input file is as easy as typing numbers: one by line, or several numbers per line. If a line has several numbers, commas or blank space(s) must separate the numbers. A line must always end with *Enter*. The last number of the line must not be followed by a comma or blank space(s). The file must not have any blank lines. These are, in fact, the requirements of the data files in **LotWon** (***Command Prompt*** lottery software) and **MDIEditor Lotto WE**.

The main purpose of **File Lines** is the cross-referencing of all filter files to create cross-platform lotto strategy files. Every lottery strategy file in ***Command Prompt LotWon*** and **MDIEditor And Lotto** has a column named *Line Number*. It refers to the corresponding line in the data file at the time the *WS* filter files were created. We need a way to save the numbers in the *Line No* column to a text file (the input to **FileLines**).

![[attachments/3b6030398e19a3479493b1ddaa0f8c05_MD5.gif]]

There are two working procedures, as seen in the screenshot above:  
~ entirely **manually** (initially it was the only procedure available)  
~ **file** -based data entry (introduced in 2018 — the highly recommended method).

## 2\. Working with the FileLines Application

In both procedures (methods) the program requires **source** files. These are the filter files (*W\**, *MD\** in **Bright / Ultimate** lottery software or the statistical reports in **MDIEditor And Lotto**). The entire operation can be very tricky, especially in the beginning. First of all, the length of the reports must be equal both in ***LotWon*** and **MDIEditor Lotto**. If you did the statistical report in **MDIEditor And Lotto** for 1000 drawings, then all four *WS* files in ***LotWon*** must be done for the same data file (on the same date) and for 1000 draws.

You can download a sample input file: [***INP-FILE.TXT***](https://saliu.com/pub/INP-FILE.TXT). It has 10 numbers, one per line; the largest number is 59. There is a duplicate number: 8. It is valid to write multiple copies of the same line. Simply put it, the input shows numbers that act as **indexes**. The indexes retrieve the corresponding **line numbers** from every **source** file and write them to a **report** file.

![[attachments/1ec6a94fe35d3f75baa7e4a4072fbeec_MD5.gif]]

You can extract lines from as many **text** files as you want to. Since this program is aimed primarily at lottery, the software works best with the special files created by the strategy-checking software. They usually have the *HIT* extension; e.g. *ST5.HIT* in the screenshot above. The lotto-specific *ST5.HIT* input file can be downloaded by visitors with paid membership. The tiny text file is part of a ZIP package that also contains the filter-input files necessary for the recommended function of this program: *F = File Input*.

### A. Manual Operation: S = Screen Prompt

**File Lines** needs to know in advance the *number of lottery filter files* to open. For example, you created the input file from an ***MDIEditor & Lotto*** strategy file for lotto-6. The 32-bit **Bright / Ultimate Software** creates 4 *W* files. The next step is very important. **FileLines** needs to know in advance the *number of lines the header* consists of. The source files (*WS* or filter files, in this example) can have *headers*. The headers represent all the lines before the first bit of filter analysis appears.

Here you have some header lengths in the FILTER files:  
**W\*.\*, MD\*.\* = 13** lines in headers (18 lines in W3.7);  
**Strategy\* (MDIEditor And Lotto WE) = 13** lines in headers;  
**DE\*.1, FR\*.1, SK\*.\*, = 13** lines in headers;  
**PAIR\*.WS = 13** lines in header;  
**LieID\*.REP = 13** lines in headers;  
**DATA\* = 0** lines in headers (NO header — they are NOT filter files).

You can always open a report in a text editor and count the lines in the header, including blank lines. ***Notepad++*** shows the line numbers in the left-most column.

The lottery strategy file in **MDIEditor And Lotto** with 13 lines in the header was created manually. The filter file automatically saved by the grand software application has no header. I do the statistical report. Go all the way down to the filter section. I select the entire section, including the header. I copy and paste to a new text file. I save it as the source file for **File Lines**.

You can open any number of filter files to select lines from. Make sure that all filter files were generated for the same number of past lottery draws as the largest index in the input file. The source files must have headers of equal lengths. You ran, say, the program for the 4 W6 filter files created by **Report6** lotto software. You generated one *report file*, e.g. *ALL-STR6.1*. You can run **FileLines** again using the data file as source. You want to know the actual lottery drawings corresponding to the lines in the strategy file. Parameters for **File Lines**: *Number of source files*: 1; *Length of header*: 0; report file: *ALL-STR6.2*.

You can combine all report files in one, using a text editor (load a file at the end of the preceding one). Better still, run ***Notepad++***, drag-select all report names and open all of them at once. You can then move from tab to tab for the best viewing of multiple reports created from the same index file (e.g. *ST5.HIT*).

You can type the corresponding indexes at the prompt. It is quick-and-easy if you already know the drawings in the strategy file. Otherwise, the best method is creating an index-input file.

**FileLines** can print selectively or randomly line numbers from any text files. You can generate random numbers using **Permute Combine** combinatorial software. Generate, say, one number per line. If the text file you want to print lines from has 1000 lines, then the largest combination number is 1000; numbers per combination = 1. How many combinations to generate: a number between 1 and 1000. Save the input file.

**File Lines** can be tricky sometimes. It works with files different from one another, as far as the headers are concerned. The key is to know exactly the structure of the text files fed to the application. The files must be in text format. The source (lottery filter) files opened in one step must have headers of equal length and an equal number of lines. The largest index in the input file must be equal or less than the largest number of lines in the source files.

### B. Script Operation: F = File Input

This highly recommended method was added in 2018. It increases the productivity by an order of magnitude. Instead of the tedious operation of entering the filter files manually, then the index input file, then choosing a name for the report — this function enters the data from a file you previously created. You took your time, entered the correct data, you avoided all errors. Your file will run the program flawlessly, almost automatically, and you can rerun the same filter-input file again and again...

![[attachments/a635cfaca21fe5687cc18f470fe76428_MD5.gif]]

The aforementioned ZIP file contains 9 sample files specifically created for the 5-number lotto games. The registered members can download it right here: [***HeaderFilterFiles.zip***](https://saliu.com/pub/HeaderFilterFiles.zip). The files are intelligently separated by software application and number of lines in the headers. You can easily adapt the file for any lottery game in the **Bright / Ultimate** grand applications. You can see the structure of one sample filter input file in the screenshot above. You saw also the names of all sample files in Section 1. A few more details —

- **HEAD-WMD.13** ~ contains the *W\*.\** and *MD\*.\** filter files (a.k.a. winning reports) created by *W = Winning Reports (W\* & MD\*)*, main menu of **Bright / Ultimate**. Default strategy input file: *ST\*.HIT*.
- **HEAD-SkDeFR.13** ~ the *SK\*.\**, *DE\*.1*, *FR\*.\** filter files created by *S = Skips, Decades, Frequencies*, menu #2. Default strategy input file: *Skip\*.HIT*.
- **HEAD-Del.13** ~ *Del\*.\** filter files created by *D = Deltas (DeltasLotto5.EXE)*, menu #2. Default strategy input file: *Del-STR\*.HIT*.
- **HEAD-LieID.13** ~ *LieID\*.\** filter files created by *D = Dedicated LIE Elimination (LieID)*, main menu. Default strategy input file: *LieIDStrat\*.HIT*.
- **HEAD-LieWS.9** ~ *LieDecade\*.WS*, *LieLastDigit\*.WS*, *LieHiLo\*.WS*, *LieOdEv\*.WS*, filter files created by *N = LIE StriNgs (LieStrings5.EXE)*, main menu. Default strategy input file: None; this type of software generates combinations that must be ***LIE Eliminated***.
- **HEAD-SkFrGr.13** ~ *SFG\*.\** filter files created by *Q = Skips & Frequency Groups-Only*, menu #2. Default strategy input file: *SFG\*.HIT*.
- **HEAD-UsrGr.13** ~ *UG\*.\** filter files created by *G = Work with User's Number Groups*, menu #2. Default strategy input file: *UG5\*.HIT*.
- **HEAD-W7.18** ~ *W\*.7* filter files created by *W = Winning Reports (W\* & MD\*)*, main menu; applicable to pick-3 and pick-4 only.
- **HEAD-MDI.13** ~ contains the *FiltersLotto\** filter report created by **MDIEditor And Lotto WE**. Default strategy input file: User created *ST-MDI.HIT*. The user checks a strategy, then opens the *Strategy* file in **Notepadd++**. Select the first column that shows the line numbers when the specific lottery strategy hit.

Axiomatic of inquisitive endeavors, you should name the *HIT* files based on the names you gave to your strategy-checking files. Obviously, you should name those files as meaningfully as you can. I published a Web page where I showed many winnings in the pick-4 digit game: [***Lottery Strategy, Systems, Software Based on *Lotto Number Frequency****](https://saliu.com/frequency-lottery.html). I named the strategy-checking report *STR-FR4-1-220*. Accordingly, I named the strategy-input file *STR-FR4-1-220.HIT*. I have another text file that explains what my lottery strategies do, what their main parameters are, how they performed, etc.

The **File Lines** software adapts greatly to your situations by saving the data you work with to an *INI* file. The defaults are offered based on that file, plus internal functions. You can easily edit the defaults in the yellow-background text line. Use the arrow keys, plus the *Home*, *End* and *Insert* keys. The *Insert* key toggles between the insert and overwrite modes.

![[attachments/38b2422b35286295d1ea738157c9aa96_MD5.gif]]

Finally, the program saves all your efforts to a **report** (see above). The naming procedure is also highly automated. The default name is based on the files you worked with. It has the *CROSS* prefix to denominate a cross-referencing file. You can use any filename you want instead.

### Recommended Steps in Running FileLines

- **Update** your data file with real results (lottery drawings); always recreate the *D* \* file (the real data plus the SIMulated file).
- Run the **filter reporting** functions for all entries specified in the *HEAD* paragraph above. I do all the reports for 1000 drawings.
- **Create a strategy** if you haven't created a bunch of them already.
- **Check the strategy** in the respective type of software. Generate the strategy report and the *HIT* file.
- Run the **File Lines** app.
- **Open the strategy report** in **Notepadd++**.
- **Drag-select all CROSS reports** created by **FileLines** to open all of them at once.
- Navigate from tab to tab to **observe patterns** of interest to further improve your lottery strategy.

## 3\. Auxiliaries in combining strategy files and generating lottery strategies

Most LotWon software users already know the shareware editor **QEdit**. It is a great program, albeit limited by the 16-bit DOS platform. It doesn't work in the newer 64-bit versions of Windows operating system.

The column-selecting feature is under the *Block* menu (*Mark column*). The shortcut is *Alt+K*. Move the prompt in front of the column to select. If you know that the column is 4 digits wide but the first entry is only 2 digits wide, move the prompt two positions to the left. Press simultaneously *Alt+K* and move the prompt to the end of the column (4 positions wide, this example). Do not select +/- at the end of the column. Press *Ctrl+J* to *Go to line*. Type a number large enough to go to the last row of the column. The entire column was selected. Press *Alt+W* to *write* the selected block to a disk file. Save the new file. I add *.INP* to its name, to remember easier that it is an input file to **File Lines**.

The best text editor is now another piece of great freeware: ***Notepad++***. Download it from here:  
[***Notepad++ text and programmer's editor***](https://notepad-plus-plus.org/).

- You should install **Notepad++** in one of the two locations to easily work with it:
- **C:\\Program Files (x86)\\Notepad++\\notepad++** — for 64-bit Windows, or –
- **C:\\Program Files\\Notepad++\\notepad++** — for 32-bit Windows

It makes it very easy to select a column. The software calls the operation *selecting a rectangular bloc of text*. You hold down the *Alt* key, then click at the beginning of the block of text, then move the mouse pointer to the end of the rectangular bloc of text. Here is how I do it with a real strategy file:

![[attachments/a49293503c648b4c45aa4aee4f6a3e00_MD5.gif]]

After I selected the column, I press *Ctrl+C* to copy the rectangular bloc, then *Ctrl+N* to open a new file, then *Ctrl+V* to paste the bloc of text, and finally *Ctrl+S* to save the file of indices.

## 4\. Advanced tips on creating lotto, lottery strategy files, strategies

The two text editors mentioned above can work well at creating pivot strategies. A pivot strategy consists of one filter as the key restriction. You can then add other filters to the pivot for a more restrictive strategy. Use the editors to select an entire column (including +/-) representing the pivot filter. Both editors have also a sort feature. ***QEdit***: *Block*, then *Sort*; shortcut: *F3 function key*.

### Important Update, February 2011

I wrote specialized software to automate the process of sorting the filters (or columns, or blocks of text). The program name is **SortFilterReports**. The lotto software sorts the *W5*, *MD5*, *GR5*, *DE5*, *FE5*, *SK5* reports by column, helping the user see more easily the filters — e.g. filters of wacky values. The sorting is done by type of winning reports. The lotto program also offers the correct choices (correct names) for filters to sort. Similar programs handle other lotto formats, especially the 6-number lotto game — components of the **Bright & Ultimate** software suites.

![[attachments/7ab56184c5db930ef04c7e2345e250cf_MD5.gif]]

Indubitably, the best sorting software in the world is **Sorting**. It can sort text files and also numeric files *by column*. Options: *S = Sort Files as Text Lines* and *C = Sort Columns (Numeric & Text)*.

![[attachments/e2ee4f3e925ed1801404385c899266ff_MD5.gif]]

If you sort in ascending order, the pivot filter will start at 0 (usually) and end with the largest value the filter has taken. If you want to use the filter as the *maximum*, select a range of values starting at 0. If there are more than 2 zeroes in 100 draws, then a pivot strategy would be *Max\_Filter=1*.

If you want to use the lottery filter as the *minimum*, select a range of values starting at the bottom of the column. If there are more than 2 higher in 100 draws, then a pivot strategy would be *Min\_Filter = High\_Value*.

If you want to use **both** the *minimum* and the *maximum* levels of a lottery filter, go somewhere to the median zone of the sorted column. For example, a value in that area that repeats: 50. Set *min\_Filter = 50* AND *Max\_Filter = 51*. It is a very tight filter setting. IF such filter setting does not yield any lotto combinations, look for another one; e.g. 51.

You can be more restrictive and select values that only occurred once in 1000 drawings. That's for the patient type. Such restrictive pivot strategies may not generate a combination in many runs.

The pivot strategy will show how many other filters fared in the same lottery drawings. Several filters can be added to the key filter. The combined strategy will be much more powerful.

People do not want to share their lotto strategies. You don't, either. I have received numerous lottery strategies by email. I have been given permission to publish only the weak strategies, in most cases. If the author believes that the lottery strategies are really good, they are for my eyes only! Some people send me good lottery strategies because I am a fair guy. I reward the authors of good lottery / gambling strategies, or ideas of good strategies.

The main goal of those who appear willing to share lottery strategies is to get something much better in exchange. Usually, the detection of *triggers* is the most sought-after item. That's the best guarded secret!

Axiomatic of daring endeavors, you might want to read real-life examples of LIE-strategy files and strategies. The text files were created for the Pennsylvania 5/43 lotto game. You can also download them freely (right-click, then *Save link*).

- [LieStrategies.txt](https://saliu.com/freeware/LieStrategies.txt)
- [ST5-Any1-1-MX-1](https://saliu.com/freeware/ST5-Any1-1-MX-1)
- [ST5-Any2-1-MX-1](https://saliu.com/freeware/ST5-Any2-1-MX-1)
- There are extraordinary details in this special material: [***Lottery Strategy, Systems, Software Based on Lotto Number Frequency***](https://saliu.com/frequency-lottery.html).

## [Resources in Lottery, Software, Systems, Lotto Wheels, Strategies](https://saliu.com/content/lottery.html)

Click to visit a comprehensive directory of pages and materials deeply dedicated to: Lottery, software, strategies, systems, lotto wheels.
- The Main [***Lotto, Lottery, Software, Strategies***](https://saliu.com/LottoWin.htm) Page.  
	Presenting software to create free winning lotto, lottery strategies, systems based on mathematics.
- [***Lotto, Lottery Software, Excel Spreadsheets: Programming, Strategies***](https://saliu.com/Newsgroups.htm).  
	Read a genuine analysis of Excel spreadsheets applied to lottery and lotto developing of software, systems, and strategies.
- [***User's Guide to*** **MDIEditor And Lotto WE**](https://saliu.com/MDI-lotto-guide.html).  
	~ Also applicable to LotWon lottery, lotto software; plus Powerball, Mega Millions, Euromillions.
- [***Visual Tutorial, Book, Manual: Lottery Software, Lotto Apps, Programs***](https://saliu.com/forum/lotto-book.html).
	***Pages dedicated to help, instructions, filters, strategies for the best lotto programs and lottery software in the world:***
- [***Documentation, Help: MDIEditor Lotto WE, Lottery Software, Strategy Tutorial***](https://saliu.com/mdi_lotto.html).
- [***MDI Editor Lotto*** Is the Best Lotto Lottery Software; You Be Judge](https://saliu.com/bbs/messages/623.html).
- [***Filters, Restrictions, Elimination, Reduction in Lotto, Lottery Software***](https://saliu.com/bbs/messages/42.html).
- [***Step-By-Step Guide to Lotto, Lottery Filters in Software***](https://saliu.com/bbs/messages/569.html).
- [***Basic Manual for Lotto Software, Lottery Software***](https://saliu.com/bbs/messages/818.html).
- [**Vertical or Positional** ***Filters In Lottery Software***](https://saliu.com/bbs/messages/838.html).
- [***Beginner's Basic Steps to*** **LotWon** ***Lottery Software, Lotto Software***](https://saliu.com/bbs/messages/896.html).
- [**Dynamic** or **Static** ***Filters: Lottery Software, Lotto Analysis, Mathematics***](https://saliu.com/bbs/messages/919.html).
- [**Skips Lottery, Lotto, Gambling, Systems, Strategy**](https://saliu.com/skip-strategy.html)
- [***Lottery Systems on Skips Improve Lotto Odds Sevenfold***](https://saliu.com/bbs/messages/923.html).
- [***Lottery Utility Software***](https://saliu.com/lottery-utility.html): ***Pick-3, 4 Lottery, Lotto-5, 6, Powerball/Mega Millions/Thunderball, Euromillions***.
- [***Lottery Strategy, Systems Based on Number Frequency***](https://saliu.com/frequency-lottery.html)
- Practical [***Lottery and Lotto Filtering in Software***](https://saliu.com/filters.html).
- [***Lotto, Lottery Strategy in Reverse: Not-to-Win Leads to Not-to-Lose or WIN***](https://saliu.com/reverse-strategy.html).
- [**Lotto Decades**: ***Software, Reports, Analysis, Strategies***](https://saliu.com/decades.html)
- [***Analysis of Best Ranges for Lotto Number Frequency, Lottery Pairs, Pairings***](https://saliu.com/lottery-lotto-pairs.html).
- [***Lotto Software for Groups of Numbers: Odd, Even, Low, High, Sums, Frequencies, User's Groups***](https://saliu.com/lotto-groups.html).
- [***Theory, Analysis of*** **Deltas** ***in Lotto, Lottery Software, Strategy, Systems***](https://saliu.com/delta-lotto-software.html).
- [***The Best Strategy for Lottery, Gambling, Sports Betting, Horse Racing, Blackjack, Roulette***](https://saliu.com/strategy-gambling-lottery.html).
- [***Pick-3 Lottery Strategy Software, System, Method, Play Pairs Last 100 Draws***](https://saliu.com/STR30.htm).
- *"The Start Is the Hardest Part"*: [***Play a Lotto Strategy, Lotto Strategies***](https://forums.saliu.com/lottery-strategies-start.html).
- ***Download*** [**Lottery Strategy Software**](https://saliu.com/infodown.html), ***Systems, Strategies***, including updates and upgrades.

**[Home](https://saliu.com/index.htm) | [Search](https://saliu.com/Search.htm) | [New Writings](https://saliu.com/bbs/index.html) | [Fundamental Formula](https://saliu.com/formula.htm) | [Odds, Generator](https://saliu.com/calculator_generator.html) | [Contents](https://saliu.com/content/index.html) | [Forums](https://forums.saliu.com/) | [Sitemap](https://saliu.com/sitemap/index.html)**