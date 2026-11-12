// Pure helpers for Forensic Replay & Geodesic Ghosting (Story 4.2).

export const GHOST_FADE_S = 1.2;

export interface ReplayPayload {
  seq: number;
  ticket: number[];
  state_vector: number[];
  agent_weights: Record<string, number>;
  qpu_fidelity: number;
  entry_hash: string;
  captured_at: string;
}

export interface FadeAlphas {
  current: number;
  ghost: number;
}

const clamp01 = (v: number): number => (v < 0 ? 0 : v > 1 ? 1 : v);

/**
 * Alphas `elapsed` seconds after a transition started. Entering: current 1 -> 0,
 * ghost 0 -> 1. Exiting (`entering = false`): the reverse. Clamped; a non-finite
 * `elapsed` counts as 0.
 */
export function fadeAlphas(elapsed: number, entering: boolean = true): FadeAlphas {
  const p = Number.isFinite(elapsed) ? clamp01(elapsed / GHOST_FADE_S) : 0;
  return entering ? { current: 1 - p, ghost: p } : { current: p, ghost: 1 - p };
}

/** Advance a [0, 1] fade progress by `dt` seconds toward the target state. */
export function stepFadeProgress(progress: number, dt: number, entering: boolean): number {
  const step = Number.isFinite(dt) && dt > 0 ? dt / GHOST_FADE_S : 0;
  return clamp01(entering ? progress + step : progress - step);
}

/** Alphas for a progress value where 1 = fully replayed (ghost visible). */
export function alphasFromProgress(progress: number): FadeAlphas {
  const p = clamp01(Number.isFinite(progress) ? progress : 0);
  return { current: 1 - p, ghost: p };
}

const isFiniteVec = (v: unknown): v is number[] =>
  Array.isArray(v) && v.length > 0 && v.every((x) => typeof x === 'number' && Number.isFinite(x));

/**
 * Wireframe sphere (latitude/longitude lines as line-segment pairs) deformed by the
 * same radial field as the manifold shader at t = 0, with the first four state-vector
 * entries (padded with 0) as frequency/deviation/cosmic/ml amplitudes.
 * Returns null for an empty or non-finite vector.
 */
export function ghostGeometry(
  stateVector: unknown,
  latSegments: number = 16,
  lonSegments: number = 24,
  samples: number = 48
): Float32Array | null {
  if (!isFiniteVec(stateVector)) return null;
  const [f = 0, d = 0, c = 0, m = 0] = stateVector;
  const radius = (phi: number, theta: number): number => {
    const field =
      f * Math.sin(3 * phi) * Math.cos(3 * theta) +
      d * Math.cos(5 * phi) * Math.sin(2 * theta) +
      c * Math.sin(7 * phi) * Math.cos(theta) +
      m * Math.cos(2 * phi) * Math.sin(5 * theta);
    // Floor keeps an extreme vector from inverting the sphere through the origin.
    return Math.max(0.5, 7 + 1.8 * field);
  };
  const point = (phi: number, theta: number, out: number[]) => {
    const R = radius(phi, theta);
    out.push(
      R * Math.sin(phi) * Math.cos(theta),
      R * Math.sin(phi) * Math.sin(theta),
      R * Math.cos(phi)
    );
  };
  const out: number[] = [];
  // Latitude rings (constant phi)
  for (let i = 1; i < latSegments; i++) {
    const phi = (i / latSegments) * Math.PI;
    for (let j = 0; j < samples; j++) {
      point(phi, (j / samples) * 2 * Math.PI, out);
      point(phi, ((j + 1) / samples) * 2 * Math.PI, out);
    }
  }
  // Meridians (constant theta)
  for (let i = 0; i < lonSegments; i++) {
    const theta = (i / lonSegments) * 2 * Math.PI;
    for (let j = 0; j < samples; j++) {
      point((j / samples) * Math.PI, theta, out);
      point(((j + 1) / samples) * Math.PI, theta, out);
    }
  }
  const arr = Float32Array.from(out);
  return arr.every(Number.isFinite) ? arr : null;
}

/** Validate an untrusted replay payload (e.g. from the engine); null if unusable. */
export function parseReplayPayload(raw: unknown): ReplayPayload | null {
  if (!raw || typeof raw !== 'object') return null;
  const r = raw as Record<string, unknown>;
  if (typeof r.seq !== 'number' || !Number.isInteger(r.seq) || r.seq < 1) return null;
  if (!isFiniteVec(r.state_vector)) return null;
  if (!Array.isArray(r.ticket) || !r.ticket.every((n) => Number.isInteger(n))) return null;
  if (typeof r.qpu_fidelity !== 'number' || !Number.isFinite(r.qpu_fidelity)) return null;
  if (typeof r.entry_hash !== 'string' || typeof r.captured_at !== 'string') return null;
  if (!ghostGeometry(r.state_vector)) return null; // must be renderable
  const w = r.agent_weights;
  if (!w || typeof w !== 'object' || Array.isArray(w)) return null;
  const weights: Record<string, number> = {};
  for (const [k, v] of Object.entries(w)) {
    if (typeof v !== 'number' || !Number.isFinite(v)) return null;
    weights[k] = v;
  }
  return {
    seq: r.seq,
    ticket: [...(r.ticket as number[])],
    state_vector: [...r.state_vector],
    agent_weights: weights,
    qpu_fidelity: r.qpu_fidelity,
    entry_hash: r.entry_hash,
    captured_at: r.captured_at,
  };
}
