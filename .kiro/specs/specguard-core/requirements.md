# Requirements Document

## Introduction

SpecGuard es una herramienta de auditoria de trazabilidad para equipos que usan
spec-driven development con Kiro. Compara los specs (`.kiro/specs/`) contra el
diff de git de un pull request y produce una matriz de trazabilidad con
veredictos accionables.

## Glossary

- **Kiro_Spec_Parser**: The SpecGuard component that loads and parses Kiro `requirements.md` and `tasks.md` files.
- **Requirement_Body**: The content after a recognized requirement heading and before the next recognized requirement heading or the end of the document.
- **Acceptance_Criteria_Section**: The portion of a Requirement_Body introduced by an acceptance-criteria heading.
- **Acceptance_Criterion**: A numbered or bulleted list entry in an Acceptance_Criteria_Section.
- **Task_ID**: A numeric task identifier composed of one or more dot-separated segments, with each segment containing one or more digits.
- **Checkbox_State**: A task checkbox containing a space for incomplete, or `x` or `X` for complete.
- **Public_API**: A callable interface that external SpecGuard consumers can import and invoke.
- **Path**: The `pathlib.Path` type accepted by the parser interfaces.
- **Requirement**: The structured requirement model returned by the parser.
- **SpecTask**: The structured task model returned by the parser.
- **Git_Diff_Parser**: The SpecGuard component that obtains and parses unified git diffs.
- **Traceability_Engine**: The deterministic SpecGuard component that matches requirements, tasks, and changed files.
- **Semantic_Refiner**: The optional SpecGuard component that refines heuristic findings through Amazon Bedrock.
- **Reporting_System**: The SpecGuard component that writes audit reports.
- **SpecGuard_CLI**: The SpecGuard command-line interface.
- **GitHub_Actions_Workflow**: The pull-request workflow that runs SpecGuard.
- **Dashboard**: The static SpecGuard traceability report viewer.
- **Finding**: An actionable audit result associated with a requirement, task, or changed file.
- **Heuristic_Result**: The findings produced by the Traceability_Engine before semantic refinement.
- **Traceability_Score**: The percentage of parsed requirements that have at least one matching changed file.

## Requirements

### Requirement 1: Parser de specs de Kiro

**User Story:** As a developer, I want SpecGuard to parse real-world Kiro spec variations, so that requirements, acceptance criteria, user stories, and tasks become structured data without breaking existing integrations.

#### Acceptance Criteria

1. WHEN a `requirements.md` heading at level `##`, `###`, or `####` starts with English `Requirement N` or Spanish `Requisito N`, with or without a colon after the numeric identifier `N`, THE Kiro_Spec_Parser SHALL extract `N`, trim surrounding whitespace from a title when a title is present, and associate the Requirement_Body with the parsed Requirement.
2. WHEN a `requirements.md` file contains multiple recognized requirement headings, THE Kiro_Spec_Parser SHALL return the parsed Requirement objects in document order and delimit each Requirement_Body at the next recognized requirement heading or the end of the document.
3. WHEN an Acceptance_Criteria_Section contains entries marked by a numeric identifier followed by `.` or `)`, `-`, or `*`, THE Kiro_Spec_Parser SHALL extract the trimmed Acceptance_Criterion text in document order.
4. WHEN a Requirement_Body contains the bold label `**User Story:**` or `**Historia de Usuario:**`, THE Kiro_Spec_Parser SHALL extract the trimmed text following the label as the user story.
5. IF a Requirement_Body has no Acceptance_Criteria_Section or the Acceptance_Criteria_Section has no list entries, THEN THE Kiro_Spec_Parser SHALL return the Requirement with an empty acceptance-criteria collection and continue parsing subsequent recognized requirements.
6. WHEN a `tasks.md` file contains a task with a Checkbox_State and a Task_ID of arbitrary segment depth, THE Kiro_Spec_Parser SHALL extract the complete Task_ID, map a space to incomplete, map `x` or `X` to complete, and return parsed SpecTask objects in document order.
7. THE Kiro_Spec_Parser SHALL preserve `parse_requirements(path: Path) -> list[Requirement]` as a Public_API signature.
8. THE Kiro_Spec_Parser SHALL preserve `parse_tasks(path: Path) -> list[SpecTask]` as a Public_API signature.
9. THE Kiro_Spec_Parser SHALL preserve `load_spec(spec_dir: Path) -> tuple[list[Requirement], list[SpecTask]]` as a Public_API signature.

### Requirement 2: Parser de diffs de git

**User Story:** As a developer, I want SpecGuard to parse a git diff, so that changed files, hunks and defined symbols are available for matching.

#### Acceptance Criteria

1. WHEN a git reference is provided, THE Git_Diff_Parser SHALL obtain the unified diff through the git CLI.
2. WHEN a unified diff contains an added line that defines a function or class in Python, JavaScript, or TypeScript, THE Git_Diff_Parser SHALL extract the defined symbol name.
3. WHEN a unified diff identifies a file as new or deleted, THE Git_Diff_Parser SHALL record the corresponding file status.

### Requirement 3: Motor de trazabilidad heuristico

**User Story:** As a developer, I want a deterministic matching engine, so that I get useful audit results without any LLM dependency.

#### Acceptance Criteria

1. WHEN parsed requirements and changed files are available, THE Traceability_Engine SHALL compute a coverage map from each requirement identifier to matching changed-file paths.
2. WHEN a parsed requirement has no matching changed file, THE Traceability_Engine SHALL emit an `uncovered_requirement` Finding for the requirement identifier.
3. WHEN a parsed task is marked complete and has no related changed file, THE Traceability_Engine SHALL emit a `phantom_task` Finding for the Task_ID.
4. WHEN a changed file matches no parsed requirement, THE Traceability_Engine SHALL emit an `orphan_code` Finding for the changed-file path.
5. WHEN a covered requirement has no associated changed test file, THE Traceability_Engine SHALL emit an `untested_criterion` Finding for the requirement identifier.
6. WHEN a heuristic audit completes, THE Traceability_Engine SHALL compute the Traceability_Score.

### Requirement 4: Refinamiento semantico con Bedrock

**User Story:** As a developer, I want an optional LLM pass over the preliminary findings, so that semantic matches missed by heuristics are detected.

#### Acceptance Criteria

1. WHERE semantic refinement is enabled, WHEN a Heuristic_Result is available, THE Semantic_Refiner SHALL send the parsed requirements, parsed tasks, truncated unified diff, and Heuristic_Result to Amazon Bedrock.
2. WHEN Amazon Bedrock returns a valid JSON array of findings, THE Semantic_Refiner SHALL replace the findings in the Heuristic_Result with the returned findings.
3. IF the Amazon Bedrock call or response processing fails, THEN THE Semantic_Refiner SHALL return the Heuristic_Result and allow report generation to complete.

### Requirement 5: Reportes y CLI

**User Story:** As a developer, I want reports in multiple formats, so that I can consume the audit from terminal, CI and a dashboard.

#### Acceptance Criteria

1. WHEN an audit completes, THE Reporting_System SHALL write `report.json` and `report.md` to the configured output directory.
2. WHEN an audit runs in a terminal, THE SpecGuard_CLI SHALL print a color-coded findings table and the Traceability_Score.
3. WHERE `--fail-under` is provided, WHEN the Traceability_Score is below the provided threshold, THE SpecGuard_CLI SHALL exit with code `1`.

### Requirement 6: Integracion con GitHub Actions

**User Story:** As a team, I want SpecGuard to run on every pull request, so that traceability is enforced automatically.

#### Acceptance Criteria

1. WHEN a pull request is opened or updated, THE GitHub_Actions_Workflow SHALL run a SpecGuard audit against the pull request base branch.
2. WHEN a SpecGuard audit produces a Markdown report, THE GitHub_Actions_Workflow SHALL post the Markdown report as a pull-request comment.

### Requirement 7: Dashboard de trazabilidad

**User Story:** As a reviewer, I want a visual traceability matrix, so that I can inspect coverage at a glance.

#### Acceptance Criteria

1. WHEN `report.json` is available, THE Dashboard SHALL render the requirement-to-file matrix with a traffic-light color scheme.
2. WHEN `report.json` contains findings, THE Dashboard SHALL list the findings grouped by verdict.
3. WHERE the Dashboard is deployed as static files, THE Dashboard SHALL load and render the traceability report using static client-side resources.
