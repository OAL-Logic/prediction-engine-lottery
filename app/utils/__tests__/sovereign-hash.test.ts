import { generateIntentionalHash } from '../sovereign-hash';

describe('Sovereign Hashing Utility', () => {
  it('should generate a 64-character hex string', () => {
    const hash = generateIntentionalHash('Operator X', '1990-01-01', 'draw-123');
    expect(hash).toHaveLength(64);
    expect(hash).toMatch(/^[a-f0-9]+$/);
  });

  it('should be deterministic for the same inputs', () => {
    const hash1 = generateIntentionalHash('Operator X', '1990-01-01', 'draw-123');
    const hash2 = generateIntentionalHash('Operator X', '1990-01-01', 'draw-123');
    expect(hash1).toBe(hash2);
  });

  it('should change if salt (drawId) changes', () => {
    const hash1 = generateIntentionalHash('Operator X', '1990-01-01', 'draw-123');
    const hash2 = generateIntentionalHash('Operator X', '1990-01-01', 'draw-124');
    expect(hash1).not.toBe(hash2);
  });

  it('should normalize inputs (trim and lowercase)', () => {
    const hash1 = generateIntentionalHash('  Operator X  ', '1990-01-01', 'draw-123');
    const hash2 = generateIntentionalHash('operator x', '1990-01-01', 'draw-123');
    expect(hash1).toBe(hash2);
  });
});
