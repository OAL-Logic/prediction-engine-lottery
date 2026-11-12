import { describe, test, expect, mock } from 'bun:test';

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

const payload = {
  seq: 1,
  ticket: [1, 2, 3],
  state_vector: [0.1, 0.2, 0.3, 0.4],
  agent_weights: { frequency: 0.25 },
  qpu_fidelity: 0.9,
  entry_hash: 'abc',
  captured_at: '2026-01-01T00:00:00Z',
};

describe('store replay slice', () => {
  const reset = () => useResonanceStore.setState({ replay: null, replayActive: false });
  test('startReplay() with nothing loaded is a no-op', () => {
    reset();
    useResonanceStore.getState().startReplay();
    expect(useResonanceStore.getState().replayActive).toBe(false);
  });
  test('startReplay(valid) loads and activates; stopReplay deactivates', () => {
    reset();
    useResonanceStore.getState().startReplay(payload);
    expect(useResonanceStore.getState().replay?.seq).toBe(1);
    expect(useResonanceStore.getState().replayActive).toBe(true);
    useResonanceStore.getState().stopReplay();
    expect(useResonanceStore.getState().replayActive).toBe(false);
    expect(useResonanceStore.getState().replay?.seq).toBe(1);
  });
  test('invalid payloads change nothing', () => {
    reset();
    useResonanceStore.getState().loadReplay(payload);
    const loaded = useResonanceStore.getState().replay;
    useResonanceStore.getState().loadReplay({ ...payload, state_vector: [NaN] });
    useResonanceStore.getState().startReplay({ ...payload, state_vector: [] });
    expect(useResonanceStore.getState().replay).toBe(loaded);
    expect(useResonanceStore.getState().replayActive).toBe(false);
  });
});
