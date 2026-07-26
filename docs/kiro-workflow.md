# Flujo de trabajo con Kiro en SpecGuard

Este documento define como el equipo usa Kiro para construir SpecGuard,
aplicando los fundamentos de desarrollo agentico vistos en el bootcamp de
Codigo Facilito + AWS. Es la referencia operativa del equipo: cualquier sesion
con Kiro debe respetar lo que aqui se establece.

## Principio rector

Pensar primero, promptear despues. El agente amplifica al desarrollador, no lo
reemplaza. Todo cambio propuesto por Kiro se revisa en la vista de diff antes
de aceptarse, se valida su seguridad y se puede interrumpir o revertir. El
control humano no se delega.

## Las dos modalidades y cuando usamos cada una

### Vibe coding session (chat libre)
Para prototipos rapidos, consultas conceptuales y codigo inmediato. En este
proyecto la usamos para: explorar APIs, ajustar el dashboard, iterar estilos,
debuggear errores puntuales. Riesgo conocido: perdida de contexto en sesiones
largas; se mitiga con los archivos de steering.

### Spec-driven development
Para todo lo que toca el nucleo del producto. Flujo secuencial
Requisitos -> Diseno -> Tareas, materializado en `.kiro/specs/specguard-core/`.
El agente ejecuta las tareas del plan paso a paso y nosotros validamos cada una.
Regla del equipo: ninguna feature del motor entra sin pasar por el spec.

## Los cuatro pilares en este repositorio

| Pilar | Ubicacion | Uso en SpecGuard |
|---|---|---|
| Specs | `.kiro/specs/specguard-core/` | Requisitos EARS, diseno y plan de tareas del producto |
| Steering | `.kiro/steering/` | Producto, stack y convenciones; se inyectan en cada interaccion |
| Hooks | `.kiro/hooks/` | Auditoria automatica al guardar tasks.md (dogfooding) |
| MCP | configuracion local | Documentacion oficial de AWS (Bedrock, Lambda) como fuente de verdad para evitar alucinaciones |

## Seleccion de modelo y esfuerzo

- Auto para el trabajo diario: Kiro selecciona el modelo segun la intencion del prompt y optimiza consumo.
- Sonnet solo para tareas de diseno o refactors donde Auto se quede corto (cuesta 1.3x).
- Effort Low/Medium por defecto; High o Max unicamente en problemas de arquitectura.
- Supervised como modo de ejecucion por defecto; Autopilot solo en tareas mecanicas de bajo riesgo (renombres, fixtures, boilerplate).

## Presupuesto de creditos (2000 por integrante)

Actualizacion verificada 2026-07-24: el multiplicador "5x vibe vs spec" que se asumia aqui ya no
es como Kiro factura. Desde el cambio a precios "Auto" (sept. 2025), todo el consumo sale de un
solo pool de creditos tasado por complejidad de tarea y uso de tokens, no por si la sesion es vibe
o spec. El unico multiplicador oficial vigente es el de modelo: Sonnet 4.6 cuesta 1.3x lo que Auto
para la misma tarea (ver `.kiro/steering/tech.md`). Estrategia actualizada:

1. Usar Auto por defecto para casi todo; es la palanca de ahorro real hoy, no el modo de sesion.
2. Reservar Sonnet 4.6 para las tareas de diseno/arquitectura donde Auto se quede corto (tarea 8
   ya se beneficio de esto).
3. Reservar un margen minimo del 15% para la recta final (video, fixes de demo).

## Reglas de prompting del equipo

- Rol asignado, contexto explicito, stack definido y restricciones de salida en cada prompt.
- Pedir el codigo en ingles: reduce consumo de tokens.
- Nada de PDFs ni archivos densos al chat: convertir antes a Markdown plano.
- Avanzar en pasos pequenos; nunca pedir estructuras masivas en un solo prompt.
- No repetir instrucciones que ya viven en steering: si algo se repite dos veces, va a un archivo de steering.

## Ciclo de trabajo por tarea

1. Abrir la tarea en `.kiro/specs/specguard-core/tasks.md`.
2. Ejecutarla con Kiro en modo spec (Supervised).
3. Revisar el diff completo antes de aceptar.
4. Correr `pytest` y `specguard audit --spec .kiro/specs/specguard-core --diff HEAD`.
5. Solo entonces marcar la tarea como completa y commitear referenciando la tarea.

El paso 4 es el corazon del proyecto: SpecGuard se audita a si mismo. Si la
herramienta detecta una tarea fantasma en nuestro propio repo, el commit no sale.

## Pendiente: validar fixtures contra specs reales de Kiro

Las fixtures de la tarea 8 (`tests/fixtures/requirements_*.md`,
`tasks_nested_ids_states.md`) fueron escritas a mano para cubrir la gramatica
descrita en el design doc, no generadas por Kiro. Un agente de codigo sin
acceso a Kiro (como el que escribio este parser) no puede generarlas de
verdad - esto requiere abrir Kiro y usarlo. Antes de dar la tarea 8 por
completamente validada:

1. En Kiro, crear un spec nuevo para una mini-feature de prueba (`.kiro/specs/kiro-format-check/`)
   con requisitos, criterios e historias de usuario reales.
2. Correr `specguard audit` contra ese spec real (o simplemente `parse_requirements`/`parse_tasks`
   sobre sus `requirements.md`/`tasks.md`) y confirmar que el parser los lee sin perder criterios
   ni corromper campos - el mismo tipo de bug que ya encontramos una vez en nuestro propio spec.
3. Si el formato real de Kiro difiere de lo asumido aqui, agregar esa variante como fixture nueva
   y ajustar el parser.
4. Borrar el spec de prueba o dejarlo como fixture adicional, segun convenga.
