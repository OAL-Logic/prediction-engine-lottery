/**
 * Sovereign Hashing Utility 🛡️
 * =========================
 * Processes sensitive user inputs (vibrational data) locally using BLAKE2b.
 * Ensures "Vibrational Sovereignty" by never transmitting raw data.
 */

import { blake2bHex } from 'blakejs';

/**
 * Generates an "Intentional Hash" from raw inputs and a deterministic salt.
 * 
 * @param name - The user's name or intentional string.
 * @param birthDate - The user's birth date.
 * @param drawId - A deterministic salt (e.g., draw ID or timestamp).
 * @returns A 64-character hex fingerprint.
 */
export function generateIntentionalHash(
  name: string,
  birthDate: string,
  drawId: string
): string {
  // Normalize inputs to ensure mathematical reproducibility
  const normalizedName = name.trim().toLowerCase();
  const normalizedDate = birthDate.trim();
  
  // Combine inputs into a single "vibrational" buffer
  const rawInput = `${normalizedName}|${normalizedDate}|${drawId}`;
  
  // Generate 64-byte BLAKE2b hash
  // blake2bHex returns the hex string directly
  return blake2bHex(rawInput);
}
