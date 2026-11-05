# ADR 001: Alcance funcional acotado e interfaz de consola en Python 3.13

- **Estado:** Aceptado
- **Fecha:** Noviembre de 2026
- **Referencia:** `estado-inicial` (commit `e5d6927`)

## Contexto
El Trabajo Práctico Integrador de Metodología de Sistemas II requiere partir de un sistema base funcional que permita diagnosticar deuda técnica, identificar *code smells*, aplicar principios SOLID/Clean Code y ejecutar refactorings seguros verificando que no se introduzcan regresiones en el comportamiento externo. Necesitamos definir el dominio, el alcance operativo y el stack tecnológico inicial sin que la complejidad accidental de infraestructura (frameworks web, motores de bases de datos o interfaces gráficas) desvíe el foco del diseño interno.

## Alternativas consideradas
1. **Aplicación web (FastAPI / Flask + HTML/React):** Aporta una interfaz visual atractiva, pero introduce capas de ruteo HTTP, plantillas y serialización que diluyen el tiempo disponible para el diagnóstico y refactoring del dominio.
2. **Interfaz gráfica de escritorio (Tkinter / PyQt):** Acopla el ciclo de vida de la aplicación a eventos de ventana y dificulta la automatización sencilla de pruebas de regresión sobre la entrada/salida.
3. **Aplicación de consola (CLI) en Python 3.13 usando únicamente la biblioteca estándar:** Permite implementar de forma directa las reglas de negocio de una agenda hospitalaria, facilita la reproducción determinista de la demo y concentra el análisis en la estructura del código.

## Decisión
Adoptamos el dominio de **agenda de turnos para la recepción del Hospital Central**, operado por consola en **Python 3.13** utilizando exclusivamente su biblioteca estándar:
- **Alcance incluido:** Tres entidades principales (`Paciente`, `Profesional`, `Turno`), cinco operaciones de negocio más listado de pacientes, seis franjas horarias fijas de 30 minutos (`09:00` a `11:30`), validaciones de no solapamiento por profesional y por paciente, y uso exclusivo de datos sintéticos ficticios sin DNI ni información médica sensible.
- **Fuera de alcance:** Facturación, obras sociales, urgencias, notificaciones, autenticación de usuarios e interfaz web.

## Consecuencias
- **Positivas:** Cero dependencias externas de ejecución (cualquier integrante o docente puede correr `python main.py` directamente); reglas de negocio claras y verificables mediante los 7 pasos de la demo; base ideal para contrastar calidad externa vs. calidad interna.
- **Negativas / Límites:** La interfaz de texto solo permite interacción local secuencial de un operador por vez y en la versión inicial (`estado-inicial`) propició que `main.py` concentrara demasiada lógica de control (hallazgo H1) y acoplamiento con las estructuras de datos (hallazgo H8), lo cual será abordado en la etapa de refactoring.