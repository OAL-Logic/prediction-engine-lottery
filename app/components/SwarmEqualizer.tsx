import React, { useMemo, useRef } from 'react';
import { PanResponder, StyleSheet, Text, View } from 'react-native';
import { useResonanceStore } from '../stores/useResonanceStore';
import { WEIGHT_KEYS, valueFromTouch, type WeightKey } from '../utils/equalizer';

const TRACK_HEIGHT = 140;

const Slider = ({ weightKey }: { weightKey: WeightKey }) => {
  const value = useResonanceStore((s) => s.weights[weightKey]);
  const setEqualizerWeight = useResonanceStore((s) => s.setEqualizerWeight);

  const panResponder = useMemo(() => {
    const apply = (y: number) => setEqualizerWeight(weightKey, valueFromTouch(y, TRACK_HEIGHT));
    return PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderTerminationRequest: () => false,
      onPanResponderGrant: (e) => apply(e.nativeEvent.locationY),
      onPanResponderMove: (e) => apply(e.nativeEvent.locationY),
    });
  }, [weightKey, setEqualizerWeight]);

  const fillHeight = Math.max(0, Math.min(1, value)) * TRACK_HEIGHT;

  return (
    <View style={styles.column}>
      <Text style={styles.valueLabel}>{value.toFixed(2)}</Text>
      <View style={styles.track} {...panResponder.panHandlers}>
        <View pointerEvents="none" style={[styles.fill, { height: fillHeight }]} />
        <View pointerEvents="none" style={[styles.thumb, { bottom: Math.max(0, fillHeight - 3) }]} />
      </View>
      <Text style={styles.keyLabel}>{weightKey.slice(0, 4).toUpperCase()}</Text>
    </View>
  );
};

export const SwarmEqualizer = () => {
  const lastRescoreMs = useResonanceStore((s) => s.lastRescoreMs);
  const ticketCount = useResonanceStore((s) => s.consensusTickets.length);
  return (
    <View>
      <View style={styles.row}>
        {WEIGHT_KEYS.map((k) => (
          <Slider key={k} weightKey={k} />
        ))}
      </View>
      <Text style={styles.meta}>
        {ticketCount.toLocaleString()} tickets rescored in {lastRescoreMs.toFixed(1)}ms
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 10 },
  column: { alignItems: 'center', width: 60 },
  valueLabel: {
    color: '#00FF66',
    fontSize: 11,
    fontFamily: 'monospace',
    fontWeight: 'bold',
    marginBottom: 6,
  },
  track: {
    width: 36,
    height: TRACK_HEIGHT,
    backgroundColor: '#1a1d24',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2b2d35',
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  fill: { width: '100%', backgroundColor: '#00FF66', opacity: 0.85 },
  thumb: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 6,
    backgroundColor: '#8A2BE2',
    borderRadius: 3,
  },
  keyLabel: {
    color: '#8A2BE2',
    fontSize: 10,
    fontWeight: 'bold',
    letterSpacing: 1.5,
    fontFamily: 'monospace',
    marginTop: 6,
  },
  meta: { color: '#666', fontSize: 10, fontFamily: 'monospace', textAlign: 'center' },
});
