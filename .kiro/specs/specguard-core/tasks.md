# Implementation Plan

## Overview

This plan preserves the existing SpecGuard implementation sequence while hardening task 8 against documented real-world Kiro spec variations.

## Tasks

- [x] 1. Set up project structure and packaging
  - pyproject.toml with hatchling, click, rich and optional extras
  - _Requirements: 5.2_

- [x] 2. Implement Kiro spec parser
  - [x] 2.1 Parse requirements.md with EARS criteria and Spanish header support
    - _Requirements: 1.1, 1.2, 1.4_
  - [x] 2.2 Parse tasks.md checkboxes with requirement references
    - _Requirements: 1.3_

- [x] 3. Implement git diff parser
  - [x] 3.1 Run git diff via subprocess and parse unified format
    - _Requirements: 2.1, 2.3_
  - [x] 3.2 Extract defined symbols from added lines
    - _Requirements: 2.2_

- [x] 4. Implement heuristic traceability engine
  - [x] 4.1 Tokenizer with snake_case and camelCase splitting
    - _Requirements: 3.1_
  - [x] 4.2 Coverage map and the five verdict detectors
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 5. Implement Bedrock semantic refinement with clean fallback
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 6. Implement JSON and Markdown reporters
  - _Requirements: 5.1_

- [x] 7. Implement CLI with audit command and fail-under gate
  - _Requirements: 5.2, 5.3_

- [x] 8. Harden spec parser against real-world Kiro spec variations
  - Parse `##` through `####` English `Requirement N` and Spanish `Requisito N` headings with or without colons, preserving document order and requirement-body boundaries
  - Parse numbered (`.` or `)`), `-`, and `*` acceptance-criteria entries in document order, both bold user-story labels, and empty or missing acceptance-criteria sections without interrupting later requirements
  - Parse complete arbitrary-depth dot-separated numeric task identifiers and map blank, `x`, and `X` checkbox states while preserving task document order
  - Preserve the public signatures of `parse_requirements`, `parse_tasks`, and `load_spec`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [ ] 9. Improve symbol extraction with language-aware parsing
  - Evaluate tree-sitter for Python and TypeScript
  - _Requirements: 2.2_

- [ ] 10. Wire GitHub Action end to end
  - [ ] 10.1 Composite action installs specguard and runs audit against base branch
    - _Requirements: 6.1_
  - [ ] 10.2 Post report.md as sticky PR comment
    - _Requirements: 6.2_

- [ ] 11. Build dashboard traceability matrix
  - [ ] 11.1 Render requirement/file matrix with traffic-light scheme from report.json
    - _Requirements: 7.1, 7.3_
  - [ ] 11.2 Findings list grouped by verdict
    - _Requirements: 7.2_

- [ ] 12. Deploy dashboard to S3 + CloudFront and engine to Lambda
  - _Requirements: 7.3_

- [ ] 13. Integration test: SpecGuard auditing its own repository
  - _Requirements: 3.6, 5.1_

## Task Dependency Graph

```json
{
  "waves": [
    {"wave": 1, "tasks": ["1"]},
    {"wave": 2, "tasks": ["2", "3"]},
    {"wave": 3, "tasks": ["4", "5", "6", "7"]},
    {"wave": 4, "tasks": ["8", "9", "10", "11"]},
    {"wave": 5, "tasks": ["12"]},
    {"wave": 6, "tasks": ["13"]}
  ]
}
```

## Notes

- Task numbering and completion states are preserved.
- Tasks 9 through 13 are unchanged.
