# Producto: SpecGuard

SpecGuard audita la trazabilidad entre un spec de Kiro y el codigo que dice
implementarlo. Responde cuatro preguntas sobre cada pull request:

1. Que requisitos estan cubiertos por codigo real.
2. Que tareas fueron marcadas como completas sin cambio de codigo asociado (tareas fantasma).
3. Que codigo no tiene requisito que lo respalde (codigo huerfano / scope creep).
4. Que criterios de aceptacion no tienen ningun test que los valide.

## Problema que resuelve

En el desarrollo guiado por agentes, el cuello de botella dejo de ser escribir
codigo: es verificarlo. Los agentes marcan tareas como completas y el humano
confia. SpecGuard cierra ese ciclo haciendo verificable el spec-driven development.

## Usuarios

Equipos que usan Kiro con specs (.kiro/specs/) y quieren garantia de que cada
merge implementa lo que el spec promete.

## Principios de producto

- El resultado heuristico debe ser util sin LLM; la capa semantica solo refina.
- Toda salida debe ser accionable: cada hallazgo apunta a un requisito, tarea o archivo concreto.
- La herramienta se audita a si misma: este repositorio corre SpecGuard sobre sus propios specs.
