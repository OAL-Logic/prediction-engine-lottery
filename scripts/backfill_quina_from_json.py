import sys
import os
import json
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(os.getcwd())

from engine.modules.storage import storage

def backfill_quina():
    inspection_dir = Path("data/inspections/br_quina")
    if not inspection_dir.exists():
        print("Error: data/inspections/br_quina does not exist!")
        return

    parsed_draws = []
    for path in sorted(inspection_dir.glob("*.json")):
        print(f"Reading {path.name}...")
        with open(path, "r") as f:
            draws = json.load(f)
            for d in draws:
                # Normalise fields
                draw_id = d.get("draw_id") or d.get("concurso") or d.get("numero") or d.get("numeroConcurso")
                date = d.get("draw_date") or d.get("date") or d.get("data") or d.get("dataApuracao")
                numbers = d.get("numbers") or d.get("dezenas") or d.get("listaDezenas")
                bonus = d.get("bonus", [])

                if not draw_id or not date or not numbers:
                    # Skip invalid
                    continue

                # Ensure numbers are integers
                numbers = [int(n) for n in numbers]
                
                # Normalise date DD/MM/YYYY to YYYY-MM-DD
                if "/" in str(date):
                    day, month, year = str(date).split("/")
                    date = f"{year}-{month}-{day}"

                parsed_draws.append({
                    "draw_id": int(draw_id),
                    "draw_date": str(date),
                    "numbers": numbers,
                    "bonus": bonus,
                    "raw_json": d
                })

    print(f"Total parsed draws: {len(parsed_draws)}")
    if parsed_draws:
        storage.save_draws("br/quina", parsed_draws)
        print("Successfully backfilled Quina database from JSON inspections!")

if __name__ == "__main__":
    backfill_quina()
