# Story 3.2: Standardized Obsidian Metadata Contract

Status: complete

## Story

As a **Knowledge Curator**,
I want every analytical command to output a consistent YAML frontmatter block in a **fresh file** and register it in a **central index**,
so that I can maintain isolated records while having a single chronological log of all analyses.

## Acceptance Criteria

1. **Standardized YAML Frontmatter**: Every `--export-md` must output a YAML block with: `source-strategy`, `confidence-rating`, and `#lottery/analysis` tags. (AC: 3.2.1) [x]
2. **Fresh File Mandate**: The system must create a new file (or overwrite if existing) for each export, preventing messy appends. (AC: 3.2.2) [x]
3. **Wikilink Indexing**: Every export must automatically append a wikilink (e.g., `[[FILENAME]]`) and timestamp to a central `docs/analysis-index.md` file. (AC: 3.2.3) [x]
4. **Data Payload**: Include a `data-payload` key with raw JSON in the frontmatter for DataviewJS parsing. (AC: 3.2.4) [x]
5. **One-Way Data Flow**: Verified that the Engine never reads from the index. (AC: 3.2.5) [x]

## Dev Notes

- **Implementation**: Standardized `_write_md` function added to both `daily.py` and `suggest.py`.
- **Indexing**: Automates the maintenance of `docs/analysis-index.md` for easy Obsidian navigation.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Implemented standardized Obsidian export for both `suggest` and `daily` commands.
- ✅ Automated wikilink registration in `docs/analysis-index.md`.
- ✅ Enforced forensic isolated-file pattern for all analytical snapshots.

### File List

- `engine/cli/commands/daily.py` (MODIFIED)
- `engine/cli/commands/suggest.py` (MODIFIED)
- `docs/analysis-index.md` (NEW/AUTOMATED)
