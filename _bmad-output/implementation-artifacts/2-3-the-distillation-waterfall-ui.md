# Story 2.3: The Distillation Waterfall UI

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **Esoteric Architect & Data Alchemist**,
I want to integrate a real-time quantum distillation and swarm telemetry console into the gestural Expo client,
So that I can monitor the live streaming log stream, hardware-distilled entropy ingestion, and active swarm search paths on the go.

## Acceptance Criteria

1. **Zustand Telemetry Store**: Extend the Zustand store (`app/stores/useResonanceStore.ts`) to manage telemetry logs state, maintaining a dynamic array of parsed telemetry messages and a connection status. Clamp the log list to a maximum of 500 entries to prevent memory overflow during long runs. (AC: 2.3.1)
2. **Stateful WebSocket Client**: Establish a stateful WebSocket connection within the Expo app pointing to `ws://localhost:8080/telemetry` with automatic reconnection logic (exponential backoff starting at 1s, capping at 10s) and status monitoring. (AC: 2.3.2)
3. **Forensic Neon Console UI**: Build a custom scrolling viewport styled under the "Forensic Neon" visual standard:
   - Deep Obsidian background (`#0B0C10`).
   - Monospaced typefaces (`monospace` font family).
   - Dynamic coloring matching the backend levels:
     - `SUCCESS` / `done`: Matrix Green (`#00FF66`).
     - `RESONANCE` / `Astro-Pulse`: Astro Violet (`#8A2BE2`).
     - `DECOHERENCE` / errors: Red (`#FF3333`).
     - `INFO` / defaults: Silver / Gray (`#999999`). (AC: 2.3.3)
4. **Auto-Scroll Behavior**: The log console must automatically scroll to the bottom upon receiving new telemetry pulses, unless the user has manually scrolled up to inspect previous logs. (AC: 2.3.4)
5. **High-Performance Continuity**: Guarantee stable and fluid UI interactions (maintaining ≥ 60 FPS) under high-frequency stream updates (up to 50 logs/second) using optimized layouts. (AC: 2.3.5)
6. **Streaming Controls**: Expose dedicated visual controls for the operator to pause/resume the live log stream and clear the existing log history. (AC: 2.3.6)

## Tasks / Subtasks

- [x] **State Store Extension**: Update `app/stores/useResonanceStore.ts`:
  - [x] Add `telemetryLogs` (array of `TelemetryMessage` objects) to `ResonanceState`.
  - [x] Add `isTelemetryConnected` (boolean) and `isTelemetryPaused` (boolean).
  - [x] Add `addTelemetryLog(log)` with a `.slice(-500)` buffer clamping guard.
  - [x] Add `setTelemetryConnected(connected)` and `setTelemetryPaused(paused)` actions.
  - [x] Add a `clearTelemetryLogs()` action.
- [x] **WebSocket Integration**:
  - [x] Create a robust connection utility or hook to manage the WebSocket lifecycle.
  - [x] Implement robust error handling, reconnect-on-close, and status tracking.
  - [x] Securely parse incoming JSON payloads into the `TelemetryMessage` structure.
- [x] **Telemetry Component development**:
  - [x] Implement `app/components/TelemetryWaterfall.tsx` as a reusable component.
  - [x] Build a sleek header with a connection status dot (glowing Matrix Green when connected, flashing Astro Violet/Red when reconnecting/disconnected) and control buttons.
  - [x] Render logs in a monospaced layout with appropriate color coding for timestamps, levels, and messages.
  - [x] Integrate auto-scroll with a `ScrollView` or `FlatList` component.
- [x] **App Integration**:
  - [x] Import and place `TelemetryWaterfall` inside `app/App.tsx`.
  - [x] Add toggle buttons/tabs to swap views or stack it cleanly under the 3D Spatial Retina.
  - [x] Style layout with modern responsive design principles.
- [x] **Testing & Verification**:
  - [x] Implement a mock mode to inject high-frequency test messages to verify performance stability.
  - [x] Test the automatic fallback and connection recovery under offline states.

## Dev Notes

- **Payload Structure**:
  ```json
  {
    "source": "engine",
    "level": "INFO" | "RESONANCE" | "DECOHERENCE" | "SUCCESS",
    "message": "Quantum state-space initialized",
    "timestamp": "2026-05-22T12:15:55Z"
  }
  ```
- **Connection Details**: Standard local address is `ws://localhost:8080/telemetry`. For real device execution, it must dynamically adapt or fall back gracefully.
- **Visual Design Rules**:
  - Background: `#0B0C10` (Dark Obsidian)
  - Text base: `#C0C0C0`
  - Success level color: `#00FF66`
  - Resonance level color: `#8A2BE2`
  - Decoherence level color: `#FF3333`
  - Status Indicator: pulsing bullet CSS-equivalent style or direct element styling.

### Project Structure Notes

- **Expo Component**: `app/components/TelemetryWaterfall.tsx` (NEW)
- **State Store**: `app/stores/useResonanceStore.ts` (UPDATE)
- **Main Entry View**: `app/App.tsx` (UPDATE)

### References

- [Source: engine/modules/telemetry.py#L17-L28]
- [Source: gateway/main.go#L69-L71]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#2.1 `ProphetTelemetryConsole`]
- [Source: _bmad-output/implementation-artifacts/5-5-real-time-telemetry-websocket.md#L11-L17]

## Dev Agent Record

### Agent Model Used

gemini-2.5-pro

### Debug Log References

- Configured stateful WebSocket connections mapping to `ws://localhost:8080/telemetry` dynamically.
- Developed an offline exponential backoff reconnect mechanism starting at 1s and capped at 10s.
- Created a robust custom Mock Injection Engine inside `TelemetryWaterfall.tsx` allowing developers to stream high-frequency logs (up to 50 logs/sec) locally without background servers running.
- Addressed memory usage optimization by strictly truncating logs at 500 entries inside the Zustand store (`app/stores/useResonanceStore.ts`).

### Completion Notes List

- ✅ Expanded Zustand state store (`app/stores/useResonanceStore.ts`) to manage parsed logs, connection, and paused states.
- ✅ Implemented stateful WebSocket connection listener featuring auto-reconnection and exponential backoff.
- ✅ Created the `TelemetryWaterfall.tsx` visual log console with "Forensic Neon" color themes mapping dynamic levels (Matrix Green `#00FF66` for success, Astro Violet `#8A2BE2` for resonance, Red `#FF3333` for decoherence).
- ✅ Integrated Pause/Resume, Clear, Mock injection controls, and glowing status dot indicators inside the component.
- ✅ Embedded `TelemetryWaterfall` directly into `app/App.tsx` below the Swarm Equalizer.

### File List

- `app/stores/useResonanceStore.ts` (MODIFIED)
- `app/components/TelemetryWaterfall.tsx` (NEW)
- `app/App.tsx` (MODIFIED)
