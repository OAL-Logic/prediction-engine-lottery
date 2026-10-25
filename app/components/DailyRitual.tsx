import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Animated,
  Easing,
} from 'react-native';
import {
  RitualItem,
  RITUAL_CATALOG,
  getDailyIndex,
  getDailyNumerologyRoot,
  getDailyRitual,
} from '../utils/daily-ritual';

export {
  RitualItem,
  RITUAL_CATALOG,
  getDailyIndex,
  getDailyNumerologyRoot,
  getDailyRitual,
};

export interface DailyRitualProps {
  initialDate?: Date | string;
  onRitualComplete?: (ritual: RitualItem) => void;
}

export function DailyRitual({ initialDate, onRitualComplete }: DailyRitualProps) {
  const [activeDate] = useState<Date | string>(initialDate || new Date());
  const [shuffleOffset, setShuffleOffset] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [secondsRemaining, setSecondsRemaining] = useState(30);
  const [isCompleted, setIsCompleted] = useState(false);

  const pulseAnim = useRef(new Animated.Value(1)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const dailyData = getDailyRitual(activeDate);
  const currentIndex = (getDailyIndex(dailyData.dateStr, RITUAL_CATALOG.length) + shuffleOffset) % RITUAL_CATALOG.length;
  const currentRitual = RITUAL_CATALOG[currentIndex];

  // Pulse animation when running
  useEffect(() => {
    let loop: Animated.CompositeAnimation | null = null;
    if (isRunning) {
      loop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.08,
            duration: 1000,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0.96,
            duration: 1000,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      );
      loop.start();
    } else {
      pulseAnim.setValue(1);
    }
    return () => {
      if (loop) loop.stop();
    };
  }, [isRunning, pulseAnim]);

  // Countdown timer logic
  useEffect(() => {
    if (isRunning && secondsRemaining > 0) {
      timerRef.current = setTimeout(() => {
        setSecondsRemaining(prev => prev - 1);
        Animated.timing(progressAnim, {
          toValue: (30 - (secondsRemaining - 1)) / 30,
          duration: 950,
          useNativeDriver: false,
        }).start();
      }, 1000);
    } else if (isRunning && secondsRemaining === 0) {
      setIsRunning(false);
      setIsCompleted(true);
      if (onRitualComplete) {
        onRitualComplete(currentRitual);
      }
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isRunning, secondsRemaining, currentRitual, onRitualComplete, progressAnim]);

  const handleStart = () => {
    setSecondsRemaining(30);
    setIsCompleted(false);
    progressAnim.setValue(0);
    setIsRunning(true);
  };

  const handlePause = () => {
    setIsRunning(false);
  };

  const handleResume = () => {
    setIsRunning(true);
  };

  const handleReset = () => {
    setIsRunning(false);
    setSecondsRemaining(30);
    setIsCompleted(false);
    progressAnim.setValue(0);
  };

  const handleShuffle = () => {
    handleReset();
    setShuffleOffset(prev => prev + 1);
  };

  // Determine current active step (0, 1, or 2)
  const currentStepIndex = Math.min(2, Math.floor((30 - secondsRemaining) / 10));

  return (
    <View style={styles.container}>
      {/* Header bar */}
      <View style={styles.headerRow}>
        <View style={styles.badgeRow}>
          <View style={[styles.typeBadge, { borderColor: currentRitual.color }]}>
            <Text style={[styles.typeBadgeText, { color: currentRitual.color }]}>
              {currentRitual.type.toUpperCase()}
            </Text>
          </View>
          <View style={styles.dateBadge}>
            <Text style={styles.dateBadgeText}>
              📅 {dailyData.formattedDate}
            </Text>
          </View>
          <View style={styles.numerologyBadge}>
            <Text style={styles.numerologyBadgeText}>
              ROOT #{dailyData.numerologyRoot}
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={styles.shuffleBtn}
          onPress={handleShuffle}
          activeOpacity={0.7}
        >
          <Text style={styles.shuffleBtnText}>🎲 Reroll</Text>
        </TouchableOpacity>
      </View>

      {/* Title & Frequency */}
      <View style={styles.titleSection}>
        <Text style={styles.ritualTitle}>{currentRitual.title}</Text>
        <Text style={styles.vibrationText}>⚡ {currentRitual.vibration}</Text>
      </View>

      {/* Manifestation Affirmation Box */}
      <View style={[styles.affirmationBox, { borderLeftColor: currentRitual.color }]}>
        <Text style={styles.affirmationQuote}>“</Text>
        <Text style={styles.affirmationText}>{currentRitual.affirmation}</Text>
      </View>

      {/* 30-Second Guided Steps */}
      <View style={styles.stepsContainer}>
        {currentRitual.steps.map((step, idx) => {
          const isCurrentStep = isRunning && currentStepIndex === idx;
          const isDoneStep = (isRunning && currentStepIndex > idx) || isCompleted;

          return (
            <View
              key={idx}
              style={[
                styles.stepRow,
                isCurrentStep && styles.stepRowActive,
                isDoneStep && styles.stepRowDone,
              ]}
            >
              <View
                style={[
                  styles.stepNumber,
                  isCurrentStep && { backgroundColor: currentRitual.color },
                  isDoneStep && styles.stepNumberDone,
                ]}
              >
                <Text
                  style={[
                    styles.stepNumberText,
                    isCurrentStep && { color: '#0B0C10', fontWeight: 'bold' },
                  ]}
                >
                  {isDoneStep ? '✓' : idx + 1}
                </Text>
              </View>
              <Text
                style={[
                  styles.stepText,
                  isCurrentStep && styles.stepTextActive,
                  isDoneStep && styles.stepTextDone,
                ]}
              >
                {step}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Timer Display & Visual Progress Bar */}
      <View style={styles.timerWrapper}>
        <View style={styles.timerHeader}>
          <Text style={styles.timerLabel}>
            {isRunning
              ? `ALIGNING FREQUENCY • PHASE ${currentStepIndex + 1}/3`
              : isCompleted
              ? '✨ 30s RITUAL COMPLETE — LUCK ANCHORED'
              : '30-SECOND MANIFESTATION PROTOCOL'}
          </Text>
          <Animated.Text
            style={[
              styles.timerDigits,
              { color: isCompleted ? '#00FF66' : currentRitual.color, transform: [{ scale: pulseAnim }] },
            ]}
          >
            {secondsRemaining}s
          </Animated.Text>
        </View>

        {/* Progress Track */}
        <View style={styles.progressTrack}>
          <Animated.View
            style={[
              styles.progressBar,
              {
                backgroundColor: currentRitual.color,
                width: progressAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['0%', '100%'],
                }),
              },
            ]}
          />
        </View>
      </View>

      {/* Action Controls */}
      <View style={styles.controlRow}>
        {!isRunning && !isCompleted && (
          <TouchableOpacity
            style={[styles.primaryActionBtn, { backgroundColor: currentRitual.color }]}
            onPress={handleStart}
            activeOpacity={0.8}
          >
            <Text style={styles.primaryActionBtnText}>▶ START 30s RITUAL</Text>
          </TouchableOpacity>
        )}

        {isRunning && (
          <>
            <TouchableOpacity
              style={styles.secondaryBtn}
              onPress={handlePause}
              activeOpacity={0.8}
            >
              <Text style={styles.secondaryBtnText}>⏸ PAUSE</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.cancelBtn}
              onPress={handleReset}
              activeOpacity={0.8}
            >
              <Text style={styles.cancelBtnText}>RESET</Text>
            </TouchableOpacity>
          </>
        )}

        {!isRunning && secondsRemaining < 30 && !isCompleted && (
          <>
            <TouchableOpacity
              style={[styles.primaryActionBtn, { backgroundColor: currentRitual.color }]}
              onPress={handleResume}
              activeOpacity={0.8}
            >
              <Text style={styles.primaryActionBtnText}>RESUME</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.cancelBtn}
              onPress={handleReset}
              activeOpacity={0.8}
            >
              <Text style={styles.cancelBtnText}>RESET</Text>
            </TouchableOpacity>
          </>
        )}

        {isCompleted && (
          <View style={styles.completedActions}>
            <TouchableOpacity
              style={[styles.primaryActionBtn, { backgroundColor: '#00FF66' }]}
              onPress={handleReset}
              activeOpacity={0.8}
            >
              <Text style={[styles.primaryActionBtnText, { color: '#0B0C10' }]}>
                ↺ REPEAT RITUAL
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#131722',
    borderRadius: 14,
    padding: 18,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#232936',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    elevation: 5,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
  },
  typeBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
  },
  dateBadge: {
    backgroundColor: '#1E2433',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  dateBadgeText: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '600',
  },
  numerologyBadge: {
    backgroundColor: '#2A1F3D',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#8B5CF6',
  },
  numerologyBadgeText: {
    color: '#D8B4FE',
    fontSize: 10,
    fontWeight: '700',
  },
  shuffleBtn: {
    backgroundColor: '#1E2433',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#334155',
  },
  shuffleBtnText: {
    color: '#CBD5E1',
    fontSize: 11,
    fontWeight: '600',
  },
  titleSection: {
    marginBottom: 10,
  },
  ritualTitle: {
    color: '#F8FAFC',
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  vibrationText: {
    color: '#64748B',
    fontSize: 11,
    fontWeight: '600',
    marginTop: 2,
    letterSpacing: 0.5,
  },
  affirmationBox: {
    backgroundColor: '#181E2C',
    borderRadius: 8,
    borderLeftWidth: 4,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 14,
    position: 'relative',
  },
  affirmationQuote: {
    position: 'absolute',
    top: -4,
    left: 4,
    color: '#334155',
    fontSize: 28,
    fontWeight: '900',
  },
  affirmationText: {
    color: '#E2E8F0',
    fontSize: 13,
    fontStyle: 'italic',
    lineHeight: 19,
    paddingLeft: 10,
    fontWeight: '500',
  },
  stepsContainer: {
    gap: 8,
    marginBottom: 16,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#161B26',
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#1E2433',
  },
  stepRowActive: {
    borderColor: '#38BDF8',
    backgroundColor: '#1A2436',
  },
  stepRowDone: {
    opacity: 0.6,
  },
  stepNumber: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#263043',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  stepNumberDone: {
    backgroundColor: '#059669',
  },
  stepNumberText: {
    color: '#E2E8F0',
    fontSize: 11,
    fontWeight: '700',
  },
  stepText: {
    color: '#94A3B8',
    fontSize: 12,
    flex: 1,
  },
  stepTextActive: {
    color: '#F1F5F9',
    fontWeight: '600',
  },
  stepTextDone: {
    textDecorationLine: 'line-through',
    color: '#64748B',
  },
  timerWrapper: {
    marginBottom: 16,
    backgroundColor: '#0F131C',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#1E2433',
  },
  timerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  timerLabel: {
    color: '#64748B',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
    flex: 1,
  },
  timerDigits: {
    fontSize: 18,
    fontWeight: '900',
    fontVariant: ['tabular-nums'],
  },
  progressTrack: {
    height: 6,
    backgroundColor: '#1E2433',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: 3,
  },
  controlRow: {
    flexDirection: 'row',
    gap: 10,
    alignItems: 'center',
  },
  primaryActionBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryActionBtnText: {
    color: '#0B0C10',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 1,
  },
  secondaryBtn: {
    flex: 1,
    backgroundColor: '#334155',
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  secondaryBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  cancelBtn: {
    backgroundColor: '#1E2433',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  cancelBtnText: {
    color: '#94A3B8',
    fontSize: 12,
    fontWeight: '700',
  },
  completedActions: {
    flex: 1,
  },
});
