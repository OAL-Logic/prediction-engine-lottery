import { describe, test, expect } from 'bun:test';
import {
  GHOST_FADE_S,
  fadeAlphas,
  ghostGeometry,
  parseReplayPayload,
  stepFadeProgress,
  alphasFromProgress,
} from '../ghost';

const payload = {
  seq: 1,
  ticket: [1, 2, 3],
  state_vector: [0.1, 0.2, 0.3, 0.4],
  agent_weights: { a: 1 },
  qpu_fidelity: 0.9,
  entry_hash: 'ab',
  captured_at: '2026-11-09T00:00:00+00:00',
};

describe('fadeAlphas', () => {
  test('fade in midpoint', () => {
    const a = fadeAlphas(GHOST_FADE_S / 2);
    expect(a.current).toBeCloseTo(0.5);
    expect(a.ghost).toBeCloseTo(0.5);
  });
  test('fade end clamps', () => {
    expect(fadeAlphas(GHOST_FADE_S)).toEqual({ current: 0, ghost: 1 });
    expect(fadeAlphas(GHOST_FADE_S * 10)).toEqual({ current: 0, ghost: 1 });
    expect(fadeAlphas(-5)).toEqual({ current: 1, ghost: 0 });
  });
  test('exit reverses', () => {
    expect(fadeAlphas(0, false)).toEqual({ current: 0, ghost: 1 });
    expect(fadeAlphas(GHOST_FADE_S, false)).toEqual({ current: 1, ghost: 0 });
  });
  test('progress stepping fades in then back out', () => {
    let p = 0;
    p = stepFadeProgress(p, GHOST_FADE_S / 2, true);
    expect(alphasFromProgress(p).ghost).toBeCloseTo(0.5);
    p = stepFadeProgress(p, GHOST_FADE_S * 5, true);
    expect(alphasFromProgress(p)).toEqual({ current: 0, ghost: 1 });
    p = stepFadeProgress(p, GHOST_FADE_S * 5, false);
    expect(alphasFromProgress(p)).toEqual({ current: 1, ghost: 0 });
  });
});

describe('ghostGeometry', () => {
  test('valid vector yields finite segment pairs', () => {
    const g = ghostGeometry([0.25, 0.25, 0.25, 0.25])!;
    expect(g).not.toBeNull();
    expect(g.length % 6).toBe(0);
    expect(Array.from(g).every(Number.isFinite)).toBe(true);
  });
  test('short vector is zero padded', () => {
    expect(ghostGeometry([0.5])).not.toBeNull();
  });
  test('bad vectors return null', () => {
    expect(ghostGeometry([])).toBeNull();
    expect(ghostGeometry([NaN, 1])).toBeNull();
    expect(ghostGeometry([Infinity])).toBeNull();
    expect(ghostGeometry(null)).toBeNull();
  });
});

describe('parseReplayPayload', () => {
  test('accepts valid', () => {
    expect(parseReplayPayload(payload)).toEqual(payload);
  });
  test('rejects bad', () => {
    expect(parseReplayPayload(null)).toBeNull();
    expect(parseReplayPayload({ ...payload, state_vector: [] })).toBeNull();
    expect(parseReplayPayload({ ...payload, state_vector: [NaN] })).toBeNull();
    expect(parseReplayPayload({ ...payload, seq: 0 })).toBeNull();
  });
});
