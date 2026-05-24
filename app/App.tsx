import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  ScrollView, 
  TouchableOpacity, 
  ActivityIndicator, 
  TextInput,
  SafeAreaView,
  StatusBar,
  Dimensions
} from 'react-native';
import { Canvas } from '@react-three/fiber';
import { SpatialRetina } from './components/SpatialRetina';
import { TelemetryWaterfall } from './components/TelemetryWaterfall';
import { generateIntentionalHash } from './utils/sovereign-hash';
import { useResonanceStore } from './stores/useResonanceStore';

const GATEWAY_URL = 'http://localhost:8080'; // Update this for real device testing
const API_KEY = 'lottery-secret-key';

interface Game {
  name: string;
  total_draws: number;
  last_draw_id: number;
}

export default function App() {
  const { 
    weights, 
    setWeights, 
    isResonating, 
    setIsResonating, 
    particleCount, 
    setActiveGame,
    setPersonalInput,
    setEsotericMetadata,
    clearEsotericMetadata,
    lastMuonStrike,
    triggerMuonStrike,
    resetMuonStrike
  } = useResonanceStore();
  const [games, setGames] = useState<Game[]>([]);
  const [selectedGame, setSelectedGame] = useState<string>('br/mega-sena');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'nerd' | 'chaos'>('nerd');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Intentional Seeding (Chaos Mode)
  const [fullName, setFullName] = useState('');
  const [birthDate, setBirthDate] = useState('1990-01-01');

  useEffect(() => {
    fetchGames();
  }, []);

  useEffect(() => {
    if (mode === 'chaos') {
      setPersonalInput(fullName || 'Operator X', birthDate || '1990-01-01', 'JACKPOT');
    }
  }, [fullName, birthDate, mode]);

  const fetchGames = async () => {
    try {
      const response = await fetch(`${GATEWAY_URL}/games`, {
        headers: { 'X-API-KEY': API_KEY }
      });
      const data = await response.json();
      setGames(data);
    } catch (err) {
      setError('Could not connect to Gateway');
    }
  };

  const generateTickets = async () => {
    setLoading(true);
    setError(null);
    try {
      const strategy = mode === 'nerd' ? 'weighted' : 'kabbalistic';
      
      // Story 1.4: Sovereign Local Hashing
      // We process the "vibrational" data locally and only send the fingerprint.
      const intentionalHash = mode === 'chaos' 
        ? generateIntentionalHash(fullName || 'Operator X', birthDate, Date.now().toString())
        : null;

      const body: any = {
        strategy,
        count: 1,
        temperature: mode === 'chaos' ? 1.2 : 1.0,
      };

      if (mode === 'chaos') {
        body.intentional_hash = intentionalHash;
        body.topic = 'JACKPOT';
        body.full_name = fullName || 'Operator X';
        body.birth_date = birthDate || '1990-01-01';
      }

      const response = await fetch(`${GATEWAY_URL}/games/${selectedGame}/suggest`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
          'X-Lottery-Version': '11.0' // v11.0 Signal
        },
        body: JSON.stringify(body)
      });

      if (!response.ok) throw new Error('API Error');
      
      const data = await response.json();
      setResult(data);

      // Check for Cosmic Ray Muon Strike bit-flip mutation in metadata
      if (data.metadata && (data.metadata.cosmic_ray_detected || data.metadata.muon_strike || data.metadata._last_muon_strike)) {
        const originalTicket = data.metadata.original_ticket || data.tickets[0] || [];
        const mutatedTicket = data.tickets[0] || [];
        
        // Compute mutated index and bitwise flip value by comparing numbers
        let mutatedIndex = 0;
        let originalVal = 0;
        let mutatedVal = 0;
        for (let i = 0; i < Math.min(originalTicket.length, mutatedTicket.length); i++) {
          if (originalTicket[i] !== mutatedTicket[i]) {
            mutatedIndex = i;
            originalVal = originalTicket[i];
            mutatedVal = mutatedTicket[i];
            break;
          }
        }

        triggerMuonStrike({
          originalTicket,
          mutatedTicket,
          mutatedIndex,
          bitFlipValue: originalVal ^ mutatedVal,
          timestamp: new Date().toISOString()
        });
      }

      if (mode === 'chaos' && data.metadata) {
        setEsotericMetadata({
          fullName: fullName || 'Operator X',
          birthDate: birthDate || '1990-01-01',
          topic: 'JACKPOT',
          personalProfile: data.metadata.kabbalistic_profile || null,
          triangle: data.metadata.kabbalistic_triangle || [],
          arcanos: data.metadata.arcanos || [],
          currentArcano: data.metadata.current_arcano || null,
          negativeSequences: data.metadata.negative_sequences || [],
          karmicLessons: data.metadata.karmic_lessons || [],
          karmicDebts: data.metadata.karmic_debts || [],
        });
      }
    } catch (err) {
      setError('Failed to generate tickets');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" />
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>ABSURDITY ENGINE</Text>
          <Text style={styles.subtitle}>Universal Synapse v11.0</Text>
        </View>

        {/* Story 2.4 Cosmic Ray Muon Strike Warning Alert Banner */}
        {lastMuonStrike && (
          <TouchableOpacity 
            style={styles.muonBanner} 
            onPress={resetMuonStrike}
            activeOpacity={0.8}
          >
            <Text style={styles.muonBannerText}>
              ⚡ COSMIC RAY DETECTED: SINGLE-EVENT UPSET (BIT-FLIP)
            </Text>
            <Text style={styles.muonBannerDetail}>
              Mutated ticket at index {lastMuonStrike.mutatedIndex} [XOR ^ {lastMuonStrike.bitFlipValue}]
            </Text>
            <Text style={styles.muonBannerSubtext}>
              Tap to dismiss warning • Manifold shockwave warp active
            </Text>
          </TouchableOpacity>
        )}

        <ScrollView style={styles.scroll}>
          {/* 3D Retina Visualization (v11.1 Prophet Synthesis) */}
          <View style={styles.retinaContainer}>
            <Text style={styles.sectionTitle}>👁️ Oracle's Spatial Retina (Riemannian Manifold)</Text>
            <View style={styles.canvasWrapper}>
              <Canvas camera={{ position: [0, 0, 15], fov: 75 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} />
                <SpatialRetina />
              </Canvas>
            </View>
          </View>

          {/* Swarm Equalizer Control Panel */}
          <View style={styles.swarmPanel}>
            <View style={styles.swarmHeader}>
              <Text style={styles.swarmTitle}>SWARM EQUALIZER</Text>
              <TouchableOpacity
                style={[styles.resonanceToggle, isResonating && styles.resonanceToggleActive]}
                onPress={() => setIsResonating(!isResonating)}
              >
                <Text style={styles.resonanceToggleText}>
                  {isResonating ? 'RESONANCE: ACTIVE' : 'RESONANCE: STANDBY'}
                </Text>
              </TouchableOpacity>
            </View>

            {(['frequency', 'deviation', 'cosmic', 'ml'] as const).map((key) => {
              const currentVal = weights[key];
              return (
                <View key={key} style={styles.equalizerRow}>
                  <Text style={styles.equalizerLabel}>
                    {key.toUpperCase()}: {currentVal.toFixed(2)}
                  </Text>
                  <View style={styles.barContainer}>
                    {Array.from({ length: 10 }).map((_, idx) => {
                      const segmentValue = (idx + 1) / 10;
                      const isActive = segmentValue <= currentVal;
                      return (
                        <TouchableOpacity
                          key={idx}
                          style={[
                            styles.barSegment,
                            isActive && styles.barSegmentActive,
                          ]}
                          onPress={() => setWeights({ [key]: segmentValue })}
                        />
                      );
                    })}
                  </View>
                </View>
              );
            })}

            <View style={styles.swarmFooter}>
              <Text style={styles.swarmInfoText}>
                Curvature warping resolved on GPU across {particleCount.toLocaleString()} nodes. Use 'HJKL' keys or drag to steer.
              </Text>
            </View>
          </View>

          {/* Swarm Telemetry Waterfall Console */}
          <TelemetryWaterfall gatewayUrl={GATEWAY_URL} />

          {/* Game Selector */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>1. Select Lottery</Text>
            <View style={styles.row}>
              {['br/mega-sena', 'br/lotofacil', 'us/powerball'].map(g => (
                <TouchableOpacity 
                  key={g}
                  style={[styles.pill, selectedGame === g && styles.pillActive]}
                  onPress={() => {
                    setSelectedGame(g);
                    setActiveGame(g);
                  }}
                >
                  <Text style={[styles.pillText, selectedGame === g && styles.pillTextActive]}>{g.split('/')[1]}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Mode Selector */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>2. Strategy Mode</Text>
            <View style={styles.row}>
              <TouchableOpacity 
                style={[styles.modeBtn, mode === 'nerd' && styles.modeBtnActive]}
                onPress={() => {
                  setMode('nerd');
                  clearEsotericMetadata();
                }}
              >
                <Text style={styles.modeIcon}>🤓</Text>
                <Text style={styles.modeText}>NERD MODE</Text>
                <Text style={styles.modeSubtext}>Statistical Weighted</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.modeBtn, mode === 'chaos' && styles.modeBtnActive]}
                onPress={() => setMode('chaos')}
              >
                <Text style={styles.modeIcon}>🔮</Text>
                <Text style={styles.modeText}>CHAOS MODE</Text>
                <Text style={styles.modeSubtext}>Kabbalistic Seeding</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Chaos Inputs */}
          {mode === 'chaos' && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>3. Intentional Seeding</Text>
              <TextInput 
                style={styles.input}
                placeholder="Full Name"
                placeholderTextColor="#666"
                value={fullName}
                onChangeText={setFullName}
              />
              <TextInput 
                style={styles.input}
                placeholder="Birth Date (YYYY-MM-DD)"
                placeholderTextColor="#666"
                value={birthDate}
                onChangeText={setBirthDate}
              />
            </View>
          )}

          {/* Action */}
          <TouchableOpacity 
            style={styles.generateBtn}
            onPress={generateTickets}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.generateText}>CALCULATE SYNAPSE</Text>}
          </TouchableOpacity>

          {error && <Text style={styles.error}>{error}</Text>}

          {/* Result */}
          {result && (
            <View style={styles.resultContainer}>
              <Text style={styles.resultTitle}>GENERATED TICKETS</Text>
              {result.tickets.map((t: number[], i: number) => (
                <View key={i} style={styles.ticket}>
                  {t.map(n => (
                    <View key={n} style={styles.ball}>
                      <Text style={styles.ballText}>{n}</Text>
                    </View>
                  ))}
                </View>
              ))}
              
              <Text style={styles.metaTitle}>ENVIRONMENTAL EVIDENCE</Text>
              <View style={styles.metaBox}>
                <Text style={styles.metaText}>Confidence: {(result.confidence * 100).toFixed(1)}%</Text>
                {Object.entries(result.metadata).map(([k, v]: [string, any]) => (
                  <Text key={k} style={styles.metaText}>• {k}: {JSON.stringify(v)}</Text>
                ))}
              </View>
            </View>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#0B0C10',
  },
  container: {
    flex: 1,
    padding: 20,
  },
  header: {
    marginBottom: 30,
    alignItems: 'center',
  },
  title: {
    color: '#00FF66',
    fontSize: 28,
    fontWeight: '900',
    letterSpacing: 2,
  },
  subtitle: {
    color: '#666',
    fontSize: 12,
    letterSpacing: 4,
    marginTop: 5,
  },
  scroll: {
    flex: 1,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 10,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  pill: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333',
  },
  pillActive: {
    backgroundColor: '#00FF66',
    borderColor: '#00FF66',
  },
  pillText: {
    color: '#999',
    fontSize: 12,
    fontWeight: 'bold',
  },
  pillTextActive: {
    color: '#000',
  },
  modeBtn: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'transparent',
    alignItems: 'center',
  },
  modeBtnActive: {
    borderColor: '#00FF66',
    backgroundColor: '#001a00',
  },
  modeIcon: {
    fontSize: 24,
    marginBottom: 5,
  },
  modeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  modeSubtext: {
    color: '#666',
    fontSize: 10,
    marginTop: 2,
  },
  input: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    fontSize: 14,
  },
  generateBtn: {
    backgroundColor: '#00FF66',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  generateText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 2,
  },
  error: {
    color: '#ff4b2b',
    textAlign: 'center',
    marginTop: 15,
    fontSize: 12,
  },
  resultContainer: {
    marginTop: 30,
    paddingBottom: 40,
  },
  resultTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    letterSpacing: 2,
  },
  ticket: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 15,
  },
  ball: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#00FF66',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#00FF66',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  ballText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 16,
  },
  metaTitle: {
    color: '#666',
    fontSize: 10,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
    letterSpacing: 1,
  },
  metaBox: {
    backgroundColor: '#111',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#00FF66',
  },
  metaText: {
    color: '#888',
    fontSize: 11,
    fontFamily: 'monospace',
    marginBottom: 4,
  },
  retinaContainer: {
    marginBottom: 30,
    height: 300,
    backgroundColor: '#0B0C10',
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#333',
  },
  canvasWrapper: {
    flex: 1,
  },
  swarmPanel: {
    backgroundColor: '#15171e',
    borderRadius: 16,
    padding: 18,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: '#8A2BE2',
  },
  swarmHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#2b2d35',
    paddingBottom: 10,
  },
  swarmTitle: {
    color: '#8A2BE2',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 2,
  },
  resonanceToggle: {
    backgroundColor: '#1f132e',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#8A2BE2',
  },
  resonanceToggleActive: {
    backgroundColor: '#003314',
    borderColor: '#00FF66',
  },
  resonanceToggleText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  equalizerRow: {
    marginBottom: 14,
  },
  equalizerLabel: {
    color: '#8A2BE2',
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 6,
    letterSpacing: 1.5,
    fontFamily: 'monospace',
  },
  barContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 4,
  },
  barSegment: {
    flex: 1,
    height: 14,
    backgroundColor: '#1a1d24',
    borderRadius: 3,
    borderWidth: 1,
    borderColor: '#2b2d35',
  },
  barSegmentActive: {
    backgroundColor: '#00FF66',
    borderColor: '#00FF66',
    shadowColor: '#00FF66',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
    elevation: 3,
  },
  swarmFooter: {
    marginTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#2b2d35',
    paddingTop: 10,
  },
  swarmInfoText: {
    color: '#666',
    fontSize: 10,
    fontFamily: 'monospace',
    lineHeight: 14,
  },
  muonBanner: {
    backgroundColor: '#2A0808',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FF3333',
    padding: 12,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#FF3333',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 4,
  },
  muonBannerText: {
    color: '#FF3333',
    fontSize: 11,
    fontWeight: '900',
    fontFamily: 'monospace',
    letterSpacing: 1,
    textAlign: 'center',
  },
  muonBannerDetail: {
    color: '#00FF66',
    fontSize: 10,
    fontWeight: 'bold',
    fontFamily: 'monospace',
    marginTop: 4,
    textAlign: 'center',
  },
  muonBannerSubtext: {
    color: '#666',
    fontSize: 9,
    fontFamily: 'monospace',
    marginTop: 4,
    textAlign: 'center',
  },
});
