# Story 2.4: Muon Strike Simulation (Cosmic Ray)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **Esoteric Architect & Chaos Analyst**,
I want to visually simulate and display real-time cosmic-ray muon strike bit-flip mutations in the gestural Expo mobile client,
So that I can monitor chaotic single-event upsets (SEUs) and quantum mutations dynamically warping the Riemannian probability manifold.

## Acceptance Criteria

1. **Muon Strike Store State**: Extend the Zustand store (`app/stores/useResonanceStore.ts`) to manage cosmic ray event states:
   - `lastMuonStrike`: Object containing `{ originalTicket: number[], mutatedTicket: number[], mutatedIndex: number, bitFlipValue: number, timestamp: string }` or `null`.
   - `muonStrikeCount`: Integer tracking total strikes captured during the session. (AC: 2.4.1)
2. **WebGL Shockwave Ripple (Shader)**: Modify the custom shader in `app/components/SpatialRetina.tsx` to project a bright Red (`#FF3333`) electromagnetic shockwave propagation centered at the coordinate of the mutated node upon a cosmic strike. The shockwave must expand radially and decay over 1.5 seconds. (AC: 2.4.2)
3. **High-Contrast Flash Alert (UI Banner)**: Display a prominent styled visual banner when a muon strike occurs:
   - Background: Dark Blood Red (`#2A0808` or `#FF3333` with high contrast).
   - Text: `⚡ COSMIC RAY DETECTED: SINGLE-EVENT UPSET (BIT FLIP) MUTATED TICKET AT INDEX X [VAL ^ Y]` rendered in monospaced font. (AC: 2.4.3)
4. **API Integration & OSINT Telemetry**: Wire the suggestion API trigger to inspect returned ticket metadata. If a cosmic ray mutation is reported by the Python Engine suggestion results, dispatch the details to the store to trigger the WebGL shockwave and UI alert banner. (AC: 2.4.4)
5. **Interactive Chaos Trigger (Manual Simulation)**: Provide a dedicated action button **`⚡ SIMULATE COSMIC STRIKE`** in the interface to allow operators to manually inject mock strikes and verify shockwave rendering at a stable 60 FPS. (AC: 2.4.5)

## Tasks / Subtasks

- [x] **Zustand Store Additions**: Update `app/stores/useResonanceStore.ts`:
  - [x] Add `lastMuonStrike` state property.
  - [x] Add `muonStrikeCount` integer state property.
  - [x] Implement `triggerMuonStrike(strikeDetails)` action to update state and increment strike count.
  - [x] Implement `resetMuonStrike()` action.
- [x] **3D Manifold WebGL Shockwave**: Update `app/components/SpatialRetina.tsx`:
  - [x] Add uniforms: `uMuonStrikeTime` (float), `uMuonStrikeOrigin` (vec3), `uMuonStrikeActive` (float).
  - [x] Calculate radial distance in vertex shader: `float dist = distance(position, uMuonStrikeOrigin);`
  - [x] Apply a wave ripple equation: `float wave = sin(dist * 3.0 - uMuonStrikeTime * 8.0) * exp(-uMuonStrikeTime * 1.5);`
  - [x] Mutate node positions and override vertex colors to Red (`#FF3333`) along the propagation wavefront.
  - [x] Hook the `useFrame` render loop to increment `uMuonStrikeTime` and disable `uMuonStrikeActive` once the 1.5-second animation finishes.
- [x] **Flash Alert Banner UI**:
  - [x] Create a custom alert component or absolute-positioned banner inside `app/App.tsx`.
  - [x] Apply a pulsing glow animation with modern design aesthetics.
- [x] **Suggestions Ingestion Logic**:
  - [x] Update suggestion request success callback in `App.tsx` to search for `cosmic_ray_detected` or `_last_muon_strike` in response metadata.
  - [x] If detected, extract mutation indexes and coordinates, and call `triggerMuonStrike`.
- [x] **Simulation Controls**:
  - [x] Embed the **`SIMULATE COSMIC STRIKE`** button under the Telemetry Console.
  - [x] Verify that manual strikes propagate smoothly at stable 60 FPS.

## Dev Notes

- **XOR Mutation Logic**:
  Bitwise XOR flip is: `mutated = original ^ bit_flip` (where `bit_flip = 1 << rand(0, 5)`).
- **Shader Calculations**:
  To compute the coordinate origin on the Fibonacci sphere, locate the mutated node's index `i` and map it to spherical coordinates using the golden spiral formula inside Three.js.
- **Visual Palette Standard**:
  - Shockwave/Alert Color: Red (`#FF3333`)
  - Status indicators: High-density monospaced warnings.

### Project Structure Notes

- **3D Manifold Render**: `app/components/SpatialRetina.tsx` (UPDATE)
- **Zustand State Store**: `app/stores/useResonanceStore.ts` (UPDATE)
- **Main App View Layout**: `app/App.tsx` (UPDATE)

### References

- [Source: docs/versions/feature-batch-6-quantum-iching-muon.md#2. Atmospheric Muon Flux]
- [Source: engine/strategies/__init__.py#L445-L485]
- [Source: docs/architecture/technical-spec.md#10. Atmospheric Muon Flux Simulation]

## Dev Agent Record

### Agent Model Used

gemini-2.5-pro

### Debug Log References

### Completion Notes List

### File List
