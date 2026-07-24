# Design Document

## Overview

SpecGuard es un pipeline de cuatro etapas: parseo de specs, parseo de diff,
motor de matching y reporteria. La capa semantica (Bedrock) es un refinador
opcional entre el motor y la reporteria.

El endurecimiento de la tarea 8 se limita a `parsers/kiro_spec.py` y sus pruebas.
La inspeccion del parser y de los fixtures actuales muestra que conviene conservar
el parseo lineal con regex, pero separar reconocimiento, limites y extraccion en
estados explicitos. No se agregan dependencias al nucleo y se mantiene Python 3.10+.

## Architecture

```
.kiro/specs/*  --> kiro_spec.py --\
                                   >--> heuristic.py --> [semantic.py] --> report/* --> CLI / CI / dashboard
git diff       --> git_diff.py  --/
```

La arquitectura y el flujo de datos no cambian. `kiro_spec.py` sigue siendo un
adaptador sin estado externo: lee Markdown, produce modelos existentes y no conoce
el motor, los reportes ni la CLI. Sus helpers nuevos seran privados y el modulo se
mantendra por debajo de 300 lineas.

## Components and Interfaces

### parsers/kiro_spec.py

#### API publica preservada

La implementacion mantiene exactamente estas firmas y tipos de retorno:

```python
def parse_requirements(path: Path) -> list[Requirement]: ...
def parse_tasks(path: Path) -> list[SpecTask]: ...
def load_spec(spec_dir: Path) -> tuple[list[Requirement], list[SpecTask]]: ...
```

`load_spec` conserva su composicion actual: busca `requirements.md` y `tasks.md`,
devuelve una lista vacia por cada archivo ausente y delega en los dos parsers. Las
regex compiladas y los helpers de segmentacion permanecen internos; no se expone
una clase ni una API nueva.

#### Parseo de requisitos por regex y estados

`parse_requirements` lee UTF-8 una vez, usa `splitlines()` y hace dos pasadas
lineales. La primera reconoce limites de cuerpos y la segunda extrae campos de cada
cuerpo. La regex de encabezado, anclada a la linea completa y con `re.IGNORECASE`,
nace del siguiente esquema:

```text
^(?P<level>#{2,4})(?!#)[ \t]+(?:Requirement|Requisito)[ \t]+
(?P<id>\d+)(?=$|[ \t]|:)(?:[ \t]*:[ \t]*|[ \t]+)?
(?P<title>.*?)[ \t]*$
```

El esquema acepta solo niveles `##`, `###` y `####`, etiquetas inglesas o
espanolas y dos formas despues del ID: `N: titulo` y `N titulo`, ademas de un
encabezado sin titulo. El ID se conserva como texto numerico; el titulo se recorta.
Si queda vacio se usa el fallback estable `Requirement <id>` para conservar el
contrato del modelo actual.

Cada coincidencia abre un `Requirement_Body`. Su inicio es la linea siguiente y su
fin es la siguiente linea que coincida con la misma regex de requisito, o EOF. Un
encabezado Markdown no reconocido permanece dentro del cuerpo y no crea ni corta
requisitos. Los segmentos se procesan en el orden de sus offsets, por lo que los
`Requirement` resultantes conservan estrictamente el orden documental.

Dentro de cada cuerpo se usa el estado `OUTSIDE_CRITERIA` o `IN_CRITERIA`. Un
encabezado Markdown `#{1,6}` cuyo texto sea `Acceptance Criteria` o
`Criterios de Aceptacion`/`Criterios de Aceptación`, con colon opcional y sin
importar mayusculas, entra en `IN_CRITERIA` y registra su nivel. Otro encabezado de
nivel igual o menor sale de la seccion; uno mas profundo se considera contenido de
la seccion. El limite del `Requirement_Body` siempre termina ambos estados.

Solo en `IN_CRITERIA` se aplica una regex de entrada equivalente a:

```text
^[ \t]*(?:(?P<number>\d+)[.)]|[-*])[ \t]+(?P<text>\S.*?)\s*$
```

Esto admite `1.`, `1)`, `-` y `*`, ignora listas de introduccion, historia o notas
fuera de la seccion, recorta el texto y conserva el orden de aparicion. Cada
criterio recibe un ID estable `<requirement-id>.<ordinal>` segun su posicion
aceptada en el cuerpo; asi los bullets y listas mixtas son univocos aunque la
numeracion fuente este repetida o salte valores. Las lineas no marcadas dentro de
la seccion no generan criterios.

La historia se busca en todo el cuerpo, independientemente del estado de criterios,
con una regex anclada que reconoce `**User Story:**` y
`**Historia de Usuario:**` (colon opcional dentro de la negrita). Se toma la
primera etiqueta reconocida y se recorta el texto posterior; si no existe o esta
vacio, `user_story` conserva `""`.

Un cuerpo sin encabezado de criterios nunca entra en `IN_CRITERIA`; una seccion
vacia nunca produce entradas. En ambos casos se devuelve el requisito con
`criteria=[]` y el procesamiento continua desde el siguiente segmento ya
delimitado, evitando que contenido de un requisito contamine al siguiente.

#### Parseo de tareas por regex y estados

`parse_tasks` recorre `tasks.md` una vez y reconoce solo lineas de tarea con el
esquema:

```text
^[ \t]*-[ \t]+\[(?P<state>[ xX])\][ \t]+
(?P<id>\d+(?:\.\d+)*)(?:\.)?[ \t]+(?P<text>.*?)\s*$
```

El grupo de ID captura la secuencia completa antes del punto separador opcional;
por ello `8`, `8.1` y `8.1.2.3` son validos sin imponer profundidad maxima. No se
generan IDs sinteticos para lineas sin ID. Un espacio mapea a `done=False`; `x` y
`X` mapean a `done=True`; otros caracteres de checkbox no son tareas validas. Los
objetos se agregan al coincidir, preservando el orden documental.

Despues de una tarea reconocida, el estado `CURRENT_TASK` permite buscar la
referencia `_Requirements: ..._` en sus lineas subordinadas hasta la siguiente
linea de tarea. Se conserva la extraccion actual de referencias separadas por
coma. La deteccion de estado e ID ocurre solo en la linea principal y no cambia el
contrato de `SpecTask`.

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

## Data Models

No cambia ningun modelo publico. `Requirement` mantiene `id`, `title`,
`user_story` y `criteria`; `AcceptanceCriterion` mantiene `id` y `text`; y
`SpecTask` mantiene `id`, `text`, `done` y `requirement_refs`. El parser normaliza
solo whitespace de bordes y estado de checkbox, sin retener sintaxis Markdown, por
lo que es deliberadamente lossy.

AuditReport agrega Requirement, SpecTask, FileChange, Finding y la matriz de
cobertura. El score es una propiedad derivada, no un campo almacenado.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

La reflexion de propiedades consolida encabezados con segmentacion porque ambos se
verifican sobre la misma secuencia ordenada, y consolida marcadores con secciones
vacias porque ambos dependen del estado de criterios. La historia y las tareas se
mantienen separadas: tienen gramaticas y salidas independientes. Las firmas
publicas son checks de compatibilidad, no propiedades aleatorias.

### Property 1: Reconocimiento, orden y aislamiento de requisitos

For any documento generado con cero o mas bloques cuyos encabezados reconocidos
varien en nivel `##`-`####`, idioma, colon, whitespace, ID y titulo, intercalados
con encabezados no reconocidos y contenido arbitrario, `parse_requirements` debe
devolver exactamente un requisito por encabezado reconocido, con ID y titulo
normalizados, en el mismo orden, y sin usar contenido posterior al siguiente
encabezado reconocido para completar el bloque anterior.

**Validates: Requirements 1.1, 1.2**

### Property 2: Criterios confinados a su seccion

For any secuencia generada de cuerpos de requisito con secciones de criterios
pobladas, vacias o ausentes, la lista resultante debe contener exactamente los
textos recortados de las entradas `N.`, `N)`, `-` y `*` encontradas mientras el
estado esta dentro de la seccion, en orden documental; entradas con la misma forma
fuera de ella no deben aparecer y una seccion vacia o ausente no debe afectar a
requisitos posteriores.

**Validates: Requirements 1.3, 1.5**

### Property 3: Extraccion bilingue de historia de usuario

For any cuerpo de requisito generado que contenga una etiqueta valida
`**User Story:**` o `**Historia de Usuario:**` y texto arbitrario, el requisito
resultante debe contener exactamente el primer texto de historia reconocido con
whitespace de bordes eliminado; etiquetas negritas no reconocidas no deben
modificarlo.

**Validates: Requirements 1.4**

### Property 4: Identidad, estado y orden de tareas

For any lista generada de tareas con IDs numericos de una o mas partes separadas
por puntos y estados de checkbox espacio, `x` o `X`, `parse_tasks` debe conservar
cada ID completo y el orden documental, mapear solo el espacio a `False`, mapear
`x` y `X` a `True`, y asociar las referencias subordinadas con la tarea que las
precede.

**Validates: Requirements 1.6**

## Error Handling

- Lineas parecidas pero fuera de la gramatica reconocida se ignoran; no producen
  objetos parciales ni excepciones de parseo.
- Un requisito sin historia, sin seccion de criterios o con seccion vacia conserva
  valores vacios y no interrumpe el siguiente requisito.
- Checkboxes con estados distintos de espacio, `x` o `X`, o tareas sin ID numerico,
  se ignoran. Los errores reales de lectura de `Path` conservan el comportamiento
  normal de I/O y no se silencian.
- `load_spec` conserva listas vacias para `requirements.md` o `tasks.md` ausentes.
- Spec sin requisitos: exit code 2 con mensaje claro.
- Fallo de git: exit code 2.
- Fallo de Bedrock: warning y fallback heuristico, exit code segun --fail-under.

## Testing Strategy

La tarea 8 usa pruebas unitarias de ejemplo, regresion y property-based testing
sobre funciones puras. No se necesita una propiedad round-trip: el parser descarta
marcadores, encabezados y whitespace deliberadamente, por lo que no existe una
serializacion inversa fiel.

### Fixtures nuevos de tarea 8

Se agregaran al menos estos cuatro archivos, pequenos y legibles:

1. `tests/fixtures/requirements_heading_variants.md`: niveles `##` a `####`,
   `Requirement`/`Requisito`, con/sin colon, titulos ausentes, encabezados no
   reconocidos, limites de cuerpo y orden.
2. `tests/fixtures/requirements_criteria_variants.md`: entradas `1.`, `2)`, `-` y
   `*`, whitespace, listas-cebo fuera de la seccion, orden y una subseccion que
   termina el estado de criterios.
3. `tests/fixtures/requirements_stories_empty_sections.md`: ambas etiquetas
   negritas, secciones vacias y requisitos sin seccion seguidos de un requisito
   poblado para probar continuidad.
4. `tests/fixtures/tasks_nested_ids_states.md`: IDs como `8`, `8.1` y
   `8.1.2.3`, estados espacio/`x`/`X`, referencias, orden y checkboxes invalidos.

### Pruebas de ejemplo y regresion

- Extender `tests/test_spec_parser.py` con pruebas parametrizadas sobre los cuatro
  fixtures y aserciones de IDs, titulos, historias, criterios, estados, referencias
  y orden exactos.
- Mantener sin cambios los fixtures canonicos existentes
  `tests/fixtures/requirements.md` y `tests/fixtures/tasks.md`; sus pruebas actuales
  deben seguir pasando para detectar regresiones del formato ya soportado.
- Agregar smoke tests de `parse_requirements(path: Path) -> list[Requirement]`,
  `parse_tasks(path: Path) -> list[SpecTask]` y
  `load_spec(spec_dir: Path) -> tuple[list[Requirement], list[SpecTask]]`, incluida
  la respuesta de `load_spec` cuando falta uno de los archivos.
- Cubrir ejemplos negativos: nivel `#` o `#####`, etiqueta desconocida, criterio
  fuera de seccion, checkbox invalido e ID de tarea no numerico.

### Property-based testing

Se usara Hypothesis como dependencia exclusiva del extra `dev`, fijada a una
version exacta al implementarse; no se agrega ninguna dependencia al nucleo. Cada
propiedad tendra un unico test con minimo 100 ejemplos y generadores acotados de
lineas Markdown/Unicode para mantener las pruebas rapidas en Python 3.10+.

Cada test incluira un comentario con este formato y el texto de su propiedad:

```text
Feature: specguard-core, Property 1: Reconocimiento, orden y aislamiento de requisitos
```

Los cuatro tests corresponderan uno-a-uno con las propiedades 1-4. Los generadores
construiran archivos temporales y modelos esperados desde componentes separados,
para no duplicar la regex productiva como oraculo. Las pruebas de ejemplo cubren
casos concretos y errores; las propiedades cubren combinaciones amplias sin
multiplicar unit tests redundantes.

Finalmente se ejecutaran `pytest` y `ruff check src tests`. El modulo
`kiro_spec.py`, el archivo de pruebas y cada fixture se mantendran por debajo de
300 lineas.
