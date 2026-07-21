# Arquitectura de SpecGuard

## Vision general

```
                +---------------------+
.kiro/specs --> | parsers/kiro_spec   |--+
                +---------------------+  |   +--------------------+     +--------------------+
                                         +-->| engine/heuristic   |---->| engine/semantic    |
                +---------------------+  |   | (deterministico)   |     | (Bedrock, opcional)|
git diff    --> | parsers/git_diff    |--+   +--------------------+     +--------------------+
                +---------------------+               |                          |
                                                      v                          v
                                             +----------------+        +-----------------+
                                             | report/json    |        | report/markdown |
                                             +----------------+        +-----------------+
                                                      |                          |
                                                      v                          v
                                             dashboard (S3/CF)          comentario en PR
```

## Modulos

- `models.py`: dataclasses del dominio (Requirement, SpecTask, FileChange, Finding, AuditReport) y el enum Verdict.
- `parsers/kiro_spec.py`: specs de Kiro (EARS + checkboxes) a datos estructurados.
- `parsers/git_diff.py`: unified diff a FileChange con simbolos extraidos.
- `engine/heuristic.py`: matriz de cobertura por solapamiento de tokens y deteccion de los cinco veredictos.
- `engine/semantic.py`: refinamiento con Claude via Bedrock converse API, con fallback total.
- `report/`: serializacion JSON (dashboard) y Markdown (PR, terminal).
- `cli.py`: comando `specguard audit` con gate `--fail-under` para CI.

## Los cinco veredictos

| Veredicto | Significado |
|---|---|
| covered | Requisito con evidencia de implementacion en el diff |
| uncovered_requirement | Requisito sin ningun cambio que lo implemente |
| phantom_task | Tarea marcada [x] sin cambio de codigo asociado |
| orphan_code | Archivo modificado sin requisito que lo respalde |
| untested_criterion | Requisito cubierto sin test que lo valide |

## Decisiones

- Heuristica primero, LLM despues: la herramienta da senal util sin credenciales AWS y nunca se cae por un fallo del modelo.
- Regex sobre tree-sitter en v0.1: cero dependencias nativas; tree-sitter queda como tarea 9 del spec.
- Dashboard estatico sin backend: report.json es el contrato; el despliegue es un bucket S3.

## Infraestructura objetivo (AWS)

- S3 + CloudFront: dashboard estatico.
- Lambda + API Gateway: ejecucion del motor para repos remotos (fase 2).
- DynamoDB: historico de reportes por repo/PR (fase 2).
- Bedrock: capa semantica.

Todo dentro de la capa gratuita para sobrevivir la ventana de evaluacion de 7 dias.
