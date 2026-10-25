import { describe, test, expect } from 'bun:test';
import {
  RITUAL_CATALOG,
  getDailyIndex,
  getDailyNumerologyRoot,
  getDailyRitual,
} from '../daily-ritual';

describe('DailyRitual Engine', () => {
  test('RITUAL_CATALOG contains valid 30-second rituals and affirmations', () => {
    expect(RITUAL_CATALOG.length).toBeGreaterThanOrEqual(10);
    RITUAL_CATALOG.forEach(ritual => {
      expect(ritual.id).toBeDefined();
      expect(ritual.title).toBeDefined();
      expect(ritual.affirmation.length).toBeGreaterThan(15);
      expect(ritual.action.length).toBeGreaterThan(15);
      expect(ritual.steps.length).toBe(3);
      expect(ritual.vibration).toBeDefined();
      expect(ritual.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
    });
  });

  test('getDailyIndex is deterministic for identical dates', () => {
    const idx1 = getDailyIndex('2026-10-25', RITUAL_CATALOG.length);
    const idx2 = getDailyIndex('2026-10-25', RITUAL_CATALOG.length);
    expect(idx1).toBe(idx2);
    expect(idx1).toBeGreaterThanOrEqual(0);
    expect(idx1).toBeLessThan(RITUAL_CATALOG.length);
  });

  test('getDailyIndex varies across different dates', () => {
    const indices = new Set([
      getDailyIndex('2026-10-25', RITUAL_CATALOG.length),
      getDailyIndex('2026-10-26', RITUAL_CATALOG.length),
      getDailyIndex('2026-10-27', RITUAL_CATALOG.length),
      getDailyIndex('2026-10-28', RITUAL_CATALOG.length),
    ]);
    expect(indices.size).toBeGreaterThan(1);
  });

  test('getDailyNumerologyRoot reduces dates to 1-9 correctly', () => {
    // 2026-10-25 -> 2+0+2+6+1+0+2+5 = 18 -> 1+8 = 9
    expect(getDailyNumerologyRoot('2026-10-25')).toBe(9);
    // 2026-01-01 -> 2+0+2+6+0+1+0+1 = 12 -> 1+2 = 3
    expect(getDailyNumerologyRoot('2026-01-01')).toBe(3);
    // 1990-01-01 -> 1+9+9+0+0+1+0+1 = 21 -> 2+1 = 3
    expect(getDailyNumerologyRoot('1990-01-01')).toBe(3);
  });

  test('getDailyRitual returns fully formed daily packet', () => {
    const result = getDailyRitual('2026-10-25');
    expect(result.dateStr).toBe('2026-10-25');
    expect(result.ritual).toBeDefined();
    expect(result.ritual.title).toBeDefined();
    expect(result.formattedDate).toContain('2026');
    expect(result.numerologyRoot).toBe(9);
  });
});
