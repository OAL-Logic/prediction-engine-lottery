# Story 4.2: 3D Interactive Correlation Map

Status: done

## Story

As a **Data Alchemist**,
I want to visualize number relationships in a 3D dodecahedron-inspired space,
so that I can identify non-Euclidean "Geometric Adjacencies" between pool candidates.

## Acceptance Criteria

1. **Dodecahedron Graph**: Render an interactive 3D graph based on the 20-vertex dodecahedron model. (AC: 4.2.1) [x]
2. **Dynamic Scaling**: Node size represents historical frequency; edge brightness represents current correlation. (AC: 4.2.2) [x]
3. **Cross-Platform Gestures**: Support standard rotate/zoom gestures (Terminal keyboard/mouse, Mobile touch). (AC: 4.2.3) [x]

## Tasks / Subtasks

- [x] Implement the `SpatialRetina` component using `@opentui/three`.
- [x] Integrate the `engine/modules/geometry.py` graph into the TUI scene.
- [x] Map real-time engine scores to vertex illumination.

## Dev Notes

- **Spatial Mapping**: Uses a vertex mapping $v = (N-1) \pmod{20}$ to distribute 60+ numbers across the polyhedron.
- **Library**: `@opentui/three` (a Zig-accelerated Three.js bridge for native terminals).

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Built the Spatial Retina component for 3D topological exploration.
- ✅ Verified adjacency-based cross-pollination boosts in the visual scene.
