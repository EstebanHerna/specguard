# Convenciones del proyecto

## Codigo
- Codigo, identificadores y mensajes de commit en ingles.
- Sin comentarios en el codigo salvo que expliquen un porque no obvio.
- Type hints en todas las firmas publicas.
- snake_case para funciones y variables, PascalCase para clases.
- Maximo 100 caracteres por linea (configurado en ruff).
- Ningun archivo de mas de 300 lineas; si crece, se divide por responsabilidad.

## Documentacion
- Documentacion de usuario en espanol (README, docs/).
- Cada modulo nuevo requiere su entrada en docs/architecture.md.

## Git
- Commits atomicos con formato: tipo(alcance): descripcion (ej. feat(parser): support Spanish EARS headers).
- Referenciar la tarea del spec en el cuerpo del commit cuando aplique (Task: 2.1).
- Nunca commitear credenciales ni variables de entorno.

## Trabajo con specs
- Todo feature nuevo nace como spec en .kiro/specs/<nombre>/ antes de escribir codigo.
- No marcar una tarea como completa sin el codigo y el test correspondiente.
- Correr specguard audit antes de cada PR: la herramienta se aplica a si misma.
