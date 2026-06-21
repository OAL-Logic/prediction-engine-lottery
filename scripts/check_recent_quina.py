import sys
import os
import duckdb
import pandas as pd

sys.path.append(os.getcwd())

def check_recent():
    db_path = os.path.join(os.getcwd(), "data", "lottery.db")
    con = duckdb.connect(db_path)
    df = con.execute("""
        SELECT draw_id, draw_date, numbers 
        FROM draws 
        WHERE lottery_id = 'br/quina' 
        ORDER BY draw_id DESC 
        LIMIT 30
    """).df()
    print("Recent 30 Quina draws:")
    print(df)
    con.close()

if __name__ == "__main__":
    check_recent()
