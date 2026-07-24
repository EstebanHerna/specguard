# Requirements Document

### Requirement 1: Historia en espanol

**Historia de Usuario:** Como usuario, quiero que la etiqueta en espanol funcione, para confiar en el parser.

#### Acceptance Criteria

1. WHEN a Spanish user story label is present THEN the parser SHALL extract it

### Requirement 2: Seccion de criterios vacia

**User Story:** As a user, I want an empty criteria section to be harmless, so that later requirements still parse.

#### Acceptance Criteria

### Requirement 3: Sin seccion de criterios

**User Story:** As a user, I want a missing criteria section to be harmless too, so that continuity is preserved.

Some prose with no Acceptance Criteria heading at all.

### Requirement 4: Requisito poblado tras los vacios

**User Story:** As a user, I want a populated requirement after empty ones, so that continuity is verified end to end.

#### Acceptance Criteria

1. WHEN prior requirements had no criteria THEN this requirement SHALL still parse correctly
2. WHEN this is the last requirement THEN its criteria SHALL be complete
