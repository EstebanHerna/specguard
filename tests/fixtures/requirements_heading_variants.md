# Requirements Document

## Introduction

Fixture: heading recognition variants (levels, language, colon, missing title, decoys).

## Requisito 1: Encabezado nivel dos con dos puntos

**User Story:** As a user, I want a level-two Spanish header with a colon, so that it is recognized.

#### Acceptance Criteria

1. WHEN this fixture is parsed THEN the parser SHALL recognize this header

### Not a requirement heading

This decoy heading and paragraph must stay inside Requirement 1 and must not
start a new requirement or leak a criterion into it.

### Requirement 2 Titulo sin dos puntos

**User Story:** As a user, I want a level-three English header without a colon, so that it still parses.

#### Acceptance Criteria

1. WHEN this fixture is parsed THEN the parser SHALL recognize a header without a colon

#### Requirement 3

No title was given after the id on purpose.

##### Acceptance Criteria

1. WHEN a requirement heading has no title THEN the parser SHALL fall back to a default title
