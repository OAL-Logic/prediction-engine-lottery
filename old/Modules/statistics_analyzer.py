class StatisticsAnalyzer:
    """
    Calculates specific lottery patterns for Lotofácil (25 numbers).
    Includes Frame (Moldura), Center (Miolo), Fibonacci, Primes, and Parity.
    """
    def __init__(self):
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        self.fibonacci = [1, 2, 3, 5, 8, 13, 21]
        self.frame = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
        self.center = [7, 8, 9, 12, 13, 14, 17, 18, 19]

    def calculate_stats(self, draw, previous_draw=None):
        """
        returns a dictionary with all relevant Lotofácil metrics.
        """
        evens = [x for x in draw if x % 2 == 0]
        odds = [x for x in draw if x % 2 != 0]
        
        lows = [x for x in draw if x <= 13]
        highs = [x for x in draw if x > 13]
        
        primes_count = len([x for x in draw if x in self.primes])
        fib_count = len([x for x in draw if x in self.fibonacci])
        frame_count = len([x for x in draw if x in self.frame])
        center_count = len([x for x in draw if x in self.center])
        
        total_sum = sum(draw)
        is_balanced_sum = 170 <= total_sum <= 220
        
        repeats = 0
        if previous_draw:
            repeats = len(set(draw) & set(previous_draw))
            
        return {
            "sum": total_sum,
            "sum_balanced": is_balanced_sum,
            "even_odd": f"{len(evens)}E / {len(odds)}O",
            "low_high": f"{len(lows)}L / {len(highs)}H",
            "primes": primes_count,
            "fibonacci": fib_count,
            "frame_center": f"{frame_count}F / {center_count}C",
            "repeats": repeats
        }

    def print_profile(self, draw, previous_draw=None, title="Statistical Profile"):
        stats = self.calculate_stats(draw, previous_draw)
        print(f"\n--- {title} ---")
        sum_status = "✅" if stats['sum_balanced'] else "❌ (Target 170-220)"
        print(f"Sum: {stats['sum']} {sum_status}")
        print(f"Parity: {stats['even_odd']}")
        print(f"Low/High: {stats['low_high']}")
        print(f"Primes: {stats['primes']}")
        print(f"Fibonacci: {stats['fibonacci']}")
        print(f"Frame/Center: {stats['frame_center']}")
        if previous_draw:
            print(f"Repeats from Last: {stats['repeats']}")

if __name__ == "__main__":
    # Test
    analyzer = StatisticsAnalyzer()
    draw = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    prev = [1, 2, 3, 20, 21, 22, 23, 24, 25, 10, 11, 12, 13, 14, 15]
    analyzer.print_profile(draw, prev)
