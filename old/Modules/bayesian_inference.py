from collections import defaultdict

class BayesianInference:
    """
    Tracks 'Hot' and 'Cold' numbers using Bayesian updating.
    Starts with a Uniform Prior and updates the 'Posterior' as new data arrives.
    """
    def __init__(self, n_range=25):
        self.n_range = n_range
        # Prior: All numbers have equal chance
        self.priors = {i: 1.0 for i in range(1, n_range + 1)}
        self.counts = defaultdict(int)
        self.total_draws = 0

    def update(self, draw):
        """
        Update counts based on a new draw.
        """
        self.total_draws += 1
        for num in draw:
            self.counts[num] += 1

    def get_probabilities(self):
        """
        Calculates the posterior probability (Likelihood * Prior).
        Since we assume a uniform prior, the posterior is proportional to frequency.
        """
        if self.total_draws == 0:
            return self.priors

        # Bayesian Likelihood: how often a number appears compared to the mean
        probabilities = {}
        for i in range(1, self.n_range + 1):
            # Laplace smoothing to avoid zero probability
            likelihood = (self.counts[i] + 1) / (self.total_draws + 2)
            probabilities[i] = likelihood
        
        return sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

    def get_hot_cold(self, top_n=5):
        probs = self.get_probabilities()
        hot = [x[0] for x in probs[:top_n]]
        cold = [x[0] for x in probs[-top_n:]]
        return hot, cold

if __name__ == "__main__":
    # Test with dummy data
    engine = BayesianInference(n_range=25)
    engine.update([1, 2, 3, 4, 5])
    engine.update([1, 2, 3, 10, 11])
    
    hot, cold = engine.get_hot_cold()
    print(f"--- Bayesian Hot/Cold ---")
    print(f"Hot (Most Likely): {hot}")
    print(f"Cold (Least Likely): {cold}")
