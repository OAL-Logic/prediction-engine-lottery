import datetime
import csv
import sys
import os
from markov_predictor import MarkovPredictor
from astronomy_engine import AstronomyEngine
from numerology_analyzer import NumerologyAnalyzer
from weather_engine import WeatherEngine
from correlation_analyzer import CorrelationAnalyzer
from bayesian_inference import BayesianInference
from statistics_analyzer import StatisticsAnalyzer
from weighted_ensemble import WeightedEnsemble

class PredictionEngine:
    def __init__(self, game_type="Lotofácil"):
        self.game_type = game_type
        self.markov = MarkovPredictor()
        self.astro = AstronomyEngine()
        self.numero = NumerologyAnalyzer()
        self.weather = WeatherEngine()
        self.corr = CorrelationAnalyzer()
        self.stats = StatisticsAnalyzer()
        
        self.config = {
            "Lotofácil": {"file": "Lotofácil.csv", "balls": 15, "top_n": 15, "range": 25},
            "Mega-Sena": {"file": "Mega-Sena.csv", "balls": 6, "top_n": 6, "range": 60}
        }
        
        cfg = self.config[game_type]
        self.bayesian = BayesianInference(n_range=cfg["range"])
        self.ensemble = WeightedEnsemble(n_range=cfg["range"])

    def load_data(self):
        game_cfg = self.config.get(self.game_type)
        data_path = os.path.join("../Data", game_cfg["file"])
        
        draws_with_dates = []
        try:
            with open(data_path, mode='r', encoding='latin-1') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                for row in reader:
                    if not row: continue
                    try:
                        date = datetime.datetime.strptime(row[1], "%d/%m/%Y")
                        balls = [int(x) for x in row[2:2+game_cfg["balls"]]]
                        draws_with_dates.append({'date': date, 'nums': balls})
                    except:
                        continue
            return draws_with_dates
        except Exception as e:
            print(f"Error processing {self.game_type} data: {e}")
            return []

    def train_models(self, data):
        draws_only = [d['nums'] for d in data]
        # Train Markov
        for i in range(len(draws_only) - 1):
            curr_draw = draws_only[i]
            next_draw = draws_only[i+1]
            for curr_num in curr_draw:
                for next_num in next_draw:
                    self.markov.transitions[curr_num][next_num] += 1
                    self.markov.total_transitions[curr_num] += 1
        
        # Train Bayesian
        for draw in draws_only:
            self.bayesian.update(draw)

    def run(self, mode="predict"):
        print(f"==========================================")
        print(f"   PREDICTION ENGINE: {self.game_type.upper()}   ")
        print(f"==========================================")
        
        data = self.load_data()
        if not data:
            print("[-] No data found.")
            return

        game_cfg = self.config.get(self.game_type)
        self.train_models(data)

        if mode == "analyze":
            print(f"[+] Generating correlation matrix for {len(data)} draws...")
            filename = f"correlation_{self.game_type.lower()}.png"
            self.corr.generate_matrix(data, output_path=filename)
            return

        # Default: Predict
        target_date = datetime.datetime.now()
        last_draw = data[-1]['nums']

        # Perform Analysis
        lp_number = self.numero.calculate_life_path(target_date)
        moon_phase = self.astro.get_moon_phase(target_date)
        weather = self.weather.get_weather_for_date(target_date)
        
        # Get probabilities from models
        markov_probs = self.markov.get_probabilities(last_draw)
        bayesian_probs = self.bayesian.get_probabilities()
        
        # Combined Weighted Recommendation
        env_context = {
            'life_path': lp_number,
            'moon_phase': moon_phase,
            'weather': weather
        }
        
        weighted_results = self.ensemble.combine(markov_probs, bayesian_probs, env_context)
        suggested_candidates = [num for num, score in weighted_results]

        # Output
        print(f"\n[+] Prediction for: {target_date.strftime('%Y-%m-%d')}")
        print(f"[+] Last Known Draw: {last_draw}")
        
        print("\n--- Model Insights ---")
        top_markov = [n for n, p in markov_probs[:5]]
        top_bayesian = [n for n, p in bayesian_probs[:5]]
        print(f"Markov Top Picks: {top_markov}")
        print(f"Bayesian 'Hot' Numbers: {top_bayesian}")
        
        # --- Balanced Game Optimization (Lotofácil Only) ---
        if self.game_type == "Lotofácil":
            # Simple balancing: Take top 15 and check sum
            suggested = sorted(suggested_candidates[:15])
            s = sum(suggested)
            
            # If sum too low (< 170), swap lowest for highest available candidates
            if s < 170:
                pool = sorted(suggested_candidates[15:], reverse=True) # highest of the rest
                for h_val in pool:
                    if h_val > suggested[0]:
                        suggested.pop(0)
                        suggested.append(h_val)
                        suggested.sort()
                        if sum(suggested) >= 170: break
            
            # If sum too high (> 220), swap highest for lowest available candidates
            elif s > 220:
                pool = sorted(suggested_candidates[15:]) # lowest of the rest
                for l_val in pool:
                    if l_val < suggested[-1]:
                        suggested.pop()
                        suggested.append(l_val)
                        suggested.sort()
                        if sum(suggested) <= 220: break
        else:
            # Standard combination for Mega-Sena
            suggested = sorted(suggested_candidates[:game_cfg['top_n']])

        print("\n--- Environmental Insights ---")
        print(f"Numerology (Life Path): {lp_number}")
        print(f"Astronomy (Moon Phase): {self.astro.get_phase_name(moon_phase)}")
        print(f"Weather (Predicted): {weather['condition']}, {weather['temperature']}°C")
        
        print("\n--- Final Balanced Recommendation (Weighted) ---")
        print(f"Suggested Set: {suggested}")
        print(f"Lucky Bonus: {lp_number}")
        
        # Add Statistical Profile for Lotofácil
        if self.game_type == "Lotofácil":
            self.stats.print_profile(suggested, last_draw, title="Suggested Set Profile")

        print("\n" + "="*42)
        print(" DISCLAIMER: Results are statistically random.")
        print("="*42)

if __name__ == "__main__":
    game = "Lotofácil"
    mode = "predict"
    
    for arg in sys.argv[1:]:
        if "mega" in arg.lower(): game = "Mega-Sena"
        if "analyze" in arg.lower(): mode = "analyze"
    
    engine = PredictionEngine(game_type=game)
    engine.run(mode=mode)
