import sys
import os
import duckdb
import pandas as pd

# Add project root to PYTHONPATH
sys.path.append(os.getcwd())

def find_june_draws():
    db_path = os.path.join(os.getcwd(), "data", "lottery.db")
    con = duckdb.connect(db_path)
    
    # Query draws for Quina in June
    df = con.execute("""
        SELECT draw_id, draw_date, numbers, raw_json 
        FROM draws 
        WHERE lottery_id = 'br/quina' AND EXTRACT(MONTH FROM draw_date) = 6
        ORDER BY draw_id ASC
    """).df()
    
    print(f"Total Quina draws in June: {len(df)}")
    
    # Filter for draws that are Quina de São João.
    # We can print all draws in late June (e.g., June 20-30) to see if we can identify them.
    # In some years, Quina de São João is the only one drawn on its day, or it's on a Saturday.
    # Let's print out all draws from June 20 to June 30 of each year.
    june_late = df[pd.to_datetime(df['draw_date']).dt.day >= 20]
    
    # Let's write the late June draws to a file to examine them
    june_late.to_csv("june_late_draws.csv", index=False)
    print("Saved late June draws to june_late_draws.csv")
    
    # Let's also see if the raw_json has fields like "observacao" or "nome" or "acumulado" or similar that might identify São João
    # We will inspect the raw_json of some of these draws.
    sample = df.iloc[-1]['raw_json'] if not df.empty else None
    print("Sample raw_json keys:", json.loads(sample).keys() if sample else "No data")

    # Let's print draws that might be São João. Specifically, Caixa API lists them as having "observacao" containing "São João" or similar
    # or the draws around June 24.
    sao_joao_candidates = []
    for idx, row in df.iterrows():
        try:
            rj = json.loads(row['raw_json'])
            obs = rj.get('observacao', '') or rj.get('nome', '') or ''
            if 'São João' in obs or 'Sao Joao' in obs or 'SÃO JOÃO' in obs:
                sao_joao_candidates.append(row)
        except Exception:
            pass
            
    print(f"Found {len(sao_joao_candidates)} draws explicitly mentioning São João:")
    for r in sao_joao_candidates:
        print(f"Draw {r['draw_id']} on {r['draw_date']}: {r['numbers']}")
        
    con.close()

if __name__ == "__main__":
    import json
    find_june_draws()
