# ADR 003: Flujo de trabajo colaborativo en Git, estilo de código y trazabilidad

- **Estado:** Aceptado
- **Fecha:** Noviembre de 2026
- **Referencia:** `estado-inicial` (commit `e5d6927`)

## Contexto
El desarrollo del TPI se realiza en equipo (tres integrantes) y exige demostrar participación equilibrada, trazabilidad completa entre problemas detectados, cambios realizados y pruebas ejecutadas, además de aplicar un proceso formal de *Code Review* y señalizar cada hito con tags específicos requeridos por la cátedra.

## Alternativas consideradas
1. **Commits directos sobre la rama `main`:** Rápido para cambios individuales pequeños, pero impide realizar revisiones de código previas a la integración, dificulta asociar evidencias y aumenta el riesgo de conflictos o roturas.
2. **Gitflow completo (ramas `develop`, `release`, `hotfix`):** Excesivamente burocrático para un proyecto académico acotado de tres integrantes.
3. **GitHub Flow basado en Issues, ramas cortas por tarea y Pull Requests con revisión obligatoria:** Equilibra agilidad con trazabilidad documental y permite auditar qué hizo y qué revisó cada integrante.

## Decisión
Adoptamos un flujo colaborativo estructurado en GitHub bajo las siguientes normas:
- **Trazabilidad por Issues y ramas:** Todo cambio parte de un Issue con criterios de cierre explícitos ("Para cerrarla") y se desarrolla en una rama específica (`feat/...`, `refactor/...`, `docs/...`, `test/...`).
- **Estandarización de formato y estilo:** Se utiliza **Black** para el formateo automático y **flake8** para el análisis de estilo PEP 8, configurados de manera compatible en `setup.cfg` para evitar contradicciones entre ambas herramientas.
- **Revisión técnica en Pull Requests:** Ninguna rama se integra a `main` sin un Pull Request revisado por otro integrante del equipo aplicando el checklist técnico del proyecto (lógica, legibilidad, diseño, manejo de errores, datos sintéticos, rendimiento y pruebas) y adjuntando evidencia de funcionamiento.
- **Hitos mediante Tags de Git:** Se marcan los estados obligatorios en `main` mediante los tags `estado-inicial`, `etapa-diagnostico`, `etapa-refactoring`, `etapa-pruebas`, `etapa-docs` y `estadorefactorizado`.

## Consecuencias
- **Positivas:** Historial de commits limpio y auditable; evidencia concreta de *Code Review* en cada Pull Request para la Etapa 7 del informe; código uniforme en estilo desde el primer commit sin discusiones manuales de formato.
- **Negativas:** Requiere coordinación entre los integrantes para aprobar los Pull Requests antes de avanzar con ramas dependientes y disciplina para mantener sincronizada la documentación de `docs/` con el informe final.
