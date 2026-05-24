# Story 6.2: OpenTUI Filter Palette

Status: complete

## Story

As a **User**,
I want a high-performance fuzzy-searchable interface to find and toggle any of the 100+ filters,
so that I can rapidly configure my analytical cockpit.

## Acceptance Criteria

1. **Fuzzy Search**: Implement a `TextInput` that filters the registry list in real-time. (AC: 6.2.1) [x]
2. **OpenTUI Native Core**: Component must be built as a `BoxRenderable` using the OpenTUI (Zig) core. (AC: 6.2.2) [x]
3. **Registry Integration**: Display all 5 tiers of analytical vectors with their metadata. (AC: 6.2.3) [x]

## Dev Notes

- **Implementation**: Created `tui/src/components/FilterPalette.ts`.
- **Aesthetic**: Uses high-fidelity "Matrix Green" terminal theme with double-borders.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Built the `FilterPalette` component in TypeScript.
- ✅ Integrated with OpenTUI native event loop for smooth fuzzy searching.
- ✅ Verified 100% type safety with `tsc --strict`.

### File List

- `tui/src/components/FilterPalette.ts` (NEW)
