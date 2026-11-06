# Revisión final con el checklist

Aplicamos el checklist de [checklist-code-review.md](checklist-code-review.md) sobre el código final, commit `465cc5e`, que ya incluye los refactorings de H2, H3, H1 y H5 y H6, y la corrección de H9. Después de ese commit solo se sumó documentación, así que el código de `main` es el mismo. Lo revisamos sobre una copia limpia del commit, sin el entorno virtual ni el archivo de trabajo local.

## Resultado por categoría

| Categoría | Resultado | Cómo lo comprobamos |
|---|---|---|
| Lógica y funcionalidad | Cumple | La demo completa, los dieciséis casos de borde, el caso de H11 y el doble conflicto dan la misma salida que `estado-inicial`: 403 líneas iguales y el mismo archivo final. Los casos que pide el checklist (fecha inválida, franja ocupada y turno ya cancelado) se rechazan con el mismo mensaje que en la versión inicial. |
| Legibilidad | Cumple, con una observación | Ninguna función pasa de 35 líneas. `main()` tiene 20, y `reservar_turno`, la más larga, hace un control por línea. Las búsquedas usan `paciente`, `profesional` y `turno`. Queda un `lambda t` en `historial_paciente` (observación 1). |
| Diseño | Cumple, con una observación | `gestion.py` solo importa `dataclasses` y `datetime`, y el único módulo que lee o escribe el archivo es `persistencia.py`. La búsqueda por número está en una sola función, `buscar_por_id`. La consola todavía lee `datos["profesionales"]` y las claves internas de la agenda (H8, observación 2). |
| Manejo de errores | Cumple en el uso normal | Ningún error se pierde sin aviso. Hay cuatro `except`. Tres convierten una entrada inválida en un mensaje claro: el número no entero, la fecha inválida y el JSON mal escrito. El cuarto, el del guardado, borra el temporal y vuelve a lanzar el error. Los fallos de H4 siguen como en el diagnóstico (observación 3). |
| Seguridad y datos | Cumple | Se validan los números, la fecha, la franja y el nombre vacío. `datos/ejemplo.json` solo trae personas ficticias. En Git solo está `datos/ejemplo.json`; `local.json` y `local.json.tmp` están en `.gitignore`. |
| Rendimiento | Cumple | El archivo se lee una sola vez, al abrir el programa, y se escribe solo cuando una operación se acepta. Lo comprobamos con cuatro operaciones rechazadas seguidas, y `local.json` quedó con los mismos bytes. |
| Pruebas | Cumple, con una observación | Pasan las 20 pruebas, Black y flake8, en la copia local y en la CI. Cada cambio tiene su prueba: la precedencia del doble conflicto (H1), el guardado fallido (H9) y las llamadas con `SolicitudTurno` (H6). Las pruebas cubren `hospital/`, no la consola (observación 4). |

SonarQube sobre el mismo commit da 0 problemas, contra los 4 de la versión inicial, y ninguna función con complejidad cognitiva mayor a 15. El detalle está en la sección 4 de [diagnostico.md](diagnostico.md).

## Observaciones

**1. Nombre de una letra en el orden del historial**
- **Qué vemos:** `historial_paciente` ordena con `lambda t: (t["fecha"], t["hora"], t["id"])`.
- **Por qué importa:** es el único nombre de una letra que queda, y en H2 cambiamos justamente ese tipo de nombres.
- **Qué proponemos:** `lambda turno:`. No cambia el comportamiento; queda para un próximo cambio, porque el código ya está cerrado.

**2. La consola conoce la forma interna de los datos (H8)**
- **Qué vemos:** `opcion_reservar_turno` recorre `datos["profesionales"]`, y `opcion_consultar_agenda` lee `franja["turno"]["turno_id"]`.
- **Por qué importa:** si cambia la estructura de los datos, hay que tocar también la consola.
- **Qué proponemos:** funciones de consulta en `gestion.py`. Ya figura en las mejoras futuras.

**3. Errores sin controlar al cargar o al leer (H4)**
- **Qué vemos:** con `local.json` en `[]` el programa se corta con `TypeError`, y en `{}`, con `KeyError`. Si faltan los dos archivos, se corta con `FileNotFoundError`, y si se cierra la entrada, con `EOFError`. El JSON mal escrito sí se informa con un aviso.
- **Por qué importa:** la persona que lo usa ve un error técnico en lugar de un aviso.
- **Qué proponemos:** validar la estructura al cargar y atrapar esos errores. Ya figura en las mejoras futuras.

**4. La consola no tiene pruebas automatizadas**
- **Qué vemos:** las pruebas importan solo `hospital.gestion` y `hospital.persistencia`.
- **Por qué importa:** las pruebas no detectan un cambio en `main.py`.
- **Qué proponemos:** por ahora, la consola se comprueba comparando la salida completa con la de la versión inicial. Una mejora sería probarla con entradas simuladas.

## Criterios de aceptación técnica sobre la versión final

| Criterio | Estado |
|---|---|
| Pasan las pruebas, Black y flake8 | Sí: 20 pruebas, en local y en la CI |
| No rompe funcionalidades ni cambia las reglas | Sí: la salida es igual a la de la versión inicial |
| Respeta los principios de diseño y las convenciones | Sí, con H8 como mejora futura |
| Maneja los errores sin ocultarlos | Sí: ningún error se pierde sin aviso; H4 queda como mejora futura |
| No agrega deuda técnica innecesaria | Sí: SonarQube pasó de 4 problemas a 0 |
| Lo revisó otro integrante | Sí: cada Pull Request integrado tuvo un revisor distinto del autor |

Ninguna observación frena la entrega. Las cuatro quedan registradas, y la 2 y la 3 ya están en las mejoras futuras del diagnóstico.
