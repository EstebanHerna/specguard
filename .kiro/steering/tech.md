# Stack tecnico

## Nucleo
- Python 3.10+, gestion con pyproject.toml (hatchling).
- CLI con click, salida de consola con rich.
- Sin dependencias pesadas en el nucleo: parsers con regex y subprocess sobre git.

## Capa semantica (opcional)
- boto3 + Amazon Bedrock (API converse), modelo Claude Haiku por defecto.
- Debe degradar limpiamente: si Bedrock falla, el reporte heuristico se entrega igual.
- Modelo configurable via variable de entorno SPECGUARD_BEDROCK_MODEL.

## Distribucion
- GitHub Action compuesta (action.yml) que comenta el reporte en el PR.
- Dashboard estatico (dashboard/index.html) sin build step, desplegable a S3 + CloudFront.

## Comandos habituales
- Instalar en desarrollo: pip install -e ".[dev,semantic]"
- Tests: pytest
- Lint: ruff check src tests
- Auditoria local: specguard audit --spec .kiro/specs/specguard-core --diff HEAD~1
