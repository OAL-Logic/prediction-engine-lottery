import { describe, test, expect } from 'bun:test';
import { confidenceLeverage, MAX_FRACTION } from '../kelly';

describe('confidenceLeverage', () => {
  test('above baseline (Python parity: 0.2 / 0.05 / 50)', () => {
    const r = confidenceLeverage(0.6, 1000)!;
    expect(r.fullKelly).toBeCloseTo(0.2, 12);
    expect(r.fraction).toBeCloseTo(0.05, 12);
    expect(r.stake).toBeCloseTo(50, 9);
    expect(r.active).toBe(true);
  });
  test('at/below baseline', () => {
    for (const p of [0.5, 0.4, 0]) {
      const r = confidenceLeverage(p, 1000)!;
      expect([r.fraction, r.stake, r.active]).toEqual([0, 0, false]);
    }
  });
  test('cap (Python parity: 0.98 -> 0.10 / 100)', () => {
    const r = confidenceLeverage(0.99, 1000)!;
    expect(r.fullKelly).toBeCloseTo(0.98, 12);
    expect(r.fraction).toBe(MAX_FRACTION);
    expect(r.stake).toBeCloseTo(100, 9);
  });
  test('zero balance', () => {
    const r = confidenceLeverage(0.9, 0)!;
    expect(r.fraction).toBeGreaterThan(0);
    expect(r.stake).toBe(0);
    expect(r.active).toBe(true);
  });
  test('negative edge gives zero', () => {
    const r = confidenceLeverage(0.55, 1000, { odds: 0.5 })!;
    expect(r.fraction).toBe(0);
    expect(r.active).toBe(false);
  });
  test('bad input returns null', () => {
    expect(confidenceLeverage(NaN, 100)).toBeNull();
    expect(confidenceLeverage(Infinity, 100)).toBeNull();
    expect(confidenceLeverage(1.2, 100)).toBeNull();
    expect(confidenceLeverage(-0.1, 100)).toBeNull();
    expect(confidenceLeverage(0.6, -1)).toBeNull();
    expect(confidenceLeverage(0.6, NaN)).toBeNull();
    expect(confidenceLeverage(0.6, 100, { odds: 0 })).toBeNull();
    expect(confidenceLeverage(0.6, 100, { odds: -1 })).toBeNull();
  });
});
