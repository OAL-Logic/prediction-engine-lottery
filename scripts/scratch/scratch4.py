from engine.cli.utils import get_adapter
adapter = get_adapter('br/lotofacil')
df = adapter.fetch()

empty_col_any = 0
empty_row_any = 0

for idx, row in df.iterrows():
    nums = set(row['numbers'])
    
    rows = [
        set(range(1, 6)),
        set(range(6, 11)),
        set(range(11, 16)),
        set(range(16, 21)),
        set(range(21, 26))
    ]
    
    cols = [
        {1, 6, 11, 16, 21},
        {2, 7, 12, 17, 22},
        {3, 8, 13, 18, 23},
        {4, 9, 14, 19, 24},
        {5, 10, 15, 20, 25}
    ]
    
    has_empty_row = any(len(nums.intersection(r)) == 0 for r in rows)
    has_empty_col = any(len(nums.intersection(c)) == 0 for c in cols)
    
    if has_empty_row: empty_row_any += 1
    if has_empty_col: empty_col_any += 1

print(f"Total draws: {len(df)}")
print(f"Draws with at least one EMPTY ROW: {empty_row_any}")
print(f"Draws with at least one EMPTY COL: {empty_col_any}")
