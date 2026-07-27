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

- [x] 9. Improve symbol extraction with language-aware parsing
  - tree-sitter for Python/JS/TS/TSX in parsers/symbols.py, wired into collect_changes with automatic fallback to the existing regex extractor when tree-sitter or the file is unavailable
  - Hunk now tracks real new-file line numbers (added_lines) so touched symbols are matched by line-range overlap, not just "was the def/class line itself added"
  - _Requirements: 2.2_

- [x] 10. Wire GitHub Action end to end
  - [x] 10.1 Composite action installs specguard and runs audit against base branch
    - _Requirements: 6.1_
  - [x] 10.2 Post report.md as sticky PR comment
    - Verified for real on PR #1 (github.com/EstebanHerna/specguard/pull/1): first-ever Action run in this repo, audit passed with --fail-under enforced, sticky comment posted
    - _Requirements: 6.2_

- [x] 11. Build dashboard traceability matrix
  - [x] 11.1 Render requirement/file matrix with traffic-light scheme from report.json
    - Live and verified: estebanherna.github.io/specguard
    - _Requirements: 7.1, 7.3_
  - [x] 11.2 Findings list grouped by verdict
    - _Requirements: 7.2_

- [x] 12. Deploy dashboard to S3 + CloudFront and engine to Lambda
  - Dashboard: deployed to GitHub Pages instead (gh-pages branch), not S3+CloudFront - see docs/architecture.md for why
  - Lambda + API Gateway + DynamoDB: deployed for real 2026-07-26 (stack `specguard-audit`, us-east-1) once AWS credentials became available. Verified end to end: POST to the live endpoint returns 200 with a full report, persisted in DynamoDB with its 7-day TTL. Two real bugs found only by actually deploying (invalid ThrottleSettings property, EDGE endpoint returning 403 via CloudFront) are documented in infra/README.md.
  - _Requirements: 7.3_

- [x] 13. Integration test: SpecGuard auditing its own repository
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

- Task numbering is preserved; completion states updated 2026-07-25 as tasks
  9, 10, 11 were implemented and verified (9: tests + self-audit; 10 and 11:
  additionally verified live, see task notes above).
- Task 12 is intentionally left partially unchecked: the AWS deployment half
  requires credentials this environment does not have. See the task note and
  infra/README.md.
- Task 8 validated against a real Kiro-generated spec on 2026-07-26
  (`.kiro/specs/kiro-format-check/`). Surfaced and fixed a hard-wrapped
  user-story limitation; see docs/kiro-workflow.md and
  `test_real_kiro_generated_spec_parses_without_loss`.
