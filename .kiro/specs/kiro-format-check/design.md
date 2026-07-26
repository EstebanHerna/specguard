# Design Document

## Overview

El `Badge_Generator` es un modulo pequeno y puro que traduce un `Report`
existente a un archivo SVG estatico. No introduce dependencias: construye el
SVG por interpolacion de cadenas. Se conecta a la CLI detras de un flag
opcional para no alterar el comportamiento por defecto.

## Architecture

```
report.json --> Report (modelo existente) --> write_badge() --> badge.svg
                                                   ^
                                          CLI --badge (opcional)
```

## Components

### Badge_Generator (`src/specguard/report/badge.py`)

- `write_badge(report: Report, path: Path) -> None`: elige color por umbral
  (verde >=90, amarillo >=70, rojo <70) y escribe el SVG.
- El texto del score se escapa antes de interpolarse en el SVG para evitar
  inyeccion, aunque el score sea numerico por construccion.

### CLI wiring (`src/specguard/cli.py`)

- Nuevo flag `--badge` en el comando `audit`.
- Cuando esta presente, tras escribir los reportes se llama a `write_badge`.
- Un fallo al escribir el badge se reporta como warning y no cambia el codigo
  de salida derivado de `--fail-under`.

## Error Handling

- Si el directorio de salida no existe, se crea (igual que los reportes).
- Cualquier excepcion al escribir el badge se captura, se emite un warning y
  se preserva el codigo de salida de la auditoria.

## Testing Strategy

- Test unitario por cada umbral de color (verde/amarillo/rojo).
- Test de que el archivo se escribe y contiene el score.
- Test de la CLI: sin `--badge` no se crea `badge.svg`; con `--badge` si.
