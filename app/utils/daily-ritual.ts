/**
 * Daily Ritual & Manifestation Engine 🌟
 * =====================================
 * Provides deterministic and randomized 30-second rituals, breathwork,
 * and manifestation affirmations for lottery luck calibrated by current date.
 */

export interface RitualItem {
  id: string;
  title: string;
  type: 'Breathing' | 'Visualization' | 'Affirmation' | 'Somatic' | 'Focus';
  affirmation: string;
  action: string;
  steps: string[];
  vibration: string;
  color: string;
}

export const RITUAL_CATALOG: RitualItem[] = [
  {
    id: 'golden-inhale',
    title: 'The Golden Inhale',
    type: 'Breathing',
    affirmation: 'I am an open channel for universal abundance and winning serendipity.',
    action: 'Close your eyes. Inhale deeply for 4 seconds visualizing golden light filling your lungs. Hold for 7 seconds feeling magnetic prosperity. Exhale slowly for 8 seconds, releasing doubt.',
    steps: [
      'Inhale golden abundance light (4s)',
      'Hold breath & feel magnetic prosperity (7s)',
      'Slow exhale, letting go of all doubt (8s)',
    ],
    vibration: '528 Hz • Solar Plexus Gold',
    color: '#FFD700',
  },
  {
    id: 'quantum-palms',
    title: 'Quantum Resonance Palms',
    type: 'Somatic',
    affirmation: 'Every cell in my body vibrates with clarity, intuition, and jackpot luck.',
    action: 'Rub your palms vigorously together for 10 seconds until warm. Place them gently over your heart. Breathe softly and whisper your affirmation three times.',
    steps: [
      'Rub palms together vigorously for warmth (10s)',
      'Place warm hands gently over your heart (10s)',
      'Whisper your affirmation with certainty 3 times (10s)',
    ],
    vibration: '432 Hz • Heart Chakra Emerald',
    color: '#00FF66',
  },
  {
    id: 'emerald-ray',
    title: 'The Emerald Ray Anchor',
    type: 'Visualization',
    affirmation: 'Infinite wealth and divine fortune flow directly into my reality today.',
    action: 'Visualize an intense emerald-green ray descending from the cosmos through your crown, bathing your hands and grounding deep into the earth.',
    steps: [
      'Visualize cosmic emerald light entering crown (10s)',
      'Feel the electric hum of fortune in your hands (10s)',
      'Anchor the vibration deep into the earth (10s)',
    ],
    vibration: '888 Hz • Abundance Ray',
    color: '#10B981',
  },
  {
    id: 'gratitude-amplifier',
    title: 'The Gratitude Amplifier',
    type: 'Affirmation',
    affirmation: 'I am deeply grateful for the blessings I have, and ready for extraordinary wins.',
    action: 'Recall three small moments of good fortune from this week. Amplify that warm gratitude in your chest, then project that feeling into today\'s draw.',
    steps: [
      'Recall 3 blessings you received this week (10s)',
      'Feel gratitude expand as radiant warmth (10s)',
      'Direct that high frequency to your lucky numbers (10s)',
    ],
    vibration: '639 Hz • Harmonic Jupiter',
    color: '#8B5CF6',
  },
  {
    id: 'drum-serendipity',
    title: 'Drum of Serendipity',
    type: 'Visualization',
    affirmation: 'The spinning lottery spheres are magnetically drawn to my chosen numbers.',
    action: 'Picture the lottery drum tumbling in slow motion. See your chosen numbers illuminated, floating with graceful certainty into the winning slots.',
    steps: [
      'Envision the lottery drum spinning in brilliant light (10s)',
      'See your numbers illuminate with soft golden glow (10s)',
      'Seal the winning visual with calm peace (10s)',
    ],
    vibration: '741 Hz • Cosmic Drum Harmonic',
    color: '#06B6D4',
  },
  {
    id: 'temple-tap',
    title: 'Third Eye Temple Tap',
    type: 'Focus',
    affirmation: 'My intuition is razor-sharp. I pick the right numbers at the perfect moment.',
    action: 'With two fingers on each hand, gently tap your temples in rhythmic beats while clearing all mental static and picturing your lucky ticket.',
    steps: [
      'Gently tap temples in slow rhythmic beats (10s)',
      'Clear mental chatter and trust your gut feeling (10s)',
      'Take one deep centering breath of intuition (10s)',
    ],
    vibration: '852 Hz • Third Eye Clarity',
    color: '#6366F1',
  },
  {
    id: 'open-palms',
    title: 'The Open Hands Blessing',
    type: 'Somatic',
    affirmation: 'I release all scarcity mindset. I am worthy and receptive to monumental luck.',
    action: 'Rest your hands on your lap with open palms facing upward. Roll your shoulders back and relax your jaw. Say softly: "I welcome my fortune."',
    steps: [
      'Open palms upward and relax shoulders completely (10s)',
      'Feel receptive cosmic energy resting in your hands (10s)',
      'Whisper "I welcome my fortune" with calm certainty (10s)',
    ],
    vibration: '963 Hz • Crown Gateway',
    color: '#EC4899',
  },
  {
    id: 'box-breath-luck',
    title: 'Box Breath of Certainty',
    type: 'Breathing',
    affirmation: 'Calm confidence is the true frequency of luck. I play from peace, not panic.',
    action: 'Perform a deliberate square breathing cycle: Inhale luck for 4s, hold in calm for 4s, exhale anxiety for 4s, hold in trust for 4s.',
    steps: [
      'Inhale luck & confidence slowly (4s) • Hold full (4s)',
      'Exhale worry & tension smoothly (4s) • Hold empty (4s)',
      'One final deep breath to lock in steady peace (14s)',
    ],
    vibration: '432 Hz • Autonomic Nervous Rest',
    color: '#3B82F6',
  },
  {
    id: 'silver-cord',
    title: 'The Silver Cord Connection',
    type: 'Visualization',
    affirmation: 'An invisible line of synchronicity links my choices to the winning outcome.',
    action: 'Envision a shimmering silver cord connecting your hands directly to the draw machine. Feel the subtle magnetic pulse of synchronicity.',
    steps: [
      'Envision a shimmering silver thread of synchronicity (10s)',
      'Send positive intent along the thread (10s)',
      'Rest in relaxed anticipation of the result (10s)',
    ],
    vibration: '396 Hz • Lunar Synchronicity',
    color: '#E2E8F0',
  },
  {
    id: 'joyful-precelebration',
    title: 'The Joyful Pre-Celebration',
    type: 'Affirmation',
    affirmation: 'I already feel the goosebumps and joy of celebrating my winning ticket.',
    action: 'Close your eyes and feel the physical sensations of matching the winning numbers: the widened eyes, the joyful grin, the wave of relief and excitement.',
    steps: [
      'Imagine the notification confirming your winning numbers (10s)',
      'Smile wide and feel the genuine goosebumps of relief (10s)',
      'Anchor this victorious feeling into your daily spirit (10s)',
    ],
    vibration: '528 Hz • High-Frequency Joy',
    color: '#F59E0B',
  },
  {
    id: 'cleansing-exhale',
    title: 'The Cleansing Wind Exhale',
    type: 'Breathing',
    affirmation: 'I release all pressure and embrace the playful magic of the universe.',
    action: 'Release all stale air with an audible whoosh. Draw in fresh, sparkling vitality. Acknowledge that serendipity loves a relaxed, playful spirit.',
    steps: [
      'Audible deep exhale, blowing away financial anxiety (10s)',
      'Inhale crisp, sparkling vitality and enthusiasm (10s)',
      'Smile and embrace the game as playful co-creation (10s)',
    ],
    vibration: '417 Hz • Stagnation Release',
    color: '#14B8A6',
  },
  {
    id: 'magnetic-sphere',
    title: 'The Golden Number Magnet',
    type: 'Focus',
    affirmation: 'My ticket is a magnet for the exact numbers drawn today.',
    action: 'Cup your hands together as if holding a glowing golden sphere. Whisper your affirmation into the space between your hands, then press them gently to your chest.',
    steps: [
      'Cup hands to shape an energetic sphere (10s)',
      'Whisper your manifestation affirmation into the center (10s)',
      'Bring hands to chest to seal the magnetic intention (10s)',
    ],
    vibration: '888 Hz • Magnetic Harmony',
    color: '#FBBF24',
  },
];

/**
 * Calculates a deterministic daily index from an ISO date string (YYYY-MM-DD).
 */
export function getDailyIndex(dateStr: string, total: number = RITUAL_CATALOG.length): number {
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = ((hash << 5) - hash) + dateStr.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) % total;
}

/**
 * Calculates the daily numerological root (1-9) from YYYY-MM-DD.
 */
export function getDailyNumerologyRoot(dateStr: string): number {
  const digits = dateStr.replace(/\D/g, '');
  if (!digits) return 7;
  let sum = digits.split('').reduce((acc, ch) => acc + parseInt(ch, 10), 0);
  while (sum > 9) {
    sum = sum.toString().split('').reduce((acc, ch) => acc + parseInt(ch, 10), 0);
  }
  return sum;
}

export function getDailyRitual(dateInput: Date | string = new Date()): {
  ritual: RitualItem;
  dateStr: string;
  formattedDate: string;
  numerologyRoot: number;
} {
  const dateObj = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  const dateStr = `${year}-${month}-${day}`;

  const idx = getDailyIndex(dateStr, RITUAL_CATALOG.length);
  const ritual = RITUAL_CATALOG[idx];
  const numerologyRoot = getDailyNumerologyRoot(dateStr);

  const formattedDate = dateObj.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return { ritual, dateStr, formattedDate, numerologyRoot };
}
