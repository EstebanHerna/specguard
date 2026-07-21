# Requirements Document

## Introduction

SpecGuard es una herramienta de auditoria de trazabilidad para equipos que usan
spec-driven development con Kiro. Compara los specs (.kiro/specs/) contra el
diff de git de un pull request y produce una matriz de trazabilidad con
veredictos accionables.

### Requirement 1: Parser de specs de Kiro

**User Story:** As a developer, I want SpecGuard to parse Kiro spec files, so that requirements, criteria and tasks become structured data.

#### Acceptance Criteria

1. WHEN a requirements.md file follows the Kiro format THEN the system SHALL extract each requirement with id, title, user story and acceptance criteria
2. WHEN a criterion uses EARS syntax (WHEN/IF/WHILE...THEN...SHALL) THEN the system SHALL capture it with a compound id (e.g. 1.2)
3. WHEN a tasks.md file contains checkbox items THEN the system SHALL extract each task with its done state and requirement references
4. IF headers are written in Spanish (Requisito N) THEN the system SHALL parse them equally

### Requirement 2: Parser de diffs de git

**User Story:** As a developer, I want SpecGuard to parse a git diff, so that changed files, hunks and defined symbols are available for matching.

#### Acceptance Criteria

1. WHEN a git reference is provided THEN the system SHALL obtain the unified diff via the git CLI
2. WHEN a diff contains added lines defining functions or classes THEN the system SHALL extract those symbol names for Python, JavaScript and TypeScript
3. WHEN a file is new or deleted THEN the system SHALL record its status accordingly

### Requirement 3: Motor de trazabilidad heuristico

**User Story:** As a developer, I want a deterministic matching engine, so that I get useful audit results without any LLM dependency.

#### Acceptance Criteria

1. WHEN requirements and changes are available THEN the system SHALL compute a coverage map from requirement ids to file paths
2. WHEN a requirement has no matching change THEN the system SHALL emit an uncovered_requirement finding
3. WHEN a task is marked done and no related code change exists THEN the system SHALL emit a phantom_task finding
4. WHEN a changed file matches no requirement THEN the system SHALL emit an orphan_code finding
5. WHEN a covered requirement has no associated test change THEN the system SHALL emit an untested_criterion finding
6. WHEN the audit completes THEN the system SHALL compute a traceability score as the percentage of covered requirements

### Requirement 4: Refinamiento semantico con Bedrock

**User Story:** As a developer, I want an optional LLM pass over the preliminary findings, so that semantic matches missed by heuristics are detected.

#### Acceptance Criteria

1. WHEN the --semantic flag is used THEN the system SHALL send requirements, tasks, truncated diff and preliminary findings to Amazon Bedrock
2. WHEN Bedrock returns a valid JSON array THEN the system SHALL replace the preliminary findings with the refined ones
3. IF the Bedrock call fails for any reason THEN the system SHALL fall back to the heuristic result without crashing

### Requirement 5: Reportes y CLI

**User Story:** As a developer, I want reports in multiple formats, so that I can consume the audit from terminal, CI and a dashboard.

#### Acceptance Criteria

1. WHEN an audit completes THEN the system SHALL write report.json and report.md to the output directory
2. WHEN the audit runs in a terminal THEN the system SHALL print a color-coded findings table and the traceability score
3. WHEN --fail-under is provided and the score is below the threshold THEN the system SHALL exit with code 1

### Requirement 6: Integracion con GitHub Actions

**User Story:** As a team, I want SpecGuard to run on every pull request, so that traceability is enforced automatically.

#### Acceptance Criteria

1. WHEN a pull request is opened or updated THEN the workflow SHALL run specguard audit against the base branch
2. WHEN the audit produces a markdown report THEN the workflow SHALL post it as a PR comment

### Requirement 7: Dashboard de trazabilidad

**User Story:** As a reviewer, I want a visual traceability matrix, so that I can inspect coverage at a glance.

#### Acceptance Criteria

1. WHEN report.json is available THEN the dashboard SHALL render the requirement/file matrix with a traffic-light color scheme
2. WHEN a finding exists THEN the dashboard SHALL list it grouped by verdict
3. WHEN the dashboard is deployed as static files THEN it SHALL work without any backend
