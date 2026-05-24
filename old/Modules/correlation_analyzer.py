import os
import csv
import datetime
from astronomy_engine import AstronomyEngine
from weather_engine import WeatherEngine

try:
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

class CorrelationAnalyzer:
    def __init__(self):
        self.astro = AstronomyEngine()
        self.weather = WeatherEngine()

    def augment_data(self, draws_with_dates):
        """
        Combines draw results with moon phase and weather data.
        draws_with_dates: list of {'date': datetime, 'nums': [int, ...]}
        """
        augmented = []
        for d in draws_with_dates:
            dt = d['date']
            moon_phase = self.astro.get_moon_phase(dt)
            w = self.weather.get_weather_for_date(dt)
            
            entry = {
                'date': dt,
                'moon_phase': moon_phase,
                'temp': w['temperature'],
                'humidity': w['humidity'],
                'avg_num': sum(d['nums']) / len(d['nums']),
                'sum_num': sum(d['nums']),
                'even_count': len([x for x in d['nums'] if x % 2 == 0])
            }
            # Add individual numbers
            for i, n in enumerate(d['nums']):
                entry[f'n{i+1}'] = n
            
            augmented.append(entry)
        return augmented

    def generate_matrix(self, draws_with_dates, output_path="correlation_matrix.png"):
        if not HAS_LIBS:
            print("[-] Pandas/Seaborn not installed. Cannot generate visual matrix.")
            print("[!] Run 'pip install -r requirements.txt' to enable this.")
            return

        data = self.augment_data(draws_with_dates)
        df = pd.DataFrame(data)
        
        # Drop non-numeric for correlation
        corr_df = df.drop(columns=['date'])
        corr = corr_df.corr()

        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Lottery vs Environment Correlation Matrix")
        
        try:
            plt.savefig(output_path)
            print(f"[+] Matrix saved to: {output_path}")
        except Exception as e:
            print(f"[-] Error saving plot: {e}")

if __name__ == "__main__":
    # Test with dummy data
    test_draws = [
        {'date': datetime.datetime(2026, 4, 1), 'nums': [1, 2, 3, 4, 5, 6]},
        {'date': datetime.datetime(2026, 4, 2), 'nums': [10, 11, 12, 13, 14, 15]},
        {'date': datetime.datetime(2026, 4, 3), 'nums': [20, 21, 22, 23, 24, 25]},
    ]
    analyzer = CorrelationAnalyzer()
    analyzer.generate_matrix(test_draws)
