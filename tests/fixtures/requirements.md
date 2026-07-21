# Requirements Document

## Introduction

Feature de ejemplo para las pruebas del parser.

### Requirement 1: Parser de specs

**User Story:** As a developer, I want to parse Kiro requirement files, so that I can audit them.

#### Acceptance Criteria

1. WHEN a requirements.md file exists THEN the system SHALL extract every requirement with its id
2. WHEN a criterion uses EARS syntax THEN the system SHALL capture it with a compound id

### Requirement 2: Parser de tareas

**User Story:** As a developer, I want to parse task checkboxes, so that I can detect phantom tasks.

#### Acceptance Criteria

1. WHEN a task is marked with [x] THEN the system SHALL flag it as done
