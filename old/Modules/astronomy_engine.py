import datetime
import math

class AstronomyEngine:
    """
    Calculates astronomical correlations (Moon Phase, Sun Position) for a given date.
    """
    def __init__(self):
        # Constants for moon phase calculation
        self.LUNAR_MONTH = 29.530588853
        # Reference new moon: 2000-01-06 18:14 UTC
        self.REFERENCE_NEW_MOON = datetime.datetime(2000, 1, 6, 18, 14)

    def get_moon_phase(self, date):
        """
        Calculates the moon phase as a float (0.0 = New Moon, 0.5 = Full Moon, 1.0 = New Moon again).
        """
        diff = date - self.REFERENCE_NEW_MOON
        days = diff.total_seconds() / 86400
        phase = (days % self.LUNAR_MONTH) / self.LUNAR_MONTH
        return phase

    def get_phase_name(self, phase):
        if phase < 0.06 or phase > 0.94: return "New Moon"
        if phase < 0.19: return "Waxing Crescent"
        if phase < 0.31: return "First Quarter"
        if phase < 0.44: return "Waxing Gibbous"
        if phase < 0.56: return "Full Moon"
        if phase < 0.69: return "Waning Gibbous"
        if phase < 0.81: return "Last Quarter"
        return "Waning Crescent"

    def analyze_correlation(self, csv_path):
        """
        Checks if certain numbers appear more often during specific moon phases.
        """
        # Note: In a real project, use pandas here. 
        # Using csv module for portability.
        import csv
        results = []
        try:
            with open(csv_path, mode='r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    date = datetime.datetime.strptime(row[0], "%Y-%m-%d")
                    nums = [int(x) for x in row[1:]]
                    phase = self.get_moon_phase(date)
                    results.append({'date': date, 'nums': nums, 'phase': self.get_phase_name(phase)})
        except Exception as e:
            print(f"Astronomy error: {e}")
            
        return results

if __name__ == "__main__":
    engine = AstronomyEngine()
    now = datetime.datetime.now()
    phase = engine.get_moon_phase(now)
    print(f"--- Astronomy Analysis ---")
    print(f"Date: {now.strftime('%Y-%m-%d')}")
    print(f"Moon Phase: {phase:.2f} ({engine.get_phase_name(phase)})")
