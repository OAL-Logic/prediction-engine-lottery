import csv
from collections import defaultdict
import datetime

class MarkovPredictor:
    """
    A 1st-order Markov Chain predictor for lottery numbers.
    """
    def __init__(self):
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.total_transitions = defaultdict(int)
        self.game_type = "unknown"
    
    def train_from_csv(self, file_path, date_col=1, first_num_col=2):
        """
        Loads CSV and trains the model.
        Lotofácil: first_num_col=2 (Bola1), last_num_col=16 (Bola15)
        Mega-Sena: first_num_col=2 (Bola1), last_num_col=7 (Bola6)
        """
        draws = []
        try:
            # Determine game type from filename
            filename = file_path.lower()
            if "lotofacil" in filename or "lotofcil" in filename:
                self.game_type = "lotofacil"
                num_count = 15
            elif "mega-sena" in filename:
                self.game_type = "mega-sena"
                num_count = 6
            else:
                num_count = 6 # default
            
            with open(file_path, mode='r', encoding='latin-1') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if not row or len(row) < first_num_col + num_count: continue
                    try:
                        # Extract the numbers based on game type
                        nums = [int(x) for x in row[first_num_col : first_num_col + num_count]]
                        draws.append(nums)
                    except ValueError:
                        continue # Skip bad rows
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return

        # Train transitions (Draw N -> Draw N+1)
        for i in range(len(draws) - 1):
            curr_draw = draws[i]
            next_draw = draws[i+1]
            
            for curr_num in curr_draw:
                for next_num in next_draw:
                    self.transitions[curr_num][next_num] += 1
                    self.total_transitions[curr_num] += 1
                    
    def get_probabilities(self, last_draw):
        scores = defaultdict(float)
        for num in last_draw:
            if num in self.transitions:
                total = self.total_transitions[num]
                for next_num, count in self.transitions[num].items():
                    scores[next_num] += (count / total)
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def predict(self, last_draw, top_n=None):
        if top_n is None:
            top_n = 15 if self.game_type == "lotofacil" else 6
            
        probs = self.get_probabilities(last_draw)
        return [num for num, score in probs[:top_n]]

if __name__ == "__main__":
    # Test with real Mega-Sena data if exists
    import os
    ms_path = "../Data/Mega-Sena.csv"
    if os.path.exists(ms_path):
        model = MarkovPredictor()
        model.train_from_csv(ms_path)
        last = [1, 5, 10, 15, 20, 25] # Example
        print(f"Mega-Sena Prediction: {model.predict(last)}")
