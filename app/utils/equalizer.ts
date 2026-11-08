// Pure helpers for the Swarm Equalizer (Story 3.3).

export type WeightKey = 'frequency' | 'deviation' | 'cosmic' | 'ml';

export interface EqualizerWeights {
  frequency: number;
  deviation: number;
  cosmic: number;
  ml: number;
}

export interface ConsensusTicket {
  id: string;
  numbers?: number[];
  /** Per-key components in [0, 1]. Missing / non-finite entries count as 0. */
  components: Partial<Record<WeightKey, number>>;
  score: number;
}

export const WEIGHT_KEYS: readonly WeightKey[] = ['frequency', 'deviation', 'cosmic', 'ml'];

export const RIPPLE_DURATION_S = 1.6;
export const RESCORE_BUDGET_MS = 100;

const clamp01 = (v: number): number => (v < 0 ? 0 : v > 1 ? 1 : v);

/**
 * Set `key` to the clamped `value` and rescale the other weights proportionally so
 * the total is 1. If the others are all 0 they share the remainder equally.
 * Returns the input unchanged (same reference) when `value` is not a finite number
 * or `key` is not a weight key.
 */
export function rebalanceWeights(
  weights: EqualizerWeights,
  key: WeightKey,
  value: number
): EqualizerWeights {
  if (typeof value !== 'number' || Number.isNaN(value) || !WEIGHT_KEYS.includes(key)) {
    return weights;
  }
  const v = clamp01(value);
  const others = WEIGHT_KEYS.filter((k) => k !== key);
  const othersSum = others.reduce((s, k) => s + (Number.isFinite(weights[k]) ? Math.max(0, weights[k]) : 0), 0);
  const remainder = 1 - v;

  const next = { ...weights } as EqualizerWeights;
  next[key] = v;
  for (const k of others) {
    if (othersSum > 0) {
      const w = Number.isFinite(weights[k]) ? Math.max(0, weights[k]) : 0;
      next[k] = (w * remainder) / othersSum;
    } else {
      next[k] = remainder / others.length;
    }
  }
  return next;
}

/**
 * Map a touch y coordinate within a vertical track to a value in [0, 1].
 * Top of the track = 1, bottom = 0, outside is clamped.
 */
export function valueFromTouch(y: number, trackHeight: number): number {
  if (!Number.isFinite(y) || !Number.isFinite(trackHeight) || trackHeight <= 0) return 0;
  return clamp01(1 - y / trackHeight);
}

const component = (t: ConsensusTicket, k: WeightKey): number => {
  const c = t?.components?.[k];
  return typeof c === 'number' && Number.isFinite(c) ? clamp01(c) : 0;
};

/**
 * Score tickets as Σ weight_k · component_k and return a new array sorted by
 * score descending. Input tickets are not mutated.
 */
export function scoreTickets(
  tickets: readonly ConsensusTicket[],
  weights: EqualizerWeights
): ConsensusTicket[] {
  const wf = Number.isFinite(weights.frequency) ? weights.frequency : 0;
  const wd = Number.isFinite(weights.deviation) ? weights.deviation : 0;
  const wc = Number.isFinite(weights.cosmic) ? weights.cosmic : 0;
  const wm = Number.isFinite(weights.ml) ? weights.ml : 0;
  const out = new Array<ConsensusTicket>(tickets.length);
  for (let i = 0; i < tickets.length; i++) {
    const t = tickets[i];
    out[i] = {
      ...t,
      score:
        wf * component(t, 'frequency') +
        wd * component(t, 'deviation') +
        wc * component(t, 'cosmic') +
        wm * component(t, 'ml'),
    };
  }
  out.sort((a, b) => b.score - a.score);
  return out;
}

// Fixed origin on the manifold (radius ~7) per slider so the wave is attributable.
const RIPPLE_ORIGINS: Record<WeightKey, [number, number, number]> = {
  frequency: [7, 0, 0],
  deviation: [0, 7, 0],
  cosmic: [0, 0, 7],
  ml: [-4.04, -4.04, -4.04],
};

export function rippleOrigin(key: WeightKey): [number, number, number] {
  const o = RIPPLE_ORIGINS[key] ?? RIPPLE_ORIGINS.frequency;
  return [o[0], o[1], o[2]];
}
