# Story 2.1: The Spatial Retina (Riemannian Manifold)

Status: ready-for-dev

## Story

As a **Data Alchemist**,
I want an intuitive 3D exploration of non-linear lottery clusters,
So that I can identify geodesic minima in the high-dimensional manifold.

## Acceptance Criteria

1. **WebGPU Rendering**: Port the existing 3D visualization logic to use **WebGPU** via `@react-three/fiber` v9.6 to ensure cross-platform performance. (AC: 2.1.1)
2. **Manifold Curvature**: The component must render a high-fidelity 3D Riemannian surface representing the lottery probability density. (AC: 2.1.2)
3. **High Node Density**: The system must maintain a stable **60 FPS** fluidity while rendering 100k+ historical nodes on modern mobile and desktop hardware. (AC: 2.1.3)
4. **Interactive Navigation**: Users must be able to rotate, zoom, and pan the manifold using gestural controls (Expo) and keyboard shortcuts `hjkl` (OpenTUI/Desktop). (AC: 2.1.4)
5. **Real-time Synchronization**: The manifold must reactive in real-time to changes in the **Swarm Equalizer** weighting. (AC: 2.1.5)

## Tasks / Subtasks

- [ ] Initialize the `@react-three/fiber` v9.6 environment in the Expo App.
- [ ] Implement the `SpatialRetina` component with WebGPU shader support.
- [ ] Develop the Riemannian surface generator using the high-dimensional cluster data from the Engine.
- [ ] Implement the instanced rendering logic to support 100k+ nodes without draw-call bottlenecks.
- [ ] Add touch and keyboard event handlers for manifold navigation.
- [ ] Integrate the `useResonanceStore` (Zustand) for real-time state synchronization with the swarm.

## Dev Notes

- **Performance**: Use **InstancedMesh** for the 100k+ nodes to minimize draw calls. Standardize on the **TSL (Three Shading Language)** for optimal cross-platform shader performance.
- **Precision**: The manifold geometry must be bijectively mapped to the Euclidean statistical space to ensure "Mathematical Transparency."
- **Alternative Interface**: Ensure the `SpatialRetina` component is reusable in the **Prophet Desktop Client (PySide6)**, possibly via a `QWebEngineView` or a native WebGPU bridge.
- **Visuals**: Adhere to the "Forensic Neon" palette (Matrix Green for nodes, Astro Violet for Great Circles).

### Project Structure Notes

- **Expo Component**: `app/src/components/spatial-retina/` (NEW)
- **State Store**: `app/src/stores/useResonanceStore.ts` (NEW)
- **TUI Integration**: `@opentui/three` (UPDATE)

### References

- [Source: docs/architecture/architecture.md#2.4 Oracle's Retina]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#2.1 `SpatialRetina`]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
