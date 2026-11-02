# Hospital Central: agenda de turnos

Trabajo Práctico Integrador de Metodología de Sistemas II (UTN, Tecnicatura Universitaria en Programación a Distancia), Comisión 4.

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

## Estado

En construcción. Las instrucciones de uso se agregan cuando esté la primera versión.
