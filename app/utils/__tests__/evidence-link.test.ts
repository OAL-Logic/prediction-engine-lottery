import { describe, expect, test } from 'bun:test';
import { matchesReplay, parseEvidenceLink } from '../evidence-link';
import type { ReplayPayload } from '../ghost';

const HASH = 'aa19bd9bd8e386517bbcbb6e660ea8ef6c68e67152e9d8fd3badf3e18be8bf1b';
// Literal link produced by engine/modules/obsidian_export.py
const LINK = `lottery://evidence/1?hash=${HASH}&coords=0.1,-2.5e-17,0.3333333333333333,1e+16`;
const COORDS = [0.1, -2.5e-17, 1 / 3, 1e16];

const replay = (over: Partial<ReplayPayload> = {}): ReplayPayload => ({
  seq: 1,
  ticket: [1, 2],
  state_vector: COORDS,
  agent_weights: { a: 1 },
  qpu_fidelity: 0.9,
  entry_hash: HASH,
  captured_at: '2026-11-12T00:00:00Z',
  ...over,
});

describe('parseEvidenceLink', () => {
  test('parses the Python-exported link exactly', () => {
    expect(parseEvidenceLink(LINK)).toEqual({ seq: 1, hash: HASH, coords: COORDS });
  });

  test.each([
    ['wrong scheme', LINK.replace('lottery', 'http')],
    ['seq zero', LINK.replace('/1?', '/0?')],
    ['negative seq', LINK.replace('/1?', '/-1?')],
    ['non-numeric seq', LINK.replace('/1?', '/x?')],
    ['missing hash', 'lottery://evidence/1?coords=0.1'],
    ['missing coords', `lottery://evidence/1?hash=${HASH}`],
    ['NaN coord', `lottery://evidence/1?hash=${HASH}&coords=0.1,NaN`],
    ['Infinity coord', `lottery://evidence/1?hash=${HASH}&coords=Infinity`],
    ['overflow coord', `lottery://evidence/1?hash=${HASH}&coords=1e999`],
    ['empty coord', `lottery://evidence/1?hash=${HASH}&coords=0.1,,0.2`],
    ['no query', 'lottery://evidence/1'],
  ])('null for %s', (_n, url) => {
    expect(parseEvidenceLink(url)).toBeNull();
  });

  test('null for non-string', () => {
    expect(parseEvidenceLink(undefined)).toBeNull();
  });
});

describe('matchesReplay', () => {
  const link = parseEvidenceLink(LINK)!;
  test('true for equal payload', () => expect(matchesReplay(link, replay())).toBe(true));
  test('false on seq/hash/coord mismatch', () => {
    expect(matchesReplay(link, replay({ seq: 2 }))).toBe(false);
    expect(matchesReplay(link, replay({ entry_hash: 'b'.repeat(64) }))).toBe(false);
    expect(matchesReplay(link, replay({ state_vector: [...COORDS.slice(0, 3), 2] }))).toBe(false);
    expect(matchesReplay(link, replay({ state_vector: COORDS.slice(0, 3) }))).toBe(false);
  });
  test('false for null link', () => expect(matchesReplay(null, replay())).toBe(false));
});
