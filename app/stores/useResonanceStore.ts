import { create } from 'zustand';

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

interface ResonanceState extends EsotericMetadata {
  weights: SwarmWeights;
  activeGame: string;
  isResonating: boolean;
  particleCount: number;
  telemetryLogs: TelemetryMessage[];
  isTelemetryConnected: boolean;
  isTelemetryPaused: boolean;
  lastMuonStrike: MuonStrikeDetails | null;
  muonStrikeCount: number;
  setWeights: (weights: Partial<SwarmWeights>) => void;
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
  weights: {
    frequency: 0.25,
    deviation: 0.25,
    cosmic: 0.25,
    ml: 0.25,
  },
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
  setWeights: (newWeights) =>
    set((state) => ({
      weights: { ...state.weights, ...newWeights },
    })),
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
