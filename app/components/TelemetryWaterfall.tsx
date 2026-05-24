import React, { useEffect, useRef, useState } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  FlatList, 
  TouchableOpacity, 
  ActivityIndicator,
  Animated
} from 'react-native';
import { useResonanceStore, TelemetryMessage } from '../stores/useResonanceStore';

interface TelemetryWaterfallProps {
  gatewayUrl?: string;
}

export function TelemetryWaterfall({ gatewayUrl = 'http://localhost:8080' }: TelemetryWaterfallProps) {
  const {
    telemetryLogs,
    isTelemetryConnected,
    isTelemetryPaused,
    addTelemetryLog,
    clearTelemetryLogs,
    setTelemetryConnected,
    setTelemetryPaused,
    triggerMuonStrike
  } = useResonanceStore();

  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);
  const [mockActive, setMockActive] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const pulseAnim = useRef(new Animated.Value(0.4)).current;

  // Pulse animation for status indicator
  useEffect(() => {
    let anim: Animated.CompositeAnimation | null = null;
    if (isTelemetryConnected) {
      pulseAnim.setValue(1);
    } else {
      anim = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0.3,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      );
      anim.start();
    }

    return () => {
      if (anim) anim.stop();
    };
  }, [isTelemetryConnected]);

  // WebSocket Connection management with exponential backoff
  useEffect(() => {
    if (isTelemetryPaused || mockActive) {
      return;
    }

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let reconnectDelay = 1000;
    let isMounted = true;

    // Resolve WebSocket URL from REST API Gateway URL
    const resolveWsUrl = (url: string) => {
      const cleanUrl = url.replace(/^http/, 'ws');
      return `${cleanUrl}/telemetry`;
    };

    const connect = () => {
      if (!isMounted) return;
      setIsConnecting(true);
      
      const wsUrl = resolveWsUrl(gatewayUrl);
      console.log(`Connecting to Telemetry Hub at: ${wsUrl}`);
      
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          if (!isMounted) return;
          console.log('Telemetry WebSocket connected.');
          setTelemetryConnected(true);
          setIsConnecting(false);
          reconnectDelay = 1000; // Reset backoff delay
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            if (data.message) {
              addTelemetryLog(data as TelemetryMessage);
            }
          } catch (e) {
            console.error('Failed to parse incoming WS telemetry:', e);
          }
        };

        ws.onclose = (e) => {
          if (!isMounted) return;
          console.log(`Telemetry WebSocket closed: ${e.reason || 'No reason given'}`);
          setTelemetryConnected(false);
          setIsConnecting(false);

          // Exponential backoff reconnection
          reconnectTimeout = setTimeout(() => {
            reconnectDelay = Math.min(reconnectDelay * 2, 10000);
            connect();
          }, reconnectDelay);
        };

        ws.onerror = (e) => {
          console.error('Telemetry WebSocket encountered error:', e);
          ws?.close();
        };
      } catch (err) {
        console.error('WebSocket initialization failure:', err);
        setIsConnecting(false);
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (ws) {
        ws.onclose = null; // Clean handler to avoid trigger on unmount
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      setTelemetryConnected(false);
    };
  }, [isTelemetryPaused, gatewayUrl, mockActive]);

  // Handle Mock Log Injection for validation
  useEffect(() => {
    if (!mockActive || isTelemetryPaused) return;

    const mockSources = ['engine', 'gateway', 'sidecar', 'swarm'];
    const mockLevels = ['INFO', 'RESONANCE', 'SUCCESS', 'DECOHERENCE'] as const;
    const mockMessages = [
      'Initializing post-quantum cryptography (PQC) handshake...',
      'Epstein-Nesbet state-space sampling expansion factor: 1.62',
      'True quantum entropy distilled successfully from hardware QPU (Sim)',
      'Connection latency spike: classical VAE simulator fallback active',
      'Resonance intersection sigil coordinates resolved at [42.19, -73.05]',
      'Pulsing solar astro-cartography alignment trigger detected',
      'Swarm Equalizer weighting applied: frequency (0.40) ml (0.60)',
      'MARL swarm trajectory deviation threshold adjusted to 0.05',
    ];

    const interval = setInterval(() => {
      const randomSource = mockSources[Math.floor(Math.random() * mockSources.length)];
      const randomLevel = mockLevels[Math.floor(Math.random() * mockLevels.length)];
      const randomMessage = mockMessages[Math.floor(Math.random() * mockMessages.length)];
      
      addTelemetryLog({
        source: randomSource,
        level: randomLevel,
        message: randomMessage,
        timestamp: new Date().toISOString(),
      });
    }, 400);

    return () => clearInterval(interval);
  }, [mockActive, isTelemetryPaused]);

  // Simulate a Cosmic Ray Single-Event Upset (XOR bit-flip)
  const simulateCosmicStrike = () => {
    const originalTicket = [4, 8, 15, 16, 23, 42];
    const mutatedIndex = Math.floor(Math.random() * 6);
    const bitFlip = 1 << (Math.floor(Math.random() * 5) + 1); // bitwise shifts 2, 4, 8, 16, 32
    const mutatedTicket = [...originalTicket];
    mutatedTicket[mutatedIndex] = originalTicket[mutatedIndex] ^ bitFlip;
    mutatedTicket.sort((a, b) => a - b);

    triggerMuonStrike({
      originalTicket,
      mutatedTicket,
      mutatedIndex,
      bitFlipValue: bitFlip,
      timestamp: new Date().toISOString()
    });

    addTelemetryLog({
      source: 'sidecar',
      level: 'DECOHERENCE',
      message: `⚡ COSMIC MUON STRIKE: Single-Event Upset caused bit-flip at index ${mutatedIndex} [XOR ^ ${bitFlip}]`,
      timestamp: new Date().toISOString()
    });
  };

  // Auto-scroll when telemetryLogs update
  useEffect(() => {
    if (shouldAutoScroll && telemetryLogs.length > 0) {
      // Small timeout to allow layout cycle to complete
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 50);
    }
  }, [telemetryLogs, shouldAutoScroll]);

  const handleScroll = (event: any) => {
    const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;
    // Check if user is within 60px of the bottom
    const isNearBottom = contentSize.height - layoutMeasurement.height - contentOffset.y < 60;
    setShouldAutoScroll(isNearBottom);
  };

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'SUCCESS':
        return '#00FF66'; // Matrix Green
      case 'RESONANCE':
        return '#8A2BE2'; // Astro Violet
      case 'DECOHERENCE':
        return '#FF3333'; // Red
      case 'INFO':
      default:
        return '#999999'; // Silver/Gray
    }
  };

  const formatTimestamp = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toTimeString().split(' ')[0]; // Returns HH:MM:SS
    } catch {
      return '--:--:--';
    }
  };

  const renderItem = ({ item }: { item: TelemetryMessage }) => {
    const color = getLevelColor(item.level);
    return (
      <View style={styles.logRow}>
        <Text style={styles.logTime}>[{formatTimestamp(item.timestamp)}]</Text>
        <Text style={[styles.logLevel, { color }]}>{item.level.padEnd(11)}</Text>
        <Text style={styles.logSource}>({item.source})</Text>
        <Text style={[styles.logMsg, { color: item.level === 'INFO' ? '#C0C0C0' : color }]}>
          {item.message}
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.consoleContainer}>
      {/* Console Header */}
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Animated.View 
            style={[
              styles.statusDot, 
              { 
                backgroundColor: isTelemetryConnected ? '#00FF66' : isConnecting ? '#8A2BE2' : '#FF3333',
                opacity: pulseAnim
              }
            ]} 
          />
          <Text style={styles.title}>SWARM TELEMETRY CONSOLE</Text>
        </View>
        
        {/* Controls */}
        <View style={styles.controlsRow}>
          <TouchableOpacity 
            style={[styles.btn, styles.btnStrike]} 
            onPress={simulateCosmicStrike}
          >
            <Text style={styles.btnTextStrike}>⚡ COSMIC</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.btn, mockActive && styles.btnActive]} 
            onPress={() => setMockActive(!mockActive)}
          >
            <Text style={[styles.btnText, mockActive && styles.btnTextActive]}>
              {mockActive ? 'MOCK: ON' : 'MOCK'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.btn, isTelemetryPaused && styles.btnPaused]} 
            onPress={() => setTelemetryPaused(!isTelemetryPaused)}
          >
            <Text style={styles.btnText}>{isTelemetryPaused ? 'RESUME' : 'PAUSE'}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.btn} onPress={clearTelemetryLogs}>
            <Text style={styles.btnText}>CLEAR</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Stream Viewport */}
      <View style={styles.viewport}>
        {telemetryLogs.length === 0 ? (
          <View style={styles.emptyContainer}>
            {isConnecting ? (
              <ActivityIndicator color="#8A2BE2" size="small" />
            ) : (
              <Text style={styles.emptyText}>
                {isTelemetryPaused 
                  ? 'CONSOLE INGESTION PAUSED'
                  : 'AWAITING TELEMETRY PULSE FROM SWARM...'}
              </Text>
            )}
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={telemetryLogs}
            renderItem={renderItem}
            keyExtractor={(item, index) => `${item.timestamp}-${index}`}
            onScroll={handleScroll}
            scrollEventThrottle={16}
            initialNumToRender={30}
            maxToRenderPerBatch={30}
            removeClippedSubviews={true}
            contentContainerStyle={styles.listContainer}
          />
        )}
      </View>
      
      {/* Console Status Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Buffer size: {telemetryLogs.length}/500 logs • Auto-scroll: {shouldAutoScroll ? 'ACTIVE' : 'LOCKED'}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  consoleContainer: {
    backgroundColor: '#050505',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#333',
    overflow: 'hidden',
    marginBottom: 25,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0D0E12',
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
    shadowColor: '#00FF66',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
  },
  title: {
    color: '#8A2BE2',
    fontSize: 11,
    fontFamily: 'monospace',
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  controlsRow: {
    flexDirection: 'row',
    gap: 6,
  },
  btn: {
    backgroundColor: '#1C1D24',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#333',
  },
  btnActive: {
    backgroundColor: '#1f132e',
    borderColor: '#8A2BE2',
  },
  btnStrike: {
    backgroundColor: '#3b0d0d',
    borderColor: '#FF3333',
  },
  btnTextStrike: {
    color: '#FF3333',
    fontSize: 9,
    fontFamily: 'monospace',
    fontWeight: 'bold',
  },
  btnPaused: {
    backgroundColor: '#2e1313',
    borderColor: '#FF3333',
  },
  btnText: {
    color: '#999',
    fontSize: 9,
    fontFamily: 'monospace',
    fontWeight: 'bold',
  },
  btnTextActive: {
    color: '#8A2BE2',
  },
  viewport: {
    height: 200,
    padding: 10,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#666',
    fontSize: 10,
    fontFamily: 'monospace',
    letterSpacing: 1,
  },
  listContainer: {
    paddingBottom: 5,
  },
  logRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 4,
    alignItems: 'flex-start',
  },
  logTime: {
    color: '#555',
    fontSize: 10,
    fontFamily: 'monospace',
    marginRight: 6,
  },
  logLevel: {
    fontSize: 10,
    fontFamily: 'monospace',
    fontWeight: 'bold',
    marginRight: 6,
  },
  logSource: {
    color: '#777',
    fontSize: 10,
    fontFamily: 'monospace',
    marginRight: 8,
  },
  logMsg: {
    fontSize: 10,
    fontFamily: 'monospace',
    flex: 1,
  },
  footer: {
    backgroundColor: '#0D0E12',
    paddingVertical: 6,
    paddingHorizontal: 15,
    borderTopWidth: 1,
    borderTopColor: '#1A1B22',
  },
  footerText: {
    color: '#444',
    fontSize: 9,
    fontFamily: 'monospace',
  },
});
