from engine.cli.utils import get_adapter
adapter = get_adapter('br/lotofacil')
df = adapter.fetch()
ticket = {1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 16, 17, 20, 21, 25}
hits = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
for idx, row in df.iterrows():
    match = len(ticket.intersection(set(row['numbers'])))
    if match >= 11:
        hits[match] += 1
print(f"Historical performance over {len(df)} draws:")
for k, v in hits.items():
    print(f"{k} hits: {v}")
