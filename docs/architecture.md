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
- `parsers/kiro_spec.py`: specs de Kiro (EARS + checkboxes) a datos estructurados via maquina de estados.
- `parsers/git_diff.py`: unified diff a FileChange, con numero de linea real por linea agregada (`Hunk.added_lines`).
- `parsers/symbols.py`: simbolos tocados por el diff via tree-sitter (Python/JS/TS/TSX) cuando esta disponible, con fallback automatico a regex si no lo esta o el lenguaje no es soportado.
- `engine/heuristic.py`: matriz de cobertura por solapamiento de tokens y deteccion de los cinco veredictos.
- `engine/semantic.py`: refinamiento con Claude via Bedrock converse API, con fallback total.
- `report/`: serializacion JSON (dashboard) y Markdown (PR, terminal).
- `cli.py`: comando `specguard audit` con gate `--fail-under` para CI.
- `infra/`: SAM (Lambda + API Gateway + DynamoDB) para exponer el motor como servicio - ver `infra/README.md`.

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
- tree-sitter como mejora, regex como piso: `parsers/git_diff.py` siempre extrae simbolos por regex primero (cero dependencias, funciona siempre); `collect_changes` intenta luego refinar con tree-sitter (extra `treesitter`) leyendo el archivo real del working tree y cruzando rangos de linea de cada definicion contra las lineas agregadas del diff. Si tree-sitter no esta instalado, el lenguaje no es soportado, o el archivo no se puede leer (por ejemplo borrado), se conserva el resultado de regex sin error.
- Dashboard estatico sin backend: report.json es el contrato. La demo del hackathon se sirve en GitHub Pages (rama `gh-pages`) en vez de S3+CloudFront, por el riesgo de que una cuenta AWS nueva reciba el "Free Plan" de 6 meses con auto-suspension (cambio de free tier de julio 2025) en vez del free tier clasico - GitHub Pages no depende de eso para sobrevivir la ventana de evaluacion.

## Infraestructura AWS (Fase 2 - desplegada y probada, 2026-07-26)

- `infra/template.yaml` (SAM): Lambda + API Gateway (REGIONAL) + DynamoDB, desplegado como stack `specguard-audit` en us-east-1. Endpoint real: `https://ble6qlnav0.execute-api.us-east-1.amazonaws.com/prod/audit`, probado de punta a punta (200 OK + persistencia en DynamoDB con TTL de 7 dias). Ver `infra/README.md` para prerequisitos, dos bugs reales encontrados al desplegar (MethodSettings, endpoint EDGE vs REGIONAL), limitaciones de seguridad conocidas (sin autenticacion, mitigado con throttling) y como reproducirlo.
- Bedrock: capa semantica opcional (`engine/semantic.py`), ya integrada en el CLI via `--semantic`.
- S3 + CloudFront: se evaluo para el dashboard estatico pero se prefirio GitHub Pages para la demo real (ver decision arriba); queda como alternativa documentada, no como plan activo.

Todo pensado para caber en la capa gratuita.
