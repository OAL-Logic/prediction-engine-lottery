import pandas as pd
from engine.adapters import get_adapter

adapter = get_adapter('br/lotofacil')
df = adapter.fetch()

all_numbers = []
for idx, row in df.iterrows():
    all_numbers.extend(row['numbers'])

freq = pd.Series(all_numbers).value_counts()
print("=== TOP 15 NUMBERS ===")
print(freq.head(15))

empty_row_counts = {1:0, 2:0, 3:0, 4:0, 5:0}
empty_col_counts = {1:0, 2:0, 3:0, 4:0, 5:0}

total_draws = len(df)

for idx, row in df.iterrows():
    nums = set(row['numbers'])
    
    rows = {
        1: set(range(1, 6)),
        2: set(range(6, 11)),
        3: set(range(11, 16)),
        4: set(range(16, 21)),
        5: set(range(21, 26))
    }
    
    cols = {
        1: {1, 6, 11, 16, 21},
        2: {2, 7, 12, 17, 22},
        3: {3, 8, 13, 18, 23},
        4: {4, 9, 14, 19, 24},
        5: {5, 10, 15, 20, 25}
    }
    
    for r, r_set in rows.items():
        if len(nums.intersection(r_set)) == 0:
            empty_row_counts[r] += 1
            
    for c, c_set in cols.items():
        if len(nums.intersection(c_set)) == 0:
            empty_col_counts[c] += 1

print("\n=== EMPTY ROWS ===")
for r, c in empty_row_counts.items():
    print(f"Row {r}: {c/total_draws:.4%} (Never drawn in {c} draws)")

print("\n=== EMPTY COLS ===")
for c, count in empty_col_counts.items():
    print(f"Col {c}: {count/total_draws:.4%} (Never drawn in {count} draws)")

