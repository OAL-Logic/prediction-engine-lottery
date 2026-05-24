import datetime

class NumerologyAnalyzer:
    """
    Calculates Numerology correlations (Life Path Number) for draw dates.
    """
    def calculate_life_path(self, date):
        """
        Sum all digits of the date (YYYY-MM-DD) until a single digit (or master number) remains.
        """
        digits = date.strftime("%Y%m%d")
        return self._sum_digits(digits)

    def _sum_digits(self, number_str):
        total = sum(int(d) for d in number_str)
        # Numerology usually reduces to 1-9, but keeps 11, 22, 33 (Master numbers)
        if total > 9 and total not in [11, 22, 33]:
            return self._sum_digits(str(total))
        return total

    def get_number_meaning(self, number):
        meanings = {
            1: "New beginnings, leadership",
            2: "Balance, harmony, diplomacy",
            3: "Communication, creativity, expression",
            4: "Structure, stability, foundation",
            5: "Change, freedom, adventure",
            6: "Responsibility, service, protection",
            7: "Inner wisdom, spirituality, analysis",
            8: "Power, abundance, success",
            9: "Completion, humanitarianism, release",
            11: "Visionary, intuition (Master Number)",
            22: "Master Builder (Master Number)",
            33: "Master Teacher (Master Number)"
        }
        return meanings.get(number, "Unknown")

if __name__ == "__main__":
    analyzer = NumerologyAnalyzer()
    test_date = datetime.datetime(2026, 4, 21)
    lp = analyzer.calculate_life_path(test_date)
    print(f"--- Numerology Analysis ---")
    print(f"Date: {test_date.strftime('%Y-%m-%d')}")
    print(f"Life Path Number: {lp} ({analyzer.get_number_meaning(lp)})")
