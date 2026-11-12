// Swarm-based fractional Kelly sizer (Story 4.3). Mirrors engine/swarm/kelly.py.

export const BASELINE_CONFIDENCE = 0.5;
export const KELLY_FRACTION = 0.25;
export const MAX_FRACTION = 0.1;
export const DEFAULT_ODDS = 1.0;

export interface KellyLeverage {
  confidence: number;
  fullKelly: number;
  fraction: number;
  stake: number;
  active: boolean;
}

export interface KellyOptions {
  odds?: number;
  baseline?: number;
  kellyFraction?: number;
  maxFraction?: number;
}

const finite = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x);

/** Size a bet from swarm confidence; returns null on invalid input. */
export function confidenceLeverage(
  confidence: number,
  vaultBalance: number,
  opts: KellyOptions = {},
): KellyLeverage | null {
  const {
    odds = DEFAULT_ODDS,
    baseline = BASELINE_CONFIDENCE,
    kellyFraction = KELLY_FRACTION,
    maxFraction = MAX_FRACTION,
  } = opts;
  if (![confidence, vaultBalance, odds, baseline, kellyFraction, maxFraction].every(finite)) {
    return null;
  }
  if (confidence < 0 || confidence > 1 || odds <= 0 || vaultBalance < 0) return null;
  if (kellyFraction < 0 || maxFraction < 0) return null;

  if (confidence <= baseline) {
    return { confidence, fullKelly: 0, fraction: 0, stake: 0, active: false };
  }
  const fullKelly = Math.max(0, (odds * confidence - (1 - confidence)) / odds);
  const fraction = Math.min(fullKelly * kellyFraction, maxFraction);
  return { confidence, fullKelly, fraction, stake: fraction * vaultBalance, active: fraction > 0 };
}
