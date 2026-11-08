import type { SwarmWeights } from '../stores/useResonanceStore';

export const MANIFOLD_PREFIX = 'MANIFOLD_STATE ';

export interface ManifoldState {
  epoch: number;
  weights: SwarmWeights;
  distanceToConsensus: number;
}

const KEYS: (keyof SwarmWeights)[] = ['frequency', 'deviation', 'cosmic', 'ml'];

/** Parse a `MANIFOLD_STATE {json}` telemetry message; null if not/invalid. */
export function parseManifoldTelemetry(message: unknown): ManifoldState | null {
  if (typeof message !== 'string' || !message.startsWith(MANIFOLD_PREFIX)) return null;
  let payload: any;
  try {
    payload = JSON.parse(message.slice(MANIFOLD_PREFIX.length));
  } catch {
    return null;
  }
  if (!payload || typeof payload !== 'object' || !payload.weights) return null;
  const w: Partial<SwarmWeights> = {};
  let sum = 0;
  for (const k of KEYS) {
    const v = payload.weights[k];
    if (typeof v !== 'number' || !Number.isFinite(v) || v < 0) return null;
    w[k] = v;
    sum += v;
  }
  if (Math.abs(sum - 1) > 1e-6) return null;
  if (!Number.isInteger(payload.epoch) || payload.epoch < 0) return null;
  const epoch: number = payload.epoch;
  const d = payload.distance_to_consensus;
  return {
    epoch,
    weights: w as SwarmWeights,
    distanceToConsensus: typeof d === 'number' && Number.isFinite(d) ? d : 0,
  };
}

/**
 * Apply a telemetry message to the store setter when it is a manifold pulse.
 * Returns true if the message was a valid pulse and was applied.
 */
export function applyManifoldMessage(
  message: unknown,
  setManifoldState: (weights: SwarmWeights, epoch: number) => void,
): boolean {
  const manifold = parseManifoldTelemetry(message);
  if (!manifold) return false;
  setManifoldState(manifold.weights, manifold.epoch);
  return true;
}
