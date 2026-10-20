# Wheeling Types

> **Category:** Combinatorial Wheeling Systems (`04-wheeling-systems`)

## Wheeling Types



In choosing the best type of wheeling system for you, you have three choices: 



- Full wheel   

- Abbreviated wheel





  **Full Wheel**


  
  A full wheel always contains All of the possible combinations that may be made with the audience of numbers you select. For instance, the sample wheel around the previous page is really a full wheel for the Pick 6 lotto game, wheeling eight numbers in 28 possible combinations.

The objective of the full wheel is to provide you with the best possible shot in a jackpot and multiple lower prizes. 

Benefits of Full Wheel: Playing a complete wheel gives you maximum coverage from the prizes if some or all of the winning numbers are in the numbers you wheeled. If all of the winning numbers have been in the audience you wheeled, you're certain to win the jackpot and multiple second and third prizes. Even though you only have a few of the winning numbers in your wheel, you are certain to have multiple winning tickets. For instance, in our sample wheel, if you have only four winning numbers out of the eight you wheeled, you are guaranteed to have five tickets that match four of six numbers and 15 tickets that match three of six. 

Drawbacks of Full Wheel: To put it simply, it isn't cheap if you wish to wheel large amounts of numbers. For instance: 



- A 9 numbers full wheel for a Pick 6 lotto game contains 84 combinations.   

- A 10 numbers full wheel for a Pick 6 lotto game contains 210 combinations.   

- A 11 numbers full wheel for a Pick 6 lotto game contains 462 combinations.   

- A 12 numbers full wheel for a Pick 6 lotto game contains 924 combinations.   

- A 13 numbers full wheel for a Pick 6 lotto game contains 1716 combinations.   

- A 14 numbers full wheel for a Pick 6 lotto game contains 3003 combinations.   

- A 15 numbers full wheel for a Pick 6 lotto game contains 5005 combinations. 



 

**Abbreviated Wheel**



An Abbreviated Wheel is a set of minimum combination that guarantees you a win   whenever you match a specified amount of the winning numbers. Below you see an   example of an Abbreviated Wheel for a Pick 6 lotto game.   It wheels 8 numbers in 7   combinations. If 4 of the 6   winning numbers are among the 8 numbers you wheel, then   you are guaranteed to have at least one successful   combination matching 4 winning numbers.





  
    
      
        
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
                
              
            

| **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |
| --- | --- | --- | --- | --- | --- | --- | --- |


        
      
    
  




  
    
      
        
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
              
                
                
                
                
                
                
                
              
            

| **1.** | **A** | **B** | **C** | **D** | **E** | **G** |
| --- | --- | --- | --- | --- | --- | --- |
| **2.** | **A** | **B** | **C** | **F** | **G** | **H** |
| **3.** | **A** | **B** | **D** | **E** | **F** | **H** |
| **4.** | **A** | **C** | **D** | **E** | **F** | **H** |
| **5.** | **A** | **D** | **E** | **F** | **G** | **H** |
| **6.** | **B** | **C** | **D** | **E** | **F** | **G** |
| **7.** | **B** | **C** | **D** | **E** | **G** | **H** |


        
      
    
  


And don't forget: You can always win more prizes than the win guarantee.   

**Benefits of Abbreviated Wheel:** It's an economical way to increase your   chances of winning! With fewer combinations to play, you can wheel a large   amount of numbers at a reasonable cost and still have a win guaranteed. By being   able to play more numbers, you greatly increase your chances of having more   winning numbers fall into your wheel and cashing in winning tickets!   

**Drawbacks of Abbreviated Wheel:** Even if all the winning numbers fall   into your wheel, you're not guaranteed winning a jackpot. However, you could   still win multiple prizes, even the jackpot - it's just not guaranteed. 

---

---

## Clean-Room Python Boilerplate

```python
from itertools import combinations

def apply_wheel_template(pool: list[int], index_template: list[list[int]]) -> list[list[int]]:
    """Map a 1-based combinatorial wheel template onto a sorted candidate pool."""
    ordered_pool = sorted(pool)
    return [sorted(ordered_pool[idx - 1] for idx in row) for row in index_template]

def verify_wheel_guarantee(
    tickets: list[list[int]],
    pool: list[int],
    draw_hit_count: int,
    guarantee_tier: int,
) -> dict[str, int | float]:
    """Verify m-if-t covering guarantee across all C(v, t) possible draw subsets of the pool."""
    ticket_sets = [set(t) for t in tickets]
    scenarios = list(combinations(pool, draw_hit_count))
    covered = sum(
        1 for s in scenarios if any(len(t & set(s)) >= guarantee_tier for t in ticket_sets)
    )
    return {
        "total_scenarios": len(scenarios),
        "covered_scenarios": covered,
        "coverage_pct": round(100.0 * covered / max(1, len(scenarios)), 2),
    }
```
