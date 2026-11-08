import { describe, test, expect, mock } from 'bun:test';
import {
  rebalanceWeights,
  valueFromTouch,
  scoreTickets,
  rippleOrigin,
  RIPPLE_DURATION_S,
  WEIGHT_KEYS,
  type ConsensusTicket,
} from '../equalizer';

// zustand is not declared in package.json and its install can be incomplete in this
// checkout. Fall back to a minimal API-compatible `create` so the real store logic
// is still exercised.
try {
  await import('zustand');
} catch {
  mock.module('zustand', () => ({
    create: (init: any) => {
      let state: any;
      const listeners = new Set<() => void>();
      const setState = (p: any) => {
        const patch = typeof p === 'function' ? p(state) : p;
        state = { ...state, ...patch };
        listeners.forEach((l) => l());
      };
      const getState = () => state;
      state = init(setState, getState);
      const hook: any = (sel: any) => (sel ? sel(state) : state);
      hook.setState = setState;
      hook.getState = getState;
      hook.subscribe = (l: () => void) => (listeners.add(l), () => listeners.delete(l));
      return hook;
    },
  }));
}
const { useResonanceStore } = await import('../../stores/useResonanceStore');

const equal = { frequency: 0.25, deviation: 0.25, cosmic: 0.25, ml: 0.25 };
const sum = (w: Record<string, number>) => Object.values(w).reduce((a, b) => a + b, 0);

const makeTickets = (n: number): ConsensusTicket[] =>
  Array.from({ length: n }, (_, i) => ({
    id: `t${i}`,
    components: {
      frequency: (i % 7) / 7,
      deviation: (i % 11) / 11,
      cosmic: (i % 13) / 13,
      ml: (i % 17) / 17,
    },
    score: 0,
  }));

describe('rebalanceWeights', () => {
  test('cosmic -> 0.7 from equal weights', () => {
    const w = rebalanceWeights(equal, 'cosmic', 0.7);
    expect(w.cosmic).toBeCloseTo(0.7, 10);
    expect(w.frequency).toBeCloseTo(0.1, 10);
    expect(w.deviation).toBeCloseTo(0.1, 10);
    expect(w.ml).toBeCloseTo(0.1, 10);
    expect(sum(w)).toBeCloseTo(1, 10);
  });
  test('others all zero share remainder equally', () => {
    const w = rebalanceWeights({ frequency: 0, deviation: 0, cosmic: 0, ml: 1 }, 'ml', 0.4);
    expect(w.ml).toBeCloseTo(0.4, 10);
    expect(w.frequency).toBeCloseTo(0.2, 10);
    expect(w.deviation).toBeCloseTo(0.2, 10);
    expect(w.cosmic).toBeCloseTo(0.2, 10);
    const z = rebalanceWeights({ frequency: 0, deviation: 0, cosmic: 0, ml: 0 }, 'ml', 0.4);
    expect(sum(z)).toBeCloseTo(1, 10);
  });
  test('clamps out-of-range, ignores NaN', () => {
    expect(rebalanceWeights(equal, 'ml', -0.5).ml).toBe(0);
    expect(sum(rebalanceWeights(equal, 'ml', -0.5))).toBeCloseTo(1, 10);
    const hi = rebalanceWeights(equal, 'ml', 1.7);
    expect(hi.ml).toBe(1);
    expect(hi.frequency).toBe(0);
    expect(rebalanceWeights(equal, 'ml', NaN)).toBe(equal);
  });
  test('proportional rescale keeps ratios', () => {
    const w = rebalanceWeights({ frequency: 0.5, deviation: 0.25, cosmic: 0.15, ml: 0.1 }, 'ml', 0.4);
    expect(w.frequency / w.deviation).toBeCloseTo(2, 10);
    expect(sum(w)).toBeCloseTo(1, 10);
  });
});

describe('valueFromTouch', () => {
  test('top / bottom / outside', () => {
    expect(valueFromTouch(0, 100)).toBe(1);
    expect(valueFromTouch(100, 100)).toBe(0);
    expect(valueFromTouch(50, 100)).toBe(0.5);
    expect(valueFromTouch(-20, 100)).toBe(1);
    expect(valueFromTouch(250, 100)).toBe(0);
  });
});

describe('scoreTickets', () => {
  test('weighted sum sorted descending', () => {
    const t: ConsensusTicket[] = [
      { id: 'a', components: { frequency: 1 }, score: 0 },
      { id: 'b', components: { ml: 1 }, score: 0 },
    ];
    const r = scoreTickets(t, { frequency: 0.2, deviation: 0, cosmic: 0, ml: 0.8 });
    expect(r.map((x) => x.id)).toEqual(['b', 'a']);
    expect(r[0].score).toBeCloseTo(0.8, 10);
    expect(r[1].score).toBeCloseTo(0.2, 10);
  });
  test('invalid components score as 0, no throw', () => {
    const t = [
      { id: 'x', components: { frequency: NaN, ml: Infinity, cosmic: 0.5 }, score: 0 },
      { id: 'y', score: 0 } as unknown as ConsensusTicket,
    ];
    const r = scoreTickets(t, equal);
    expect(r.find((x) => x.id === 'x')!.score).toBeCloseTo(0.125, 10);
    expect(r.find((x) => x.id === 'y')!.score).toBe(0);
  });
  test('10,000 tickets under 100ms', () => {
    const t = makeTickets(10000);
    const start = performance.now();
    const r = scoreTickets(t, rebalanceWeights(equal, 'cosmic', 0.7));
    const ms = performance.now() - start;
    expect(ms).toBeLessThan(100);
    for (let i = 1; i < r.length; i++) expect(r[i - 1].score).toBeGreaterThanOrEqual(r[i].score);
  });
});

describe('ripple helpers', () => {
  test('origin per key and duration', () => {
    expect(RIPPLE_DURATION_S).toBeGreaterThan(0);
    const origins = WEIGHT_KEYS.map((k) => rippleOrigin(k).join(','));
    expect(new Set(origins).size).toBe(4);
  });
});

describe('store setEqualizerWeight', () => {
  test('updates weights, rescores, ripples atomically', () => {
    const s = useResonanceStore;
    s.setState({ weights: { ...equal }, ripple: { id: 0, key: null } });
    s.getState().setConsensusTickets(makeTickets(10000));
    const before = s.getState().ripple.id;
    s.getState().setEqualizerWeight('cosmic', 0.7);
    const st = s.getState();
    expect(st.weights.cosmic).toBeCloseTo(0.7, 10);
    expect(sum(st.weights)).toBeCloseTo(1, 10);
    expect(st.ripple.id).toBe(before + 1);
    expect(st.ripple.key).toBe('cosmic');
    expect(st.lastRescoreMs).toBeGreaterThanOrEqual(0);
    expect(st.lastRescoreMs).toBeLessThan(100);
    expect(st.consensusTickets).toHaveLength(10000);
    expect(st.consensusTickets[0].score).toBeGreaterThanOrEqual(st.consensusTickets[9999].score);
  });
  test('NaN is a no-op', () => {
    const s = useResonanceStore;
    const w = s.getState().weights;
    const id = s.getState().ripple.id;
    s.getState().setEqualizerWeight('ml', NaN);
    expect(s.getState().weights).toBe(w);
    expect(s.getState().ripple.id).toBe(id);
  });
});

describe('store telemetry weight updates rescore tickets', () => {
  const tickets: ConsensusTicket[] = [
    { id: 'a', components: { frequency: 1 }, score: 0 },
    { id: 'b', components: { ml: 1 }, score: 0 },
  ];
  test('setWeights rescores without rippling', () => {
    const s = useResonanceStore;
    s.setState({ weights: { ...equal }, ripple: { id: 5, key: null } });
    s.getState().setConsensusTickets(tickets);
    s.getState().setWeights({ frequency: 0.1, ml: 0.9 });
    const st = s.getState();
    expect(st.consensusTickets.map((t) => t.id)).toEqual(['b', 'a']);
    expect(st.consensusTickets[0].score).toBeCloseTo(0.9, 10);
    expect(st.ripple.id).toBe(5);
  });
  test('setManifoldState rescores without rippling', () => {
    const s = useResonanceStore;
    s.setState({ weights: { ...equal }, ripple: { id: 7, key: null } });
    s.getState().setConsensusTickets(tickets);
    s.getState().setManifoldState({ frequency: 0.9, deviation: 0, cosmic: 0, ml: 0.1 }, 3);
    const st = s.getState();
    expect(st.consensusTickets.map((t) => t.id)).toEqual(['a', 'b']);
    expect(st.consensusTickets[0].score).toBeCloseTo(0.9, 10);
    expect(st.manifoldEpoch).toBe(3);
    expect(st.ripple.id).toBe(7);
  });
});
