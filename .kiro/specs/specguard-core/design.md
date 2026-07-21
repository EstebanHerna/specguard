# Design Document

## Overview

SpecGuard es un pipeline de cuatro etapas: parseo de specs, parseo de diff,
motor de matching y reporteria. La capa semantica (Bedrock) es un refinador
opcional entre el motor y la reporteria.

```
.kiro/specs/*  --> kiro_spec.py --\
                                   >--> heuristic.py --> [semantic.py] --> report/* --> CLI / CI / dashboard
git diff       --> git_diff.py  --/
```

## Components

### parsers/kiro_spec.py
Regex tolerantes al formato real de Kiro: headers `### Requirement N`,
user stories en negrita, criterios EARS numerados, checkboxes de tasks.md con
referencias `_Requirements: x.y_`. Soporta headers en espanol.

### parsers/git_diff.py
Ejecuta `git diff --unified=3 <ref>` via subprocess y parsea el unified diff a
FileChange/Hunk. Extrae simbolos definidos en lineas agregadas (def/class,
function, const/let, metodos) con una regex multipatron.

### engine/heuristic.py
Tokeniza requisitos y cambios (con split de snake_case y camelCase), calcula
solapamiento de tokens y construye la matriz de cobertura con un umbral
configurable. Deriva los cinco veredictos a partir de la matriz.

### engine/semantic.py
Prompt unico a Bedrock converse API con salida JSON estricta. Todo error se
captura y degrada al resultado heuristico (requisito 4.3). El modelo es
configurable por variable de entorno.

### report/
json_report.py serializa AuditReport completo (lo consume el dashboard).
markdown_report.py genera el reporte legible que se publica como comentario de PR.

### cli.py
Grupo click con el comando `audit`. Orquesta el pipeline y aplica --fail-under
como gate de CI.

## Data Model

AuditReport agrega Requirement, SpecTask, FileChange, Finding y la matriz de
cobertura. El score es una propiedad derivada, no un campo almacenado.

## Error Handling

- Spec sin requisitos: exit code 2 con mensaje claro.
- Fallo de git: exit code 2.
- Fallo de Bedrock: warning y fallback heuristico, exit code segun --fail-under.

## Testing Strategy

Unit tests por parser con fixtures de archivos reales de Kiro, tests del motor
con objetos construidos a mano, y un test de humo del CLI via CliRunner.
