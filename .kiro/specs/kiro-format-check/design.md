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

## Components and Interfaces

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

## Data Models

No se introduce ningun modelo nuevo. `write_badge` consume `AuditReport`
(existente en `models.py`) exclusivamente a traves de su propiedad publica
`score: float`; no lee ni depende de ningun otro campo del reporte. No hay
estado persistido: la funcion es pura entrada-a-archivo, sin retornar ni
mantener nada entre llamadas.

## Correctness Properties

Feature pequena y de umbrales fijos: se documentan como propiedades
informales en vez de Hypothesis, consistente con el alcance de
`Testing Strategy` mas abajo.

### Property 1: El umbral de color es total y mutuamente excluyente

For any `score` en `[0, 100]`, exactamente un color aplica: verde si
`score >= 90`, amarillo si `70 <= score < 90`, rojo si `score < 70`. No hay
huecos ni solapes en los limites 70 y 90.

**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: El flag `--badge` es la unica fuente de efecto secundario

For any ejecucion de `audit`, sin `--badge` ninguna llamada a `write_badge`
ocurre y `badge.svg` no se crea; con `--badge`, se llama exactamente una vez,
usando el mismo `AuditReport` ya calculado para los demas reportes.

**Validates: Requirements 2.1, 2.2**

### Property 3: Un fallo al escribir el badge no cambia el resultado de la auditoria

For any excepcion que `write_badge` levante, el codigo de salida deriva
unicamente de `--fail-under` contra el score; la excepcion se captura, se
reporta como warning, y el codigo de salida es identico al que hubiera sido
sin `--badge`.

**Validates: Requirements 2.3**

## Error Handling

- Si el directorio de salida no existe, se crea (igual que los reportes).
- Cualquier excepcion al escribir el badge se captura, se emite un warning y
  se preserva el codigo de salida de la auditoria.

## Testing Strategy

- Test unitario por cada umbral de color (verde/amarillo/rojo).
- Test de que el archivo se escribe y contiene el score.
- Test de la CLI: sin `--badge` no se crea `badge.svg`; con `--badge` si.
