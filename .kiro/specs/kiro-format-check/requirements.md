# Requirements Document

## Introduction

Esta feature agrega un badge SVG de score de trazabilidad que el equipo puede
embeber en el README. El badge se genera a partir del `report.json` que ya
produce SpecGuard, sin dependencias nuevas. Este spec fue generado con Kiro
para validar que el parser de SpecGuard lee correctamente un spec real de Kiro
(no solo las fixtures escritas a mano).

## Glossary

- **Badge_Generator**: The SpecGuard component that renders an SVG traceability badge from a report.
- **Traceability_Score**: The percentage of parsed requirements that have at least one matching changed file.
- **SpecGuard_CLI**: The SpecGuard command-line interface.
- **Report**: The structured audit result model produced by the engine.

## Requirements

### Requirement 1: Generacion del badge SVG

**User Story:** As a maintainer, I want SpecGuard to emit an SVG traceability
badge, so that the current score is visible directly in the README.

#### Acceptance Criteria

1. WHEN an audit produces a `report.json` with a Traceability_Score, THE Badge_Generator SHALL write a `badge.svg` file to the configured output directory.
2. WHEN the Traceability_Score is at or above 90, THE Badge_Generator SHALL render the badge with a green fill.
3. WHEN the Traceability_Score is below 90 and at or above 70, THE Badge_Generator SHALL render the badge with a yellow fill.
4. WHEN the Traceability_Score is below 70, THE Badge_Generator SHALL render the badge with a red fill.
5. THE Badge_Generator SHALL preserve `write_badge(report: Report, path: Path) -> None` as a public signature.

### Requirement 2: Integracion opcional en la CLI

**User Story:** As a developer, I want the badge emitted only when I ask for it, so that existing audit runs are unaffected by default.

#### Acceptance Criteria

1. WHERE the `--badge` flag is provided, WHEN an audit completes, THE SpecGuard_CLI SHALL invoke the Badge_Generator for the completed report.
2. IF the `--badge` flag is not provided, THEN THE SpecGuard_CLI SHALL NOT write a `badge.svg` file.
3. WHEN the Badge_Generator fails to write the badge, THE SpecGuard_CLI SHALL report a warning and exit with the audit's own exit code.
