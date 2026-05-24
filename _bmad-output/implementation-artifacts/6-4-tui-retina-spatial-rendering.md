# Story 6.4: TUI Retina Spatial Rendering

Status: complete

## Story

As a **Chaos Researcher**,
I want to visualize high-dimensional number correlations in a 3D topographic map,
so that I can identify non-Euclidean patterns and geometric singularities.

## Acceptance Criteria

1. **3D Rendering**: Implement a rotating dodecahedron wireframe with 60 nodes. (AC: 6.4.1) [x]
2. **OpenTUI Three**: Built using the `@opentui/three` native Zig WGPU bridge. (AC: 6.4.2) [x]
3. **Geometric Correlation**: Map node size/brightness to frequency/correlation scores. (AC: 6.4.3) [x]

## Dev Notes

- **Implementation**: Created `tui/src/components/SpatialRetina.ts`.
- **Environment**: Optimized for **Bun** + OpenTUI native core for smooth 3D animation in the terminal.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Built the `SpatialRetina` 3D topographic cockpit.
- ✅ Integrated with `@opentui/three` for high-performance native rendering.
- ✅ Verified rotating geometry and node mapping.

### File List

- `tui/src/components/SpatialRetina.ts` (NEW)
