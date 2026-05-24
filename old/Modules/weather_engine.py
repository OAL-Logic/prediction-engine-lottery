import random

class WeatherEngine:
    """
    Simulates or fetches weather conditions for draw dates.
    In a production app, this would call OpenWeatherMap or Visual Crossing API.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.weather_types = ["Sunny", "Rainy", "Cloudy", "Stormy", "Snowy", "Windy"]

    def get_weather_for_date(self, date):
        """
        Mock function to simulate historical weather based on the date seed.
        Ensures consistency for the same date.
        """
        random.seed(date.strftime("%Y%m%d"))
        temp = random.randint(15, 35) # Celsius
        condition = random.choice(self.weather_types)
        humidity = random.randint(30, 90)
        return {
            "condition": condition,
            "temperature": temp,
            "humidity": humidity
        }

    def analyze_weather_correlation(self, draw_results):
        """
        Example logic: "Do even numbers appear more on Rainy days?"
        """
        stats = {w: {"evens": 0, "odds": 0} for w in self.weather_types}
        
        for draw in draw_results:
            weather = self.get_weather_for_date(draw['date'])
            cond = weather['condition']
            for n in draw['nums']:
                if n % 2 == 0:
                    stats[cond]["evens"] += 1
                else:
                    stats[cond]["odds"] += 1
        return stats

if __name__ == "__main__":
    import datetime
    engine = WeatherEngine()
    test_date = datetime.datetime.now()
    weather = engine.get_weather_for_date(test_date)
    print(f"--- Weather Analysis ---")
    print(f"Date: {test_date.strftime('%Y-%m-%d')}")
    print(f"Simulated Weather: {weather['condition']}, {weather['temperature']}°C")
