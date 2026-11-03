# Hospital Central: agenda de turnos

Trabajo Práctico Integrador de Metodología de Sistemas II (UTN, Tecnicatura Universitaria en Programación a Distancia), Comisión 15.

Es una agenda de turnos para la recepción de un hospital: registrar pacientes, reservar y cancelar turnos y consultar la agenda de cada profesional. Funciona por consola y guarda los datos en un archivo JSON.

Sobre esta base vamos a hacer el diagnóstico de calidad, los refactorings y la revisión de código que pide el TPI.

## Integrantes

- Agustín Emiliano Sotelo Carmelich
- Bruno Giuliano Vapore
- Santiago Octavio Varela

## Preparar el entorno

Usamos Python 3.13. El programa no necesita dependencias; Black y flake8 son solo para revisar el formato y el estilo.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Antes de subir un cambio conviene correr:

```bash
python -m black --check .
python -m flake8 .
```

La configuración de flake8 está en `setup.cfg` y acepta el largo de línea y los espacios que deja Black, para que las dos herramientas no se contradigan.

## Cómo usarlo

```bash
python main.py
```

La primera vez se crea `datos/local.json` a partir de `datos/ejemplo.json`, que trae cuatro profesionales y dos pacientes ficticios. Los cambios se guardan en `datos/local.json` (no se sube al repositorio). Para volver a los datos de ejemplo, se borra ese archivo.

El menú tiene estas opciones:

1. Registrar paciente
2. Listar pacientes
3. Reservar turno
4. Cancelar turno
5. Consultar la agenda de un profesional
6. Consultar los turnos de un paciente

## Reglas

- Los números de paciente y de turno se generan solos y no se repiten, aunque haya turnos cancelados.
- El nombre del paciente no puede estar vacío y se le quitan los espacios de los extremos. Dos pacientes pueden llamarse igual.
- Para reservar tienen que existir el paciente y el profesional.
- La fecha va como `AAAA-MM-DD` y tiene que ser válida.
- Los turnos duran 30 minutos, en las franjas `09:00`, `09:30`, `10:00`, `10:30`, `11:00` y `11:30`.
- Ni el profesional ni el paciente pueden tener dos turnos activos en la misma fecha y franja.
- Un turno nuevo queda `ACTIVO`; al cancelarlo pasa a `CANCELADO` y se conserva en el historial.
- Cancelar un turno que no existe o que ya estaba cancelado avisa y no cambia nada.
- Una operación rechazada no modifica los datos.
- Las consultas salen ordenadas por fecha, horario y número de turno.
- Los cambios aceptados se mantienen al cerrar y volver a abrir el programa.
- Si `datos/local.json` está dañado, el programa avisa y se cierra sin sobrescribirlo.

## Demo

Partiendo de los datos de ejemplo (sin `datos/local.json`):

1. Opción 5, profesional 1, fecha `2026-11-10`: las seis franjas están libres.
2. Opción 3: paciente 1 (Ana Gómez), profesional 1, `2026-11-10`, `09:00`. Se reserva el turno 1.
3. Opción 3: paciente 2 (Carlos Ruiz), profesional 1, misma fecha y horario. Se rechaza porque el profesional está ocupado.
4. Opción 3: paciente 1, profesional 2, misma fecha y horario. Se rechaza porque Ana ya tiene un turno a esa hora.
5. Opción 4: turno 1. Queda cancelado.
6. Opción 3: paciente 2, profesional 1, `2026-11-10`, `09:00`. Ahora se reserva (turno 2).
7. Opción 0 para salir, volver a ejecutar `python main.py` y consultar la opción 5 y la opción 6 con el paciente 1: el turno 2 sigue en la agenda y el turno 1 aparece cancelado en el historial de Ana.
