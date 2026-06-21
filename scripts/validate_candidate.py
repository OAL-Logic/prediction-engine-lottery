import sys
import os

sys.path.append(os.getcwd())

from engine.cli.utils import get_adapter
from engine.modules.harmony import registry

def validate():
    adapter = get_adapter("br/quina")
    df = adapter.fetch()
    rules = adapter.rules
    
    ticket = [16, 26, 28, 29, 55]
    print(f"Validating ticket: {ticket}")
    
    filters = ["sum_range", "parity", "breadth", "no_consecutive", "no_arithmetic", "birthday_bias", "no_same_last_digit", "prime_count"]
    
    for name in filters:
        func = registry.get(name)
        if func:
            try:
                res = func(ticket, rules, df=df)
                print(f"Filter '{name}': {'PASS' if res else 'FAIL'}")
            except Exception as e:
                print(f"Filter '{name}' error: {e}")
        else:
            print(f"Filter '{name}' not found in registry")

if __name__ == "__main__":
    validate()
