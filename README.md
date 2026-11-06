# Hospital Central: agenda de turnos

Trabajo Práctico Integrador de Metodología de Sistemas II (UTN, Tecnicatura Universitaria en Programación a Distancia), Comisión 15.

Es una agenda de turnos para la recepción de un hospital: registrar pacientes, reservar y cancelar turnos y consultar la agenda de cada profesional y los turnos de cada paciente. Funciona por consola y guarda los datos en un archivo JSON.

Sobre la versión inicial (tag `estado-inicial`) hicimos el diagnóstico de calidad, cuatro refactorings, una corrección del guardado, pruebas automatizadas y la revisión de código. La versión final está en el tag `estadorefactorizado` y conserva el mismo comportamiento visible.

## Integrantes

- Agustín Emiliano Sotelo Carmelich
- Bruno Giuliano Vapore
- Santiago Octavio Varela

## Tecnologías

- **Python 3.13**, solo con la biblioteca estándar (`json`, `pathlib`, `dataclasses`, `datetime`, `os` y `shutil`). El programa no tiene dependencias.
- **unittest** y **tempfile** para las pruebas.
- **Black 26.10.0** para el formato y **flake8 7.4.1** para el estilo (`requirements-dev.txt`).
- **GitHub Actions** para la integración continua (`.github/workflows/ci.yml`).
- **SonarQube Community Build 26.9** para el análisis estático del diagnóstico. No hace falta para usar el programa.
- **Git y GitHub**, con issues, milestones y Pull Requests revisados por otro integrante.

## Estructura

```text
main.py                    consola: el menú y una función por opción
hospital/gestion.py        reglas de la agenda y SolicitudTurno
hospital/persistencia.py   carga y guardado del archivo JSON
datos/ejemplo.json         datos ficticios de partida
tests/                     20 pruebas de pacientes, turnos y persistencia
docs/                      diagnóstico, refactorings, checklist, decisiones y evidencias
.github/workflows/ci.yml   integración continua
```

## Cómo usarlo

Solo hace falta Python 3.13. Se puede ejecutar desde cualquier carpeta, porque las rutas de los datos se arman a partir de la ubicación de `main.py`.

En macOS y Linux:

```bash
python3 main.py
```

En Windows (PowerShell o cmd):

```powershell
py main.py
```

Si hay varias versiones de Python instaladas, en Windows se puede elegir con `py -3.13 main.py`, y en macOS y Linux con `python3.13 main.py`.

La primera vez se crea `datos/local.json` a partir de `datos/ejemplo.json`, que trae cuatro profesionales y dos pacientes ficticios. Los cambios se guardan en `datos/local.json` (no se sube al repositorio). Para volver a los datos de ejemplo, se borra ese archivo.

El menú tiene estas opciones:

```text
1. Registrar paciente
2. Listar pacientes
3. Reservar turno
4. Cancelar turno
5. Consultar la agenda de un profesional
6. Consultar los turnos de un paciente
0. Salir
```

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
7. Opción 0 para salir, volver a ejecutar el programa y consultar la opción 5 y la opción 6 con el paciente 1: el turno 2 sigue en la agenda y el turno 1 aparece cancelado en el historial de Ana.

## Pruebas y estilo

Las pruebas no necesitan nada más que Python:

```bash
python3 -m unittest discover -s tests -v   # macOS y Linux
py -m unittest discover -s tests -v        # Windows
```

Para Black y flake8 hace falta un entorno virtual con las herramientas de desarrollo.

En macOS y Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

En Windows, con PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

En cmd, el entorno se activa con `.venv\Scripts\activate.bat`. Si PowerShell no deja ejecutar `Activate.ps1`, se puede usar cmd.

Con el entorno activado, en cualquier sistema:

```bash
python -m black --check .
python -m flake8 .
```

La configuración de flake8 está en `setup.cfg` y acepta el largo de línea y los espacios que deja Black, para que las dos herramientas no se contradigan.

La integración continua corre Black, flake8 y las pruebas en cada push y en cada Pull Request. `main` no acepta un cambio si esos controles no pasan o si no lo aprobó otro integrante.

## Documentación

- [`docs/diagnostico.md`](docs/diagnostico.md): la calidad externa e interna, los once hallazgos, el análisis de SonarQube de la versión inicial y de la final, y el estado de cada hallazgo.
- [`docs/refactorings.md`](docs/refactorings.md): cada refactoring, con el código antes y después, sus commits y cómo se comprobó.
- [`docs/checklist-code-review.md`](docs/checklist-code-review.md): el checklist de revisión y los criterios de aceptación.
- [`docs/adr/`](docs/adr/): las decisiones técnicas (alcance y consola, persistencia en JSON y flujo de trabajo en Git).
- [`docs/evidencias/`](docs/evidencias/): las capturas de SonarQube.

## Tags

| Tag | Qué marca |
|---|---|
| `estado-inicial` | La versión inicial, antes de refactorizar |
| `etapa-diagnostico` | El diagnóstico documentado |
| `etapa-refactoring` | Los refactorings integrados y documentados |
| `etapa-pruebas` | La verificación final con las pruebas |
| `estadorefactorizado` | El código final, revisado y comprobado |
| `etapa-docs` | La documentación final y los enlaces |

## Entrega

Los enlaces al informe y al video se agregan con la entrega final (#32).
