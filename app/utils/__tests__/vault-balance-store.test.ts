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

describe('store vault balance (Story 4.3)', () => {
  test('defaults to 1000', () => {
    expect(useResonanceStore.getState().vaultBalance).toBe(1000);
  });

  test('accepts zero and positive balances', () => {
    useResonanceStore.getState().setVaultBalance(250);
    expect(useResonanceStore.getState().vaultBalance).toBe(250);
    useResonanceStore.getState().setVaultBalance(0);
    expect(useResonanceStore.getState().vaultBalance).toBe(0);
  });

  test('ignores NaN, negative and infinite values', () => {
    useResonanceStore.getState().setVaultBalance(75);
    for (const bad of [NaN, -5, Infinity, -Infinity]) {
      useResonanceStore.getState().setVaultBalance(bad);
      expect(useResonanceStore.getState().vaultBalance).toBe(75);
    }
  });
});
