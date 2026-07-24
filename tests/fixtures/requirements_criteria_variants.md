# Requirements Document

### Requirement 1: Formatos de criterio mixtos

**User Story:** As a user, I want mixed criteria markers, so that all common Kiro formats parse.

Before the criteria section, a decoy list must be ignored:
- This bullet is outside Acceptance Criteria and must not become a criterion
- Neither must this one

#### Acceptance Criteria

1.   WHEN extra whitespace surrounds a numbered entry THEN it SHALL still be trimmed
2) WHEN a criterion uses a closing parenthesis THEN it SHALL be recognized
- WHEN a criterion uses a dash bullet THEN it SHALL be recognized
* WHEN a criterion uses an asterisk bullet THEN it SHALL be recognized

##### Notes

This subsection is deeper than the criteria heading, so it stays inside the
section, but this plain paragraph must not become a criterion.

### Requirement 2: Seccion de criterios cerrada por subtitulo

**User Story:** As a user, I want a shallower heading to close the section, so that trailing content is not miscounted.

#### Acceptance Criteria

1. WHEN this criterion is parsed THEN it SHALL be the only one recorded

#### Out of criteria now

- This bullet lives after the criteria section closed and must not be counted
