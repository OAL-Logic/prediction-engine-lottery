import sys
import os
import duckdb
import pandas as pd

sys.path.append(os.getcwd())

def find_real_sao_joao():
    db_path = os.path.join(os.getcwd(), "data", "lottery.db")
    con = duckdb.connect(db_path)
    df = con.execute("""
        SELECT draw_id, draw_date, numbers 
        FROM draws 
        WHERE lottery_id = 'br/quina' 
        ORDER BY draw_id ASC
    """).df()
    
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    df['prev_date'] = df['draw_date'].shift(1)
    df['gap_days'] = (df['draw_date'] - df['prev_date']).dt.days
    
    # We look for draws in June where the gap is >= 5 days.
    # Note: Quina de São João started in 2011.
    sao_joao = df[(df['draw_date'].dt.month == 6) & (df['gap_days'] >= 5) & (df['draw_date'].dt.year >= 2011)]
    
    print("Detected Quina de São João Draws:")
    for idx, row in sao_joao.iterrows():
        print(f"Year {row['draw_date'].year}: Draw {row['draw_id']} on {row['draw_date'].strftime('%Y-%m-%d')} (gap: {row['gap_days']} days) -> {row['numbers']}")
        
    con.close()

if __name__ == "__main__":
    find_real_sao_joao()
