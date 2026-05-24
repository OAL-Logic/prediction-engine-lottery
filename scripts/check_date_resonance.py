from datetime import date
from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name, moon_distance_ratio, tidal_intensity

target_date = date(2026, 5, 24)
ratio = moon_phase_ratio(target_date)
name = phase_name(target_date)
dist = moon_distance_ratio(target_date)
tide = tidal_intensity(ratio, dist)

print(f"Date: {target_date}")
print(f"Moon Phase: {name} ({ratio:.4f})")
print(f"Moon Distance: {dist:.4f}")
print(f"Tidal Intensity: {tide:.4f}")
