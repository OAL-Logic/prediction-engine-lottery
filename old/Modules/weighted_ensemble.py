from collections import defaultdict
import datetime

class WeightedEnsemble:
    def __init__(self, n_range=25):
        self.n_range = n_range
        self.weights = {
            "markov": 0.4,
            "bayesian": 0.4,
            "environmental": 0.2
        }

    def combine(self, markov_probs, bayesian_probs, environmental_context):
        """
        markov_probs: list of (num, prob)
        bayesian_probs: list of (num, prob)
        environmental_context: {'life_path': int, 'moon_phase': float, 'weather': dict}
        """
        scores = defaultdict(float)
        
        # 1. Markov Scores (already probabilities)
        m_dict = dict(markov_probs)
        for i in range(1, self.n_range + 1):
            scores[i] += self.weights["markov"] * m_dict.get(i, 0.0)
            
        # 2. Bayesian Scores (already probabilities)
        b_dict = dict(bayesian_probs)
        for i in range(1, self.n_range + 1):
            scores[i] += self.weights["bayesian"] * b_dict.get(i, 0.0)
            
        # 3. Environmental Scores
        # Simple heuristic: bonus if number shares digits with life path or is related to moon
        env_scores = self.calculate_environmental_scores(environmental_context)
        for i in range(1, self.n_range + 1):
            scores[i] += self.weights["environmental"] * env_scores.get(i, 0.0)
            
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def calculate_environmental_scores(self, context):
        env_scores = defaultdict(float)
        lp = context.get('life_path', 0)
        
        # Life Path influence (numbers that reduce to LP or contain LP)
        for i in range(1, self.n_range + 1):
            # Reduced digit
            if (i % 9 == lp % 9) or (str(lp) in str(i)):
                env_scores[i] += 0.5
        
        # Moon phase influence (just a fun mapping)
        moon = context.get('moon_phase', 0.5)
        # Higher numbers on full moon (0.5), lower on new moon (0.0/1.0)
        for i in range(1, self.n_range + 1):
            rel_pos = i / self.n_range
            moon_dist = 1.0 - abs(moon - 0.5) * 2 # 1.0 at full moon, 0.0 at new moon
            if abs(rel_pos - moon_dist) < 0.2:
                env_scores[i] += 0.3
        
        # Normalize env_scores to 0.0-1.0 range roughly
        max_s = max(env_scores.values()) if env_scores else 1.0
        for i in env_scores:
            env_scores[i] /= max_s
            
        return env_scores
