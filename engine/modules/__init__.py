"""
Analysis modules — stateless functions that operate on a canonical DataFrame.

Each module exposes a single top-level function:
    frequency.analyze(df, rules)   -> FrequencyResult
    deviation.analyze(df, rules)   -> DeviationResult
    correlation.analyze(df, rules) -> CorrelationResult

All functions are pure: same input → same output, no side effects.
"""
