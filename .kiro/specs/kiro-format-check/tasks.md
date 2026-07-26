# Implementation Plan

## Overview

This plan implements an optional SVG traceability badge derived from the
existing `report.json`, wired behind a `--badge` CLI flag. This spec was
originally written to validate SpecGuard's parser against real Kiro output
with the tasks left unimplemented on purpose - it has since been implemented
for real, unchanged from what's specified below, and is live at
estebanherna.github.io/specguard/badge.svg.

## Tasks

- [x] 1. Implement the Badge_Generator module
  - Create `src/specguard/report/badge.py` with `write_badge(report, path)`
  - Select fill color by score threshold and render the SVG
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Wire the optional `--badge` flag into the CLI
  - [x] 2.1 Add the `--badge` option to the audit command
    - _Requirements: 2.1, 2.2_
  - [x] 2.2 Report a warning on badge write failure without changing exit code
    - _Requirements: 2.3_

- [x] 3. Add tests for thresholds and CLI behavior
  - Unit tests for green/yellow/red thresholds and file contents
  - CLI tests for presence and absence of `--badge`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2_

## Task Dependency Graph

```json
{
  "waves": [
    {"wave": 1, "tasks": ["1"]},
    {"wave": 2, "tasks": ["2", "2.1", "2.2"]},
    {"wave": 3, "tasks": ["3"]}
  ]
}
```

## Notes

- Originally a parser-validation fixture with tasks intentionally left
  unchecked; promoted to a real shipped feature (2026-07-26) once the spec
  proved out clean against the parser, implemented exactly as designed above.
