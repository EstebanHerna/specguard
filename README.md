# SpecGuard

Audita si tu codigo realmente implementa tu spec de Kiro.

Reto: **Productividad para desarrolladores** - Hackathon Kiro, Codigo Facilito + AWS.

## El problema

En el desarrollo guiado por agentes, el cuello de botella dejo de ser escribir
codigo: es verificarlo. Kiro genera specs estructurados (requisitos, diseno,
tareas) y luego implementa a partir de ellos, pero nadie verifica que el codigo
resultante cumpla lo que el spec promete. El agente marca la tarea como
completa y el humano confia.

## La solucion

SpecGuard compara el spec (`.kiro/specs/`) contra el diff de git de un pull
request y produce una matriz de trazabilidad con cinco veredictos:

| Veredicto | Significado |
|---|---|
| `covered` | Requisito con evidencia de implementacion en el diff |
| `uncovered_requirement` | Requisito sin ningun cambio que lo implemente |
| `phantom_task` | Tarea marcada `[x]` sin cambio de codigo asociado |
| `orphan_code` | Archivo modificado sin requisito que lo respalde |
| `untested_criterion` | Requisito cubierto sin test que lo valide |

El motor heuristico es deterministico y funciona sin LLM. Con `--semantic`,
Amazon Bedrock (Claude) refina los hallazgos; si Bedrock falla, el resultado
heuristico se entrega igual.

## Instalacion

```bash
pip install -e ".[dev]"           # nucleo + tests
pip install -e ".[dev,semantic]"  # + capa Bedrock
```

## Uso

```bash
specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1
specguard audit --spec .kiro/specs/specguard-core --diff main...feature --semantic
specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1 --fail-under 70
```

Salidas: tabla en terminal, `reports/report.json` y `reports/report.md`.

### Dashboard

```bash
specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1 -o dashboard
python -m http.server -d dashboard 8080
```

Estatico, sin backend: desplegable tal cual a S3 + CloudFront.

### GitHub Action

El workflow en `.github/workflows/specguard.yml` corre la auditoria en cada PR
y publica el reporte como comentario. Tambien puede consumirse como action
compuesta desde otros repos (`action.yml`).

## Dogfooding

Este repositorio se audita a si mismo: el spec del producto vive en
`.kiro/specs/specguard-core/`, las convenciones en `.kiro/steering/`, y un hook
de Kiro reejecuta la auditoria cada vez que se guarda `tasks.md`. La
metodologia de trabajo con Kiro esta documentada en `docs/kiro-workflow.md`.

## Arquitectura

Ver `docs/architecture.md`. Resumen: parsers (spec y diff) -> motor heuristico
-> refinamiento Bedrock opcional -> reportes JSON/Markdown -> CLI, CI y dashboard.

## Tests

```bash
pytest
ruff check src tests
```

## Licencia

MIT
