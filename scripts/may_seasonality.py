import json
from collections import Counter
from datetime import datetime

# Load all 2026 data + previous years if available
files = [
    'data/inspections/br_lotofacil/2026.json',
    'data/inspections/br_lotofacil/2025.json',
    'data/inspections/br_lotofacil/2024.json',
    'data/inspections/br_lotofacil/2023.json',
    'data/inspections/br_lotofacil/2022.json',
    'data/inspections/br_lotofacil/2021.json'
]

may_draws = []
for f_path in files:
    try:
        with open(f_path, 'r') as f:
            data = json.load(f)
            for draw in data:
                date_key = 'draw_date' if 'draw_date' in draw else 'date'
                if date_key not in draw:
                    continue
                dt = datetime.strptime(draw[date_key], '%Y-%m-%d')
                if dt.month == 5:
                    may_draws.append(draw['numbers'])
    except FileNotFoundError:
        continue

# Frequency in May
may_counts = Counter()
for nums in may_draws:
    may_counts.update(nums)

# Sort by frequency
top_may = may_counts.most_common(25)

print(f"Analyzed {len(may_draws)} draws from May (2021-2026)")
print("Top Frequencies in May:")
for num, count in top_may:
    percentage = (count / len(may_draws)) * 100
    print(f"Number {num:02}: {count} hits ({percentage:.1f}%)")
