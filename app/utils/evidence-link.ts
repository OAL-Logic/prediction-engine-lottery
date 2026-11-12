// Deep-link parsing for Obsidian-exported evidence (Story 4.4).
import type { ReplayPayload } from './ghost';

export interface EvidenceLink {
  seq: number;
  hash: string;
  coords: number[];
}

const NUM = /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/;
const PREFIX = 'lottery://evidence/';

/** Parse `lottery://evidence/<seq>?hash=<h>&coords=<c1,c2,...>`; null if malformed. */
export function parseEvidenceLink(url: unknown): EvidenceLink | null {
  if (typeof url !== 'string' || !url.startsWith(PREFIX)) return null;
  const rest = url.slice(PREFIX.length);
  const q = rest.indexOf('?');
  if (q < 0) return null;
  const seqStr = rest.slice(0, q);
  if (!/^\d+$/.test(seqStr)) return null;
  const seq = Number(seqStr);
  if (!Number.isSafeInteger(seq) || seq < 1) return null;

  // Manual split: '+' in exponents (1e+16) must not be decoded as a space.
  const params = new Map<string, string>();
  for (const part of rest.slice(q + 1).split('&')) {
    const eq = part.indexOf('=');
    if (eq < 0) return null;
    const k = part.slice(0, eq);
    if (params.has(k)) return null;
    params.set(k, part.slice(eq + 1));
  }
  const hash = params.get('hash');
  const rawCoords = params.get('coords');
  if (!hash || !/^[0-9a-fA-F]+$/.test(hash) || !rawCoords) return null;

  const coords: number[] = [];
  for (const tok of rawCoords.split(',')) {
    if (!NUM.test(tok)) return null;
    const n = Number(tok);
    if (!Number.isFinite(n)) return null;
    coords.push(n);
  }
  return { seq, hash, coords };
}

/** True only when seq, hash and every coordinate equal the replay payload. */
export function matchesReplay(link: EvidenceLink | null, replay: ReplayPayload | null): boolean {
  if (!link || !replay) return false;
  const sv = replay.state_vector;
  return (
    link.seq === replay.seq &&
    link.hash === replay.entry_hash &&
    Array.isArray(sv) &&
    link.coords.length === sv.length &&
    link.coords.every((c, i) => c === sv[i])
  );
}
