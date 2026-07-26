# Stack tecnico

## Nucleo
- Python 3.10+, gestion con pyproject.toml (hatchling).
- CLI con click, salida de consola con rich.
- Sin dependencias pesadas obligatorias: parsers con regex y subprocess sobre git por defecto.

## Extraccion de simbolos (opcional, extra `treesitter`)
- tree-sitter + tree-sitter-python/-javascript/-typescript, activado automaticamente si esta
  instalado (incluido en el extra `dev`).
- Refina, nunca reemplaza obligatoriamente: si no esta instalado, el lenguaje no es soportado o el
  archivo no se puede leer, se conserva el resultado de regex sin error.
- Cruza el rango de lineas de cada definicion (funcion/clase/interfaz) contra las lineas
  realmente agregadas del diff (`Hunk.added_lines`), no solo si la linea de la firma fue agregada.

## Capa semantica (opcional)
- boto3 + Amazon Bedrock (API converse), modelo Claude Haiku por defecto.
- Debe degradar limpiamente: si Bedrock falla, el reporte heuristico se entrega igual.
- Modelo configurable via variable de entorno SPECGUARD_BEDROCK_MODEL.

## Precios de Kiro (verificado 2026-07-24)
- Confirmado y vigente en kiro.dev/pricing: usar Sonnet 4.6 cuesta 1.3x lo que cuesta Auto para
  la misma tarea. No hay multiplicador oficial publicado para Haiku ni Opus.
- El "5x vibe vs spec" que se manejaba antes ya no aplica: Kiro unifico el cobro en un solo pool
  de creditos "Auto" facturado por complejidad de tarea/uso de tokens (cambio de sept. 2025), no
  por categoria de sesion. No planificar el presupuesto de creditos asumiendo ese multiplicador.

## Distribucion
- GitHub Action compuesta (action.yml) que comenta el reporte en el PR. Valores de contexto de
  GitHub (`github.base_ref`, `github.action_path`, inputs) siempre via `env:`, nunca interpolados
  directo en `run:` (mitiga script injection).
- Dashboard estatico (dashboard/index.html) sin build step. Demo en vivo en GitHub Pages (rama
  `gh-pages`); tambien desplegable a S3 + CloudFront.
- `infra/` (SAM): Lambda + API Gateway + DynamoDB para exponer el motor como servicio. Codigo
  listo, no desplegado (requiere credenciales AWS propias) - ver infra/README.md.

## Comandos habituales
- Instalar en desarrollo: pip install -e ".[dev,semantic]"
- Tests: pytest
- Lint: ruff check src tests
- Auditoria local: specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1
