import pandas as pd
import json

def filter_sao_joao():
    df = pd.read_csv("june_late_draws.csv")
    df['date_dt'] = pd.to_datetime(df['draw_date'])
    
    # Specific draw numbers for Quina de São João
    sao_joao_draw_ids = [2627, 2925, 3225, 3525, 3825, 4114, 4412, 4706, 5002, 5299, 5590, 5881, 6172, 6462]
    
    # Let's see what is in June 2025 (year 2025)
    df_2025 = df[df['date_dt'].dt.year == 2025]
    print("June 2025 draws:")
    for idx, row in df_2025.iterrows():
        print(f"Draw {row['draw_id']} on {row['draw_date']}: {row['numbers']}")
        
    # Usually Quina de São João is the draw on a Saturday around June 20-27.
    # In 2025, June 21 was Saturday, June 28 was Saturday.
    # Let's find the draw number. In 2025, the draw was 6750. Let's check.
    
    # Let's filter our dataframe
    sao_joao_records = df[df['draw_id'].isin(sao_joao_draw_ids)]
    
    # Let's find 2025 draw ID
    # In 2025, there is a draw that had no draws for several days before it (as it accumulates sales for São João).
    # We can check the gap between draw dates.
    # Usually, Quina has draws Monday to Saturday (daily).
    # For Quina de São João, sales are exclusive for about a week before, so there are no normal draws for about a week, or it's a huge jump.
    # Let's print out all draws between June 15 and June 30, 2025
    df_june_2025_all = df[(df['date_dt'].dt.year == 2025) & (df['date_dt'].dt.day >= 15) & (df['date_dt'].dt.day <= 30)]
    print("\nJune 15-30, 2025 draws:")
    print(df_june_2025_all[['draw_id', 'draw_date', 'numbers']])
    
if __name__ == "__main__":
    filter_sao_joao()
