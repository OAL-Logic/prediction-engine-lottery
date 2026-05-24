# Story 4.1: The Confidence Saliency Layer

Status: done

## Story

As a **User**,
I want abstract filter outputs to be translated into "Heat Currents" and "Statistical Fog,"
so that I can intuitively sense where the system has high confidence versus high noise.

## Acceptance Criteria

1. **Saliency Mapping**: The system must map score density to color gradients (Heat) and variance to opacity (Fog) in the TUI. (AC: 4.1.1) [x]
2. **Dynamic Range**: The visualizer must automatically scale its range based on the min/max scores of the current tensor. (AC: 4.1.2) [x]
3. **Toggleable Masking**: The user can toggle "Confidence Masking" to hide regions below a specific signal-to-noise ratio. (AC: 4.1.3) [x]

## Tasks / Subtasks

- [x] Implement saliency color mapping logic in `tui/src/utils/saliency.ts`.
- [x] Integrate saliency rendering into the `WheelMatrix` and `FilterPalette` components.
- [x] Add a configuration toggle for "Nerd Mode" opacity/fog levels.

## Dev Notes

- **Implementation**: Uses ANSI 256-color escape codes to simulate gradients in the terminal.
- **Fog Logic**: Implemented via braille pattern density and character dimming.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Developed saliency algorithm for mapping high-dimensional scores to terminal aesthetics.
- ✅ Integrated with OpenTUI's reactive state for real-time fog updates.
