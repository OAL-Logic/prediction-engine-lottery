import sys
import os
import httpx
import json

# Set project root path to the current worktree
project_root = os.getcwd()
sys.path.append(project_root)

from engine.modules.storage import storage

def backfill_mega():
    print("Fetching all Mega-Sena draws from API...")
    url = "https://loteriascaixa-api.herokuapp.com/api/megasena"
    
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        resp = client.get(url)
        if resp.status_code != 200:
            print(f"Failed to fetch data: HTTP {resp.status_code}")
            return
        
        data = resp.json()
        print(f"Successfully fetched {len(data)} draws.")
        
        parsed_draws = []
        for row in data:
            try:
                draw_id = int(row['concurso'])
                date_str = row['data'] # format DD/MM/YYYY
                if '/' in date_str:
                    day, month, year = date_str.split('/')
                    draw_date = f"{year}-{month}-{day}"
                else:
                    draw_date = date_str
                
                numbers = [int(n) for n in row['dezenas']]
                bonus = []
                
                parsed_draws.append({
                    "draw_id": draw_id,
                    "draw_date": draw_date,
                    "numbers": numbers,
                    "bonus": bonus,
                    "raw_json": row
                })
            except Exception as e:
                print(f"Error parsing row: {row}. Error: {e}")
        
        print(f"Parsed {len(parsed_draws)} draws. Saving to database...")
        storage.save_draws("br/mega-sena", parsed_draws)
        print("Mega-Sena data backfilled successfully in the database!")

if __name__ == "__main__":
    backfill_mega()
