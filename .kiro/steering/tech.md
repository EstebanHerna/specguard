# Stack tecnico

## Nucleo
- Python 3.10+, gestion con pyproject.toml (hatchling).
- CLI con click, salida de consola con rich.
- Sin dependencias pesadas en el nucleo: parsers con regex y subprocess sobre git.

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
- GitHub Action compuesta (action.yml) que comenta el reporte en el PR.
- Dashboard estatico (dashboard/index.html) sin build step, desplegable a S3 + CloudFront.

## Comandos habituales
- Instalar en desarrollo: pip install -e ".[dev,semantic]"
- Tests: pytest
- Lint: ruff check src tests
- Auditoria local: specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1
