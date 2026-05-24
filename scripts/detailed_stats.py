import json

with open('data/inspections/br_lotofacil/2026.json', 'r') as f:
    data = json.load(f)

# Sort by draw_id descending (latest first)
data.sort(key=lambda x: x['draw_id'], reverse=True)

latest_draws = data[:10]
all_numbers = range(1, 26)
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]

stats = {}
for n in all_numbers:
    stats[n] = {
        'freq_3': 0,
        'freq_5': 0,
        'freq_10': 0,
        'last_seen': -1,
        'is_prime': n in primes
    }

for i, draw in enumerate(data):
    nums = set(draw['numbers'])
    for n in all_numbers:
        if n in nums:
            if stats[n]['last_seen'] == -1:
                stats[n]['last_seen'] = i
            if i < 3:
                stats[n]['freq_3'] += 1
            if i < 5:
                stats[n]['freq_5'] += 1
            if i < 10:
                stats[n]['freq_10'] += 1
    if i >= 10:
        break

# Cycle analysis: which numbers are missing to complete a set of 25 starting from the beginning of the cycle?
# We usually look at how many draws ago the cycle started.
# A cycle ends when all 25 numbers have appeared at least once.
missing_for_cycle = []
current_cycle_nums = set()
draws_count = 0
for draw in data:
    current_cycle_nums.update(draw['numbers'])
    draws_count += 1
    if len(current_cycle_nums) == 25:
        # Found the start of the current cycle (backwards)
        # But we want the missing numbers *now*
        break

# Correct cycle logic:
missing_now = set(all_numbers)
cycle_draws = 0
for draw in data:
    missing_now -= set(draw['numbers'])
    cycle_draws += 1
    if not missing_now:
        # All numbers appeared in the last 'cycle_draws'
        break

# The numbers that were the LAST to appear in the previous cycle are usually good candidates.
# But simpler: the numbers currently missing from the latest draws are the ones that will "close" the cycle.
currently_missing = set(all_numbers) - set(data[0]['numbers'])
# How many draws since each missing number appeared?
missing_gaps = {}
for n in currently_missing:
    gap = 0
    for draw in data:
        if n in draw['numbers']:
            break
        gap += 1
    missing_gaps[n] = gap

print(json.dumps({
    'stats': stats,
    'missing_gaps': missing_gaps,
    'latest_draw': data[0]['numbers']
}, indent=2))
