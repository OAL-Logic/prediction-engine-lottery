import duckdb
import sys
import os

db_path = os.path.join(os.getcwd(), "data", "lottery.db")

def inspect_db():
    print(f"Connecting to DuckDB database at {db_path}...")
    try:
        con = duckdb.connect(db_path)
        tables = con.execute("SHOW TABLES").fetchall()
        print("Tables in database:", tables)
        for table in tables:
            tname = table[0]
            print(f"\nTable: {tname}")
            schema = con.execute(f"PRAGMA table_info({tname})").fetchall()
            print("Schema:")
            for col in schema:
                print(col)
            
            # Count by lottery_id
            counts = con.execute(f"SELECT lottery_id, COUNT(*), MIN(draw_id), MAX(draw_id) FROM {tname} GROUP BY lottery_id").fetchall()
            print("Counts by lottery_id:")
            for row in counts:
                print(row)
        con.close()
    except Exception as e:
        print("Error inspecting database:", e)

if __name__ == "__main__":
    inspect_db()
