"""
Wheels Module — combinatorial ticket-set generators.

A 'wheel' is a set of tickets covering a specific pool of numbers to 
guarantee a prize tier (e.g., '4 if 6' means if 6 numbers fall in your 
pool, you hit at least one 4-match).
"""

from .full_wheel import generate_full_wheel
from .key_wheel import generate_key_wheel
from .abbreviated import generate_abbreviated_wheel
from .evaluator import evaluate_prizes
