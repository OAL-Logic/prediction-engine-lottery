import { create } from 'zustand';
import {
  rebalanceWeights,
  scoreTickets,
  type ConsensusTicket,
  type WeightKey,
} from '../utils/equalizer';
import { parseReplayPayload, type ReplayPayload } from '../utils/ghost';

export interface SwarmWeights {
  frequency: number;
  deviation: number;
  cosmic: number;
  ml: number;
}

export interface PersonalProfile {
  motivation: number;
  impression: number;
  expression: number;
  destiny: number;
  mission: number;
}

export interface EsotericMetadata {
  fullName: string;
  birthDate: string;
  topic: string;
  personalProfile: PersonalProfile | null;
  triangle: number[][];
  arcanos: number[];
  currentArcano: number | null;
  negativeSequences: number[];
  karmicLessons: number[];
  karmicDebts: number[];
}

export interface TelemetryMessage {
  source: string;
  level: 'INFO' | 'RESONANCE' | 'DECOHERENCE' | 'SUCCESS';
  message: string;
  timestamp: string;
}

export interface MuonStrikeDetails {
  originalTicket: number[];
  mutatedTicket: number[];
  mutatedIndex: number;
  bitFlipValue: number;
  timestamp: string;
}

export interface RippleState {
  id: number;
  key: WeightKey | null;
}

interface ResonanceState extends EsotericMetadata {
  weights: SwarmWeights;
  manifoldEpoch: number;
  activeGame: string;
  isResonating: boolean;
  particleCount: number;
  telemetryLogs: TelemetryMessage[];
  isTelemetryConnected: boolean;
  isTelemetryPaused: boolean;
  lastMuonStrike: MuonStrikeDetails | null;
  muonStrikeCount: number;
  consensusTickets: ConsensusTicket[];
  ripple: RippleState;
  lastRescoreMs: number;
  /** Loaded forensic replay payload (Story 4.2), or null. */
  replay: ReplayPayload | null;
  /** True while the ghost is the target view (current manifold fading out). */
  replayActive: boolean;
  /** Validate and load a payload without starting; invalid input is ignored. */
  loadReplay: (raw: unknown) => void;
  /** Start replay; with a payload it is validated and loaded first, without it the loaded one is reused. */
  startReplay: (raw?: unknown) => void;
  stopReplay: () => void;
  /** User's vault balance used for Confidence Leverage sizing (Story 4.3). */
  vaultBalance: number;
  /** Ignores non-finite or negative values. */
  setVaultBalance: (balance: number) => void;
  setConsensusTickets: (tickets: ConsensusTicket[]) => void;
  setEqualizerWeight: (key: WeightKey, value: number) => void;
  setWeights: (weights: Partial<SwarmWeights>) => void;
  setManifoldState: (weights: SwarmWeights, epoch: number) => void;
  setActiveGame: (game: string) => void;
  setIsResonating: (isResonating: boolean) => void;
  setParticleCount: (count: number) => void;
  setPersonalInput: (fullName: string, birthDate: string, topic: string) => void;
  setEsotericMetadata: (data: Partial<EsotericMetadata>) => void;
  clearEsotericMetadata: () => void;
  addTelemetryLog: (log: TelemetryMessage) => void;
  clearTelemetryLogs: () => void;
  setTelemetryConnected: (connected: boolean) => void;
  setTelemetryPaused: (paused: boolean) => void;
  triggerMuonStrike: (strike: MuonStrikeDetails) => void;
  resetMuonStrike: () => void;
}

export const useResonanceStore = create<ResonanceState>((set) => ({
  consensusTickets: [],
  ripple: { id: 0, key: null },
  lastRescoreMs: 0,
  replay: null,
  replayActive: false,
  loadReplay: (raw) =>
    set(() => {
      const replay = parseReplayPayload(raw);
      return replay ? { replay } : {};
    }),
  startReplay: (raw) =>
    set((state) => {
      const replay = raw === undefined ? state.replay : parseReplayPayload(raw);
      if (!replay) return {};
      return { replay, replayActive: true };
    }),
  stopReplay: () => set({ replayActive: false }),
  vaultBalance: 1000,
  setVaultBalance: (balance) =>
    set(() =>
      typeof balance === 'number' && Number.isFinite(balance) && balance >= 0
        ? { vaultBalance: balance }
        : {},
    ),
  weights: {
    frequency: 0.25,
    deviation: 0.25,
    cosmic: 0.25,
    ml: 0.25,
  },
  manifoldEpoch: 0,
  activeGame: 'br/mega-sena',
  isResonating: true,
  particleCount: 100000, // 100k+ nodes standard
  fullName: 'GEMINI ENGINE',
  birthDate: '1990-01-01',
  topic: '',
  personalProfile: null,
  triangle: [],
  arcanos: [],
  currentArcano: null,
  negativeSequences: [],
  karmicLessons: [],
  karmicDebts: [],
  telemetryLogs: [],
  isTelemetryConnected: false,
  isTelemetryPaused: false,
  lastMuonStrike: null,
  muonStrikeCount: 0,
  setConsensusTickets: (tickets) =>
    set((state) => {
      const start = performance.now();
      const consensusTickets = scoreTickets(tickets, state.weights);
      return { consensusTickets, lastRescoreMs: performance.now() - start };
    }),
  setEqualizerWeight: (key, value) =>
    set((state) => {
      if (typeof value !== 'number' || Number.isNaN(value)) return {};
      const weights = rebalanceWeights(state.weights, key, value);
      if (weights === state.weights) return {};
      const start = performance.now();
      const consensusTickets = scoreTickets(state.consensusTickets, weights);
      const lastRescoreMs = performance.now() - start;
      return {
        weights,
        consensusTickets,
        lastRescoreMs,
        ripple: { id: state.ripple.id + 1, key },
      };
    }),
  setWeights: (newWeights) =>
    set((state) => {
      const weights = { ...state.weights, ...newWeights };
      const start = performance.now();
      const consensusTickets = scoreTickets(state.consensusTickets, weights);
      return { weights, consensusTickets, lastRescoreMs: performance.now() - start };
    }),
  setManifoldState: (weights, epoch) =>
    set((state) => {
      const merged = { ...state.weights, ...weights };
      const start = performance.now();
      const consensusTickets = scoreTickets(state.consensusTickets, merged);
      return {
        weights: merged,
        manifoldEpoch: epoch,
        consensusTickets,
        lastRescoreMs: performance.now() - start,
      };
    }),
  setActiveGame: (game) => set({ activeGame: game }),
  setIsResonating: (isResonating) => set({ isResonating }),
  setParticleCount: (particleCount) => set({ particleCount }),
  setPersonalInput: (fullName, birthDate, topic) =>
    set({ fullName, birthDate, topic }),
  setEsotericMetadata: (data) =>
    set((state) => ({ ...state, ...data })),
  clearEsotericMetadata: () =>
    set({
      fullName: 'GEMINI ENGINE',
      birthDate: '1990-01-01',
      topic: '',
      personalProfile: null,
      triangle: [],
      arcanos: [],
      currentArcano: null,
      negativeSequences: [],
      karmicLessons: [],
      karmicDebts: [],
    }),
  addTelemetryLog: (log) =>
    set((state) => {
      if (state.isTelemetryPaused) return {};
      return {
        telemetryLogs: [...state.telemetryLogs, log].slice(-500),
      };
    }),
  clearTelemetryLogs: () => set({ telemetryLogs: [] }),
  setTelemetryConnected: (isTelemetryConnected) => set({ isTelemetryConnected }),
  setTelemetryPaused: (isTelemetryPaused) => set({ isTelemetryPaused }),
  triggerMuonStrike: (strike) =>
    set((state) => ({
      lastMuonStrike: strike,
      muonStrikeCount: state.muonStrikeCount + 1,
    })),
  resetMuonStrike: () => set({ lastMuonStrike: null }),
}));
