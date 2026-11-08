import { describe, test, expect } from 'bun:test';
import { parseManifoldTelemetry, applyManifoldMessage } from '../manifold-telemetry';

const good = {
  epoch: 3,
  weights: { frequency: 0.4, deviation: 0.3, cosmic: 0.2, ml: 0.1 },
  distance_to_consensus: 0.12,
};

describe('parseManifoldTelemetry', () => {
  test('parses a valid pulse', () => {
    const r = parseManifoldTelemetry('MANIFOLD_STATE ' + JSON.stringify(good));
    expect(r?.epoch).toBe(3);
    expect(r?.weights).toEqual(good.weights);
    expect(r?.distanceToConsensus).toBe(0.12);
  });
  test('ignores other messages', () => {
    expect(parseManifoldTelemetry('Swarm round 1')).toBeNull();
    expect(parseManifoldTelemetry(undefined)).toBeNull();
  });
  test('ignores malformed JSON and bad weights', () => {
    expect(parseManifoldTelemetry('MANIFOLD_STATE {nope')).toBeNull();
    expect(parseManifoldTelemetry('MANIFOLD_STATE {"epoch":1}')).toBeNull();
    const bad = { ...good, weights: { ...good.weights, ml: 0.5 } };
    expect(parseManifoldTelemetry('MANIFOLD_STATE ' + JSON.stringify(bad))).toBeNull();
    const nan = { ...good, weights: { ...good.weights, ml: 'x' } };
    expect(parseManifoldTelemetry('MANIFOLD_STATE ' + JSON.stringify(nan))).toBeNull();
  });
  test('rejects missing or invalid epoch instead of resetting to 0', () => {
    for (const epoch of [undefined, -1, 1.5, '3']) {
      const p = { ...good, epoch };
      expect(parseManifoldTelemetry('MANIFOLD_STATE ' + JSON.stringify(p))).toBeNull();
    }
  });
});

describe('applyManifoldMessage', () => {
  test('forwards a valid pulse to the store setter', () => {
    const calls: any[] = [];
    const ok = applyManifoldMessage('MANIFOLD_STATE ' + JSON.stringify(good), (w, e) => calls.push([w, e]));
    expect(ok).toBe(true);
    expect(calls).toEqual([[good.weights, 3]]);
  });
  test('leaves the store untouched for other or invalid messages', () => {
    const calls: any[] = [];
    const set = (w: any, e: number) => calls.push([w, e]);
    expect(applyManifoldMessage('Swarm round 1', set)).toBe(false);
    expect(applyManifoldMessage('MANIFOLD_STATE {nope', set)).toBe(false);
    expect(calls.length).toBe(0);
  });
});
